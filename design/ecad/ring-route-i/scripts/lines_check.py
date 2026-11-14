# lines_check.py p4p5.log xcheck.log linestretch-far.log : judges the 8 controlled-line limits of design/ecad/ring/pcb/board-notes-r4.md
# ("The 8 controlled-line limits") on one board, from the read-back log (rb/p4p5.py), the pcbnew cross-check log (rb/xcheck_clear.py)
# and the board itself. Run with KiCad's Python. Prints one line per limit and RESULT PASS / FAIL n; exit 1 on any FAIL.
#  1 antenna L1 clearance >= 0.200 mm (P4.2)
#  2 antenna ground under the line outside the copper-free zone 100.0000 percent (A1, lead's ruling)
#  3 XC1 gap >= 0.20 mm (P5 XC1 on L3)          4 XC2 gap >= 0.20 mm (P5 XC2 on L3)
#  5 USB Zdiff: accepted as routed in round 4 -> figures must be the accepted ones (92.10 at min gap, 104.70 at modal gap)
#  6 XL1 length: accepted at 9.343 mm -> shortest drawn path <= 9.343
#  7 XL1 gap, 8 XL2 gap: waived inside U1's ball field; beyond 1.0 mm outside U1's body only the nets accepted in round 4 may come
#    closer than 0.20 mm (tracks and vias): XL1 -> U1_VBUS, XL2 -> LCD_SCK (board-notes-r4.md, ring-lines/logs/linestretch-far2-t07.log),
#    read from round 4's own script linestretch.py run with FAR=1.0 (copy in rb/).
import sys, re, math
O = 100.0
rb = open(sys.argv[1]).read(); xc = open(sys.argv[2]).read()
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
ls = open(sys.argv[3]).read()
ACCEPT = {"XL1": {"U1_VBUS"}, "XL2": {"LCD_SCK"}}
import ast
for i, net in ((7, "XL1"), (8, "XL2")):
    m = re.search(r"%s per neighbour net \(tracks and vias\) minimum gap under 0\.20: (\{.*\})" % net, ls)
    d = ast.literal_eval(m.group(1)) if m else None
    foreign = {k: v for k, v in (d or {}).items() if k not in ACCEPT[net]}
    judge(i, d is not None and not foreign, "%s, tracks and vias closer than 0.20 mm more than 1.0 mm outside U1's body (round 4's linestretch.py, FAR=1.0): %s; accepted in round 4: %s; not accepted: %s" % (
        net, d, sorted(ACCEPT[net]), foreign or "none"))
print("RESULT", "PASS" if not fails else "FAIL %d: %s" % (len(fails), " ".join(map(str, fails))))
sys.exit(1 if fails else 0)
