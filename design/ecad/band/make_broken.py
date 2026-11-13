#!/usr/bin/env python3
"""Writes three broken copies of a good board into evidence/broken/ (KiCad Python).
 swapped : the two charging pad discs CP1 and CP2 of flex2-us9 swap places (a line leads to the wrong pad)
 missing : the land footprint PRT1 of flex2-us9 is removed
 length  : every outline point of flex1-us9 beyond u = 8 moves 0.30 mm outward (tail 0.30 mm too long)"""
import os, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "evidence", "broken")
os.makedirs(OUT, exist_ok=True)
OX = 50.0

b = pcbnew.LoadBoard(os.path.join(HERE, "flex2-us9.kicad_pcb"))
fps = {f.GetReference(): f for f in b.GetFootprints()}
p1, p2 = fps["CP1"].GetPosition(), fps["CP2"].GetPosition()
fps["CP1"].SetPosition(p2); fps["CP2"].SetPosition(p1)
pcbnew.SaveBoard(os.path.join(OUT, "flex2-us9.kicad_pcb"), b)
os.replace(os.path.join(OUT, "flex2-us9.kicad_pcb"), os.path.join(OUT, "broken_swapped_flex2-us9.kicad_pcb"))

b = pcbnew.LoadBoard(os.path.join(HERE, "flex2-us9.kicad_pcb"))
for f in b.GetFootprints():
    if f.GetReference() == "PRT1":
        b.Remove(f)
pcbnew.SaveBoard(os.path.join(OUT, "broken_missing_flex2-us9.kicad_pcb"), b)

b = pcbnew.LoadBoard(os.path.join(HERE, "flex1-us9.kicad_pcb"))
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        for get, setter in ((d.GetStart, d.SetStart), (d.GetEnd, d.SetEnd)):
            p = get()
            if ToMM(p.x) - OX > 8.0:
                setter(VECTOR2I(p.x + FromMM(0.30), p.y))
pcbnew.SaveBoard(os.path.join(OUT, "broken_length_flex1-us9.kicad_pcb"), b)
b = pcbnew.LoadBoard(os.path.join(HERE, "flex1-us9.kicad_pcb"))
fa = [f for f in b.GetFootprints() if f.GetReference() == "J_BAND_A"][0]
pd = {p.GetNumber(): p for p in fa.Pads()}
q1, q4 = pd["1"].GetPosition(), pd["4"].GetPosition()
pd["1"].SetPosition(q4); pd["4"].SetPosition(q1)
pcbnew.SaveBoard(os.path.join(OUT, "broken_mate_flex1-us9.kicad_pcb"), b)
print("written", sorted(os.listdir(OUT)))
