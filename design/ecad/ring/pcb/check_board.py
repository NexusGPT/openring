#!/usr/bin/env python3
"""check_board.py [board.kicad_pcb] -- run with ./run_kipy.sh check_board.py. Exit 0 = all checks pass, 1 = any FAIL.

1 every board part of parts.csv has exactly one footprint, from OpenRing or OpenRingBand, and no footprint is extra
2 every pad's net equals the netlist net of its pin, and every netlist pin of a board part has a pad
3 no two courtyards on the same face overlap (KiCad's courtyard polygons; exception declared by the plan R2.3: U5 with U3)
4 every pad lies inside the outline; every courtyard lies inside it (ANT1 may pass by 0.10, U5 and U6 by 0.20: bodies flush
  with the edge, plan R2.5); no courtyard of another part enters the antenna copper-free zone or a tail keep-out; no via
  and no track of another net inside the antenna zone; no via in a tail keep-out
5 every part sits within 0.05 mm of the placement table placement-final.csv (round 2: the plan's current table with the
  board's own moves, board-notes-r2.md), on the face the table names
6 the scripted escapes match the plan's tables a.3 and b.2 (check_escapes.py)
7 KiCad's rules check (kicad-cli pcb drc --severity-all --all-track-errors) reports 0 violations and 0 unconnected items

Output folder (review 4 note N7): the rules check report <board name>-drc.json is written beside the board that is checked (so a run
on the delivered board writes into the design folder). Set the environment variable CHECK_BOARD_OUT to a folder (it must exist) to
write the report there instead; with the variable unset or empty the behaviour is as before.
"""
import csv, json, math, os, subprocess, sys
import pcbnew
from pcbnew import ToMM, FromMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
RING = os.path.dirname(HERE)
DESIGN = os.path.dirname(os.path.dirname(RING))
board_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ring.kicad_pcb"))
TABLE = os.path.join(HERE, "placement-final.csv")       # round 2: the full table the board is built from (board-notes-r2.md)
KC = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
OX = OY = 100.0
BAND_ONLY = {"RT1", "BT1", "SW1", "SW2", "SW3", "SW4", "SW5", "M1", "CP1", "CP2", "CP3", "CP4", "DISP1"}
OVERRIDE = {}       # round 2: no override; every position is a row of placement-final.csv
ANT_ZONE = [(-13.60, 3.10), (-9.20, 3.10), (-9.20, 3.30), (-8.75, 3.30), (-8.75, 6.30), (-13.60, 6.30)]
TAILS = {"J_BAND_A": (-3.50, -5.60, -1.00, -3.40), "J_BAND_B": (-3.50, 3.40, -1.00, 5.60)}
EDGE_OK = {"ANT1": 0.10, "U5": 0.20, "U6": 0.20}
CY_PAIR_OK = {frozenset(("U5", "U3"))}
ANT_NETS = {"RF_FEED", "ANT_TRIM"}

def rows(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))
fails = []
def fail(msg):
    fails.append(msg); print("FAIL", msg)
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY + y))
def poly(pts):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for x, y in pts: s.Append(P(x, y))
    return s
def rect(r): return poly([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])])
def area(s): return s.Area() / 1e12 if s.OutlineCount() else 0.0
def inter(a, b_):
    c = pcbnew.SHAPE_POLY_SET(a); c.BooleanIntersection(b_); return area(c)

parts = rows(os.path.join(RING, "parts.csv"))
want = [p["reference"] for p in parts if p["reference"] not in BAND_ONLY]
pin_net = {(r["reference"], r["pin_number"]): r["net"] for r in rows(os.path.join(RING, "netlist.csv"))}
table = {}
for r in rows(TABLE):
    table.setdefault(r["reference"], r)
board = pcbnew.LoadBoard(board_path)
fps = {}
for fp in board.GetFootprints():
    fps.setdefault(fp.GetReference(), []).append(fp)

# 1
for ref in want:
    if len(fps.get(ref, [])) != 1:
        fail("1 %s has %d footprints" % (ref, len(fps.get(ref, []))))
for ref, l in fps.items():
    if ref not in want:
        fail("1 extra footprint %s" % ref)
    elif l[0].GetFPID().GetLibNickname() not in ("OpenRing", "OpenRingBand"):
        fail("1 %s footprint from library %s" % (ref, l[0].GetFPID().GetLibNickname()))
n1 = len(want)

# 2
n2 = 0
for ref in want:
    if ref not in fps:
        continue
    pads = {}
    for pad in fps[ref][0].Pads():
        pads.setdefault(pad.GetNumber(), []).append(pad.GetNetname())
    for num, nets in pads.items():
        for got in nets:
            n2 += 1
            exp = pin_net.get((ref, num), "")
            if got != exp:
                fail("2 %s pad %s net '%s' but netlist says '%s'" % (ref, num, got, exp))
    for (r2, pin), n in pin_net.items():
        if r2 == ref and n and pin not in pads:
            fail("2 %s netlist pin %s (net %s) has no pad" % (ref, pin, n))

# 3
cy = {}
for ref, l in fps.items():
    fp = l[0]
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    c = pcbnew.SHAPE_POLY_SET(fp.GetCourtyard(layer))
    if c.OutlineCount() == 0:
        fail("3 %s has no courtyard" % ref)
    cy[ref] = (fp.IsFlipped(), c)
