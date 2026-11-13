#!/usr/bin/env python3
"""check_escapes.py [board] -- compares the escapes of U1 and U2 on the board with the plan's tables a.3 and b.2
(design/wiring/ring-board-plan.md), ball by ball: the via in the land (span), the layer the escape leaves on, its net, its
direction, and that a ball marked "none" has no via and no track. Exit 0 = every ball matches, 1 = any mismatch.
Run with ./run_kipy.sh check_escapes.py"""
import math, os, re, sys
import pcbnew
from pcbnew import ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "wiring", "ring-board-plan.md")
board = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ring.kicad_pcb")
b = pcbnew.LoadBoard(board)
OX = OY = 100.0
LN = {"F.Cu": "L1", "In1.Cu": "L2", "In2.Cu": "L3", "B.Cu": "L4"}

def table(after, until):
    txt = open(PLAN).read()
    sec = txt.split(after, 1)[1].split(until, 1)[0]
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in sec.splitlines()
            if l.startswith("| ") and not l.startswith("| Ball") and not l.startswith("|---")]
def span_of(v):
    if v.startswith("none"): return None
    if "stacked" in v and "L1-L2, L2-L3" in v: return ("L1", "L3")
    # round 3: "through via L1-L4" and "blind via L1-L3" rows (lead's decision of 2026-11-13, pin changes for routing) read too
    m = re.search(r"via (L\d)-(L\d)", v)
    return (m.group(1), m.group(2)) if m else "?"
def direction(esc):
    m = re.search(r"\b(north|south|west|east)\b", esc)
    return m.group(1) if m else None

fps = {f.GetReference(): f for f in b.GetFootprints()}
vias, segs = [], []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        vias.append(((ToMM(t.GetPosition().x) - OX, ToMM(t.GetPosition().y) - OY), LN[b.GetLayerName(t.TopLayer())], LN[b.GetLayerName(t.BottomLayer())], t.GetNetname()))
    else:
        segs.append(((ToMM(t.GetStart().x) - OX, ToMM(t.GetStart().y) - OY), (ToMM(t.GetEnd().x) - OX, ToMM(t.GetEnd().y) - OY), LN[b.GetLayerName(t.GetLayer())], t.GetNetname(), t.IsLocked()))

fails, n = [], 0
def check(chip, rows):
    global n
    for row in rows:
        ball, pin, netn, land, layer, vtext, esc = row[:7]
        pad = [p for p in fps[chip].Pads() if p.GetNumber() == ball][0]
        c = (ToMM(pad.GetPosition().x) - OX, ToMM(pad.GetPosition().y) - OY)
        n += 1
        vs = [v for v in vias if math.dist(v[0], c) < 0.002]
        ts = [s for s in segs if math.dist(s[0], c) < 0.002 or math.dist(s[1], c) < 0.002]
        want_span = span_of(vtext)
        if layer == "none":
            if vs or ts or pad.GetNetname():
                fails.append("%s %s: plan says not connected, board has net %r, %d vias, %d tracks at the land" % (chip, ball, pad.GetNetname(), len(vs), len(ts)))
            continue
        if pad.GetNetname() != netn:
            fails.append("%s %s: pad net %s, plan %s" % (chip, ball, pad.GetNetname(), netn)); continue
        got_span = (vs[0][1], vs[0][2]) if vs else None
        if len(vs) > 1:
            fails.append("%s %s: %d vias in the land" % (chip, ball, len(vs)))
        if got_span != want_span:
            fails.append("%s %s: via %s, plan %s" % (chip, ball, got_span, want_span)); continue
        if vs and vs[0][3] != netn:
            fails.append("%s %s: via net %s, plan %s" % (chip, ball, vs[0][3], netn))
        # round 3 (lead's decision of 2026-11-13, pin changes for routing): F4 (LCD_TE) and F9 (OLED_PWR_EN) have no scripted
        # escape; the router's track joins the via in the land. Pad net, via span, one via and via net are checked above.
        if esc.startswith("router joins the via"):
            continue
        on = [s for s in ts if s[2] == layer and s[4]]
        if not on:
            fails.append("%s %s: no locked escape track on %s at the land (tracks there: %s)" % (chip, ball, layer, [(s[2], s[3]) for s in ts])); continue
        if any(s[3] != netn for s in on):
            fails.append("%s %s: escape track net %s, plan %s" % (chip, ball, [s[3] for s in on], netn)); continue
        d = direction(esc)
        if d and not ("bridge" in esc or "joined to" in esc or "south-west" in esc):
            ok_dir = False
            for s in on:
                o = s[1] if math.dist(s[0], c) < 0.002 else s[0]
                dx, dy = o[0] - c[0], o[1] - c[1]
                got = "east" if abs(dx) >= abs(dy) and dx > 0 else "west" if abs(dx) >= abs(dy) else "south" if dy > 0 else "north"
                ok_dir = ok_dir or got == d
            if not ok_dir:
                fails.append("%s %s: escape leaves %s, plan %s" % (chip, ball, [("%.2f,%.2f" % ((s[1] if math.dist(s[0], c) < 0.002 else s[0]))) for s in on], d))

# W2 round 2, lead's ruling b (board-notes-r2.md): B5, B9, G4, H4 are not connected (their test pads are removed); their rows
# of table a.3 are checked as "none" (no net, no via, no track at the land). Expected value changed by that ruling.
NC_R2 = {"B5", "B9", "G4", "H4"}
check("U1", [r[:4] + ["none", "none", "not connected (W2 round 2, ruling b)"] + r[7:] if r[0] in NC_R2 else r
             for r in table("### a.3 Ball by ball", "Differences from Nordic")])
check("U2", table("### b.2 Escape plan", "PVSS1 (A7) and PVSS2"))
for f in fails:
    print("FAIL", f)
print("balls checked: %d (U1 61 and U2 35 from the plan tables a.3 and b.2)" % n)
print("RESULT PASS" if not fails else "RESULT FAIL %d" % len(fails))
sys.exit(1 if fails else 0)
