# Writes a copy of a board with ONE track removed: the longest track of net <net>. Run with run_kipy.sh.
import pcbnew, sys
src, dst, net = sys.argv[1], sys.argv[2], sys.argv[3]
b = pcbnew.LoadBoard(src)
cands = [t for t in b.GetTracks() if t.GetNetname() == net and t.GetClass() == "PCB_TRACK"]
cands.sort(key=lambda t: -t.GetLength())
for t in cands[:1]:
    if True:
        print("removed track of %s from (%.3f,%.3f) to (%.3f,%.3f) on %s" % (net, pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y), pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y), b.GetLayerName(t.GetLayer())))
        b.Remove(t); break
pcbnew.SaveBoard(dst, b)
print("saved", dst)
