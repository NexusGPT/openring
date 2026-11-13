# move.py ref x y rot reason : changes one row of placement-final.csv (kicad_x, kicad_y follow) and logs it
import csv, sys
p=(__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/placement-final.csv")
ref, x, y, rot, why = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
rows = list(csv.DictReader(open(p))); hdr = list(rows[0].keys()); n = 0
for r in rows:
    if r['reference'] == ref:
        print('move %s (%s, %s, %s) -> (%.3f, %.3f, %s): %s' % (ref, r['x_mm'], r['y_mm'], r['rotation_deg'], x, y, rot, why))
        r['x_mm'], r['y_mm'], r['rotation_deg'] = '%.3f' % x, '%.3f' % y, rot
        r['kicad_x'], r['kicad_y'] = '%.3f' % (x + 100), '%.3f' % (y + 100); n += 1
assert n == 1, (ref, n)
w = csv.DictWriter(open(p, 'w', newline=''), hdr); w.writeheader(); w.writerows(rows)
