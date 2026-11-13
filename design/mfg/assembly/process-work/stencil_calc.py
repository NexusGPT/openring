"""Area ratio of every paste opening of the delivered paste Gerbers, per stencil thickness.
Rule (TI SLUA271C p.11, saved as design/datasheets/proc_ti_slua271c_qfn_son_attachment.pdf):
  area ratio = opening area / (perimeter x thickness); laser stencil needs >= 0.66; nickel formed prints down to 0.57;
  aspect ratio = width / thickness > 1.5.
Paste maker (Kester NP505-HR TDS p.1): "Consistent print performance to 0.55AR (SAC305)".
Openings are read from the Gerber aperture of each flash; the land under each flash is found in the pad dumps of the
joint table helper (joint-table-work/pads/<board>-pads.csv, same origin, Y turned).
Flex boards have no paste file: their lands are read from the pad dumps (Alps paste thickness 0.08 mm).
Run: design/.venv/bin/python -B process-work/stencil_calc.py  (writes process-work/logs/stencil_calc.log)
"""
import csv, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PADS = os.path.join(ROOT, "design/mfg/assembly/joint-table-work/pads")
FILES = [
    ("ring", "B", "design/ecad/ring/pcb/fab/gerber/ring-B_Paste.gbr"),
    ("ring", "F", "design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr"),
    ("case_main", "F", "design/ecad/case/pcb/fab/case_main/gerber/case_main-F_Paste.gbr"),
    ("case_main", "B", "design/ecad/case/pcb/fab/case_main/gerber/case_main-B_Paste.gbr"),
]
THICK = [0.050, 0.075, 0.080, 0.100, 0.120]
TOL = 0.02


def shape_of(defn, macros):
    """(kind, w, h, area, perimeter) of one aperture definition."""
    m = re.match(r"C,([\d.]+)", defn)
    if m:
        d = float(m.group(1))
        return ("circle %.3f" % d, d, d, math.pi * d * d / 4, math.pi * d)
    m = re.match(r"R,([\d.]+)X([\d.]+)", defn)
    if m:
        w, h = float(m.group(1)), float(m.group(2))
        return ("rect %.3f x %.3f" % (w, h), w, h, w * h, 2 * (w + h))
    m = re.match(r"RoundRect,(.+)", defn)
    if m:
        v = [float(x) for x in m.group(1).split("X")]
        r = v[0]
        xs, ys = v[1:9:2], v[2:9:2]
        w = max(xs) - min(xs) + 2 * r
        h = max(ys) - min(ys) + 2 * r
        area = w * h - (4 - math.pi) * r * r
        per = 2 * (w + h) - (8 - 2 * math.pi) * r
        return ("roundrect %.3f x %.3f r %.3f" % (w, h, r), w, h, area, per)
    m = re.match(r"(FreePoly\d+),", defn)
    if m:
        pts = macros[m.group(1)]
        area = 0.5 * abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))))
        per = sum(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))
        w = max(p[0] for p in pts) - min(p[0] for p in pts)
        h = max(p[1] for p in pts) - min(p[1] for p in pts)
        return ("polygon %.3f x %.3f" % (w, h), w, h, area, per)
    raise SystemExit("unknown aperture " + defn)


def read_gerber(path):
    macros, aps, flashes = {}, {}, []
    txt = open(path, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"%AM(\w+)\*\s*4,1,(\d+),([^%]*?)\*%", txt, re.S):
        nums = [float(x) for x in re.findall(r"-?[\d.]+", m.group(3))]
        n = int(m.group(2))
        pts = [(nums[2 * i], nums[2 * i + 1]) for i in range(n)]
        macros[m.group(1)] = pts
    cur, x, y = None, None, None
    for raw in txt.split("\n"):
        line = raw.strip()
        m = re.match(r"%ADD(\d+)(.+)\*%", line)
        if m:
            aps[int(m.group(1))] = m.group(2)
            continue
        if line.startswith("%") or line.startswith("G04"):
            continue
        m = re.match(r"(?:G54)?D(\d+)\*$", line)
        if m and int(m.group(1)) >= 10:
            cur = int(m.group(1))
            continue
        mx = re.search(r"X(-?\d+)", line)
        my = re.search(r"Y(-?\d+)", line)
        if mx:
            x = int(mx.group(1)) / 1e6
        if my:
            y = int(my.group(1)) / 1e6
        if line.endswith("D03*"):
            flashes.append((cur, x, y))
    return macros, aps, flashes


