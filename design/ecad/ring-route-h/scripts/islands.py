# islands.py board : for each GND zone fill outline on every copper layer, its bbox, area and how many GND vias / through-pads touch it
import sys, pcbnew
from pcbnew import ToMM, VECTOR2I
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1])
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == "GND"]
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() != "GND": continue
    for l in z.GetLayerSet().CuStack():
        f = z.GetFilledPolysList(l)
        for i in range(f.OutlineCount()):
            one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(f.COutline(i))
            for h in range(f.HoleCount(i)): one.AddHole(f.CHole(i, h))
            n = sum(1 for v in vias if v.IsOnLayer(l) and one.Contains(v.GetPosition()))
            bb = one.BBox()
            print("%-6s outline %3d area %8.4f mm2 GND vias %3d bbox x %.3f..%.3f y %.3f..%.3f" % (b.GetLayerName(l), i, one.Area() / 1e12, n, ToMM(bb.GetLeft()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetBottom()) - O))
