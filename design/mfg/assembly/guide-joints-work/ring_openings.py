"""Independent check of the pin board paste file: its openings are stroked circles (D02 move, then G02/G03 arcs
with I/J offsets, drawn with a round aperture), not D03 flashes, so check_joints.py rule R4 (flashes only) cannot see
them. This reads every arc, takes its centre (start + I, J) and its radius, adds the aperture width, and matches each
ring to a pin pad of the pad dump (Gerber Y = -pad y, as R4 assumes).
Run: design/.venv/bin/python -I <this file> <gerber> <pads.csv>"""
import csv, math, re, sys

gbr, pads = sys.argv[1], sys.argv[2]
ap, cur, x, y, dec = {}, None, None, None, 6
rings = []
for raw in open(gbr, encoding="utf-8"):
    l = raw.strip()
    m = re.match(r"%ADD(\d+)C,([\d.]+)\*%", l)
    if m:
        ap[int(m.group(1))] = float(m.group(2))
        continue
    m = re.match(r"D(\d+)\*$", l)
    if m and int(m.group(1)) >= 10:
        cur = int(m.group(1))
        continue
    mx, my = re.search(r"X(-?\d+)", l), re.search(r"Y(-?\d+)", l)
    mi, mj = re.search(r"I(-?\d+)", l), re.search(r"J(-?\d+)", l)
    nx = int(mx.group(1)) / 10 ** dec if mx else x
    ny = int(my.group(1)) / 10 ** dec if my else y
    if l.endswith("D01*") and (mi or mj):
        i = int(mi.group(1)) / 10 ** dec if mi else 0.0
        j = int(mj.group(1)) / 10 ** dec if mj else 0.0
        cx, cy = x + i, y + j
        r = math.hypot(i, j)
        rings.append((round(cx, 4), round(cy, 4), r, ap.get(cur, 0.0)))
    if l.endswith("D03*"):
        print("FLASH", nx, ny)
    x, y = nx, ny
centres = {}
for cx, cy, r, w in rings:
    centres.setdefault((cx, cy), []).append((r, w))
print("arcs", len(rings), "distinct centres", len(centres))
pins = [p for p in csv.DictReader(open(pads, newline="")) if re.fullmatch(r"P[1-4]", p["ref"])]
found = 0
for p in sorted(pins, key=lambda p: p["ref"]):
    px, py = float(p["x_mm"]), -float(p["y_mm"])
    hit = [(c, v) for c, v in centres.items() if abs(c[0] - px) <= 0.02 and abs(c[1] - py) <= 0.02]
    if hit:
        (c, v) = hit[0]
        r, w = v[0]
        print("PIN %s pad %s (%.4f, %.4f): ring centre (%.4f, %.4f), inner diameter %.3f, outer diameter %.3f, pad %s x %s"
              % (p["ref"], p["pad"], px, py, c[0], c[1], 2 * r - w, 2 * r + w, p["w_mm"], p["h_mm"]))
        found += 1
    else:
        print("PIN %s pad %s (%.4f, %.4f): NO ring" % (p["ref"], p["pad"], px, py))
print("RESULT ring openings on pin pads: %d of %d" % (found, len(pins)))
