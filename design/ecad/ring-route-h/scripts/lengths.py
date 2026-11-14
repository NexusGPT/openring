# lengths.py base new : track length and via count per J1 net, and GND pour area per copper layer, base and new
import sys, pcbnew
from pcbnew import ToMM
NETS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["DECA", "DECD", "VDD_1V8", "VSET1", "VSET2", "XL1", "XL2"]
A = pcbnew.LoadBoard(sys.argv[1]); B = pcbnew.LoadBoard(sys.argv[2])
def stats(b, n):
    L = sum(ToMM(t.GetLength()) for t in b.GetTracks() if t.GetNetname() == n and t.Type() != pcbnew.PCB_VIA_T)
    V = sum(1 for t in b.GetTracks() if t.GetNetname() == n and t.Type() == pcbnew.PCB_VIA_T)
    return L, V
for n in NETS:
    (la, va), (lb, vb) = stats(A, n), stats(B, n)
    print("net %-9s track base %7.3f mm new %7.3f mm (%+.3f), vias base %2d new %2d" % (n, la, lb, lb - la, va, vb))
def pour(b):
    r = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "GND": continue
        for l in z.GetLayerSet().CuStack(): r[b.GetLayerName(l)] = r.get(b.GetLayerName(l), 0) + z.GetFilledPolysList(l).Area() / 1e12
    return r
pa, pb = pour(A), pour(B)
for k in sorted(pa): print("GND pour %-6s base %8.3f mm2 new %8.3f mm2 (%+.3f)" % (k, pa[k], pb.get(k, 0), pb.get(k, 0) - pa[k]))
print("lengths done")
