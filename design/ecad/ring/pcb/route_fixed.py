#!/usr/bin/env python3
"""route_fixed.py [board] -- adds the scripted copper of design/wiring/ring-board-plan.md step g.5 to ring.kicad_pcb
and locks every piece. Run after build_board.py: ./run_kipy.sh route_fixed.py

(a) every ball escape of U1 (table a.3) and U2 (table b.2), parsed from the plan's own tables: via in the land as listed
    (span from the "Via" column), track of the class width from the land toward the listed direction, up to 0.50 mm past
    the body edge, ending in a free end; where a placed part's pad stands closer, the track stops 0.075 mm before it
    (or ends in that pad when it is the same net). Special rows: E2, F2 (via L2-L3 at X 2.00), F1, G1 (stack L1-L3),
    D3 (L2 ground), B7 SW1 and D7 SW2 to their coils, C7 PVDD to C74, A7, E7 PVSS stacks, A6 AVSS;
(b) the antenna line of d.1 (0.120 mm) with its match parts, stubs, far-end trim part and ground stitching;
(c) the USB pair escape of d.2 down its lane (0.100 / 0.075);
(d) the 32 MHz crystal lines of d.4 on L3;
(e, f) tail land exits (f.3, rewritten for the land numbers of the band library);
(g) a ground stack at every ground pad (within 0.4 mm of the pad where room allows).
Every piece is checked against all pads and earlier copper before it is added (gap 0.075, 0.20 for the RF and USB lines).
Coordinates in model mm (KiCad = model + 100). Layers: L1 F.Cu, L2 In1.Cu, L3 In2.Cu, L4 B.Cu.
"""
import math, os, re, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PLAN = os.path.join(DESIGN, "wiring", "ring-board-plan.md")
BOARD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ring.kicad_pcb")
OX = OY = 100.0
LY = {"L1": pcbnew.F_Cu, "L2": pcbnew.In1_Cu, "L3": pcbnew.In2_Cu, "L4": pcbnew.B_Cu}
ORDER = ["L1", "L2", "L3", "L4"]
DEVIATIONS, NOTES = [], []
GAP = 0.075

b = pcbnew.LoadBoard(BOARD)
def net(n): return b.FindNet(n)
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY + y))
FP = {f.GetReference(): f for f in b.GetFootprints()}
def pad(ref, num):
    for p in FP[ref].Pads():
        if p.GetNumber() == num:
            c = p.GetPosition(); return (ToMM(c.x) - OX, ToMM(c.y) - OY)
    raise KeyError((ref, num))
def padnet(ref, num):
    for p in FP[ref].Pads():
        if p.GetNumber() == num:
            return p.GetNetname()
def padat_net(ref, n):
    m = [p.GetNumber() for p in FP[ref].Pads() if p.GetNetname() == n]
    assert len(m) == 1, (ref, n, m); return m[0]

# ---------------------------------------------------------------- geometry
def pseg(p, a, c):
    ax, ay = a; bx, by = c; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.dist(p, (ax + t * dx, ay + t * dy))
def cross(a, b_, c, d):
    def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b_, c) * o(a, b_, d) < 0 and o(c, d, a) * o(c, d, b_) < 0
def segseg(a, b_, c, d):
    if cross(a, b_, c, d): return 0.0
    return min(pseg(a, c, d), pseg(b_, c, d), pseg(c, a, b_), pseg(d, a, b_))
def rect_pt(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2]); dy = max(r[1] - p[1], 0, p[1] - r[3]); return math.hypot(dx, dy)
def rect_seg(a, b_, r):
    if rect_pt(a, r) == 0 or rect_pt(b_, r) == 0: return 0.0
    corners = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    edges = list(zip(corners, corners[1:] + corners[:1]))
    return min(segseg(a, b_, c, d) for c, d in edges)

OBST = []   # (layers set, net, kind, geom, halfwidth, cls)
for f in b.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox()
        r = (ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX, ToMM(bb.GetBottom()) - OY)
        ls = {l for l in ORDER if p.IsOnLayer(LY[l])}
        OBST.append((ls, p.GetNetname(), "rect", r, 0.0, "pad", f.GetReference() + "." + p.GetNumber()))
def dist_to(o, kind, g, hw):
    ols, onet, okind, og, ohw, ocls, oname = o
    if kind == "seg":
        if okind == "rect": d = rect_seg(g[0], g[1], og)
        elif okind == "seg": d = segseg(g[0], g[1], og[0], og[1])
        else: d = pseg(og, g[0], g[1])
    else:  # circle at g
        if okind == "rect": d = rect_pt(g, og)
        elif okind == "seg": d = pseg(g, og[0], og[1])
        else: d = math.dist(g, og)
    return d - hw - ohw
NETCLS = {}
for n in ("ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED", "ANT_TRIM"): NETCLS[n] = "RF"
for n in ("USB_DP", "USB_DN"): NETCLS[n] = "USB"
def need_gap(n, kind, o):
    ocls = NETCLS.get(o[1]); mine = NETCLS.get(n)
    g = GAP
    if mine == "RF" and kind == "seg": g = 0.2
    if ocls == "RF" and o[2] == "seg": g = 0.2
    if mine == "USB" and kind == "seg" and o[5] != "pad" and not USBEXIT[0]: g = 0.2
    if ocls == "USB" and o[2] == "seg" and kind in ("seg", "circ") and o[5] != "usbexit": g = 0.2
    if mine == "RF" and NETCLS.get(o[1]) == "RF": g = GAP
    if mine == "USB" and NETCLS.get(o[1]) == "USB": g = GAP          # inside the pair: 0.075
    if o[5] == "rfexit" or RFEXIT[0]: g = GAP if g == 0.2 and (o[5] == "rfexit" or RFEXIT[0]) else g
    return g
