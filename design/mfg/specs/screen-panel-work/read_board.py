"""Read-only look at the routed ring board (design/ecad/ring/pcb/ring.kicad_pcb) with KiCad's pcbnew.
Run: design/ecad/ring/pcb/run_kipy.sh <this file> <board> > logs/read_board.log 2>&1
Prints: outline box, copper layer count, thickness setting, per face: parts, courtyard area (union by a 0.05 grid),
free area of the board outline per face, the hand-end regions used by the connection options, copper (tracks, vias,
pads) per layer inside those regions. Model coordinates = KiCad - 100 (placement-final.csv columns)."""
import sys
import pcbnew

B = pcbnew.LoadBoard(sys.argv[1])
MM = 1e6
OFF = 100.0


def mm(v):
    return v / MM


bb = B.GetBoardEdgesBoundingBox()
x0, y0, x1, y1 = mm(bb.GetX()) - OFF, mm(bb.GetY()) - OFF, mm(bb.GetRight()) - OFF, mm(bb.GetBottom()) - OFF
print(f"board file {sys.argv[1]}")
print(f"outline box X {x0:.3f}..{x1:.3f} Y {y0:.3f}..{y1:.3f} size {x1 - x0:.3f} x {y1 - y0:.3f}")
print(f"copper layers {B.GetCopperLayerCount()}")
ds = B.GetDesignSettings()
print(f"board thickness setting {mm(ds.GetBoardThickness()):.3f}")

# outline polygon for area
outline = pcbnew.SHAPE_POLY_SET()
B.GetBoardPolygonOutlines(outline, False)
print(f"outline area {outline.Area() / MM / MM:.3f} mm2")

STEP = 0.05


def in_outline(x, y):
    return outline.Contains(pcbnew.VECTOR2I(int((x + OFF) * MM), int((y + OFF) * MM)))


# courtyards per face
faces = {"F": pcbnew.F_CrtYd, "B": pcbnew.B_CrtYd}
cy = {"F": [], "B": []}
parts = {"F": [], "B": []}
for fp in B.GetFootprints():
    side = "B" if fp.IsFlipped() else "F"
    ref = fp.GetReference()
    parts[side].append(ref)
    poly = fp.GetCourtyard(faces[side])
    if poly.OutlineCount() == 0:
        r = fp.GetBoundingBox(False, False)
        cy[side].append((ref, mm(r.GetX()) - OFF, mm(r.GetY()) - OFF, mm(r.GetRight()) - OFF, mm(r.GetBottom()) - OFF, None))
    else:
        r = poly.BBox()
        cy[side].append((ref, mm(r.GetX()) - OFF, mm(r.GetY()) - OFF, mm(r.GetRight()) - OFF, mm(r.GetBottom()) - OFF, poly))
for s in ("F", "B"):
    print(f"face {s} ({'under face, toward the floor' if s == 'F' else 'screen face'}): {len(parts[s])} parts: {' '.join(sorted(parts[s]))}")


def covered(side, x, y):
    p = pcbnew.VECTOR2I(int((x + OFF) * MM), int((y + OFF) * MM))
    for ref, a, b, c, d, poly in cy[side]:
        if a <= x <= c and b <= y <= d:
            if poly is None or poly.Contains(p):
                return ref
    return None


def grid(xa, xb, ya, yb):
    n = 0
    x = xa + STEP / 2
    while x < xb:
        y = ya + STEP / 2
        while y < yb:
            yield x, y
            y += STEP
        x += STEP


def area_stats(side, xa, xb, ya, yb):
    tot = cov = 0
    refs = set()
    for x, y in grid(xa, xb, ya, yb):
        if not in_outline(x, y):
            continue
        tot += 1
        r = covered(side, x, y)
        if r:
            cov += 1
            refs.add(r)
    a = STEP * STEP
    return tot * a, cov * a, sorted(refs)


for s in ("F", "B"):
    t, c, _ = area_stats(s, x0, x1, y0, y1)
    print(f"face {s}: outline {t:.2f} mm2 (grid 0.05), courtyards {c:.2f} mm2, free {t - c:.2f} mm2 ({100 * (t - c) / t:.1f} percent)")

# regions of the connection options (model coordinates)
REG = {
    "A: J1 land field, under face, hand end (thin model v9 J1 at -11.650,-0.150, 3.35 x 6.1 turned 270)": ("F", -13.325, -9.975, -3.200, 2.900),
    "A: tail run under the board end from the board edge to J1's entry": ("F", -13.600, -13.325, -2.550, 2.250),
    "B1: 15 hot-bar lands on the screen face at the hand end (strip 1.2 x 5.0)": ("B", -13.600, -12.400, -2.650, 2.350),
    "B2: 15 hot-bar lands on the under face at the hand end (strip 1.2 x 5.0)": ("F", -13.600, -12.400, -2.650, 2.350),
    "hand-end strip X -13.6 to -8.75 (all Y), under face": ("F", -13.600, -8.750, -6.300, 6.300),
    "hand-end strip X -13.6 to -8.75 (all Y), screen face": ("B", -13.600, -8.750, -6.300, 6.300),
    "antenna copper-free zone X -13.60..-8.75, Y 3.10..6.30": ("F", -13.600, -8.750, 3.100, 6.300),
}

