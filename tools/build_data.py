"""Parse RP1 URDF + decimate STL meshes -> compact JSON/binary payload for the HTML viewer."""
import sys, json, base64, math
import xml.etree.ElementTree as ET
import numpy as np, trimesh

DESC, OUT, TOTAL_TRIS = sys.argv[1], sys.argv[2], int(sys.argv[3])
root = ET.parse(f"{DESC}/urdf/rp1.urdf").getroot()

def vec(s, d=(0, 0, 0)):
    return [float(x) for x in s.split()] if s else list(d)

links = {}
for l in root.findall("link"):
    v = l.find("visual")
    mesh = v.find("geometry/mesh").get("filename").split("/")[-1]
    col = v.find("material/color").get("rgba").split()
    links[l.get("name")] = dict(
        mesh=mesh, color=[float(c) for c in col[:3]],
        vorigin=vec(v.find("origin").get("xyz")), vrpy=vec(v.find("origin").get("rpy")),
        mass=float(l.find("inertial/mass").get("value")),
    )
joints = []
for j in root.findall("joint"):
    lim = j.find("limit")
    joints.append(dict(
        name=j.get("name"), type=j.get("type"), parent=j.find("parent").get("link"),
        child=j.find("child").get("link"), xyz=vec(j.find("origin").get("xyz")),
        rpy=vec(j.find("origin").get("rpy")), axis=vec(j.find("axis").get("xyz") if j.find("axis") is not None else None, (0, 0, 1)),
        lower=float(lim.get("lower", 0)) if lim is not None else 0, upper=float(lim.get("upper", 0)) if lim is not None else 0,
        effort=float(lim.get("effort", 0)) if lim is not None else 0, velocity=float(lim.get("velocity", 0)) if lim is not None else 0,
    ))

meshes = {}
for n in links:
    m = trimesh.load(f"{DESC}/meshes/{links[n]['mesh']}", force="mesh")
    m.merge_vertices(); m.remove_unreferenced_vertices()
    meshes[n] = m
orig = sum(len(m.faces) for m in meshes.values())
ratio = min(1.0, TOTAL_TRIS / orig)
print("original tris", orig, "ratio", round(ratio, 3))

blob, parts = bytearray(), {}
total = 0
for n, m in meshes.items():
    target = max(400, int(len(m.faces) * ratio))
    if target < len(m.faces):
        m = m.simplify_quadric_decimation(face_count=target)
    v = np.asarray(m.vertices, dtype="<f4"); f = np.asarray(m.faces, dtype="<u4")
    pad = (-len(blob)) % 4; blob += b"\0" * pad
    vo = len(blob); blob += v.tobytes()
    io = len(blob); blob += f.tobytes()
    parts[n] = dict(vo=vo, vn=len(v), io=io, fn=len(f))
    total += len(f)
    print(f"{n:28s} {len(f):7d} tris")
print("final tris", total, "bytes", len(blob))

json.dump(dict(name=root.get("name"), links=links, joints=joints, parts=parts,
               bin=base64.b64encode(bytes(blob)).decode()), open(OUT, "w"), separators=(",", ":"))
