import sys, pcbnew
from pcbnew import ToMM, FromMM, VECTOR2I
b = pcbnew.LoadBoard(sys.argv[1])
outl = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outl, False)
print("outline polys", outl.OutlineCount())
for i in range(outl.OutlineCount()):
    bb = outl.Outline(i).BBox(); print(i, ToMM(bb.GetLeft()), ToMM(bb.GetRight()), ToMM(bb.GetTop()), ToMM(bb.GetBottom()))
for x in (95.5, 96.5, 103.0, 103.5, 104.5):
    print(x, outl.Contains(VECTOR2I(FromMM(x), FromMM(98.4))))
