import sys, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(sys.argv[1])
for f in b.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox()
        print("PAD", f.GetReference(), p.GetNumber(), p.GetNetname(), "layers", [b.GetLayerName(l) for l in p.GetLayerSet().Seq()],
              "x %.3f..%.3f y %.3f..%.3f" % (ToMM(bb.GetLeft()), ToMM(bb.GetRight()), ToMM(bb.GetTop()), ToMM(bb.GetBottom())))
for d in b.GetDrawings():
    print("DRAW", d.GetClass(), b.GetLayerName(d.GetLayer()))
for t in b.GetTracks():
    bb = t.GetBoundingBox()
    print("TRK", t.GetClass(), b.GetLayerName(t.GetLayer()), t.GetNetname(), "x %.3f..%.3f y %.3f..%.3f" % (ToMM(bb.GetLeft()), ToMM(bb.GetRight()), ToMM(bb.GetTop()), ToMM(bb.GetBottom())))
for z in b.Zones():
    bb = z.GetBoundingBox()
    print("ZONE", z.GetNetname(), [b.GetLayerName(l) for l in z.GetLayerSet().Seq()], "x %.3f..%.3f y %.3f..%.3f" % (ToMM(bb.GetLeft()), ToMM(bb.GetRight()), ToMM(bb.GetTop()), ToMM(bb.GetBottom())))
