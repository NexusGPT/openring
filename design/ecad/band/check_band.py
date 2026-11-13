#!/usr/bin/env python3
"""Checks the band flexible circuit boards.  Run with KiCad's own Python:  ../ring/pcb/run_kipy.sh check_band.py [--dir D] [--files a.kicad_pcb,b.kicad_pcb]
Exit 0 only when, for every board:
  b. the board has an outline, a stiffener outline (User.1), fold lines (Dwgs.User), copper on both layers, vias;
     the flat outline length equals the model path of that ring size (+ the fold and foot of this design) within 0.05 mm, by two measures:
     the formulas of design/mech/thin/thin.py (band_geom.py) and the STEP files of design/mfg/parts/flex-tail-* (model_lengths.csv from measure_step.py);
  c. the copper joins exactly the lands that design/ecad/ring/netlist.csv joins (contact of the real copper shapes, not the net labels),
     and `kicad-cli pcb drc --severity-all --all-track-errors` reports 0 violations and 0 unconnected items.
Exit 1 on any failure."""
import csv, math, os, re, subprocess, sys
import pcbnew
from pcbnew import ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import band_geom as G
import band_layout as L

KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
NETLIST = os.path.join(os.path.dirname(HERE), "ring", "netlist.csv")
OX, OY = 50.0, 80.0
TOL_LEN = 0.05
EPS = 1e-6

args = sys.argv[1:]
DIR = HERE
FILES = None
while args:
    a = args.pop(0)
    if a == "--dir":
        DIR = args.pop(0)
    elif a == "--files":
        FILES = args.pop(0).split(",")
if FILES is None:
    FILES = [f"flex{k}-us{us}.kicad_pcb" for k in (1, 2) for us in G.SIZES]

# ---------------------------------------------------------------- netlist
nets = {}      # net -> set of (ref, pin)
with open(NETLIST, newline="") as f:
    for r in csv.DictReader(f):
        if r["net"]:
            nets.setdefault(r["net"], set()).add((r["reference"], r["pin_number"]))
TAIL_REFS = {1: {"J_BAND_A", "SW1", "SW2", "SW3", "SW4", "SW5", "M1"}, 2: {"J_BAND_B", "BT1", "RT1", "CP1", "CP2", "CP3", "CP4"}}


def terminals(ref, num):
    """pad number on the tail -> netlist (ref, pin) terminals"""
    if ref in ("J_BAND_A", "J_BAND_B"):
        return {(ref, num)}
    if ref == "PRT1":
        return {(r, p) for (r, p), n in L.PRT1_MAP.items() if n == num}
    if ref.startswith("CP"):
        return {(ref, "1")}
    return {(ref, num)}


# ---------------------------------------------------------------- geometry
def d_pt_seg(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def seg_cross(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)


def d_seg_seg(a, b, c, d):
    if seg_cross(a, b, c, d):
        return 0.0
    return min(d_pt_seg(a, c, d), d_pt_seg(b, c, d), d_pt_seg(c, a, b), d_pt_seg(d, a, b))


def pt_in_rect(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def d_pt_rect(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2]); dy = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dy)


def d_seg_rect(a, b, r):
    if pt_in_rect(a, r) or pt_in_rect(b, r):
        return 0.0
    c = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    return min(d_seg_seg(a, b, c[i], c[(i + 1) % 4]) for i in range(4))


def gap(s1, s2):
    """clearance between two shapes (0 or less = touching)"""
    k1, k2 = s1[0], s2[0]
    if k1 > k2:
        s1, s2, k1, k2 = s2, s1, k2, k1
    # order: circ < rect < seg
    if k1 == "circ" and k2 == "circ":
        return math.hypot(s1[1] - s2[1], s1[2] - s2[2]) - s1[3] - s2[3]
    if k1 == "circ" and k2 == "rect":
        return d_pt_rect((s1[1], s1[2]), s2[1:]) - s1[3]
    if k1 == "circ" and k2 == "seg":
        return d_pt_seg((s1[1], s1[2]), s2[1], s2[2]) - s1[3] - s2[3] / 2
    if k1 == "rect" and k2 == "rect":
        dx = max(s1[1] - s2[3], s2[1] - s1[3], 0); dy = max(s1[2] - s2[4], s2[2] - s1[4], 0)
        return math.hypot(dx, dy)
    if k1 == "rect" and k2 == "seg":
        return d_seg_rect(s2[1], s2[2], s1[1:]) - s2[3] / 2
    if k1 == "seg" and k2 == "seg":
        return d_seg_seg(s1[1], s1[2], s2[1], s2[2]) - s1[3] / 2 - s2[3] / 2
    raise ValueError((k1, k2))


