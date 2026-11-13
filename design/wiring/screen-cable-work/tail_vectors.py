"""tail_vectors.py <pdf>: dump every vector item of page 5 of the screen drawing (TOH095XVT-01) in three windows:
front view below the panel end, side view, back view. Coordinates in PDF points. Read only."""
import sys
import pymupdf
doc = pymupdf.open(sys.argv[1])
pg = doc[4]
wins = {"front": (195, 240, 320, 375), "side": (360, 90, 420, 380), "back": (470, 240, 560, 375)}
for name, (x0, y0, x1, y1) in wins.items():
    print("=== window", name, (x0, y0, x1, y1))
    rows = set()
    for d in pg.get_drawings():
        for it in d["items"]:
            pts = [p for p in it[1:] if hasattr(p, "x")]
            if it[0] == "re":
                r = it[1]; pts = [r.tl, r.br]
            if not pts:
                continue
            if all(x0 <= p.x <= x1 and y0 <= p.y <= y1 for p in pts):
                rows.add((it[0], tuple((round(p.x, 2), round(p.y, 2)) for p in pts), round(d.get("width") or 0, 2)))
    for r in sorted(rows, key=lambda r: (r[1][0][1], r[1][0][0])):
        print(r)
