"""Measure the screen's ledge and FPC bond from the vector drawing on page 5 of design/datasheets/display_TOH095XVT-01.pdf.
Scale: the panel outline width is 12.8 mm and its length 27.35 mm (dimension text on the same page).
Prints the x and y of the long straight lines in the front view, in mm from the panel's top-left corner."""
import sys
import pymupdf

pdf = sys.argv[1]
doc = pymupdf.open(pdf)
pg = doc[4]
segs = []
for d in pg.get_drawings():
    for it in d["items"]:
        if it[0] == "l":
            a, b = it[1], it[2]
            segs.append((a.x, a.y, b.x, b.y))
        elif it[0] == "re":
            r = it[1]
            segs += [(r.x0, r.y0, r.x1, r.y0), (r.x0, r.y1, r.x1, r.y1), (r.x0, r.y0, r.x0, r.y1), (r.x1, r.y0, r.x1, r.y1)]
# front view lies in x 190..330 pt (the left drawing); vertical lines = panel sides, horizontal lines = glass edges
fv = [s for s in segs if 200 <= min(s[0], s[2]) <= 320 and 100 <= min(s[1], s[3]) <= 300]
horiz = sorted({(round(s[1], 2), round(min(s[0], s[2]), 2), round(max(s[0], s[2]), 2)) for s in fv if abs(s[1] - s[3]) < 0.01 and abs(s[0] - s[2]) > 20})
vert = sorted({(round(s[0], 2), round(min(s[1], s[3]), 2), round(max(s[1], s[3]), 2)) for s in fv if abs(s[0] - s[2]) < 0.01 and abs(s[1] - s[3]) > 3})
print("horizontal lines (y pt, x0 pt, x1 pt):")
for h in horiz:
    print("  ", h)
print("vertical lines (x pt, y0 pt, y1 pt):")
for v in vert:
    print("  ", v)
# derived values: panel = the longest vertical pair; upper glass end = the full-width horizontal line just above the panel end
side = [v for v in vert if v[2] - v[1] > 130]
xl, xr = min(v[0] for v in side), max(v[0] for v in side)
yt, yb = min(v[1] for v in side), max(v[2] for v in side)
sx, sy = (xr - xl) / 12.8, (yb - yt) / 27.35
xc = (xl + xr) / 2
full = [h for h in horiz if abs(h[1] - xl) < 0.05 and abs(h[2] - xr) < 0.05 and yt + 1 < h[0] < yb - 1]
y_upper = max(h[0] for h in full)
fing = [v for v in vert if v[2] - v[1] < 6 and v[1] > y_upper]
fpc = [v for v in vert if v[1] > y_upper and v[2] - v[1] > 30 and xl - 2 < v[0] < xr + 2]
print(f"scale x {sx:.4f} pt/mm, y {sy:.4f} pt/mm; panel x {xl}..{xr} pt, y {yt}..{yb} pt")
print(f"ledge (lower glass only) length from the panel end: {(yb - y_upper) / sy:.3f} mm")
print(f"bond fingers: {len(fing)} lines, from {(yb - max(f[2] for f in fing)) / sy:.3f} to {(yb - min(f[1] for f in fing)) / sy:.3f} mm from the panel end; across {(min(f[0] for f in fing) - xc) / sx:.3f} to {(max(f[0] for f in fing) - xc) / sx:.3f} mm from the centre line")
print(f"FPC outline: across {(min(f[0] for f in fpc) - xc) / sx:.3f} to {(max(f[0] for f in fpc) - xc) / sx:.3f} mm; starts {(yb - min(f[1] for f in fpc)) / sy:.3f} mm inside the panel end; full width to {(max(f[2] for f in fpc) - yb) / sy:.3f} mm beyond the panel end")
aa = [v for v in vert if abs(v[1] - 127.11) < 0.05]
if aa:
    print(f"active area along the panel: {(aa[0][1] - yt) / sy:.3f} mm from the far end, {(yb - aa[0][2]) / sy:.3f} mm from the ledge end")
# model coordinates (placement.csv row screen: X -13.675 at the ledge end)
X0 = -13.675
print(f"in model X: ledge X {X0:.3f} to {X0 + (yb - y_upper) / sy:.3f}; bond fingers X {X0 + (yb - max(f[2] for f in fing)) / sy:.3f} to {X0 + (yb - min(f[1] for f in fing)) / sy:.3f}; FPC on the glass from X {X0:.3f} to {X0 + (yb - min(f[1] for f in fpc)) / sy:.3f}")