# ---------------------------------------------------------------- one board
def check_board(fname):
    res = []
    path = os.path.join(DIR, fname)
    kind = int(re.search(r"flex(\d)", fname).group(1))
    us = int(re.search(r"us(\d+)", fname).group(1))
    S = G.Size(us)
    ok = True

    def fail(msg):
        nonlocal ok
        ok = False
        res.append("  FAIL " + msg)

    if not os.path.exists(path):
        return False, [f"  FAIL {fname}: file missing"]
    b = pcbnew.LoadBoard(path)
    # ---- outline
    xs, ys = [], []
    n_edge = 0
    for d in b.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            n_edge += 1
            for p in (d.GetStart(), d.GetEnd()):
                xs.append(ToMM(p.x) - OX); ys.append(ToMM(p.y) - OY)
    if n_edge < 8:
        fail(f"outline has only {n_edge} segments")
    length = max(xs) - min(xs) if xs else 0.0
    model = S.path1 if kind == 1 else S.path2
    want_formula = model + G.FOOT_EXTRA
    step_rows = [r for r in csv.DictReader(open(os.path.join(HERE, "model_lengths.csv"))) if r["tail"] == f"FLEX{kind}" and int(r["us"]) == us]
    want_step = float(step_rows[0]["path_total"])      # model v8 files: fold and foot already inside
    res.append(f"  outline length {length:.4f}  formula {want_formula:.4f} (diff {length - want_formula:+.4f})  STEP {want_step:.4f} (diff {length - want_step:+.4f})  [limit {TOL_LEN}]")
    if abs(length - want_formula) > TOL_LEN:
        fail("outline length differs from the model path formula")
    if abs(length - want_step) > TOL_LEN:
        fail("outline length differs from the STEP path")
    # ---- drawings
    n_fold = sum(1 for d in b.GetDrawings() if d.GetLayer() == pcbnew.Dwgs_User and hasattr(d, "GetShape") and d.GetShape() == pcbnew.SHAPE_T_SEGMENT)
    n_stiff = sum(1 for d in b.GetDrawings() if d.GetLayer() == pcbnew.User_1 and hasattr(d, "GetShape") and d.GetShape() == pcbnew.SHAPE_T_SEGMENT)
    if n_fold < 4:
        fail(f"fold lines on Dwgs.User: {n_fold} segments (need 4 or more)")
    need_st = 8 if kind == 1 else 4
    if n_stiff < need_st:
        fail(f"stiffener outlines on User.1: {n_stiff} segments (need {need_st} or more)")
    # ---- copper shapes
    prims = []   # (shape, layers set, owner) owner = (ref, padnum) or None
    n_via = 0
    layers_used = set()
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            n_via += 1
            c = t.GetPosition()
            prims.append((("circ", ToMM(c.x), ToMM(c.y), ToMM(t.GetWidth(pcbnew.F_Cu)) / 2), {"F", "B"}, None))
        else:
            a, e = t.GetStart(), t.GetEnd()
            ly = "F" if t.GetLayer() == pcbnew.F_Cu else "B"
            layers_used.add(ly)
            prims.append((("seg", (ToMM(a.x), ToMM(a.y)), (ToMM(e.x), ToMM(e.y)), ToMM(t.GetWidth())), {ly}, None))
    refs = {}
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        refs[ref] = fp
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            ly = {"F"} if p.IsOnLayer(pcbnew.F_Cu) else {"B"}
            if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
                c = p.GetPosition()
                shp = ("circ", ToMM(c.x), ToMM(c.y), ToMM(p.GetSize().x) / 2)
            else:
                shp = ("rect", ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom()))
            prims.append((shp, ly, (ref, p.GetNumber())))
    if n_via < 4:
        fail(f"only {n_via} vias")
    if not ({"F", "B"} <= layers_used):
        fail(f"copper lines on layers {sorted(layers_used)} (need both)")
    present = set()
    for ref_, fp_ in refs.items():
        for p_ in fp_.Pads():
            present |= terminals(ref_, p_.GetNumber())
    # ---- connectivity from the copper shapes
    n = len(prims)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if not (prims[i][1] & prims[j][1]):
                continue
            if gap(prims[i][0], prims[j][0]) <= EPS:
                parent[find(i)] = find(j)
    comps = {}
    for i in range(n):
        if prims[i][2] is not None:
            comps.setdefault(find(i), set()).update(terminals(*prims[i][2]))
    got = sorted(sorted(c) for c in comps.values())
    exp = []
    for net, pins in nets.items():
        t = {(r, p) for (r, p) in pins if r in TAIL_REFS[kind] and (r, p) in present}
        if t:
            exp.append(sorted(t))
    exp = sorted(exp)
    # every tail ref must be present on the board
    for r in TAIL_REFS[kind] - {"BT1", "RT1"} if kind == 2 else TAIL_REFS[kind]:
        if r not in refs and not (kind == 2 and r == "J_BAND_B" and False):
            fail(f"part {r} missing on the board")
    if kind == 2 and "PRT1" not in refs:
        fail("part PRT1 missing")
    if got != exp:
        for g in got:
            if g not in exp:
                fail(f"copper joins {g} which is not a netlist net")
        for e in exp:
            if e not in got:
                fail(f"netlist net {e} is not joined exactly by the copper")
    res.append(f"  copper components with a land {len(got)}, netlist nets on this tail {len(exp)}, vias {n_via}, shapes {n}")
    # ---- mating: lay the tail foot on the main board lands (F.Cu face of the tail touches the board)
    side = 1 if kind == 2 else -1
    jref = "J_BAND_B" if kind == 2 else "J_BAND_A"
    lib = pcbnew.FootprintLoad(os.path.join(HERE, "OpenRingBand.pretty"), jref + "_BOARD")
    board_land = {}
    for p in lib.Pads():
        board_land[p.GetNumber()] = (-2.25 + ToMM(p.GetPosition().x), side * 4.325 + ToMM(p.GetPosition().y))
    n_mate = 0
    worst = 0.0
    for p in refs[jref].Pads():
        num = p.GetNumber()
        u = ToMM(p.GetPosition().x) - OX
        v = side * (ToMM(p.GetPosition().y) - OY)
        X, Y = v - 2.5, side * (3.4 + u)           # tail (u, v) -> ring model (X, Y): F.Cu face up against the board, no mirror
        bx, by = board_land[num]
        d = math.hypot(X - bx, Y - by)
        worst = max(worst, d)
        net_want = [n for n, pins in nets.items() if (jref, num) in pins]
        if d > 0.05 or p.GetNetname() not in net_want:
            fail(f"mating: land {num} {p.GetNetname()} tail at ({X:.3f},{Y:.3f}) board land at ({bx:.3f},{by:.3f}) off by {d:.3f}, board net {net_want}")
        n_mate += 1
    res.append(f"  mating: {n_mate} lands on the main board lands of the same net, worst offset {worst:.4f} mm [limit 0.05]")
    # ---- DRC
    rpt = os.path.join(DIR, fname.replace(".kicad_pcb", "-drc.rpt"))
    r = subprocess.run([KICAD_CLI, "pcb", "drc", "--severity-all", "--all-track-errors", "-o", rpt, path], capture_output=True, text=True)
    txt = open(rpt).read() if os.path.exists(rpt) else ""
    m1 = re.search(r"Found (\d+) DRC violations", txt)
    m2 = re.search(r"Found (\d+) unconnected", txt)
    v = int(m1.group(1)) if m1 else -1
    u = int(m2.group(1)) if m2 else -1
    res.append(f"  kicad-cli drc: violations {v}, unconnected {u}")
    if v != 0 or u != 0:
        fail(f"DRC violations {v}, unconnected {u}")
    return ok, res


all_ok = True
count = 0
for fn in FILES:
    ok, lines = check_board(fn)
    count += 1
    print(f"{'PASS' if ok else 'FAIL'} {fn}")
    for ln in lines:
        print(ln)
    all_ok = all_ok and ok
print(f"RESULT: {'PASS' if all_ok else 'FAIL'} boards checked {count}")
sys.exit(0 if all_ok else 1)
