# make_broken.py in out REF dx dy : copy of the board with footprint REF moved by (dx, dy) mm, nothing else changed
import sys, pcbnew
from pcbnew import FromMM, VECTOR2I
b = pcbnew.LoadBoard(sys.argv[1]); m = b.FindFootprintByReference(sys.argv[3])
p = m.GetPosition(); m.SetPosition(VECTOR2I(p.x + FromMM(float(sys.argv[4])), p.y + FromMM(float(sys.argv[5]))))
b.Save(sys.argv[2]); print("moved", sys.argv[3], "by", sys.argv[4], sys.argv[5], "saved", sys.argv[2])
