#!/usr/bin/env python3
"""Checks the two case board files against the netlist.
usage: check_boards.py [case_main.kicad_pcb [case_pins.kicad_pcb]]      (re-runs itself under KiCad's Python when pcbnew is missing)
Exit 0 only when ALL of these hold:
  1. every pad of both boards has the net the netlist gives its (reference, pin) (no-connect pins: no net); every pad number exists in the netlist;
     the PCB2 ends of the wires (WP1 WP2 WP3 WP4 WP7) carry the net of W1 W2 W3 W4 W7
  2. every netlist pin of every placed part has a pad on the board that carries the part, and every part of parts.csv is on one of the two boards (once)
  3. no two courtyards overlap on a board
  4. every pad (copper and hole) lies inside the board outline with at least the copper edge clearance
  6. silkscreen marks: P1..P4 on their own piece of PCB2, W1 W2 W3 W4 W7 beside their holes on PCB1, "W5 +", "W6 -" and TH1 at theirs, every text 1.0 mm high or more
  5. kicad-cli pcb drc --severity-all --all-track-errors reports 0 violations and 0 unconnected items on each board
Exit 1 otherwise.  Also prints (information, not a failure) the USB D+/D- track length difference."""
import csv, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)
try:
    import pcbnew
except ImportError:
    K = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9"
    env = dict(os.environ, PYTHONPATH=K + "/lib/python3.9/site-packages")
    os.execve(K + "/bin/python3", [K + "/bin/python3"] + sys.argv, env)
from pcbnew import ToMM

KC = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
MAIN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "case_main.kicad_pcb")
PINS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "case_pins.kicad_pcb")
TMP = os.environ.get("CHECK_BOARDS_TMP", os.path.join(HERE, "evidence"))
FAIL = []


def fail(m):
    FAIL.append(m)
    print("FAIL", m)


def ok(m):
    print("ok  ", m)


parts = {r["reference"]: r for r in csv.DictReader(open(os.path.join(CASE, "parts.csv")))}
netrows = list(csv.DictReader(open(os.path.join(CASE, "netlist.csv"))))
pinnet = {(r["reference"], r["pin_number"]): r["net"] for r in netrows}
pins_of = {}
for r in netrows:
    pins_of.setdefault(r["reference"], set()).add(r["pin_number"])
WIRE_ENDS = {"WP1": "W1", "WP2": "W2", "WP3": "W3", "WP4": "W4", "WP7": "W7"}
for _wp, _w in WIRE_ENDS.items():      # the pin-board end of a wire carries the net of the wire's main-board hole (netlist rows WP* since review m4)
    if pinnet.get((_wp, "1")) is None or pinnet.get((_wp, "1")) != pinnet.get((_w, "1")):
        fail("netlist: %s net %r differs from %s net %r" % (_wp, pinnet.get((_wp, "1")), _w, pinnet.get((_w, "1"))))
VIRTUAL = {"BT1"}                      # the cell: no copper, drawn on F.Fab only


def expected(ref, pin):
    return pinnet.get((ref, pin), None)


def run_drc(path, tag):
    out = os.path.join(TMP, "check_drc_%s_%s.json" % (tag, os.path.basename(os.path.dirname(os.path.abspath(path))) or "x"))
    out = os.path.join(TMP, "check_drc_%s_%d.json" % (tag, os.getpid()))
    with open(out + ".log", "w") as lg:
        rc = subprocess.call([KC, "pcb", "drc", "--severity-all", "--all-track-errors", "--format", "json", "-o", out, path], stdout=lg, stderr=subprocess.STDOUT)
    if not os.path.exists(out):
        return None, None, rc
    rep = json.load(open(out))
    return len(rep.get("violations", [])), len(rep.get("unconnected_items", [])), rc


def court_bbox(fp):
    best = None
    for g in fp.GraphicalItems():
        if g.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            bb = g.GetBoundingBox()
            best = bb if best is None else (best.Merge(bb) or best)
    return best


