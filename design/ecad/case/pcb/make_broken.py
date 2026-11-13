#!/usr/bin/env python3
"""Writes four broken copies of case_main.kicad_pcb into pcb/broken/ (KiCad's Python), one fault each:
  broken_wrongnet   pad 1 of R3 moved to net GND (the netlist says 3V3)
  broken_outside    U4 moved 60 mm to the right (outside the outline)
  broken_notrack    the longest track of net SD_D0 deleted (unconnected item)
  broken_nopart     R30 removed
usage: run_kipy.sh make_broken.py [good board]"""
import os, shutil, sys
import pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
GOOD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "case_main.kicad_pcb")
OUT = os.path.join(HERE, "broken")
os.makedirs(OUT, exist_ok=True)


def fresh(name):
    b = pcbnew.LoadBoard(GOOD)
    pro = GOOD.replace(".kicad_pcb", ".kicad_pro")
    shutil.copy(pro, os.path.join(OUT, name + ".kicad_pro"))
    return b


def save(b, name):
    pcbnew.SaveBoard(os.path.join(OUT, name + ".kicad_pcb"), b)
    print("wrote", name)


b = fresh("broken_wrongnet")
gnd = [n for n in b.GetNetsByNetcode().values() if n.GetNetname() == "GND"][0]
for fp in b.GetFootprints():
    if fp.GetReference() == "R3":
        for p in fp.Pads():
            if p.GetNumber() == "1":
                print("R3.1 was", p.GetNetname())
                p.SetNet(gnd)
save(b, "broken_wrongnet")
b = fresh("broken_outside")
for fp in b.GetFootprints():
    if fp.GetReference() == "U4":
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(pos.x + pcbnew.FromMM(60), pos.y))
save(b, "broken_outside")
b = fresh("broken_notrack")
tr = [t for t in b.GetTracks() if t.GetNetname() == "SD_D0" and t.Type() == pcbnew.PCB_TRACE_T]
tr.sort(key=lambda t: -t.GetLength())
print("deleting a track of SD_D0, length %.3f mm" % pcbnew.ToMM(tr[0].GetLength()))
b.Remove(tr[0])
save(b, "broken_notrack")
b = fresh("broken_nopart")
for fp in list(b.GetFootprints()):
    if fp.GetReference() == "R30":
        b.Remove(fp)
save(b, "broken_nopart")