USBEXIT = [False]
RFEXIT = [False]     # the first RF piece, C1 to L2 inside the chip's ball area: default gap (as Nordic's layout; rule area RF_CHIP_EXIT)
def conflicts(layers, n, kind, g, hw):
    out = []
    for o in OBST:
        if not (o[0] & layers) or (o[1] == n and n):
            continue
        d = dist_to(o, kind, g, hw)
        if d < need_gap(n, kind, o) - 1e-4:
            out.append((o[6] if o[5] == "pad" else o[5] + ":" + o[1] + "@" + (("(%.3f, %.3f)" % o[3]) if o[2] == "circ" else str(o[3])[:60]), round(d, 3)))
    return out
KO = [(-13.60, 3.10, -9.20, 6.30), (-9.20, 3.30, -8.75, 6.30), (-3.50, -5.60, -1.00, -3.40), (-3.50, 3.40, -1.00, 5.60)]   # R2.0 antenna zone, tail keep-outs
def inside_board(x, y, m):
    hx, hy, rc = 13.6, 6.3, 0.8
    if abs(x) > hx - m or abs(y) > hy - m: return False
    if abs(x) > hx - rc and abs(y) > hy - rc and math.hypot(abs(x) - (hx - rc), abs(y) - (hy - rc)) > rc - m: return False
    return True

ADDED = {"seg": 0, "via": {}}
def track(layer, pts, w, n, check=True, tag=""):
    for a, c in zip(pts[:-1], pts[1:]):
        if math.dist(a, c) < 1e-6:
            continue
        UA = (3.80, 0.80, 4.75, 1.95)      # USB_CHIP_EXIT rule area of build_board.py
        USBEXIT[0] = NETCLS.get(n) == "USB" and min(a[0], c[0]) < UA[2] and max(a[0], c[0]) > UA[0] and min(a[1], c[1]) < UA[3] and max(a[1], c[1]) > UA[1]
        if check:
            cf = conflicts({layer}, n, "seg", (a, c), w / 2)
            if cf:
                raise SystemExit("scripted track %s %s %s-%s conflicts %s" % (tag, n, a, c, cf))
        t = pcbnew.PCB_TRACK(b); t.SetLayer(LY[layer]); t.SetStart(P(*a)); t.SetEnd(P(*c))
        t.SetWidth(FromMM(w)); t.SetNet(net(n)); t.SetLocked(True); b.Add(t); ADDED["seg"] += 1
        OBST.append(({layer}, n, "seg", (a, c), w / 2, "rfexit" if RFEXIT[0] else "usbexit" if USBEXIT[0] else "seg", "track"))
        USBEXIT[0] = False
def span_layers(l0, l1):
    i0, i1 = ORDER.index(l0), ORDER.index(l1)
    return set(ORDER[min(i0, i1):max(i0, i1) + 1])
def via_ok(x, y, l0, l1, n):
    if not inside_board(x, y, 0.25): return False
    if any(k[0] - 0.1 < x < k[2] + 0.1 and k[1] - 0.1 < y < k[3] + 0.1 for k in KO): return False
    if conflicts(span_layers(l0, l1), n, "circ", (x, y), 0.1): return False
    for o in OBST:      # hole to hole 0.20 (hole 0.10): via centres 0.30 apart unless the same spot
        if o[5] == "via" and math.dist(o[3], (x, y)) < 0.30 and math.dist(o[3], (x, y)) > 1e-6:
            if o[1] != n: return False
            if math.dist(o[3], (x, y)) < 0.30: return False
    return True
def via(x, y, l0, l1, n, check=True, tag=""):
    if check and not via_ok(x, y, l0, l1, n):
        raise SystemExit("scripted via %s %s at (%.3f, %.3f) %s-%s conflicts %s" % (tag, n, x, y, l0, l1, conflicts(span_layers(l0, l1), n, "circ", (x, y), 0.1)))
    v = pcbnew.PCB_VIA(b)
    if (l0, l1) == ("L1", "L4"): v.SetViaType(pcbnew.VIATYPE_THROUGH)
    elif "L1" in (l0, l1) or "L4" in (l0, l1): v.SetViaType(pcbnew.VIATYPE_BLIND)
    else: v.SetViaType(pcbnew.VIATYPE_BURIED)
    v.SetLayerPair(LY[l0], LY[l1]); v.SetPosition(P(x, y)); v.SetWidth(FromMM(0.2)); v.SetDrill(FromMM(0.1))
    v.SetNet(net(n)); v.SetLocked(True); b.Add(v)
    k = l0 + "-" + l1; ADDED["via"][k] = ADDED["via"].get(k, 0) + 1
    OBST.append((span_layers(l0, l1), n, "circ", (x, y), 0.1, "via", "via"))
    return v
def longest(layer, a, c, w, n, minlen=0.12):
    """longest clear straight piece from a toward c (step 0.025): returns its end, or None"""
    L = math.dist(a, c)
    if L < 1e-6: return a
    ux_, uy_ = (c[0] - a[0]) / L, (c[1] - a[1]) / L
    s = L
    while s >= minlen - 1e-9:
        e = (a[0] + ux_ * s, a[1] + uy_ * s)
        if not conflicts({layer}, n, "seg", (a, e), w / 2):
            return e
        s -= 0.025
    return None

# ---------------------------------------------------------------- plan tables
def table(after, until):
    txt = open(PLAN).read()
    sec = txt.split(after, 1)[1].split(until, 1)[0]
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in sec.splitlines()
            if l.startswith("| ") and not l.startswith("| Ball") and not l.startswith("|---")]
def span_of(via_text):
    if via_text.startswith("none"): return None
    if "stacked" in via_text and "L1-L2, L2-L3" in via_text: return ("L1", "L3")
    m = re.search(r"microvia (L\d)-(L\d)", via_text)
    return (m.group(1), m.group(2)) if m else "?"
