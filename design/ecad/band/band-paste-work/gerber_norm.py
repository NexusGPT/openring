#!/usr/bin/env python3
"""Geometry of a KiCad Gerber file as a sorted list of objects, independent of aperture numbers and object order.
Objects: FLASH <aperture definition> at (x, y); DRAW <aperture definition> from (x0, y0) to (x1, y1) (ends sorted);
REGION <sorted list of vertices>; ARC <aperture> centre and ends (G02/G03 with I, J). Attributes (%TO, %TA, %TD) are ignored except the aperture function, which is kept with the definition.
usage as module: objects(path) -> list; as script: gerber_norm.py a.gbr b.gbr  (prints equal/differ and counts)"""
import re, sys


def objects(path):
    txt = open(path).read()
    ap = {}
    func = ""
    cur = None
    x = y = 0
    out = []
    region = None
    pending_func = ""
    mode = "G1"
    for raw in re.split(r"\*%?\n?|%", txt):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("TA.AperFunction"):
            pending_func = s[3:]
            continue
        if s.startswith("TD"):
            pending_func = ""
            continue
        m = re.match(r"ADD(\d+)(.*)", s)
        if m:
            ap[m.group(1)] = m.group(2) + ("|" + pending_func if pending_func else "")
            continue
        if s == "G36":
            region = []
            continue
        if s == "G37":
            out.append("REGION " + " ".join(sorted(region)))
            region = None
            continue
        if s in ("G01", "G1", "G02", "G2", "G03", "G3", "G75", "G74"):
            if s in ("G01", "G1", "G02", "G2", "G03", "G3"):
                mode = s.replace("G0", "G")
            continue
        m = re.match(r"^(?:G0?([123]))?(?:X(-?\d+))?(?:Y(-?\d+))?I(-?\d+)J(-?\d+)D0?1$", s)
        if m:                                   # circular arc: ARC <aperture> centre (cx, cy) from - to (ends sorted) and direction
            if m.group(1):
                mode = "G" + m.group(1)
            nx = int(m.group(2)) if m.group(2) else x
            ny = int(m.group(3)) if m.group(3) else y
            cx, cy = x + int(m.group(4)), y + int(m.group(5))
            out.append(f"ARC {cur} centre ({cx},{cy}) {(x, y)}->{(nx, ny)} {mode}")
            x, y = nx, ny
            continue
        m = re.match(r"^(?:G0?1)?(?:X(-?\d+))?(?:Y(-?\d+))?D0?([123])$", s)
        if m and (m.group(1) or m.group(2) or m.group(3)):
            nx = int(m.group(1)) if m.group(1) else x
            ny = int(m.group(2)) if m.group(2) else y
            op = m.group(3)
            if region is not None:
                region.append(f"({nx},{ny})")
            elif op == "3":
                out.append(f"FLASH {cur} ({nx},{ny})")
            elif op == "1":
                a, b = sorted([(x, y), (nx, ny)])
                out.append(f"DRAW {cur} {a}-{b}")
            x, y = nx, ny
            continue
        m = re.match(r"^D(\d{2,})$", s)
        if m:
            cur = ap.get(m.group(1), "?" + m.group(1))
            continue
    return sorted(out)


if __name__ == "__main__":
    A, B = objects(sys.argv[1]), objects(sys.argv[2])
    print(f"objects {len(A)} vs {len(B)}: {'EQUAL' if A == B else 'DIFFER'}")
    if A != B:
        sa, sb = set(A), set(B)
        for o in sorted(sa - sb)[:5]:
            print("  only A:", o)
        for o in sorted(sb - sa)[:5]:
            print("  only B:", o)
    sys.exit(0 if A == B else 1)
