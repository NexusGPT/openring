# parses every a.3 and b.2 via cell with the old and the new span rule; prints rows whose parsed span differs
import re
def old(v):
    if v.startswith("none"): return None
    if "stacked" in v and "L1-L2, L2-L3" in v: return ("L1", "L3")
    m = re.search(r"microvia (L\d)-(L\d)", v); return (m.group(1), m.group(2)) if m else "?"
def new(v):
    if v.startswith("none"): return None
    if "stacked" in v and "L1-L2, L2-L3" in v: return ("L1", "L3")
    m = re.search(r"via (L\d)-(L\d)", v); return (m.group(1), m.group(2)) if m else "?"
txt = open((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/wiring/ring-board-plan.md")).read()
n = d = 0
for a, u in (("### a.3 Ball by ball", "Differences from Nordic"), ("### b.2 Escape plan", "PVSS1 (A7) and PVSS2")):
    for l in txt.split(a, 1)[1].split(u, 1)[0].splitlines():
        if l.startswith("| ") and not l.startswith("| Ball"):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            n += 1
            if old(c[5]) != new(c[5]): d += 1; print("differs", c[0], c[5], old(c[5]), new(c[5]))
print("rows", n, "differ", d)
