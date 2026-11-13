# rm_tp.py <in board> <out board>: removes footprints TP8, TP9, TP11 (no net, no copper, checked by tp_copper.py), saves,
# then reloads both boards and prints their counts
import sys, pcbnew
def counts(b):
    t = list(b.GetTracks())
    return len(b.GetFootprints()), sum(1 for x in t if x.Type() == pcbnew.PCB_VIA_T), sum(1 for x in t if x.Type() != pcbnew.PCB_VIA_T), b.GetAreaCount()
b = pcbnew.LoadBoard(sys.argv[1])
refs = [f.GetReference() for f in b.GetFootprints() if f.GetReference() in ("TP8", "TP9", "TP11")]
for r in refs:
    f = b.FindFootprintByReference(r)
    assert all(p.GetNetCode() == 0 for p in f.Pads()), r
    b.Delete(f); print("removed", r)
pcbnew.SaveBoard(sys.argv[2], b)
print("saved", sys.argv[2])
print("in:  footprints %d, vias %d, tracks %d, zones %d" % counts(pcbnew.LoadBoard(sys.argv[1])))
print("out: footprints %d, vias %d, tracks %d, zones %d" % counts(pcbnew.LoadBoard(sys.argv[2])))
