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
def pads(board):
    return list(csv.DictReader(open(os.path.join(PADS, board + "-pads.csv"))))
def on_land(feats, px, py, sx, sy, gy_sign):
    hits = []
    for f in feats:
        cx, cy = f[1], f[2] * gy_sign
        if abs(cx - px) <= sx / 2 + 1e-6 and abs(cy - py) <= sy / 2 + 1e-6: hits.append(f)
    return hits
def report(name, gbr, board, refs, gy=-1, want=None):
    feats = parse(gbr)
    ps = [p for p in pads(board) if p["ref"] in refs or (p["ref"] + ":" + p["pad"]) in refs]
    n_with = 0
    for p in ps:
        px, py = float(p["x"]), float(p["y"]); sx, sy = float(p["sx"]), float(p["sy"])
        if float(p["orient"]) % 180 == 90: sx, sy = sy, sx
        h = on_land(feats, px, py, sx, sy, gy)
        if h: n_with += 1
        desc = "; ".join("%s %.3fx%.3f" % (f[0], f[3], f[4]) for f in h[:6])
        print("%s %s:%s net=%s openings=%d %s" % (name, p["ref"], p["pad"], p["net"], len(h), desc))
    print("RESULT %s lands=%d with_opening=%d file_features=%d" % (name, len(ps), n_with, len(feats)))
    return feats
R = ROOT
report("ringF_JBAND", R + "/ring/pcb/fab/gerber/ring-F_Paste.gbr", "ring", {"J_BAND_A", "J_BAND_B"})
report("ringF_ANT1", R + "/ring/pcb/fab/gerber/ring-F_Paste.gbr", "ring", {"ANT1"})
report("ringF_C83", R + "/ring/pcb/fab/gerber/ring-F_Paste.gbr", "ring", {"C83"})
report("ringB_TP", R + "/ring/pcb/fab/gerber/ring-B_Paste.gbr", "ring", {"TP1", "TP3", "TP4", "TP5", "TP6", "TP12", "TP14", "TP15", "TP17", "TP18", "TP19", "TP21"})
report("ringB_J1", R + "/ring/pcb/fab/gerber/ring-B_Paste.gbr", "ring", {"J1"})
for s in range(7, 14):
    report("flex1-us%d_F_SW" % s, R + "/band/fab/flex1-us%d/flex1-us%d-F_Paste.gbr" % (s, s), "flex1-us%d" % s, {"SW1", "SW2", "SW3", "SW4", "SW5"})
    report("flex1-us%d_F_other" % s, R + "/band/fab/flex1-us%d/flex1-us%d-F_Paste.gbr" % (s, s), "flex1-us%d" % s, {"M1", "J_BAND_A"})
    report("flex2-us%d_B_CP" % s, R + "/band/fab/flex2-us%d/flex2-us%d-B_Paste.gbr" % (s, s), "flex2-us%d" % s, {"CP1", "CP2", "CP3", "CP4"})
report("case_pins_F_P", R + "/case/pcb/fab/case_pins/gerber/case_pins-F_Paste.gbr", "case_pins", {"P1", "P2", "P3", "P4", "WP1", "WP2", "WP3", "WP4", "WP7", "E1"})
report("case_main_F_W", R + "/case/pcb/fab/case_main/gerber/case_main-F_Paste.gbr", "case_main", {"W1", "W2", "W3", "W4", "W5", "W6", "W7", "TH1"})
