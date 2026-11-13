"""Option D: what copper of a copy of ring.kicad_pcb lies (a) in the two edge notches X -3.55..-1.45, |Y| 5.305..6.30 on any layer,
(b) at the new B.Cu land field X -3.40..-1.60, |Y| 3.343..4.843 on B.Cu. usage: run_kipy.sh check_notch.py <board>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
def rects(y0, y1, x0, x1):
    return [(x0 + 100, x1 + 100, y0 + 100, y1 + 100), (x0 + 100, x1 + 100, -y1 + 100, -y0 + 100)]
areas = [("notch", rects(5.305, 6.30, -3.55, -1.45), None), ("B.Cu land field", rects(3.343, 4.843, -3.40, -1.60), pcbnew.B_Cu)]
for name, rs, lay in areas:
    for r in rs:
        box = pcbnew.BOX2I(pcbnew.VECTOR2I(int(r[0] * 1e6), int(r[2] * 1e6)), pcbnew.VECTOR2L(int((r[1] - r[0]) * 1e6), int((r[3] - r[2]) * 1e6)))
        found = {}
        for t in b.GetTracks():
            if lay is not None and t.GetClass() != "PCB_VIA" and t.GetLayer() != lay:
                continue
            if t.GetBoundingBox().Intersects(box):
                k = ("via" if t.GetClass() == "PCB_VIA" else "track " + b.GetLayerName(t.GetLayer())) + " " + t.GetNetname()
                found[k] = found.get(k, 0) + 1
        for z in b.Zones():
            for l in z.GetLayerSet().Seq():
                if lay is not None and l != lay:
                    continue
                poly = z.GetFilledPolysList(l)
                cx, cy = (r[0] + r[1]) / 2, (r[2] + r[3]) / 2
                if poly.Contains(pcbnew.VECTOR2I(int(cx * 1e6), int(cy * 1e6))):
                    k = f"zone fill {b.GetLayerName(l)} {z.GetNetname()} (at the centre)"
                    found[k] = found.get(k, 0) + 1
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if (lay is None or p.IsOnLayer(lay)) and p.GetBoundingBox().Intersects(box):
                    k = f"pad {fp.GetReference()}.{p.GetNumber()} {p.GetNetname()}"
                    found[k] = found.get(k, 0) + 1
        print(f"{name} X {r[0]-100:.2f}..{r[1]-100:.2f} Y {r[2]-100:.3f}..{r[3]-100:.3f}: " + ("; ".join(f"{k} x{v}" for k, v in sorted(found.items())) if found else "no copper"))
