"""Adds four paste openings (F.Paste) over the spring pin pads P1 to P4 of case_pins.kicad_pcb. Add only: no pad, hole, track, zone or outline is touched.
Shape: a ring, outer dia 1.70 mm (the pad, p3_harwin_p70.txt line 68) and inner dia 1.10 mm (the hole, line 69), drawn as one circle outline of dia 1.40 mm with stroke 0.30 mm. Idempotent.
usage: add_pin_paste.py <board>"""
import sys, pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
path = sys.argv[1]
b = pcbnew.LoadBoard(path)
have = [d for d in b.GetDrawings() if d.GetClass() == "PCB_SHAPE" and d.GetLayer() == pcbnew.F_Paste]
n = 0
for f in b.GetFootprints():
    if f.GetReference() not in ("P1", "P2", "P3", "P4"):
        continue
    pad = [p for p in f.Pads()][0]
    c = pad.GetPosition()
    if any(abs(d.GetCenter().x - c.x) < 10 and abs(d.GetCenter().y - c.y) < 10 for d in have):
        print("exists", f.GetReference()); continue
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetLayer(pcbnew.F_Paste)
    s.SetCenter(c); s.SetEnd(VECTOR2I(c.x + FromMM(0.70), c.y))
    s.SetFilled(False); s.SetWidth(FromMM(0.30))
    b.Add(s); n += 1
    print("added", f.GetReference(), "at %.3f %.3f" % (ToMM(c.x), ToMM(c.y)))
b.Save(path)
print("DONE added", n)
