"""Pads of the parts used as board-side probe points (copy of ring.kicad_pcb). usage: run_kipy.sh dump_probe_pads.py <board> <out>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
want = {"C83", "C84", "U11", "R1", "C71", "C72", "C28", "C29", "R61", "R62"}
out = ["ref,pad,net,side,x_model,y_model,size_x,size_y"]
for fp in b.GetFootprints():
    if fp.GetReference() in want:
        for p in fp.Pads():
            c, s = p.GetPosition(), p.GetSize()
            out.append(f"{fp.GetReference()},{p.GetNumber()},{p.GetNetname()},{'F' if fp.GetLayer() == pcbnew.F_Cu else 'B'},{c.x/1e6-100:.3f},{c.y/1e6-100:.3f},{s.x/1e6:.3f},{s.y/1e6:.3f}")
open(sys.argv[2], "w").write("\n".join(sorted(out)) + "\n")
print(len(out) - 1, "pads")