def direction(esc):
    m = re.search(r"\b(north|south|west|east)\b", esc)
    return m.group(1) if m else None
U1T = table("### a.3 Ball by ball", "Differences from Nordic")
# W2 round 2, lead's ruling b (board-notes-r2.md): B5 (DBG_RX), B9 (SPARE_P2_03), G4 (SPARE_P3_05), H4 (JOY_CENTER) are not
# connected (their test pads are removed); their rows of table a.3 are read as "none" (land only, no via, no track)
NC_R2 = {"B5", "B9", "G4", "H4"}
U1T = [r[:4] + ["none", "none", "not connected (W2 round 2, ruling b)"] + r[7:] if r[0] in NC_R2 else r for r in U1T]
U2T = table("### b.2 Escape plan", "PVSS1 (A7) and PVSS2")
D = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
def body_end(cx, cy, hw, hh, x, y, d, past=0.5):
    dx, dy = D[d]
    return (cx + dx * (hw + past), y) if dx else (x, cy + dy * (hh + past))
ESC = []   # chip, ball, net, layer, span, direction, end, note

def gnd_stack_near(pts, prefer, n="GND", w=0.15):
    """a free L1-L4 stack at `prefer`, else in a spiral round it (0.05 grid, 0.6 mm) joined to it by a clear L1 track, else
    along the polyline pts (from its end back). Round 2: the spiral comes before the walk back, so that a ground escape's
    stack stays at its far end (plan a.2: at least 1.0 mm from the body) and not in front of the chip's other escapes"""
    cand = [prefer]
    for rr in [0.05 * i for i in range(1, 13)]:
        for k in range(24):
            ang = 2 * math.pi * k / 24
            cand.append((prefer[0] + rr * math.cos(ang), prefer[1] + rr * math.sin(ang)))
    for (a, c) in reversed(list(zip(pts[:-1], pts[1:]))):
        L = math.dist(a, c)
        for i in range(int(L / 0.025) + 1):
            cand.append((c[0] + (a[0] - c[0]) * i * 0.025 / max(L, 1e-9), c[1] + (a[1] - c[1]) * i * 0.025 / max(L, 1e-9)))
    for c in cand:
        if via_ok(c[0], c[1], "L1", "L4", n) and (math.dist(c, prefer) < 1e-6 or not conflicts({"L1"}, n, "seg", (prefer, c), w / 2)):
            return c
    return None

def escape(chip, ball, layer, x, y, d, end, w, n, sp, gnd_stack=False):
    # round 2: a pad of the same net straight ahead within 1.2 mm on the escape's layer: the escape runs into its centre
    # (U1 A5 into the coil L1's pad 1, U1 E10 into C1's pad 1); the router then has nothing to add there
    if n and n != "GND":
        dx_, dy_ = D[d]
        for o in OBST:
            if o[5] == "pad" and o[1] == n and layer in o[0] and not o[6].startswith(chip + "."):
                cx_, cy_ = (o[3][0] + o[3][2]) / 2, (o[3][1] + o[3][3]) / 2
                along = (cx_ - x) * dx_ + (cy_ - y) * dy_
                hits = (o[3][0] + 0.02 <= x <= o[3][2] - 0.02) if dx_ == 0 else (o[3][1] + 0.02 <= y <= o[3][3] - 0.02)
                if 0 < along < 2.5 and hits:
                    tgt = (x, cy_) if dx_ == 0 else (cx_, y)
                    if not conflicts({layer}, n, "seg", ((x, y), tgt), w / 2):
                        end = tgt; break
    e = longest(layer, (x, y), end, w, n)
    if gnd_stack and w > 0.1 and (e is None or math.dist(e, end) > 1e-6):
        # round 2: a ground escape that 0.15 does not carry to its full length is tried at 0.10 (U1 A7 passes between the
        # pads of the coil L1 of the round 4 table at 0.10 only: 0.098 to each pad)
        e2 = longest(layer, (x, y), end, 0.1, n)
        if e2 is not None and (e is None or math.dist(e2, end) < math.dist(e, end) - 0.2):
            DEVIATIONS.append("%s %s (%s): escape 0.10 wide, not %.2f: at %.2f it stops %.3f short" % (chip, ball, n, w, w, math.dist(e, end) if e else -1))
            e, w = e2, 0.1
    if e is None:
        DEVIATIONS.append("%s %s (%s): no clear escape on %s toward %s" % (chip, ball, n, layer, d)); ESC.append((chip, ball, n, layer, sp, d, None, "blocked")); return
    note = "full" if math.dist(e, end) < 1e-6 else "stopped %.3f short of the full length by %s" % (math.dist(e, end), ",".join(c[0] for c in conflicts({layer}, n, "seg", ((x, y), end), w / 2)))
    track(layer, [(x, y), e], w, n, tag=chip + ball)
    if gnd_stack:
        s = gnd_stack_near([(x, y), e], e, n, w)
        if s:
            if math.dist(s, e) > 1e-6 and not any(pseg(s, (x, y), e) < 1e-6 for _ in [0]):
                track("L1", [e, s], w, n)
            via(s[0], s[1], "L1", "L4", n, tag=chip + ball)
        else:
            NOTES.append("%s %s: no room for its ground stack near the escape end" % (chip, ball))
    ESC.append((chip, ball, n, layer, sp, d, e, note))

