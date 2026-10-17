"""Decimate board meshes (colour-preserving), read board BOMs, write elec.json for the viewer."""
import json, base64, glob, numpy as np, openpyxl, fast_simplification
from scipy.spatial import cKDTree

BOARDS = {  # key: (title, part no, revision, qty, function, target tris)
 'main':     ('RBE-MAIN-RK3588S', 'YCL.E000278', 'V1.6.1pro', 1, 'Main controller: RK3588 SoC (6 TOPS NPU, 8 GB LPDDR4x, 32 GB eMMC) + 480 MHz real-time MCU; power-sequencing hub, 5x CAN-FD, e-stop.', 70000),
 'backhub':  ('RBE-PWR-BACKHUB', 'YCL.E000191', 'V2.1', 1, 'Back interface board: USB/Type-C/GbE expansion, power routing, 30 V small-battery charge/discharge, Jetson NX slot.', 70000),
 'chg140':   ('RBE-PWR-140WCHG', 'YCL.E000223', 'V1.0', 1, '140 W charging management for the 48 V main battery (charging dock).', 40000),
 'hotswap':  ('RBE-PWR-HOTSWAP', 'YCL.E000268', 'V2.0', 1, 'Small-battery (30 V) protection board, hot-swappable backup power.', 25000),
 'mingmei':  ('RBE-PWR-MINGMEI-BC', 'YCL.E000060', 'V1.1', 1, '48 V battery-pack adapter board.', 8800),
 'head':     ('RBE-PWR-HEAD', 'YCL.E000225', 'V2.0', 1, 'Head board: mic array, speaker system, HD camera, MIPI display, on-board AI voice engine.', 60000),
 'imu':      ('RBE-SENS-IMU', 'YCL.E000059', 'V1.0', 1, 'High-precision IMU for biped balance, placed away from motor power loops.', 12000),
 'fan':      ('RBE-PWR-FAN', 'YCL.E000062', 'V2.0', 1, 'Hip cooling-fan power and speed control board.', 12000),
 'mcap':     ('RBE-PWR-MCAP', 'YCL.E000057', 'V3.1', 2, 'Motor capacitor board: local bulk energy storage, absorbs commutation spikes, stabilises the bus.', 14800),
 'hand':     ('RBE-PWR-HANDPlusPro', 'YCL.E000211', 'V1.0', 2, 'Hand adapter board: interface between hand-joint harness and main controller.', 12000),
 'comm433':  ('RBE-COMM-433TX', 'YCL.E000212', 'V1.0', 1, '433 MHz transmitter board (wireless e-stop link).', 12000),
 'lamp':     ('LOGO lamp board', 'YCL.E000063', 'V2.0', 1, 'LOGO status light board, driven directly by the main controller.', 12000),
 'indicator':('Back power indicator', 'YCL.E000255', 'V1.0', 1, 'Externally visible power / charge status LED.', 7800),
 'fpc':      ('USB3.0 FPC flex board', 'YCL.E000270', 'V1.0', 1, 'High-speed differential link between the main board and the back interface board.', 900),
}
BOMFILE = {'main':'03_RBE-MAIN','backhub':'12_RBE_PWR_BACKHUB','chg140':'11_RBE_PWR_140WCHG','hotswap':'07_RBE-PWR-HOTSWAP',
 'head':'06_RBE-PWR-HEAD','imu':'10_RBE-SENS-IMU','fan':'04_RBE-PWR-FAN','mcap':'08_RBE-PWR-MCAP','hand':'05_RBE-PWR-HAND',
 'comm433':'02_RBE-COMM','lamp':'13_','indicator':'14_','fpc':'01_FPC'}

def bom(key):
    if key not in BOMFILE: return None
    f = [g for g in glob.glob('hw/pcb/02_PCB__*01_BOM*.xlsx') if f'02_PCB__{BOMFILE[key]}' in g][0]
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0]
    rows = [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
    hdr = [str(c) for c in rows[0]]
    ci, cq, cd = hdr.index('Comment'), hdr.index('Quantity'), hdr.index('Designator')
    lines = [r for r in rows[1:] if r[cq]]
    total = sum(int(r[cq]) for r in lines)
    key_parts = []
    for r in lines:
        d = str(r[cd] or '')
        if d[:1] in 'UJQXYMLDKT' and not d.startswith(('D', 'L')) or d.startswith(('U', 'J', 'Y', 'X', 'M', 'Q')):
            key_parts.append(str(r[ci])[:30])
    seen, uniq = set(), []
    for k in key_parts:
        if k not in seen: seen.add(k); uniq.append(k)
    return dict(lines=len(lines), parts=total, key=uniq[:6])

blob = bytearray(); out = {}
for key, (title, pn, rev, qty, fn, target) in BOARDS.items():
    z = np.load(f'hw/mesh/{key}.npz'); P = z['p'].astype(np.float64); I = z['i'].astype(np.int64); C = z['c']
    lo, hi = P.min(0), P.max(0)
    ctr = np.array([(lo[0]+hi[0])/2, (lo[1]+hi[1])/2, 0.0])   # centre in plane; z=0 stays at STEP board datum
    P = P - ctr
    n0 = len(I)
    if n0 > target:
        # colour-class-wise decimation: each class keeps its exact colour and cannot bleed into its neighbours
        q = (C[I[:, 0]].astype(int) // 32)
        cls = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
        ratio = target / n0
        Ps, Is, Cs, nv = [], [], [], 0
        for c in np.unique(cls):
            fi = I[cls == c]
            used, inv = np.unique(fi, return_inverse=True)
            vp, fp = P[used], inv.reshape(-1, 3)
            col = np.round(C[fi[:, 0]].mean(0)).astype('u1')
            want = max(40, int(len(fp) * ratio))
            if want < len(fp):
                vp, fp = fast_simplification.simplify(vp.astype(np.float32), fp.astype(np.int32), target_reduction=1 - want/len(fp), agg=3)
            Ps.append(vp); Is.append(fp.astype(np.int64) + nv); Cs.append(np.tile(col, (len(vp), 1))); nv += len(vp)
        P, I, C = np.vstack(Ps), np.vstack(Is), np.vstack(Cs)
    P = P.astype('<f4'); I = I.astype('<u4'); C = np.ascontiguousarray(C.astype('u1'))
    for arr in (P, I, C):
        blob += b'\0' * ((-len(blob)) % 4)
        pass
    def put(a):
        blob.extend(b'\0' * ((-len(blob)) % 4)); o = len(blob); blob.extend(a.tobytes()); return o
    vo, io, co = put(P), put(I), put(C)
    size = (hi - lo) * 1000
    out[key] = dict(title=title, pn=pn, rev=rev, qty=qty, fn=fn, vn=len(P), fnum=len(I), vo=vo, io=io, co=co,
                    size=[round(float(s), 1) for s in size], bom=bom(key), tris0=n0)
    print(f'{key:10s} {n0:7d} -> {len(I):6d} tris  size_mm {np.round(size,1)}')
json.dump(dict(boards=out, bin=base64.b64encode(bytes(blob)).decode()), open('elec.json', 'w'), separators=(',', ':'))
print('blob bytes', len(blob))
