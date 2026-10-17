"""STEP (XCAF, coloured) -> merged triangle mesh with per-vertex colour. Units mm -> metres.
usage: step2mesh.py in.step out.npz [min_diag_mm] [deflection_mm]"""
import sys, numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool, XCAFDoc_ColorType
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

src, dst = sys.argv[1], sys.argv[2]
MIN_DIAG = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
DEFL = float(sys.argv[4]) if len(sys.argv) > 4 else 0.1
ANG = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6

app = XCAFApp_Application.GetApplication_s()
doc = TDocStd_Document(TCollection_ExtendedString("MDTV-XCAF"))
app.InitDocument(doc)
rd = STEPCAFControl_Reader(); rd.SetColorMode(True); rd.SetNameMode(False)
assert rd.ReadFile(src) == 1, "read failed"
rd.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

def label_color(lab):
    return shape_color(XCAFDoc_ShapeTool.GetShape_s(lab))
def shape_color(shp):
    c = Quantity_Color()
    for t in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        if ct.GetColor(shp, t, c): return (c.Red(), c.Green(), c.Blue())
    return None

P, I, C = [], [], []; nv = 0; skipped = 0
def emit(shape, loc, col):
    global nv, skipped
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box)
    if box.IsVoid(): return
    x0, y0, z0, x1, y1, z1 = box.Get()
    if ((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2) ** .5 < MIN_DIAG: skipped += 1; return
    BRepMesh_IncrementalMesh(shape, DEFL, False, ANG, True)
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current())
        fl = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, fl)
        if tri is not None:
            tr = (loc * fl).Transformation()
            fc = shape_color(f) or col or (0.55, 0.55, 0.55)
            n = tri.NbNodes()
            pts = np.empty((n, 3))
            for i in range(1, n + 1):
                p = tri.Node(i).Transformed(tr); pts[i-1] = (p.X(), p.Y(), p.Z())
            rev = f.Orientation() == TopAbs_REVERSED
            idx = np.empty((tri.NbTriangles(), 3), dtype=np.int64)
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                idx[i-1] = (a, c, b) if rev else (a, b, c)
            P.append(pts); I.append(idx - 1 + nv); C.append(np.tile(fc, (n, 1))); nv += n
        ex.Next()

def walk(lab, loc, col):
    col = label_color(lab) or col
    if st.IsAssembly_s(lab):
        seq = TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab, seq)
        for i in range(1, seq.Length() + 1):
            comp = seq.Value(i)
            cl = XCAFDoc_ShapeTool.GetLocation_s(comp)
            ref = TDF_Label()
            if XCAFDoc_ShapeTool.GetReferredShape_s(comp, ref):
                walk(ref, loc * cl, label_color(comp) or col)
    else:
        emit(XCAFDoc_ShapeTool.GetShape_s(lab), loc, col)

free = TDF_LabelSequence(); st.GetFreeShapes(free)
for i in range(1, free.Length() + 1): walk(free.Value(i), TopLoc_Location(), None)

P = np.vstack(P) * 0.001; I = np.vstack(I); C = np.vstack(C)
np.savez_compressed(dst, p=P.astype('f4'), i=I.astype('u4'), c=(C * 255).round().astype('u1'))
lo, hi = P.min(0), P.max(0)
print(f"{src.split('/')[-1][:40]}: {len(I)} tris, skipped {skipped}, size_mm {np.round((hi-lo)*1000,1)}, min_mm {np.round(lo*1000,1)}")