def check_board(path, tag, want_parts):
    if not os.path.exists(path):
        fail("%s: file %s missing" % (tag, path))
        return set()
    b = pcbnew.LoadBoard(path)
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    # 1 and 2: pad nets and pins
    bad = 0
    n_pads = 0
    for ref, fp in fps.items():
        base = ref
        if ref in VIRTUAL:
            continue
        pn = set()
        for p in fp.Pads():
            num = p.GetNumber()
            if num == "":
                continue
            n_pads += 1
            pn.add(num)
            want = expected(ref, num)
            if want is None:
                fail("%s: pad %s.%s is not in the netlist" % (tag, ref, num)); bad += 1
                continue
            got = p.GetNetname()
            if got != want:
                fail("%s: pad %s.%s net %r, netlist says %r" % (tag, ref, num, got, want)); bad += 1
        miss = pins_of.get(ref, set()) - pn
        if miss:
            fail("%s: %s has no pad for netlist pins %s" % (tag, ref, sorted(miss))); bad += 1
    if not bad:
        ok("%s: %d pads, every pad net equals the netlist, every netlist pin of the placed parts has a pad" % (tag, n_pads))
    # 3: courtyards
    boxes = {}
    for ref, fp in fps.items():
        if ref in VIRTUAL:
            continue
        bb = court_bbox(fp)
        if bb is not None:
            boxes[ref] = bb
    ov = []
    rl = sorted(boxes)
    for i, a in enumerate(rl):
        for c in rl[i + 1:]:
            A, B = boxes[a], boxes[c]
            w = min(A.GetRight(), B.GetRight()) - max(A.GetLeft(), B.GetLeft())
            h = min(A.GetBottom(), B.GetBottom()) - max(A.GetTop(), B.GetTop())
            same_side = (fps[a].GetLayer() == fps[c].GetLayer())
            if w > 1000 and h > 1000 and same_side:        # more than 1 um each way
                ov.append((a, c))
    if ov:
        fail("%s: courtyards overlap: %s" % (tag, ov[:10]))
    else:
        ok("%s: no courtyard overlap (%d courtyards)" % (tag, len(boxes)))
    # 4: pads inside outline
    outl = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outl, False)
    edge = b.GetDesignSettings().m_CopperEdgeClearance
    segs = []
    for d in b.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            segs.append((d.GetStart().x, d.GetStart().y, d.GetEnd().x, d.GetEnd().y))

    def dist_to_edge(x, y):
        best = 1e18
        for (ax, ay, bx, by) in segs:
            vx, vy, wx, wy = bx - ax, by - ay, x - ax, y - ay
            l2 = vx * vx + vy * vy
            t = max(0.0, min(1.0, (vx * wx + vy * wy) / l2)) if l2 else 0.0
            dx, dy = x - (ax + t * vx), y - (ay + t * vy)
            best = min(best, (dx * dx + dy * dy) ** 0.5)
        return best
    outside = []
    for ref, fp in fps.items():
        if ref in VIRTUAL:
            continue
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            for (x, y) in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetLeft(), bb.GetBottom()), (bb.GetRight(), bb.GetBottom())):
                if (not outl.Contains(pcbnew.VECTOR2I(x, y))) or dist_to_edge(x, y) < edge - 1000:
                    outside.append((ref, p.GetNumber()))
                    break
    if outside:
        fail("%s: pads outside the board outline (or closer than the copper edge clearance): %s" % (tag, sorted(set(outside))[:12]))
    else:
        ok("%s: every pad inside the outline, edge clearance %.2f mm" % (tag, ToMM(edge)))
    # 5: rules check
    v, u, rc = run_drc(path, tag)
    if v is None:
        fail("%s: kicad-cli drc produced no report (exit %s)" % (tag, rc))
    elif v or u:
        fail("%s: rules check %d violations, %d unconnected items" % (tag, v, u))
    else:
        ok("%s: rules check 0 violations, 0 unconnected items (kicad-cli pcb drc --severity-all --all-track-errors)" % tag)
    # information: USB pair
    lp = ln = 0.0
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T:
            if t.GetNetname() == "USB_D+":
                lp += ToMM(t.GetLength())
            elif t.GetNetname() == "USB_D-":
                ln += ToMM(t.GetLength())
    if lp or ln:
        print("info %s: USB_D+ %.3f mm, USB_D- %.3f mm, difference %.3f mm" % (tag, lp, ln, abs(lp - ln)))
    return set(r for r in fps if r not in VIRTUAL) | (set(r for r in fps if r in VIRTUAL) & want_parts)


on_main = check_board(MAIN, "PCB1", set(parts))
on_pins = check_board(PINS, "PCB2", set(parts))
# every part of the netlist on one of the two boards, once
allp = set(parts)
placed = on_main | on_pins
dup = (on_main & on_pins)
missing = sorted(allp - placed)
extra = sorted(placed - allp)
if missing:
    fail("parts of the netlist on neither board: %s" % missing)
if extra:
    fail("parts on a board that are not in the netlist: %s" % extra)
if dup:
    fail("parts on both boards: %s" % sorted(dup))
if not (missing or extra or dup):
    ok("all %d parts of parts.csv are on exactly one board (%d on PCB1 incl. the cell, %d on PCB2 incl. the five wire ends)" % (len(allp), len(on_main), len(on_pins)))