def main():
    out = []
    for board, face, rel in FILES:
        path = os.path.join(ROOT, rel)
        macros, aps, flashes = read_gerber(path)
        pads = list(csv.DictReader(open(os.path.join(PADS, board + "-pads.csv"), newline="")))
        cu = face + ".Cu"
        pads = [p for p in pads if cu in p["layers"].split()]
        groups = {}
        unmatched = 0
        for ap, fx, fy in flashes:
            hit = [p for p in pads if abs(float(p["x_mm"]) - fx) <= TOL and abs(-float(p["y_mm"]) - fy) <= TOL]
            name = ",".join(sorted({"%s:%s" % (p["ref"], p["pad"]) for p in hit})) if hit else "NO LAND"
            if not hit:
                unmatched += 1
            groups.setdefault(ap, []).append(name)
        out.append("FILE %s (board %s face %s): %d openings, %d apertures, %d openings with no land" % (rel, board, face, len(flashes), len(groups), unmatched))
        rows = []
        for ap, names in groups.items():
            kind, w, h, area, per = shape_of(aps[ap], macros)
            refs = {}
            for n in names:
                for part in n.split(","):
                    r = part.split(":")[0]
                    refs[r] = refs.get(r, 0) + 1
            ar = {t: area / (per * t) for t in THICK}
            rows.append((min(ar.values()), ap, kind, w, h, area, len(names), refs, ar))
        rows.sort(key=lambda r: (r[0], r[1]))
        for _, ap, kind, w, h, area, n, refs, ar in rows:
            arx = " ".join("t%.3f=%.3f" % (t, ar[t]) for t in THICK)
            aspect = " ".join("t%.3f=%.2f" % (t, min(w, h) / t) for t in THICK)
            reflist = " ".join("%s(%d)" % (r, c) for r, c in sorted(refs.items()))
            out.append("  D%d %s area %.4f mm2 n=%d | AR %s | aspect %s | lands %s" % (ap, kind, area, n, arx, aspect, reflist))
        # thickness that keeps every opening >= 0.66
        if not rows:
            out.append("  no opening in this file")
            continue
        worst = rows[0]
        kind, area = worst[2], worst[5]
        w, h = worst[3], worst[4]
        per = area / (worst[8][THICK[0]] * THICK[0])
        tmax = area / (per * 0.66)
        out.append("  smallest area ratio: D%d %s; largest thickness with area ratio >= 0.66: %.4f mm; with >= 0.57: %.4f mm; with >= 0.55: %.4f mm"
                   % (worst[1], kind, tmax, area / (per * 0.57), area / (per * 0.55)))
    # flex lands (no paste file)
    for b in ["flex1-us%d" % s for s in range(7, 14)]:
        pads = list(csv.DictReader(open(os.path.join(PADS, b + "-pads.csv"), newline="")))
        sw = [p for p in pads if p["ref"].startswith("SW")]
        sizes = sorted({(float(p["w_mm"]), float(p["h_mm"])) for p in sw})
        line = "FLEX %s: %d switch lands, sizes %s" % (b, len(sw), sizes)
        for w, h in sizes:
            line += " | %.2fx%.2f AR at t0.080 = %.3f" % (w, h, w * h / (2 * (w + h) * 0.08))
        out.append(line)
    for b in ["flex2-us%d" % s for s in range(7, 14)]:
        pads = list(csv.DictReader(open(os.path.join(PADS, b + "-pads.csv"), newline="")))
        cp = [p for p in pads if p["ref"].startswith("CP")]
        out.append("FLEX %s: %d disc lands, sizes %s, layers %s" % (b, len(cp), sorted({(p["w_mm"], p["h_mm"]) for p in cp}), sorted({p["layers"] for p in cp})))
    log = os.path.join(HERE, "logs", "stencil_calc.log")
    open(log, "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
