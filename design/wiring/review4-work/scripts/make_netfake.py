# Copy of a board with the net of one pad changed to another existing net. Run with run_kipy.sh.
import pcbnew, sys
src, dst, ref, pad, net = sys.argv[1:6]
b = pcbnew.LoadBoard(src)
n = b.FindNet(net)
for fp in b.GetFootprints():
    if fp.GetReference() == ref:
        for p in fp.Pads():
            if p.GetNumber() == pad:
                print("pad %s:%s net %s -> %s" % (ref, pad, p.GetNetname(), net)); p.SetNet(n)
pcbnew.SaveBoard(dst, b); print("saved", dst)
