import re, sys
W = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/")
def count(path):
    t = open(path).read()
    arcs = re.findall(r"^X(-?\d+)Y(-?\d+)D02\*\nG75\*\nG0[23]\*\nX(-?\d+)Y(-?\d+)I(-?\d+)J(-?\d+)D01\*", t, re.M)
    cx = set()
    for x0, y0, x1, y1, i, j in arcs:
        cx.add((int(x0) + int(i), int(y0) + int(j)))
    flashes = len(re.findall(r"^X-?\d+Y-?\d+D03\*", t, re.M))
    regions = len(re.findall(r"^G36\*", t, re.M))
    return len(arcs), len(cx), flashes, regions
for lab, p in (("before", W + "case-proc-work/before/fab/case_pins/gerber/case_pins-F_Paste.gbr"), ("after", W + "fab/case_pins/gerber/case_pins-F_Paste.gbr")):
    a, c, f, r = count(p)
    print("case_pins F_Paste", lab, "arcs", a, "ring openings", c, "flashes", f, "regions", r)