tracks = list(B.GetTracks())
pads = [p for fp in B.GetFootprints() for p in fp.Pads()]
lname = {l: B.GetLayerName(l) for l in range(pcbnew.PCB_LAYER_ID_COUNT) if pcbnew.IsCopperLayer(l)}
cu_layers = [l for l in lname if B.IsLayerEnabled(l)]


def copper_in(xa, xb, ya, yb):
    out = {}
    box = pcbnew.BOX2I(pcbnew.VECTOR2I(int((xa + OFF) * MM), int((ya + OFF) * MM)), pcbnew.VECTOR2L(int((xb - xa) * MM), int((yb - ya) * MM)))
    for t in tracks:
        if t.GetBoundingBox().Intersects(box):
            if t.Type() == pcbnew.PCB_VIA_T:
                key = ("via", t.GetNetname())
            else:
                key = (B.GetLayerName(t.GetLayer()), t.GetNetname())
            out[key] = out.get(key, 0) + 1
    for p in pads:
        if p.GetBoundingBox().Intersects(box):
            for l in cu_layers:
                if p.IsOnLayer(l):
                    key = ("pad " + B.GetLayerName(l), p.GetParentFootprint().GetReference() + ":" + p.GetNetname())
                    out[key] = out.get(key, 0) + 1
    zones = []
    for z in B.Zones():
        if z.GetBoundingBox().Intersects(box):
            zones.append((z.GetNetname(), ",".join(B.GetLayerName(l) for l in z.GetLayerSet().Seq()), z.GetIsRuleArea()))
    return out, zones


for name, (s, xa, xb, ya, yb) in REG.items():
    t, c, refs = area_stats(s, xa, xb, ya, yb)
    print(f"REGION {name}: face {s} X {xa}..{xb} Y {ya}..{yb}: inside outline {t:.2f} mm2, under courtyards {c:.2f} mm2 ({', '.join(refs) or 'none'})")
    cu, zones = copper_in(xa, xb, ya, yb)
    by_layer = {}
    for (lay, net), n in sorted(cu.items()):
        by_layer.setdefault(lay, []).append(f"{net}x{n}")
    for lay, items in by_layer.items():
        print(f"   copper {lay}: {len(items)} nets: {' '.join(items)}")
    for zn in zones:
        print(f"   zone net {zn[0] or '-'} layers {zn[1]} rule_area {zn[2]}")

# J1 and the nets on it today
for fp in B.GetFootprints():
    if fp.GetReference() == "J1":
        pos = fp.GetPosition()
        print(f"J1 today: side {'B' if fp.IsFlipped() else 'F'} at ({mm(pos.x) - OFF:.3f}, {mm(pos.y) - OFF:.3f}) turn {fp.GetOrientationDegrees():.1f}")
        for p in fp.Pads():
            print(f"   J1 pad {p.GetNumber()} net {p.GetNetname()}")
print("RESULT read done")

# rule areas (keep-outs) and the J1 nets: routed length per layer, vias, far end
print("RULE AREAS")
for z in B.Zones():
    if z.GetIsRuleArea():
        r = z.GetBoundingBox()
        print(f"   rule area '{z.GetZoneName()}' layers {','.join(B.GetLayerName(l) for l in z.GetLayerSet().Seq())} box X {mm(r.GetX()) - OFF:.3f}..{mm(r.GetRight()) - OFF:.3f} Y {mm(r.GetY()) - OFF:.3f}..{mm(r.GetBottom()) - OFF:.3f} no_tracks {z.GetDoNotAllowTracks()} no_vias {z.GetDoNotAllowVias()} no_fp {z.GetDoNotAllowFootprints()}")
JN = ["ELVSS", "ELVDD", "VDD_3V0", "VDD_1V8", "SWIRE", "LCD_TE", "LCD_RST", "LCD_CS", "LCD_SCK", "LCD_DCX", "LCD_MOSI"]
print("J1 NETS (tracks of the net anywhere on the board)")
for n in JN:
    L = {}
    nv = 0
    for t in tracks:
        if t.GetNetname() != n:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            nv += 1
        else:
            k = B.GetLayerName(t.GetLayer())
            L[k] = L.get(k, 0) + mm(t.GetLength())
    ends = [f"{p.GetParentFootprint().GetReference()}.{p.GetNumber()}@({mm(p.GetPosition().x) - OFF:.2f},{mm(p.GetPosition().y) - OFF:.2f})" for p in pads if p.GetNetname() == n]
    print(f"   {n}: length {' '.join(f'{k} {v:.2f}' for k, v in sorted(L.items()))} total {sum(L.values()):.2f} mm, vias {nv}, pads {' '.join(ends)}")
print("RESULT read2 done")