# 6: silkscreen marks (review 2026-11-13, minor m2): the two outer pieces of PCB2 cannot be swapped unseen, and the five wire holes of PCB1 are named
def check_marks(main_path, pins_path):
    MIN_H, MIN_T = 1.0, 0.15          # the board maker's smallest legible text: height 1.0 mm, stroke 0.15 mm (evidence/capab_jlc.html.txt, 'Legend' rows)
    bad = 0
    def texts(b, layer):
        return [(d.GetText(), ToMM(d.GetPosition().x), ToMM(d.GetPosition().y), ToMM(d.GetTextHeight()), ToMM(d.GetTextThickness()))
                for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == layer]
    b2 = pcbnew.LoadBoard(pins_path)
    outl = pcbnew.SHAPE_POLY_SET(); b2.GetBoardPolygonOutlines(outl, False)
    boxes = []
    for i in range(outl.OutlineCount()):
        bb = outl.Outline(i).BBox(); boxes.append((ToMM(bb.GetLeft()), ToMM(bb.GetRight())))
    def piece(x):
        for i, (l, r) in enumerate(boxes):
            if l <= x <= r:
                return i
        return None
    fps = {f.GetReference(): f for f in b2.GetFootprints()}
    for layer, lname in ((pcbnew.F_SilkS, "F.SilkS"), (pcbnew.B_SilkS, "B.SilkS")):
        tx = texts(b2, layer)
        for ref in ("P1", "P2", "P3", "P4"):
            if lname == "F.SilkS" and ref in ("P2", "P3"):
                continue                      # no room for a 1.0 mm text on the front of the inner piece (board-notes.md, Round 3 marks); its marks are on the back
            pc = piece(ToMM(fps[ref].GetPosition().x))
            mine = [t for t in tx if t[0].split(" ")[0] == ref and piece(t[1]) == pc]
            if not mine:
                fail("PCB2: no %s mark with the text %r in the piece that carries pin %s" % (lname, ref, ref)); bad += 1
        for t in tx:
            ref = t[0].split(" ")[0]
            if ref in fps and piece(t[1]) != piece(ToMM(fps[ref].GetPosition().x)):
                fail("PCB2: %s text %r stands on another piece than pin %s" % (lname, t[0], ref)); bad += 1
            if t[3] < MIN_H - 1e-6 or t[4] < MIN_T - 1e-6:
                fail("PCB2: %s text %r is %.2f mm high, stroke %.2f mm: below the maker's smallest legible text (%.1f / %.2f)" % (lname, t[0], t[3], t[4], MIN_H, MIN_T)); bad += 1
    b1 = pcbnew.LoadBoard(main_path)
    tx = texts(b1, pcbnew.B_SilkS)
    f1 = {f.GetReference(): f for f in b1.GetFootprints()}
    for w in ("W1", "W2", "W3", "W4", "W7"):
        px, py = ToMM(f1[w].GetPosition().x), ToMM(f1[w].GetPosition().y)
        mine = [t for t in tx if t[0].split(" ")[0] == w and abs(t[2] - py) < 0.5 and 0 < t[1] - px < 5.0]
        if not mine:
            fail("PCB1: no B.SilkS mark %s on the row of hole %s (right of it)" % (w, w)); bad += 1
    # wiring review 2, F5: the case cell's two lead holes and the thermistor holes are named, so the cell leads cannot be swapped unseen
    for w, want in (("W5", "W5 +"), ("W6", "W6 -"), ("TH1", "TH1")):
        if w not in f1:
            fail("PCB1: no footprint %s" % w); bad += 1; continue
        px, py = ToMM(f1[w].GetPosition().x), ToMM(f1[w].GetPosition().y)
        mine = [t for t in tx if t[0] == want and ((t[1] - px) ** 2 + (t[2] - py) ** 2) ** 0.5 < 3.0]
        if not mine:
            fail("PCB1: no B.SilkS mark %r within 3.0 mm of %s" % (want, w)); bad += 1
    for t in tx:
        if t[3] < MIN_H - 1e-6 or t[4] < MIN_T - 1e-6:
            fail("PCB1: B.SilkS text %r below the maker's smallest legible text" % t[0]); bad += 1
    if not bad:
        ok("marks: P1 and P4 marked on their own wing (front and back), P2 and P3 on the inner piece (back), W1 W2 W3 W4 W7, 'W5 +', 'W6 -' and TH1 on the main board (bottom face); every text at least %.1f mm high, %.2f mm stroke" % (MIN_H, MIN_T))


check_marks(MAIN, PINS)
print("RESULT", "FAIL %d" % len(FAIL) if FAIL else "PASS", "check_boards", os.path.basename(MAIN), os.path.basename(PINS))
sys.exit(1 if FAIL else 0)
