# lines_check.py p4p5.log xcheck.log board.kicad_pcb : judges the 8 controlled-line limits of design/ecad/ring/pcb/board-notes-r4.md
# ("The 8 controlled-line limits") on one board, from the read-back log (rb/p4p5.py), the pcbnew cross-check log (rb/xcheck_clear.py)
# and the board itself. Run with KiCad's Python. Prints one line per limit and RESULT PASS / FAIL n; exit 1 on any FAIL.
#  1 antenna L1 clearance >= 0.200 mm (P4.2)
#  2 antenna ground under the line outside the copper-free zone 100.0000 percent (A1, lead's ruling)
#  3 XC1 gap >= 0.20 mm (P5 XC1 on L3)          4 XC2 gap >= 0.20 mm (P5 XC2 on L3)
#  5 USB Zdiff: accepted as routed in round 4 -> figures must be the accepted ones (92.10 at min gap, 104.70 at modal gap)
#  6 XL1 length: accepted at 9.343 mm -> shortest drawn path <= 9.343
#  7 XL1 gap, 8 XL2 gap: waived inside U1's ball field (1.0 mm round any U1 ball); beyond it only the accepted items may be closer
#    than 0.20 mm: XL1 -> U1_VBUS's via, XL2 -> LCD_SCK's via (board-notes-r4.md). Every other-net track, via and pad within 0.20 mm
#    of an XL1 / XL2 track on the same layer and beyond 1.0 mm of every U1 ball is listed from the board file.
import sys, re, math, pcbnew
from pcbnew import ToMM
O = 100.0
rb = open(sys.argv[1]).read(); xc = open(sys.argv[2]).read()
b = pcbnew.LoadBoard(sys.argv[3])
fails = []
def judge(n, ok, txt):
    print("LIMIT %s %s: %s" % (n, "MET" if ok else "EXCEEDED", txt))
    if not ok: fails.append(n)
def num(pat, s=rb):
    m = re.search(pat, s)
    return float(m.group(1)) if m else None
v = num(r"P4\.2 antenna L1 draws: nearest other-net L1 copper ([\d.]+) mm")
judge(1, v is not None and v >= 0.200, "antenna L1 clearance %s mm (limit >= 0.200)" % v)
v = num(r"A1 antenna reference outside the copper-free zone: L2 GND covers ([\d.]+) percent")
judge(2, v is not None and v >= 100.0, "antenna ground under the line outside the copper-free zone %s percent (limit 100)" % v)
for i, net in ((3, "XC1"), (4, "XC2")):
    v = num(r"P5 %s on L3: nearest other-net copper ([\d.]+) mm" % net)
    judge(i, v is not None and v >= 0.20, "%s gap on L3 %s mm (limit >= 0.20)" % (net, v))
zmin = num(r"Zdiff at modal gap [\d.]+ ohm, at min gap ([\d.]+) ohm"); zmod = num(r"Zdiff at modal gap ([\d.]+) ohm")
judge(5, zmin == 92.10 and zmod == 104.70, "USB Zdiff %s at min gap, %s at modal gap (accepted as routed in round 4: 92.10 / 104.70)" % (zmin, zmod))
v = num(r"P5 XL1 \('U1', 'B6'\) -> \('X2', '1'\): shortest drawn path ([\d.]+) mm")
judge(6, v is not None and v <= 9.343, "XL1 shortest drawn path %s mm (accepted at 9.343 in round 4; limit 9.0 waived)" % v)
u1 = b.FindFootprintByReference("U1")
balls = [(ToMM(p.GetPosition().x) - O, ToMM(p.GetPosition().y) - O) for p in u1.Pads()]
def segd(p, a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
def P(v): return (ToMM(v.x) - O, ToMM(v.y) - O)
ACCEPT = {"XL1": {("U1_VBUS", "via")}, "XL2": {("LCD_SCK", "via")}}
for i, net in ((7, "XL1"), (8, "XL2")):
    mine = [t for t in b.GetTracks() if t.GetNetname() == net and t.Type() != pcbnew.PCB_VIA_T]
    found = {}
    for t in mine:
        a, c, w, lay = P(t.GetStart()), P(t.GetEnd()), ToMM(t.GetWidth()) / 2, t.GetLayer()
        n = max(2, int(math.hypot(c[0] - a[0], c[1] - a[1]) / 0.01) + 1)
        pts = [(a[0] + (c[0] - a[0]) * k / (n - 1), a[1] + (c[1] - a[1]) * k / (n - 1)) for k in range(n)]
        pts = [q for q in pts if min(math.hypot(q[0] - x, q[1] - y) for x, y in balls) > 1.0]
        if not pts: continue
        for o in b.GetTracks():
            if o.GetNetname() == net or not o.IsOnLayer(lay): continue
            if o.Type() == pcbnew.PCB_VIA_T:
                cpos = P(o.GetPosition()); r = ToMM(o.GetWidth(lay)) / 2; kind = "via"
                d = min(math.hypot(q[0] - cpos[0], q[1] - cpos[1]) for q in pts) - r - w
            else:
                kind = "track"; s, e, r = P(o.GetStart()), P(o.GetEnd()), ToMM(o.GetWidth()) / 2
                d = min(segd(q, s, e) for q in pts) - r - w
            if d < 0.20:
                k = (o.GetNetname(), kind); found[k] = min(found.get(k, 9), round(d, 4))
        for m in b.GetFootprints():
            for p in m.Pads():
                if p.GetNetname() == net or not p.IsOnLayer(lay): continue
                bb = p.GetBoundingBox(); r = (ToMM(bb.GetLeft()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetBottom()) - O)
                d = min(math.hypot(max(r[0] - q[0], 0, q[0] - r[2]), max(r[1] - q[1], 0, q[1] - r[3])) for q in pts) - w
                if d < 0.20:
                    k = (p.GetNetname() or "(no net)", "pad " + m.GetReference()); found[k] = min(found.get(k, 9), round(d, 4))
    foreign = {k: v for k, v in found.items() if k not in ACCEPT[net]}
    judge(i, not foreign, "%s: other-net copper closer than 0.20 mm beyond 1.0 mm of U1's balls: accepted %s, not accepted %s" % (
        net, {"%s %s" % k: v for k, v in found.items() if k in ACCEPT[net]}, {"%s %s" % k: v for k, v in foreign.items()} or "none"))
print("RESULT", "PASS" if not fails else "FAIL %d: %s" % (len(fails), " ".join(map(str, fails))))
sys.exit(1 if fails else 0)