# ---------------------------------------------------------------- (a) U1, table a.3
u1 = FP["U1"]; ux, uy = ToMM(u1.GetPosition().x) - OX, ToMM(u1.GetPosition().y) - OY
U1HW, U1HH = 3.020 / 2, 2.430 / 2
# round 2: U1's signal escapes end U1_PAST mm past the body edge (the plan's "up to 0.50"): in the round 4 table L1 (the DC/DC
# coil), C4 and C6 stand 0.25 to 0.4 mm north of the body, and 0.5 mm stubs on three layers in the same columns left the
# router no place for a via (board-notes-r2.md, step 3)
U1_PAST = float(os.environ.get("U1_PAST", "0.15"))
rows1 = {}
for row in U1T:
    ball, pin, netn, land, layer, vtext, esc = row[:7]
    x, y = pad("U1", ball)
    lx, ly = [float(v) for v in land.replace("+", "").split(",")]
    if abs(lx - x) > 0.002 or abs(ly - y) > 0.002:
        raise SystemExit("U1 %s land on the board (%.3f, %.3f) differs from the plan table (%s)" % (ball, x, y, land))
    pn = padnet("U1", ball) or ""
    if layer == "none":
        if pn: raise SystemExit("U1 %s should be no-connect, pad net %s" % (ball, pn))
        ESC.append(("U1", ball, "", "none", None, None, None, "no-connect")); continue
    if pn != netn:
        raise SystemExit("U1 %s pad net %s, plan %s" % (ball, pn, netn))
    rows1[ball] = (netn, layer, span_of(vtext), direction(esc), x, y)
# vias in the lands first (they constrain every layer), then tracks
for ball, (n, layer, sp, d, x, y) in rows1.items():
    if sp: via(x, y, sp[0], sp[1], n, tag="U1" + ball)
# crystal lines (d.4) right after the vias: they own the column 1 and 2 lines on L3
x1_1, x1_3 = pad("X1", "1"), pad("X1", "3")
def plen(pts): return sum(math.dist(a, c) for a, c in zip(pts[:-1], pts[1:]))
a1p, a2p = pad("U1", "A1"), pad("U1", "A2")
xc2 = [a1p, (a1p[0], x1_3[1]), x1_3]
xb = a2p[0] + 0.426                                   # XC1 meander east of its line: two 0.426 legs, rows 0.20 apart (d.4: lengths within 0.5)
xc1 = [a2p, (a2p[0], x1_1[1] - 0.40), (xb, x1_1[1] - 0.40), (xb, x1_1[1] - 0.20), (a2p[0], x1_1[1] - 0.20), (a2p[0], x1_1[1]), x1_1]
for pts, padxy, n, ball in ((xc2, x1_3, "XC2", "A1"), (xc1, x1_1, "XC1", "A2")):
    via(padxy[0], padxy[1], "L1", "L3", n, tag="X1 " + n)
    track("L3", pts, 0.1, n, tag="crystal " + n)
    ESC.append(("U1", ball, n, "L3", ("L1", "L3"), "south", padxy, "to X1 (d.4)"))
L_XC2, L_XC1 = plen(xc2), plen(xc1)
NOTES.append("crystal lines on L3: XC2 (A1) %.3f mm, XC1 (A2) %.3f mm, difference %.3f mm (plan d.4: 6.0 or less each, within 0.5)" % (L_XC2, L_XC1, abs(L_XC2 - L_XC1)))
# ---------------------------------------------------------------- (b) antenna line, d.1 and e (round 2: placed right after the crystal lines, before the ball escapes, so that no ground stack of an escape lands on its 0.20 gap)
RFW = 0.12
c1 = pad("U1", "C1")
L2a, L2b = pad("L2", "1"), pad("L2", "2")
L3a, L3b = pad("L3", "1"), pad("L3", "2")
L4a, L4b = pad("L4", "1"), pad("L4", "2")
C3a, C12a, C89a, C13a = pad("C3", "1"), pad("C12", "1"), pad("C89", "1"), pad("C13", "1")
feed = pad("ANT1", "1")
yl = c1[1]
XR, YR, XRISE = 0.0, 3.30, -6.70                 # round 2 reserve lanes: X -0.26..0.26, Y 3.04..3.56, X -6.96..-6.44
RFEXIT[0] = True
track("L1", [c1, (L2a[0], yl)], RFW, "ANT1_NODE", tag="RF1")
RFEXIT[0] = False
track("L1", [(L2b[0], yl), (L3a[0], yl)], RFW, "ANT2_NODE", tag="RF2")
track("L1", [(C3a[0], yl), C3a], RFW, "ANT2_NODE", tag="C3 stub")
line3 = [(L3b[0], yl), (XR + 0.2, yl), (XR, yl + 0.2), (XR, YR - 0.2), (XR - 0.2, YR), (XRISE + 0.2, YR), (XRISE, YR + 0.2), (XRISE, L4a[1] - 0.2), (XRISE - 0.2, L4a[1]), L4a]
track("L1", line3, RFW, "ANT3_NODE", tag="RF3")
track("L1", [(XR + 0.2, yl), (C12a[0], yl), C12a], RFW, "ANT3_NODE", tag="C12 stub")      # the shunt's stub leaves the line at the corner
track("L1", [(C89a[0], L4a[1]), C89a], RFW, "ANT3_NODE", tag="C89 stub")
track("L1", [L4b, feed], RFW, "RF_FEED", tag="feed")
track("L1", [(C13a[0], L4b[1]), C13a], RFW, "RF_FEED", tag="C13 stub")
rf_len = sum(math.dist(a, c) for a, c in zip(line3[:-1], line3[1:])) + math.dist(c1, (L2a[0], yl)) + math.dist((L2b[0], yl), (L3a[0], yl)) + math.dist(L4b, feed)
NOTES.append("antenna line length from U1 C1 to the feed land, legs only (match parts excluded): %.2f mm" % rf_len)
a2, a3, a4 = pad("ANT1", "2"), pad("ANT1", "3"), pad("ANT1", "4")
lt1, lt2 = pad("LT1", "1"), pad("LT1", "2")
track("L1", [a2, a3], 0.15, "ANT_TRIM", tag="trim")
track("L1", [a3, (lt1[0], a3[1]), lt1], 0.15, "ANT_TRIM", tag="trim2")
s = gnd_stack_near([lt2, (lt2[0], 2.95)], (lt2[0] + 0.2, 2.95))
track("L1", [lt2, (lt2[0], s[1]), s], 0.15, "GND", tag="LT1 gnd"); via(s[0], s[1], "L1", "L4", "GND", tag="LT1 gnd")
s4 = gnd_stack_near([a4, (a4[0] + 0.9, a4[1])], (a4[0] + 0.9, a4[1]))
track("L1", [a4, (s4[0], a4[1]), s4], 0.15, "GND", tag="ANT1.4 gnd"); via(s4[0], s4[1], "L1", "L4", "GND", tag="ANT1.4 gnd")
for ref in ("C3", "C12", "C13", "C89"):
    g, f1 = pad(ref, "2"), pad(ref, "1")
    dx, dy = g[0] - f1[0], g[1] - f1[1]; nn = math.hypot(dx, dy)
    want = (g[0] + dx / nn * 0.3, g[1] + dy / nn * 0.3)
    s = gnd_stack_near([g, want], want)
    track("L1", [g, s], 0.15, "GND", tag=ref + " gnd"); via(s[0], s[1], "L1", "L4", "GND", tag=ref + " gnd")