names = sorted(cy); n3 = 0
for i, a in enumerate(names):
    for b_ in names[i + 1:]:
        if cy[a][0] != cy[b_][0]:
            continue
        n3 += 1
        ov = inter(cy[a][1], cy[b_][1])
        if ov > 1e-6 and frozenset((a, b_)) not in CY_PAIR_OK:
            fail("3 courtyards overlap: %s %s (%.4f mm2)" % (a, b_, ov))

# 4
outline = pcbnew.SHAPE_POLY_SET()
if not board.GetBoardPolygonOutlines(outline, True):
    fail("4 no closed outline")
antz = poly(ANT_ZONE)
n4 = 0
for ref, l in fps.items():
    fp = l[0]
    for pad in fp.Pads():
        n4 += 1
        if not outline.Contains(pad.GetPosition()):
            fail("4 %s pad %s centre outside the outline" % (ref, pad.GetNumber()))
    c = pcbnew.SHAPE_POLY_SET(cy[ref][1]); c.BooleanSubtract(outline)
    tol = EDGE_OK.get(ref, 0.0)
    if area(c) > 1e-4:
        bb = c.BBox()
        depth = min(ToMM(bb.GetWidth()), ToMM(bb.GetHeight()))
        if depth > tol + 0.03:
            fail("4 %s courtyard leaves the outline (%.4f mm2, %.3f mm deep)" % (ref, area(c), depth))
    if ref not in ("ANT1", "LT1") and not fp.IsFlipped() and inter(cy[ref][1], antz) > 1e-6:
        fail("4 %s courtyard enters the antenna copper-free zone" % ref)
    for t, r in TAILS.items():
        if ref != t and not fp.IsFlipped() and inter(cy[ref][1], rect(r)) > 1e-6:
            fail("4 %s courtyard enters the %s keep-out" % (ref, t))
for t in board.GetTracks():
    pos = t.GetPosition()
    if t.Type() == pcbnew.PCB_VIA_T:
        x, y = ToMM(pos.x) - OX, ToMM(pos.y) - OY
        if antz.Contains(pos):
            fail("4 via (%s) inside the antenna copper-free zone at (%.3f, %.3f)" % (t.GetNetname(), x, y))
        for tn, r in TAILS.items():
            if r[0] < x < r[2] and r[1] < y < r[3]:
                fail("4 via (%s) inside the %s keep-out at (%.3f, %.3f)" % (t.GetNetname(), tn, x, y))
    else:
        if t.GetNetname() in ANT_NETS or (t.GetNetname() == "GND" and t.GetLayer() == pcbnew.F_Cu):
            continue
        for p_ in (t.GetStart(), t.GetEnd()):
            if antz.Contains(p_):
                fail("4 track (%s, %s) inside the antenna copper-free zone" % (t.GetNetname(), board.GetLayerName(t.GetLayer())))
                break

# 5
n5 = 0
for ref, l in fps.items():
    if ref not in table:
        fail("5 %s has no row in the placement table" % ref); continue
    r = table[ref]
    wx, wy = OVERRIDE.get(ref, (float(r["x_mm"]), float(r["y_mm"])))
    c = l[0].GetPosition()
    dx, dy = ToMM(c.x) - OX - wx, ToMM(c.y) - OY - wy
    n5 += 1
    if abs(dx) > 0.05 or abs(dy) > 0.05:
        fail("5 %s at offset (%.3f, %.3f) from the placement table" % (ref, dx, dy))
    if (r["side"] == "B") != l[0].IsFlipped():
        fail("5 %s on the wrong face" % ref)

# 6
ce = subprocess.run([sys.executable, os.path.join(HERE, "check_escapes.py"), board_path], capture_output=True, text=True)
last6 = [l for l in ce.stdout.splitlines() if l.startswith("RESULT")]
if ce.returncode != 0:
    fail("6 check_escapes.py exit %d: %s" % (ce.returncode, " | ".join(l for l in ce.stdout.splitlines() if l.startswith("FAIL"))[:600]))

# 7
rep = board_path[:-10] + "-drc.json"
if os.environ.get("CHECK_BOARD_OUT"):   # optional output folder, default unchanged (header, N7)
    rep = os.path.join(os.path.abspath(os.environ["CHECK_BOARD_OUT"]), os.path.basename(rep))
d = subprocess.run([KC, "pcb", "drc", "--severity-all", "--all-track-errors", "--format", "json", "-o", rep, board_path], capture_output=True, text=True)
try:
    j = json.load(open(rep))
    nv, nu = len(j.get("violations", [])), len(j.get("unconnected_items", []))
    kinds = {}
    for v in j.get("violations", []):
        kinds[v["type"]] = kinds.get(v["type"], 0) + 1
except Exception as e:
    nv = nu = -1; kinds = {"drc report unreadable": str(e)}
if nv != 0 or nu != 0:
    fail("7 rules check: %d violations %s, %d unconnected items" % (nv, kinds, nu))

print("checked: %d parts (1), %d pad nets (2), %d courtyard pairs (3), %d pads and every courtyard, via and track for the outline and keep-outs (4), %d table positions (5), escapes: %s (6), rules check: %d violations, %d unconnected (7)"
      % (n1, n2, n3, n4, n5, last6[0] if last6 else "no result", nv, nu))
if fails:
    print("RESULT: FAIL, %d problems" % len(fails)); sys.exit(1)
print("RESULT: PASS"); sys.exit(0)
