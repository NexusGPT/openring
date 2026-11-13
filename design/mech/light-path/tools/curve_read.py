"""Read a datasheet curve from the PDF's vector paths (no raster reading).
curve_read.py <pdf> <page> <x0,y0,x1,y1 plot box in pt> <xmin,xmax,ymin,ymax axis values> <x query list or 'y=' query list>
The axis values map to the box edges (left/right, bottom/top). Prints every non-grid polyline in the box and the
interpolated values at the queries. Gridlines (straight horizontal or vertical segments) are skipped."""
import sys
import pymupdf

pdf, page = sys.argv[1], int(sys.argv[2])
bx = [float(v) for v in sys.argv[3].split(",")]
ax = [float(v) for v in sys.argv[4].split(",")]
q = sys.argv[5]
doc = pymupdf.open(pdf)
pg = doc[page - 1]
pts = []
for d in pg.get_drawings():
    for it in d["items"]:
        if it[0] == "l":
            seg = [it[1], it[2]]
        elif it[0] == "c":
            seg = [it[1], it[2], it[3], it[4]]
        else:
            continue
        a, b = seg[0], seg[-1]
        if abs(a.x - b.x) < 0.05 or abs(a.y - b.y) < 0.05:
            continue  # grid or axis line
        for p in (a, b):
            if bx[0] - 0.5 <= p.x <= bx[2] + 0.5 and bx[1] - 0.5 <= p.y <= bx[3] + 0.5:
                pts.append((p.x, p.y))
pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))


def to_val(x, y):
    vx = ax[0] + (x - bx[0]) / (bx[2] - bx[0]) * (ax[1] - ax[0])
    vy = ax[2] + (bx[3] - y) / (bx[3] - bx[1]) * (ax[3] - ax[2])
    return vx, vy


vals = sorted(to_val(x, y) for x, y in pts)
print(f"{len(vals)} curve points in the box")
for vx, vy in vals:
    print(f"  x {vx:.4f}  y {vy:.4f}")
if q.startswith("y="):
    for t in (float(v) for v in q[2:].split(",")):
        s = sorted(vals, key=lambda p: p[1])
        for (x1, y1), (x2, y2) in zip(s, s[1:]):
            if y1 <= t <= y2 and y2 > y1:
                print(f"at y {t}: x {x1 + (t - y1) / (y2 - y1) * (x2 - x1):.4f}")
                break
        else:
            print(f"at y {t}: outside the curve")
else:
    for t in (float(v) for v in q.split(",")):
        for (x1, y1), (x2, y2) in zip(vals, vals[1:]):
            if x1 <= t <= x2 and x2 > x1:
                print(f"at x {t}: y {y1 + (t - x1) / (x2 - x1) * (y2 - y1):.4f}")
                break
        else:
            print(f"at x {t}: outside the curve")
