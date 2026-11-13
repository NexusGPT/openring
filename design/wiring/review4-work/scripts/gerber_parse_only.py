# Reads delivered paste gerbers and says, for each named land, which paste openings lie on it (my own parser).
# usage: gerber_check.py  (paths fixed below; prints one line per land and RESULT lines)
import re, csv, sys, math, os
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad")
PADS = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work/pads")
def parse(path):
    txt = open(path).read()
    fs = re.search(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%", txt); dec = int(fs.group(2))
    ap = {}
    for m in re.finditer(r"%ADD(\d+)([A-Za-z_0-9]+),?([^*]*)\*%", txt):
        ap[int(m.group(1))] = (m.group(2), [float(v) for v in m.group(3).split("X") if v.strip() and re.fullmatch(r"[-0-9.]+", v.strip())])
    feats = []  # (kind, cx, cy, w, h)
    cur = None; x = y = 0.0; region = False; rpts = []; lastx = lasty = 0.0
    body = re.sub(r"%[^%]*%", "", txt)
    for st in body.split("*"):
        st = st.strip()
        if not st: continue
        if st == "G36": region = True; rpts = []; continue
        if st == "G37":
            if rpts:
                xs = [p[0] for p in rpts]; ys = [p[1] for p in rpts]
                feats.append(("region", (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys)))
            region = False; continue
        m = re.fullmatch(r"(?:G0?[123])?D(\d+)", st)
        if m and int(m.group(1)) >= 10: cur = int(m.group(1)); continue
        m = re.match(r"(?:G0?([123]))?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0?([123])$", st)
        if m:
            nx = int(m.group(2)) / 10 ** dec if m.group(2) else x
            ny = int(m.group(3)) / 10 ** dec if m.group(3) else y
            d = int(m.group(6))
            if region:
                if d in (1, 2): rpts.append((nx, ny))
            elif d == 3:
                a = ap.get(cur, ("?", []))
                w = a[1][0] if a[1] else 0; h = a[1][1] if len(a[1]) > 1 else w
                feats.append(("flash:" + a[0], nx, ny, w, h))
            elif d == 1:
                a = ap.get(cur, ("?", [0])); wd = a[1][0] if a[1] else 0
                feats.append(("draw", (x + nx) / 2, (y + ny) / 2, abs(nx - x) + wd, abs(ny - y) + wd))
                if m.group(4) or m.group(5):  # arc: record its centre too
                    cxx = x + int(m.group(4) or 0) / 10 ** dec; cyy = y + int(m.group(5) or 0) / 10 ** dec
                    rr = math.hypot(x - cxx, y - cyy)
                    feats.append(("arc", cxx, cyy, 2 * rr + wd, 2 * rr - wd))
            x, y = nx, ny
    return feats