NOTES.append("antenna line path as R2.0 item 3: X 0.00 leg, Y 3.30 leg, rise along X %.2f, into L4 and the feed land" % XRISE)
DEVIATIONS.append("LT1 ground: a stack just below the zone edge (Y 3.10), not a via in J1's mounting pad (R2.0 item 4): J1's pads MP keep no net, so the netlist and the schematic do not change")
# stitching: L1-L4 stacks both sides of the line every 1.0 mm, 0.46 mm from its centre, where free
legs = [((XR, yl + 0.5), (XR, YR - 0.5)), ((XR - 0.5, YR), (XRISE + 0.5, YR)), ((XRISE, YR + 0.5), (XRISE, L4a[1] - 0.4))]
nst = ntry = 0
for (s0, e0) in legs:
    L = math.dist(s0, e0); k = max(1, int(round(L / 1.0)))
    dx, dy = (e0[0] - s0[0]) / L, (e0[1] - s0[1]) / L
    for i in range(k + 1):
        px, py = s0[0] + dx * L * i / k, s0[1] + dy * L * i / k
        for side in (-1, 1):
            ntry += 1
            q = (px - dy * side * 0.46, py + dx * side * 0.46)
            if via_ok(q[0], q[1], "L1", "L4", "GND"):
                via(q[0], q[1], "L1", "L4", "GND"); nst += 1
NOTES.append("RF stitching stacks: %d placed of %d sites (sites blocked by a pad, the tail keep-out or other copper are left out)" % (nst, ntry))

# ---------------------------------------------------------------- (c) USB pair, d.2: U1 H6/H7 to U9 and the tail B lands, all scripted
# D- runs on the inner line, D+ on the edge-side line (d.2). U9 (rotated 90) has pins 1 (D+) and 2 (D-) at the west end of its
# south row and no-net pins 9, 10 north of them, so the pair cannot flow through; it reaches the two pins by short stubs:
# D+ from below (edge-side line Y 6.065), D- from the channel between U9's two pad rows (Y 5.20, one 0.100 track fits).
USBW = 0.1
h6, h7 = pad("U1", "H6"), pad("U1", "H7")
u9p1, u9p2 = pad("U9", "1"), pad("U9", "2")
tdp, tdn = pad("J_BAND_B", padat_net("J_BAND_B", "USB_DP")), pad("J_BAND_B", padat_net("J_BAND_B", "USB_DN"))
XDN, XDP = 4.40, 4.575            # lane (round 2 reserve X 4.15 to 4.83), pitch 0.175
YDP, YDN = 6.065, 5.89            # edge-side and inner line along the +Y edge (d.2)
YCH = (pad("U9", "10")[1] + u9p1[1]) / 2   # channel between U9's rows
k = (XDN - (1.55 + (XDN - h6[0]))) + 0.1755 * math.sqrt(2)      # D+ diagonal parallel to D-'s, 0.175 apart (x - y = k)
yd0 = h7[0] - k
dp = [h7, (h7[0], yd0), (XDP, XDP - k), (XDP, YDP), (u9p1[0], YDP), (tdp[0], YDP), tdp]
dn0 = [h6, (h6[0], 1.55), (XDN, 1.55 + (XDN - h6[0])), (XDN, YCH), (u9p2[0], YCH), (1.85, YCH), (1.85, YDN), (tdn[0], YDN), tdn]
need = sum(math.dist(a, c) for a, c in zip(dp[:-1], dp[1:])) - sum(math.dist(a, c) for a, c in zip(dn0[:-1], dn0[1:]))
amp = min(0.30, max(0.0, need / 4))                   # two bumps toward -Y on the inner line (D+ runs on the edge side)
xs0 = -1.45
bumps = [(xs0, YDN), (xs0, YDN - amp), (xs0 - 0.25, YDN - amp), (xs0 - 0.25, YDN), (xs0 - 0.50, YDN), (xs0 - 0.50, YDN - amp), (xs0 - 0.75, YDN - amp), (xs0 - 0.75, YDN)]
dn = [h6, (h6[0], 1.55), (XDN, 1.55 + (XDN - h6[0])), (XDN, YCH), (u9p2[0], YCH), (1.85, YCH), (1.85, YDN)] + (bumps if amp > 0.01 else []) + [(tdn[0], YDN), tdn]
track("L1", dn, USBW, "USB_DN", tag="USB_DN")
track("L1", dp, USBW, "USB_DP", tag="USB_DP")
track("L1", [(u9p2[0], YCH), (u9p2[0], u9p2[1])], USBW, "USB_DN", tag="U9 pin 2 stub")
track("L1", [(u9p1[0], YDP), (u9p1[0], u9p1[1])], USBW, "USB_DP", tag="U9 pin 1 stub")
for pn_, l1_ in (("3", "L4"), ("4", "L3"), ("5", "L3")):       # pins boxed in by the pair: via in the pad
    q = pad("U9", pn_); via(q[0], q[1], "L1", l1_, padnet("U9", pn_), tag="U9 pin " + pn_)
