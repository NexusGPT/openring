# readback_placement.py board table : every row of the placement table against the board: the footprint exists, its library name,
# side (F = F.Cu, B = B.Cu), x and y (0.0005 mm), rotation (mod 360), kicad_x and kicad_y; and every board footprint has a row.
# Prints each mismatch, then RESULT PASS/FAIL; exit 1 on any mismatch.
import sys, csv, pcbnew
from pcbnew import ToMM
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1]); bad = []; n = 0
fps = {m.GetReference(): m for m in b.GetFootprints()}
seen = set()
for r in csv.DictReader(open(sys.argv[2], newline="")):
    ref = r["reference"]; n += 1; seen.add(ref)
    m = fps.get(ref)
    if m is None: bad.append("%s: no footprint on the board" % ref); continue
    lib = "%s:%s" % (m.GetFPID().GetLibNickname(), m.GetFPID().GetLibItemName())
    x, y = ToMM(m.GetPosition().x), ToMM(m.GetPosition().y)
    side = "F" if m.GetLayer() == pcbnew.F_Cu else "B"
    rot = round(m.GetOrientationDegrees()) % 360
    for name, ok, have in (("footprint", r["footprint"] == lib, lib), ("side", r["side"] == side, side),
                           ("x_mm", abs(float(r["x_mm"]) - (x - O)) < 5e-4, "%.3f" % (x - O)), ("y_mm", abs(float(r["y_mm"]) - (y - O)) < 5e-4, "%.3f" % (y - O)),
                           ("rotation_deg", int(float(r["rotation_deg"])) % 360 == rot, rot),
                           ("kicad_x", abs(float(r["kicad_x"]) - x) < 5e-4, "%.3f" % x), ("kicad_y", abs(float(r["kicad_y"]) - y) < 5e-4, "%.3f" % y)):
        if not ok: bad.append("%s %s: table %s, board %s" % (ref, name, r[name], have))
for ref in sorted(set(fps) - seen): bad.append("%s: on the board, no row in the table" % ref)
for x in bad: print("FAIL", x)
print("rows checked", n, "board footprints", len(fps))
print("RESULT", "PASS" if not bad else "FAIL %d" % len(bad))
sys.exit(1 if bad else 0)
