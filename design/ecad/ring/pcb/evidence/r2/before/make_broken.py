#!/usr/bin/env python3
"""make_broken.py <kind> <out folder> -- writes <out>/broken_<kind>.kicad_pcb, a broken copy of ring.kicad_pcb, with the
project, rules and library table beside it, for the check_board.py failure proof. Kinds:
  net      a wrong net on a pad (U1 A4 put on GND)
  outside  a part moved outside the outline (C79 12 mm toward +X)
  track    a routed track deleted (the longest unlocked track)
  missing  a part missing (C5 removed)
  antvia   a via inside the antenna copper-free zone (GND stack at (-11.0, 4.0))
  swap     one ball's escape swapped (U1 B4 and D5: via spans and escape layers exchanged)
Run with ./run_kipy.sh make_broken.py <kind> <folder>"""
import os, shutil, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
H = os.path.dirname(os.path.abspath(__file__))
kind, outdir = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(os.path.join(H, "ring.kicad_pcb"))
def fp(ref): return [f for f in b.GetFootprints() if f.GetReference() == ref][0]
if kind == "net":
    [x for x in fp("U1").Pads() if x.GetNumber() == "A4"][0].SetNet(b.FindNet("GND"))
elif kind == "outside":
    c = fp("C79"); c.SetPosition(c.GetPosition() + VECTOR2I(FromMM(12), 0))
elif kind == "track":
    t = max([t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and not t.IsLocked()], key=lambda t: t.GetLength())
    print("deleted", t.GetNetname(), b.GetLayerName(t.GetLayer()), round(ToMM(t.GetLength()), 3))
    b.Remove(t)
elif kind == "missing":
    b.Remove(fp("C5"))
elif kind == "antvia":
    v = pcbnew.PCB_VIA(b); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetPosition(VECTOR2I(FromMM(100 - 11.0), FromMM(100 + 4.0))); v.SetWidth(FromMM(0.2)); v.SetDrill(FromMM(0.1))
    v.SetNet(b.FindNet("GND")); b.Add(v)
elif kind == "swap":
    pads = {p.GetNumber(): p.GetPosition() for p in fp("U1").Pads()}
    at = lambda p, q: abs(p.x - q.x) < 2000 and abs(p.y - q.y) < 2000
    vb4 = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and at(t.GetPosition(), pads["B4"])][0]
    vd5 = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and at(t.GetPosition(), pads["D5"])][0]
    l4, l5 = (vb4.TopLayer(), vb4.BottomLayer()), (vd5.TopLayer(), vd5.BottomLayer())
    vb4.SetLayerPair(*l5); vd5.SetLayerPair(*l4)
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T and (at(t.GetStart(), pads["B4"]) or at(t.GetEnd(), pads["B4"])) and t.GetLayer() == pcbnew.In1_Cu:
            t.SetLayer(pcbnew.In2_Cu)
        elif t.Type() == pcbnew.PCB_TRACE_T and (at(t.GetStart(), pads["D5"]) or at(t.GetEnd(), pads["D5"])) and t.GetLayer() == pcbnew.In2_Cu:
            t.SetLayer(pcbnew.In1_Cu)
os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, "broken_%s.kicad_pcb" % kind)
pcbnew.SaveBoard(out, b)
shutil.copy(os.path.join(H, "ring.kicad_pro"), out[:-10] + ".kicad_pro")
shutil.copy(os.path.join(H, "ring.kicad_dru"), out[:-10] + ".kicad_dru")
open(os.path.join(outdir, "fp-lib-table"), "w").write(open(os.path.join(H, "fp-lib-table")).read().replace("${KIPRJMOD}", H))
print("written", out)