ldn, ldp = plen(dn), plen(dp)
NOTES.append("USB pair lengths U1 to tail land: D- %.3f mm, D+ %.3f mm, difference %.3f mm (stubs to U9: D- %.3f, D+ %.3f)" % (ldn, ldp, abs(ldn - ldp), abs(u9p2[1] - YCH), abs(YDP - u9p1[1])))
ESC.append(("U1", "H6", "USB_DN", "L1", None, "south", (XDN, YCH), "USB pair to U9 pin 2 and tail B"))
ESC.append(("U1", "H7", "USB_DP", "L1", None, "south", (XDP, YDP), "USB pair to U9 pin 1 and tail B"))
DEVIATIONS.append("USB pair: no flow-through over U9 pins 1, 2 (U9 pins 9, 10 have no net and lie on that path); stubs of %.3f (D-) and %.3f (D+) mm reach the pins" % (abs(u9p2[1] - YCH), abs(YDP - u9p1[1])))

# round 2: signal escapes first, ground escapes (with their L1-L4 stacks) after them, so that a ground stack never lands on
# another ball's L2 or L3 escape line (plan a.2: the ground stacks sit off every escape line)
for ball, (n, layer, sp, d, x, y) in sorted(rows1.items(), key=lambda kv: kv[1][0] == "GND"):
    if ball in ("A1", "A2", "C1", "H6", "H7"):
        continue
    w = 0.15 if n == "GND" else 0.1
    if ball == "D3":
        e = longest("L2", (x, y), (ux - U1HW - 0.3, y), 0.1, n)
        track("L2", [(x, y), e], 0.1, n, tag="U1D3")
        # round 2: run 3 left D3's L2 ground piece cut off (R2/full3/gnd_islands.log); a stack L2-L4 at the track's end
        # joins it to the L4 plane (the line is on L1, so L2 under it stays ground)
        if via_ok(e[0], e[1], "L2", "L4", n): via(e[0], e[1], "L2", "L4", n, tag="U1D3")
        else: NOTES.append("U1 D3: no room for the L2-L4 stack at its L2 track end (%.3f, %.3f)" % e)
        ESC.append(("U1", ball, n, layer, sp, "west", e, "into the L2 ground")); continue
    if ball in ("E2", "F2"):
        track("L2", [(x, y), (2.00, y)], w, n, tag="U1" + ball); via(2.00, y, "L2", "L3", n, tag="U1" + ball)
        ESC.append(("U1", ball, n, layer, sp, d, (2.00, y), "via L2-L3 at X 2.00")); continue
    if ball in ("F1", "G1"):
        xs = 2.30 if ball == "G1" else 1.70
        e = longest("L1", (x, y), (xs, y), w, n)
        if e is not None and math.dist(e, (xs, y)) < 1e-6 and via_ok(xs, y, "L1", "L3", n):
            track("L1", [(x, y), (xs, y)], w, n, tag="U1" + ball); via(xs, y, "L1", "L3", n, tag="U1" + ball)
            ESC.append(("U1", ball, n, layer, sp, d, (xs, y), "stack L1-L3 at X %.2f" % xs)); continue
        # round 2 table: C7 and C5 stand west of the F and G balls (plan round 4, zone R3), so the L1-L3 stack of a.2 has no
        # room; the escape is the L1 stub west (table a.3: L1, west) and the router makes the RF crossing
        e = longest("L1", (x, y), (ux - U1HW - 0.5, y), w, n)
        track("L1", [(x, y), e], w, n, tag="U1" + ball)
        DEVIATIONS.append("U1 %s: no room for the L1-L3 stack at X %.2f (C7, C5 of the round 4 table); L1 stub west to (%.3f, %.3f), crossing left to the router" % (ball, xs, e[0], e[1]))
        ESC.append(("U1", ball, n, layer, sp, d, e, "L1 stub west, crossing by the router")); continue
    end = body_end(ux, uy, U1HW, U1HH, x, y, d, 1.0 if n == "GND" else U1_PAST)
    if layer in ("L2", "L3") and n != "GND":
        # round 2: an inner-layer escape ends at the outermost ball site of its line (table a.3: "straight through the row A
        # site" and so on); the router continues it. Ending there keeps the line beyond the body free for the vias of the
        # L1 escapes of the same column (board-notes-r2.md, step 3)
        ring1 = {"north": (x, uy - 1.078), "south": (x, uy + 1.074), "west": (ux - 1.402, y), "east": (ux + 1.399, y)}[d]
        end = ring1
    escape("U1", ball, layer, x, y, d, end, w, n, sp, gnd_stack=(n == "GND"))
if any(e_[1] == "F1" and "X 1.70" in e_[7] for e_ in ESC):
    DEVIATIONS.append("U1 F1: stack L1-L3 at X 1.70, not 2.30: at 2.30 its L2 land would sit on F2's L2 track (Y 0.324, to X 2.00)")

