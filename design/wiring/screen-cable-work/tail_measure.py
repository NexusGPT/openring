#!/usr/bin/env python3
"""tail_measure.py <display pdf>: measures the stock screen cable (FPC tail) of the Tailor Pixels TOH095XVT-01 from the vector
lines of its drawing, page 5 of design/datasheets/display_TOH095XVT-01.pdf (PyMuPDF, read only).

Scale: the panel outline printed 12.8 (width) and 27.35 (length) on the same page sets pt/mm in X and Y; the printed 20 (panel end to
the cable end), 3.2 (contact field) and 4.8 (cable end width) are then CHECKS of that scale, not inputs. Distances along the cable
are from the panel end (the lower glass end, y = 262.92 pt in the front view). Front view: the face that shows the lit area."""
import sys
import pymupdf

pg = pymupdf.open(sys.argv[1])[4]
L = []
for d in pg.get_drawings():
    for it in d["items"]:
        if it[0] == "l":
            L.append((round(it[1].x, 2), round(it[1].y, 2), round(it[2].x, 2), round(it[2].y, 2)))
        elif it[0] == "re":
            r = it[1]
            L += [(r.x0, r.y0, r.x1, r.y0), (r.x0, r.y1, r.x1, r.y1), (r.x0, r.y0, r.x0, r.y1), (r.x1, r.y0, r.x1, r.y1)]


def vert(x0, x1, ymin_len, yb0=0, yb1=999):
    return sorted({(l[0], min(l[1], l[3]), max(l[1], l[3])) for l in L if abs(l[0] - l[2]) < 0.01 and x0 <= l[0] <= x1
                   and abs(l[1] - l[3]) >= ymin_len and yb0 <= min(l[1], l[3]) and max(l[1], l[3]) <= yb1})


def horiz(y0, y1, xmin_len, xb0=0, xb1=999):
    return sorted({(l[1], min(l[0], l[2]), max(l[0], l[2])) for l in L if abs(l[1] - l[3]) < 0.01 and y0 <= l[1] <= y1
                   and abs(l[0] - l[2]) >= xmin_len and xb0 <= min(l[0], l[2]) and max(l[0], l[2]) <= xb1})


# panel outline, front view (screen_ledge.log of design/mech/light-path: sides x 234.42 / 300.25, y 121.94..262.92)
side = vert(230, 305, 130)
xl, xr = min(v[0] for v in side), max(v[0] for v in side)
yt, yb = min(v[1] for v in side), max(v[2] for v in side)
sx, sy = (xr - xl) / 12.8, (yb - yt) / 27.35
xc = (xl + xr) / 2
print(f"panel outline (front view): x {xl}..{xr} pt, y {yt}..{yb} pt; scale X {sx:.4f} pt/mm (printed 12.8), Y {sy:.4f} pt/mm (printed 27.35); "
      f"X/Y scale ratio {sx / sy:.4f}")


def mx(x):
    return (x - xc) / sx


def my(y):
    return (y - yb) / sy


# wide part: the long verticals below the panel end
wide = [v for v in vert(230, 305, 30) if v[1] >= yb - 6 and min(abs(v[0] - xl), abs(v[0] - xr)) < 2]
print("wide part sides:", wide)
wl, wr = min(v[0] for v in wide), max(v[0] for v in wide)
w_end = max(v[2] for v in wide)
print(f"wide part: Y {mx(wl):.3f} to {mx(wr):.3f} from the panel centre line, width {(wr - wl) / sx:.3f} mm; straight sides from "
      f"{my(min(v[1] for v in wide)):.3f} (inside the panel end) to {my(w_end):.3f} mm beyond the panel end")
# end of the wide part: the horizontal lines at the shoulder
sh = horiz(w_end + 0.5, w_end + 4, 5, wl - 1, wr + 1)
print("shoulder lines:", sh)
y_sh = max(h[0] for h in sh) if sh else None
print(f"shoulder (wide part end, after the 0.5 corner arcs): {my(y_sh):.3f} mm beyond the panel end; corner radius {(y_sh - w_end) / sy:.3f} (Y) / "
      f"{(min(h[1] for h in sh) - wl) / sx:.3f} (X)")
neck = [v for v in vert(250, 285, 20) if y_sh < v[1] < y_sh + 5]
print("neck sides:", neck)
nl, nr = min(v[0] for v in neck), max(v[0] for v in neck)
print(f"neck: Y {mx(nl):.3f} to {mx(nr):.3f}, width {(nr - nl) / sx:.3f} mm (printed 4.8); neck sides start {my(min(v[1] for v in neck)):.3f} mm beyond the panel end "
      f"(after the 0.5 inner fillets)")
ends = horiz(360, 370, 20, 240, 300)
print("cable end lines:", ends)
y_end = max(h[0] for h in ends) if ends else None
print(f"cable end: {my(y_end):.3f} mm beyond the panel end (printed 20)")
grid = horiz(349, 351, 20, 220, 285)
print("contact field top lines:", grid)
y_cf = min(h[0] for h in grid)
print(f"contact field / stiffener: from {my(y_cf):.3f} to {my(y_end):.3f} mm, length {(y_end - y_cf) / sy:.3f} (printed 3.2)")
x3 = horiz(276, 280, 30, 230, 305)
print(f"line across the full width at {my(x3[0][0]):.3f} mm beyond the panel end (not labelled on the page)" if x3 else "no line at 3 mm")
# side view: thicknesses (x scale of the front view is reused: same drawing, 1:1 scale box)
print("side view (x 383..388 pt): panel 383.90..388.01 = %.3f mm (printed 0.8); upper layer 383.90..385.43 = %.3f to y 247.71 (ledge); "
      "tail 386.23..386.72 = %.3f; stiffener 385.71..386.23 = %.3f from y 349.5 to 366.01 = %.3f mm; tail + stiffener 385.71..386.72 = %.3f (printed 0.2 +-0.03 incl. PI stiffener)"
      % ((388.01 - 383.90) / sx, (385.43 - 383.90) / sx, (386.72 - 386.23) / sx, (386.23 - 385.71) / sx, (366.01 - 349.5) / sy, (386.72 - 385.71) / sx))
# back view contact fingers: pitch from the finger edges at y 353.1
fing = sorted({l[0] for l in L if abs(l[0] - l[2]) < 0.01 and 490 < l[0] < 520 and abs(min(l[1], l[3]) - 353.1) < 0.05 and abs(max(l[1], l[3]) - 354.39) < 0.05})
print(f"back view finger edges at the field top (x pt): {fing}")
if len(fing) > 4:
    d = [round(b - a, 2) for a, b in zip(fing, fing[1:])]
    print(f"  steps {d}; pitch from pairs of like edges {(fing[-1] - fing[0]) / (len(fing) / 2 - 0.5) / sx if len(fing) % 2 == 0 else 0:.3f} mm (approx.)")
print("RESULT done")
