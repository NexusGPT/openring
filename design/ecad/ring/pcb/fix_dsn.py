#!/usr/bin/env python3
"""fix_dsn.py in.dsn out.dsn -- prepares KiCad's Specctra export of ring.kicad_pcb for Freerouting (plan step g.6).

1. one padstack per via span, each a 200 um circle on every layer it touches (Via[0-1], [1-2], [2-3], [0-2], [1-3], [0-3]),
   all six in the structure's via list and in every class (laser microvias and their stacks, plan c.2);
2. board rule width 100, clearance 75 (c.5); class PWR keeps its width;
3. the ground planes are taken out (ground is made by the zones and the scripted stacks, not routed) and GND moves to its
   own class GNDZ; RF and USB are fully scripted: the router is run with -inc GNDZ,RF,USB so it leaves those nets alone;
5. via_at_smd on: a laser microvia may stand in an SMD land (filled and plated over, plan c.2);
4. the two rule areas without restrictions (RF_CHIP_EXIT, USB_CHIP_EXIT: they only scope two rules of ring.kicad_dru) are not
   keep-outs: removed; the antenna copper-free zone gets a wire keep-out on every layer next to its via keep-out.
Prints what it changed; exits 1 if an expected piece is not found.
"""
import re, sys

src = open(sys.argv[1]).read()
out = src
L = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]

def blocks(text, head):
    """(start, end) of every balanced block that starts with head"""
    res, i = [], 0
    while True:
        i = text.find(head, i)
        if i < 0: return res
        d, j = 0, i
        while True:
            if text[j] == "(": d += 1
            elif text[j] == ")":
                d -= 1
                if d == 0: break
            j += 1
        res.append((i, j + 1)); i = j + 1

# 3. planes out
pl = blocks(out, "(plane GND")
for s, e in reversed(pl):
    out = out[:s] + out[e:]
print("planes removed:", len(pl))

# 4. scope-only rule areas out; antenna wire keep-out added
removed = 0
for s, e in reversed(blocks(out, '(keepout ""')):
    blk = out[s:e]
    nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", blk.split("polygon", 1)[1])[1:]]
    xs, ys = nums[0::2], nums[1::2]
    box = (min(xs), min(ys), max(xs), max(ys))
    if box in ((103800.0, -101950.0, 104750.0, -100800.0), (101900.0, -99950.0, 102800.0, -99250.0)):
        out = out[:s] + out[e:]; removed += 1
print("scope-only rule areas removed:", removed)
if removed != 2: sys.exit("expected 2 scope-only rule areas (F.Cu only)")
ant = [out[s:e] for s, e in blocks(out, '(via_keepout ""') if "86400 -103100" in out[s:e]]
if len(ant) != 4: sys.exit("antenna via keep-outs: %d, want 4" % len(ant))
add = "".join("    " + a.replace("(via_keepout", "(wire_keepout", 1) + "\n" for a in ant)
i = out.find("    (via \"Via[")
out = out[:i] + add + out[i:]
print("antenna wire keep-outs added:", len(ant))

# 1. padstacks and via lists
names = []
spans = [(0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3)]
ps = ""
for a, b in spans:
    n = "Via[%d-%d]_200:100_um" % (a, b); names.append(n)
    if '(padstack "%s"' % n in out:
        continue
    ps += '    (padstack "%s"\n' % n + "".join("      (shape (circle %s 200))\n" % L[k] for k in range(a, b + 1)) + "      (attach off)\n    )\n"
m = "  )\n  (network"
if out.count(m) != 1: sys.exit("library end not found")
out = out.replace(m, ps + m)
vl = re.search(r"\(via \"Via\[[^\n]*\)\n", out)
vl_line = "(via " + " ".join('"%s"' % n for n in names) + ")\n"
out = out[:vl.start()] + vl_line + out[vl.end():]
uv = len(re.findall(r'\(use_via "Via\[0-3\]_200:100_um"\)', out))
out = re.sub(r'\(use_via "Via\[0-3\]_200:100_um"\)', "(use_via " + " ".join('"%s"' % n for n in names) + ")", out)
print("padstacks added:", ps.count("(padstack"), "classes given six vias:", uv)

# 5. via in pad allowed (any-layer HDI: filled and plated-over laser vias, plan c.2): Freerouting may put a microvia in an SMD land
if "(via_at_smd" not in out:
    out = out.replace(vl_line, vl_line + "    (control (via_at_smd on))\n", 1)
    print("via_at_smd on")

# 2. board rule
r0 = "    (rule\n      (width 100)\n      (clearance 75)\n"
if r0 not in out: sys.exit("board rule not as expected")

# 3. GND to its own class
cl = re.search(r"\(class kicad_default ([^(]*)", out)
members = cl.group(1).split()
if "GND" not in members: sys.exit("GND not in kicad_default")
members.remove("GND")
new = "(class kicad_default " + " ".join(members) + "\n      "
out = out[:cl.start()] + new + out[cl.end():]
gz = '    (class GNDZ GND\n      (circuit\n        (use_via %s)\n      )\n      (rule\n        (width 150)\n        (clearance 75)\n      )\n    )\n' % " ".join('"%s"' % n for n in names)
i = out.find("    (class USB")
out = out[:i] + gz + out[i:]
print("GND moved to class GNDZ")

open(sys.argv[2], "w").write(out)
print("fix_dsn: written", sys.argv[2], "protect wires", out.count("(type fix)"), "or", out.count("(type protect)"))