# ---------------------------------------------------------------- (a) U2, table b.2
u2 = FP["U2"]; vx, vy = ToMM(u2.GetPosition().x) - OX, ToMM(u2.GetPosition().y) - OY
U2HW, U2HH = 2.3775 / 2, 3.0775 / 2
rows2 = {}
for row in U2T:
    ball, pin, netn, land, layer, vtext, esc = row[:7]
    x, y = pad("U2", ball)
    lx, ly = [float(v) for v in land.replace("+", "").split(",")]
    if abs(lx - x) > 0.002 or abs(ly - y) > 0.002:
        raise SystemExit("U2 %s land on the board (%.3f, %.3f) differs from the plan table (%s)" % (ball, x, y, land))
    pn = padnet("U2", ball) or ""
    if layer == "none":
        if pn: raise SystemExit("U2 %s should be no-connect, pad net %s" % (ball, pn))
        ESC.append(("U2", ball, "", "none", None, None, None, "no-connect")); continue
    if pn != netn:
        raise SystemExit("U2 %s pad net %s, plan %s" % (ball, pn, netn))
    w = 0.25 if "0.25" in esc else 0.2 if "0.2," in esc else 0.15 if ("0.15" in esc or netn in ("GND", "VSYS", "VBAT", "VBUS")) else 0.1
    rows2[ball] = (netn, layer, span_of(vtext), direction(esc), x, y, w)
for ball, (n, layer, sp, d, x, y, w) in rows2.items():
    if sp: via(x, y, sp[0], sp[1], n, tag="U2" + ball)
L71p1, L72p1, C74p1 = pad("L71", "1"), pad("L72", "1"), pad("C74", "1")
for ball, (n, layer, sp, d, x, y, w) in sorted(rows2.items(), key=lambda kv: kv[1][0] == "GND"):
    if ball in ("B2", "C2", "D2"):
        track("L1", [(x, y), pad("U2", ball[0] + "1")], 0.15, n, tag="U2" + ball)
        ESC.append(("U2", ball, n, layer, sp, "bridge", pad("U2", ball[0] + "1"), "joined to %s1" % ball[0])); continue
    if ball == "B7":
        pts = [(x, y), (x, 1.65), (L71p1[0], 1.65), L71p1]
        track("L1", pts, 0.15, n, tag="SW1"); ESC.append(("U2", ball, n, layer, sp, d, L71p1, "to L71 pad 1")); continue
    if ball == "D7":
        pts = [(x, y), (x, 1.55), (L72p1[0], 1.55 + abs(x - L72p1[0])), L72p1]
        track("L1", pts, 0.15, n, tag="SW2"); ESC.append(("U2", ball, n, layer, sp, d, L72p1, "to L72 pad 1")); continue
    if ball == "C7":
        track("L1", [(x, y), (x, C74p1[1]), C74p1], 0.15, n, tag="PVDD"); ESC.append(("U2", ball, n, layer, sp, d, C74p1, "to C74 pad 1")); continue
    if ball in ("A7", "E7"):
        want = (10.00, y) if ball == "A7" else (7.00, y)
        e = longest("L1", (x, y), want, 0.2, n)
        track("L1", [(x, y), e], 0.2, n, tag="U2" + ball)
        s = gnd_stack_near([(x, y), e], e)
        via(s[0], s[1], "L1", "L4", n, tag="U2" + ball)
        ESC.append(("U2", ball, n, layer, sp, d, e, "own ground stack at (%.2f, %.2f)" % s)); continue
    end = body_end(vx, vy, U2HW, U2HH, x, y, d, 1.0 if n == "GND" else 0.5)
    if layer == "L2":
        # round 2: as for U1, an inner-layer escape ends 0.10 past the outermost ball site of its line (table b.2: "through
        # the A4 site" and so on), so the L1 escapes of the same row keep room for a via beyond it
        end = {"north": (x, vy - 1.257 - 0.10), "south": (x, vy + 1.257 + 0.10), "west": (vx - 0.880 - 0.10, y), "east": (vx + 0.880 + 0.10, y)}[d]
    escape("U2", ball, layer, x, y, d, end, w, n, sp, gnd_stack=(n == "GND"))

# round 2 (b): U1 E10 and U2 E4 are both VDD_1V8 and face each other on L1 along Y 0.00; with the strip between U1 and U2
# emptied (C1, C2, R71, R72, C14 on the screen face) one L1 track joins their escape ends (run 9 and piece 12: walled in)
_e10 = [e_ for e_ in ESC if e_[0] == "U1" and e_[1] == "E10" and e_[6]]
_e4 = [e_ for e_ in ESC if e_[0] == "U2" and e_[1] == "E4" and e_[6]]
if _e10 and _e4 and abs(_e10[0][6][1] - _e4[0][6][1]) < 0.01:
    a_, c_ = _e10[0][6], _e4[0][6]
    if not conflicts({"L1"}, "VDD_1V8", "seg", (a_, c_), 0.05):
        track("L1", [a_, c_], 0.1, "VDD_1V8", tag="E10-E4 join"); NOTES.append("VDD_1V8: U1 E10 joined to U2 E4 on L1 (%.3f to %.3f)" % (a_[0], c_[0]))
    else:
        NOTES.append("VDD_1V8: E10-E4 join blocked by %s" % conflicts({"L1"}, "VDD_1V8", "seg", (a_, c_), 0.05))

# ---------------------------------------------------------------- (e, f) tail land exits (f.3, for the pads of the band library)
def ex(ref, num, pts, w, n, stack):
    p0 = pad(ref, num)
    if padnet(ref, num) != n:
        raise SystemExit("%s pad %s is %s, exit written for %s" % (ref, num, padnet(ref, num), n))
    track("L1", [p0] + pts, w, n, tag="%s.%s" % (ref, num))
    if stack:
        via(pts[-1][0], pts[-1][1], stack[0], stack[1], n, tag="%s.%s" % (ref, num))
