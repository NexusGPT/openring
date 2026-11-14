# update_placement.py board table : rewrite the rows of J1 and the eight parts in the placement table from the board (side F/B, x, y,
# rotation 0..359, zone text without commas, kicad_x, kicad_y); every other row, the row order and the CRLF line ends stay as they are. Prints each row before and after.
import sys, csv, pcbnew
from pcbnew import ToMM
O = 100.0
REFS = ["J1", "C1", "C2", "C5", "C7", "C14", "FB1", "R71", "R72"]
ZONE = {"J1": "A2 under face hand end (board A2 2026-11-13)"}
b = pcbnew.LoadBoard(sys.argv[1])
rows = list(csv.reader(open(sys.argv[2], newline="")))
head = rows[0]; ix = {k: i for i, k in enumerate(head)}
n = 0
for r in rows[1:]:
    ref = r[ix["reference"]]
    if ref not in REFS: continue
    m = b.FindFootprintByReference(ref)
    x, y = ToMM(m.GetPosition().x), ToMM(m.GetPosition().y)
    old = list(r)
    r[ix["side"]] = "F" if m.GetLayer() == pcbnew.F_Cu else "B"
    r[ix["x_mm"]] = "%.3f" % (x - O); r[ix["y_mm"]] = "%.3f" % (y - O)
    r[ix["rotation_deg"]] = "%d" % (round(m.GetOrientationDegrees()) % 360)
    r[ix["zone"]] = ZONE.get(ref, "A2 under face (board A2 2026-11-13)")
    r[ix["kicad_x"]] = "%.3f" % x; r[ix["kicad_y"]] = "%.3f" % y
    print("before", ",".join(old)); print("after ", ",".join(r)); n += 1
with open(sys.argv[2], "w", newline="") as f:
    csv.writer(f, lineterminator="\r\n").writerows(rows)  # the table uses CRLF line ends
print("rows changed", n, "of", len(rows) - 1)
