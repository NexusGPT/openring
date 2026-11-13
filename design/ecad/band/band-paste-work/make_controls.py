#!/usr/bin/env python3
"""Broken copies of delivered boards for the controls (run with run_kipy.sh). Writes into <out>:
  ctl-paste1/flex1-us9.kicad_pcb : F.Paste removed from one switch land (SW2 pad 1)
  ctl-paste2/flex2-us9.kicad_pcb : one B.Paste disc removed
  ctl-label/flex1-us9.kicad_pcb  : the drawing text 'LAND 7 = VMOT ...' removed
  ctl-copper/flex2-us9.kicad_pcb : one track moved 0.1 mm (for the dump compare)
usage: run_kipy.sh make_controls.py <band dir> <out dir>"""
import os, shutil, sys
import pcbnew
from pcbnew import FromMM, VECTOR2I

band, out = sys.argv[1], sys.argv[2]


def load(name, sub):
    d = os.path.join(out, sub)
    os.makedirs(d, exist_ok=True)
    for ext in (".kicad_pro", ".kicad_dru"):
        shutil.copy(os.path.join(band, name + ext), d)
    return pcbnew.LoadBoard(os.path.join(band, name + ".kicad_pcb")), os.path.join(d, name + ".kicad_pcb")


b, p = load("flex1-us9", "ctl-paste1")
for fp in b.GetFootprints():
    if fp.GetReference() == "SW2":
        for pad in fp.Pads():
            if pad.GetNumber() == "1":
                ls = pad.GetLayerSet(); ls.RemoveLayer(pcbnew.F_Paste); pad.SetLayerSet(ls)
                print("removed F.Paste from SW2 pad 1")
pcbnew.SaveBoard(p, b)

b, p = load("flex2-us9", "ctl-paste2")
discs = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.B_Paste]
b.Remove(discs[0])
print("removed one B.Paste disc of", len(discs))
pcbnew.SaveBoard(p, b)

b, p = load("flex1-us9", "ctl-label")
for d in list(b.GetDrawings()):
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetText().startswith("LAND 7 = VMOT"):
        b.Remove(d)
        print("removed text", repr(d.GetText()))
pcbnew.SaveBoard(p, b)

b, p = load("flex2-us9", "ctl-copper")
t = [x for x in b.GetTracks() if x.Type() != pcbnew.PCB_VIA_T][0]
t.SetEnd(t.GetEnd() + VECTOR2I(FromMM(0.1), 0))
print("moved the end of one track by 0.1 mm, net", t.GetNetname())
pcbnew.SaveBoard(p, b)
print("controls written")