def padat(ref, x, y):
    for p in FP[ref].Pads():
        c = p.GetPosition()
        if abs(ToMM(c.x) - OX - x) < 0.01 and abs(ToMM(c.y) - OY - y) < 0.01:
            return p.GetNumber(), p.GetNetname()
    raise KeyError((ref, x, y))
# tail B (lands: band-interface.md section 2 = library)
ex("J_BAND_B", padat("J_BAND_B", -3.015, 3.875)[0], [(-3.75, 3.875)], 0.15, "VBAT", ("L1", "L3"))
ex("J_BAND_B", padat("J_BAND_B", -2.505, 3.875)[0], [(-2.505, 4.325), (-0.85, 4.325)], 0.1, "NTC", ("L1", "L3"))
ex("J_BAND_B", padat("J_BAND_B", -1.995, 3.875)[0], [(-1.485, 3.875), (-0.85, 3.875)], 0.2, "GND", ("L1", "L4"))
ex("J_BAND_B", padat("J_BAND_B", -1.995, 4.775)[0], [(-0.85, 4.775)], 0.25, "VBUS", ("L1", "L3"))
# tail A: the library numbers differ from the f.3 table; exits by position and net
A = {(x, y): padat("J_BAND_A", x, y) for x in (-3.015, -2.505, -1.995, -1.485) for y in (-3.875, -4.775)}
NOTES.append("J_BAND_A lands in the band library: " + ", ".join("%s %s at (%.3f, %.3f)" % (v[0], v[1], k[0], k[1]) for k, v in sorted(A.items())))
# tail A: far row (Y -3.875) straight toward the board middle to stacks at Y -3.25; near row (Y -4.775): east column east
# along its row, second column into the row gap and east, third column south under the tail then east, west column south
# then west (U10's pads stand 0.25 mm west of the keep-out, so no stack fits west of the lands on the land rows)
def exA(x, yy, pts, st, w=None):
    num, n = A[(x, yy)]
    ex("J_BAND_A", num, pts, w or (0.2 if n == "GND" else 0.15 if n == "VMOT" else 0.1), n, ("L1", "L4") if n == "GND" else st)
for x in (-3.015, -2.505, -1.995, -1.485):
    exA(x, -3.875, [(x, -3.25)], ("L1", "L3"))
exA(-1.485, -4.775, [(-0.85, -4.775)], ("L1", "L3"))
exA(-2.505, -4.775, [(-2.505, -4.325), (-0.85, -4.325)], ("L1", "L3"))
exA(-1.995, -4.775, [(-1.995, -5.45), (-0.85, -5.45)], ("L1", "L3"))
exA(-3.015, -4.775, [(-3.015, -5.45), (-3.65, -5.45)], ("L1", "L3"))
DEVIATIONS.append("tail A exits follow the land numbers of the band library (they differ from the plan's f.3 table, which follows an older land order)")

# ---------------------------------------------------------------- (g) ground stacks at ground pads
ngs, nmiss = 0, []
gpads = []
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() == "GND" and p.IsOnLayer(pcbnew.F_Cu) and f.GetReference() not in ("U1", "U2"):
            bb = p.GetBoundingBox()
            fc = f.GetPosition()
            gpads.append((f.GetReference(), p.GetNumber(), (ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX, ToMM(bb.GetBottom()) - OY),
                          (ToMM(fc.x) - OX, ToMM(fc.y) - OY)))
for ref, num, r, fcen in gpads:
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    # one stack serves the ground pads within 0.8 mm (the L1 ground copper joins them); more stacks only block the routing
    if any(o[5] == "via" and o[1] == "GND" and rect_pt(o[3], r) < 0.8 for o in OBST):
        continue
    out_ang = math.atan2(cy - fcen[1], cx - fcen[0]) if math.hypot(cy - fcen[1], cx - fcen[0]) > 1e-6 else 0.0
    angs = sorted(range(24), key=lambda k: abs(math.remainder(2 * math.pi * k / 24 - out_ang, 2 * math.pi)))   # away from the part first
    best = None
    for rr in [0.0] + [0.05 * i for i in range(1, 9)]:
        for k in angs:
            ang = 2 * math.pi * k / 24
            x = cx + ((r[2] - r[0]) / 2 + rr + 0.0) * math.cos(ang); y = cy + ((r[3] - r[1]) / 2 + rr) * math.sin(ang)
            if rect_pt((x, y), r) > 0.4 + 1e-9: continue
            if not via_ok(x, y, "L1", "L4", "GND"): continue
            if rect_pt((x, y), r) > 1e-9 and conflicts({"L1"}, "GND", "seg", ((cx, cy), (x, y)), 0.075):
                continue
            best = (x, y); break
        if best: break
    if not best:
        nmiss.append("%s.%s" % (ref, num)); continue
    if rect_pt(best, r) > 1e-9:
        track("L1", [(cx, cy), best], 0.15, "GND", check=False)
    via(best[0], best[1], "L1", "L4", "GND"); ngs += 1
NOTES.append("ground stacks at ground pads: %d added; pads with no free spot within 0.4 mm (they reach L4 through the L1 ground copper): %s" % (ngs, " ".join(nmiss) or "none"))

pcbnew.SaveBoard(BOARD, b)
nl = sum(1 for t in b.GetTracks() if t.IsLocked())
print("scripted segments", ADDED["seg"], "vias by span", dict(sorted(ADDED["via"].items())), "locked items", nl)
for e in ESC:
    print("ESCAPE", e[0], e[1], e[2] or "-", e[3], "-".join(e[4]) if e[4] else "no-via", e[5], ("(%.3f, %.3f)" % e[6]) if e[6] else "-", e[7])
for d in DEVIATIONS: print("DEVIATION", d)
for n_ in NOTES: print("NOTE", n_)
