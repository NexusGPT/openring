#!/usr/bin/env python3
"""Placement of the parts of PCB1 (main board) by simulated annealing, seeded, reproducible.
Run with KiCad's Python: design/ecad/ring/pcb/run_kipy.sh design/ecad/case/pcb/place_pcb1.py [seed] [iterations]
Writes placement_pcb1.json: ref -> [u, d, rot, side] in the board frame (u right = case x - pcb1_x0, d down = - case y, KiCad rotation degrees).
Fixed parts: U1, J1, LED1 (positions from the case model, see geom.py). Everything else moves.
Cost = weighted half-perimeter wire length of every net but GND + penalties for courtyard overlap, parts outside the outline, parts in the antenna
keep-out, wire pads far from the floor slot.  A run is accepted only when the penalties are 0 (printed at the end)."""
import csv, json, math, os, random, sys
import pcbnew
from pcbnew import ToMM
import geom

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)
LIB = os.path.join(HERE, "OpenRingCase.pretty")

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
ITER = int(sys.argv[2]) if len(sys.argv) > 2 else 300000
random.seed(seed)

parts = {r["reference"]: r for r in csv.DictReader(open(os.path.join(CASE, "parts.csv")))}
nets = {}
pinnet = {}
for r in csv.DictReader(open(os.path.join(CASE, "netlist.csv"))):
    if r["net"]:
        nets.setdefault(r["net"], []).append((r["reference"], r["pin_number"]))
        pinnet[(r["reference"], r["pin_number"])] = r["net"]

PCB2_PARTS = {"P1", "P2", "P3", "P4", "E1"}
VIRTUAL = {"BT1"}
FIXED = {"U1", "J1", "LED1", "W1", "W2", "W3", "W4", "W7"}
bottom_refs = {r for r in parts if r.startswith("TP")}
refs = [r for r in parts if r not in PCB2_PARTS and r not in VIRTUAL]

_fpcache = {}


def fpdata(name):
    if name in _fpcache:
        return _fpcache[name]
    fp = pcbnew.FootprintLoad(LIB, name)
    pads = []
    for p in fp.Pads():
        pos = p.GetPosition(); sz = p.GetSize()
        pads.append((p.GetNumber(), ToMM(pos.x), ToMM(pos.y), ToMM(sz.x), ToMM(sz.y)))
    court = None
    for g in fp.GraphicalItems():
        if g.GetLayer() == pcbnew.F_CrtYd:
            bb = g.GetBoundingBox()
            court = (ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom()))
    _fpcache[name] = (pads, court)
    return _fpcache[name]


def rot(x, y, deg):
    t = math.radians(deg)
    return (x * math.cos(t) + y * math.sin(t), -x * math.sin(t) + y * math.cos(t))


def rect_rot(r, deg):
    pts = [rot(x, y, deg) for x in (r[0], r[2]) for y in (r[1], r[3])]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


class Item:
    pass


items = {}
for ref in refs:
    name = parts[ref]["footprint"].split(":")[1]
    pads, court = fpdata(name)
    it = Item()
    it.ref = ref
    it.pads = pads
    it.court = court
    it.fixed = ref in FIXED
    it.side = "B" if ref in bottom_refs else "F"
    it.u, it.d, it.rot = 0.0, 0.0, 0
    items[ref] = it

# fixed parts (geom.py: values from the case model)
items["U1"].u, items["U1"].d, items["U1"].rot = geom.U1_U, geom.U1_D, 180
items["J1"].u, items["J1"].d, items["J1"].rot = geom.J1_U, geom.J1_D, 270
items["LED1"].u, items["LED1"].d, items["LED1"].rot = geom.LED_U, geom.LED_D, 0
# wire pads of W1 W2 W7 W3 W4: one column down the middle of the floor slot (case.py line 827), 1.6 mm apart, in the order of the pins along Y
_us = (geom.SLOT[0] + geom.SLOT[2]) / 2
for _w, _d in (("W1", -3.2), ("W2", -1.6), ("W7", 0.0), ("W3", 1.6), ("W4", 3.2)):
    items[_w].u, items[_w].d, items[_w].rot = round(_us * 20) / 20, _d, 0


def world_court(it, margin=0.0, u=None, d=None, r=None):
    u = it.u if u is None else u
    d = it.d if d is None else d
    r = it.rot if r is None else r
    c = it.court
    if it.side == "B":
        c = (-c[2], c[1], -c[0], c[3])
    rr = rect_rot(c, r)
    return (u + rr[0] - margin, d + rr[1] - margin, u + rr[2] + margin, d + rr[3] + margin)


def world_pad(it, num_idx, u=None, d=None, r=None):
    u = it.u if u is None else u
    d = it.d if d is None else d
    r = it.rot if r is None else r
    n, x, y, w, h = it.pads[num_idx]
    if it.side == "B":
        x = -x
    px, py = rot(x, y, r)
    return u + px, d + py


# nets used for the wire length: everything except GND; weights
WEIGHT = {"VBUS_IN": 3.0, "SYS": 3.0, "BAT": 3.0, "SW": 4.0, "PMID": 3.0, "VRING": 2.0, "3V3": 0.4, "REGN": 2.0, "BTST": 3.0, "U3_L1": 4.0, "U3_L2": 4.0,
          "FB": 3.0, "TS": 2.0, "USB_D+": 2.0, "USB_D-": 2.0, "U5_ILIM": 2.0, "ILIM": 2.0}
net_pads = {}
for n, lst in nets.items():
    if n == "GND":
        continue
    lstok = []
    for (ref, pin) in lst:
        if ref in items:
            it = items[ref]
            for i, p in enumerate(it.pads):
                if p[0] == pin:
                    lstok.append((ref, i))
    if len(lstok) >= 2:
        net_pads[n] = lstok

# GND pins: a part with a GND pin wants to sit near the board's GND vias: ignore (plane everywhere).

BX0, BX1 = 0.0, geom.BOARD_W
BY0, BY1 = geom.BOARD_D0, geom.BOARD_D1        # d range (down)
EDGE = 0.05                                           # courtyard to board edge
PAD_EDGE = 0.25                                       # pad copper to board edge (copper edge clearance 0.2 + 0.05)
EXTRA = float(os.environ.get("PLACE_EXTRA", "0.0"))   # extra gap kept between courtyards for routing channels (mm)
ANT = geom.ANT_KEEPOUT                                # (u0, d0, u1, d1) no parts on top
SLOT = geom.SLOT                                      # (u0, d0, u1, d1) floor slot: wire pads close to it


def overlap_area(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def pad_outside_pen(ref):
    it = items[ref]
    pen = 0.0
    for i in range(len(it.pads)):
        n, x, y, w, h = it.pads[i]
        px, py = world_pad(it, i)
        # axis-aligned half sizes after rotation
        hw, hh = (w / 2, h / 2) if it.rot % 180 == 0 else (h / 2, w / 2)
        pen += max(0, BX0 + PAD_EDGE - (px - hw)) + max(0, (px + hw) - (BX1 - PAD_EDGE)) + max(0, BY0 + PAD_EDGE - (py - hh)) + max(0, (py + hh) - (BY1 - PAD_EDGE))
    return pen


def outside_pen(c):
    p = 0.0
    p += max(0, BX0 + EDGE - c[0]) + max(0, c[2] - (BX1 - EDGE)) + max(0, BY0 + EDGE - c[1]) + max(0, c[3] - (BY1 - EDGE))
    return p


ITEM_NETS = {}
for n, lst in net_pads.items():
    for ref, i in lst:
        ITEM_NETS.setdefault(ref, set()).add(n)
_courts = {}


# extra margin around the courtyard of the fine pitch parts, so that their pads can be fanned out (router diagnosis: pins boxed in by parts 0.4 mm away)
_M = float(os.environ.get("PLACE_IC", "1.0"))
IC_MARGIN = {"U2": 0.7 * _M, "U3": 0.4 * _M, "U5": 0.4 * _M, "U6": 0.4 * _M, "U4": 0.4 * _M, "L1": 0.1, "L2": 0.1}


for _kv in os.environ.get("PLACE_MARG", "").split(","):
    if ":" in _kv:
        _k, _v = _kv.split(":")
        IC_MARGIN[_k] = float(_v)


def court_of(ref):
    it = items[ref]
    return world_court(it, (IC_MARGIN.get(ref, 0.0) + EXTRA / 2) if not it.fixed else 0.0)


def net_hpwl(n):
    xs, ys = [], []
    for ref, i in net_pads[n]:
        x, y = world_pad(items[ref], i)
        xs.append(x); ys.append(y)
    return WEIGHT.get(n, 1.0) * ((max(xs) - min(xs)) + (max(ys) - min(ys)))


OUTW = float(os.environ.get("PLACE_OUTW", "200"))
OVP = float(os.environ.get("PLACE_OVP", "400"))       # overlap penalty per mm2 (refine runs use 6000)
START = os.environ.get("PLACE_START", "")              # json of a previous run to refine
T_START = float(os.environ.get("PLACE_T0", "3.0"))


def pair_pen(ra, rb):
    a, b = items[ra], items[rb]
    pen = 0.0
    if a.side == b.side:
        pen += OVP * overlap_area(_courts[ra], _courts[rb])
    elif a.side == "F" and (rb.startswith("TP")) and (ra.startswith("W") or ra == "TH1"):
        pen += OVP * overlap_area(_courts[ra], _courts[rb])
    elif b.side == "F" and (ra.startswith("TP")) and (rb.startswith("W") or rb == "TH1"):
        pen += OVP * overlap_area(_courts[ra], _courts[rb])
    return pen


def single_pen(r):
    it = items[r]
    c = _courts[r]
    pen = 0.0
    if r != "J1":
        pen += OUTW * (outside_pen(c) + pad_outside_pen(r))
    if it.side == "F" and r != "U1":
        pen += 400.0 * overlap_area(c, ANT)
    if r in ("W1", "W2", "W3", "W4", "W7"):
        pen += 4.0 * geom.dist_to_rect(it.u, it.d, SLOT)
    return pen


def local_cost(refs_):
    """cost terms that involve any of refs_ (pairs counted once per ref in refs_)"""
    for r in refs_:
        _courts[r] = court_of(r)
    cost = 0.0
    nets_ = set()
    for r in refs_:
        nets_ |= ITEM_NETS.get(r, set())
        cost += single_pen(r)
    for n in nets_:
        cost += net_hpwl(n)
    for r in refs_:
        for o in items:
            if o != r:
                if o in refs_ and o < r:
                    continue
                cost += pair_pen(r, o)
    return cost


def total_cost(detail=False):
    for r in items:
        _courts[r] = court_of(r)
    wl = sum(net_hpwl(n) for n in net_pads)
    ov = out = keep = far = 0.0
    rl = list(items)
    for i, ra in enumerate(rl):
        far += 4.0 * geom.dist_to_rect(items[ra].u, items[ra].d, SLOT) if ra in ("W1", "W2", "W3", "W4", "W7") else 0.0
        out += (outside_pen(_courts[ra]) + pad_outside_pen(ra)) if ra != "J1" else 0.0
        if items[ra].side == "F" and ra != "U1":
            keep += overlap_area(_courts[ra], ANT)
        for rb in rl[i + 1:]:
            ov += pair_pen(ra, rb) / OVP
    if detail:
        return wl, ov, out, keep, far
    return wl + OVP * ov + OUTW * out + 400.0 * keep + far


HINTS = {"U4": (10.8, -12.0, 90), "U2": (19.3, -13.0, 0), "L1": (19.8, -8.3, 0), "U3": (18.5, 4.5, 0), "L2": (19.8, 9.0, 0), "U5": (18.5, -2.0, 0),
         "U6": (18.5, 1.0, 0), "C2": (21.5, -15.5, 0), "C3": (21.5, -9.5, 0)}


def initial():
    free_f = [r for r in items if not items[r].fixed and items[r].side == "F"]
    free_b = [r for r in items if not items[r].fixed and items[r].side == "B"]
    for r in free_f:
        it = items[r]
        while True:
            it.u = random.uniform(5.0, 22.0)
            it.d = random.uniform(BY0 + 1.0, BY1 - 1.0)
            it.rot = random.choice((0, 90, 180, 270))
            c = world_court(it)
            if overlap_area(c, ANT) == 0 and overlap_area(c, geom.U1_BODY) == 0:
                break
    for r, (hu, hd, hr) in HINTS.items():
        if r in items:
            items[r].u, items[r].d, items[r].rot = hu, hd, hr
    for k, r in enumerate(free_b):
        it = items[r]
        it.u = 3.0 + 2.0 * (k % 8)
        it.d = -4.0 + 2.0 * (k // 8)
        it.rot = 0


def anneal():
    movers = [r for r in items if not items[r].fixed]
    cur = total_cost()
    best = cur
    best_state = {r: (items[r].u, items[r].d, items[r].rot) for r in items}
    T0, T1 = T_START, 0.02
    for k in range(ITER):
        T = T0 * (T1 / T0) ** (k / ITER)
        r = random.choice(movers)
        it = items[r]
        m = random.random()
        scale = max(0.1, (5.0 if not START else 0.6) * (1 - k / ITER))
        if m < 0.12:
            r2 = random.choice(movers)
            o2 = items[r2]
            if o2.side != it.side or r2 == r:
                continue
            before = local_cost([r, r2])
            (it.u, it.d, it.rot), (o2.u, o2.d, o2.rot) = (o2.u, o2.d, o2.rot), (it.u, it.d, it.rot)
            after = local_cost([r, r2])
            if after <= before or random.random() < math.exp((before - after) / T):
                cur += after - before
            else:
                (it.u, it.d, it.rot), (o2.u, o2.d, o2.rot) = (o2.u, o2.d, o2.rot), (it.u, it.d, it.rot)
                local_cost([r, r2])
        else:
            old = (it.u, it.d, it.rot)
            before = local_cost([r])
            if m < 0.7:
                it.u += random.gauss(0, scale)
                it.d += random.gauss(0, scale)
            elif m < 0.88 and it.side == "F":
                it.rot = (it.rot + random.choice((90, 180, 270))) % 360
            else:
                it.u = random.uniform(1.0, 22.0)
                it.d = random.uniform(BY0 + 1.0, BY1 - 1.0)
            it.u = round(it.u * 20) / 20
            it.d = round(it.d * 20) / 20
            after = local_cost([r])
            if after <= before or random.random() < math.exp((before - after) / T):
                cur += after - before
            else:
                it.u, it.d, it.rot = old
                local_cost([r])
        if cur < best - 1e-9:
            best = cur
            best_state = {x: (items[x].u, items[x].d, items[x].rot) for x in items}
        if k % 50000 == 0:
            print("iter", k, "T %.3f" % T, "cost %.1f best %.1f" % (cur, best), flush=True)
    for x, (u, d, rr) in best_state.items():
        items[x].u, items[x].d, items[x].rot = u, d, rr
    total_cost()


if __name__ == "__main__":
    if START:
        _d = json.load(open(START))
        for _r, (_u, _dd, _rot, _sd) in _d.items():
            if _r in items:
                items[_r].u, items[_r].d, items[_r].rot = _u, _dd, _rot
        for _r in ("U1", "J1", "LED1"):
            pass
    else:
        initial()
    anneal()
    # snap to 0.05 mm
    for it in items.values():
        if not it.fixed:
            it.u = round(it.u * 20) / 20
            it.d = round(it.d * 20) / 20
    total_cost()
    wl, ov, out, keep, far = total_cost(True)
    print("seed", seed, "wire length %.1f overlap %.4f outside %.3f antenna %.4f far %.2f" % (wl, ov, out, keep, far))
    outp = os.path.join(HERE, "work", "placement_pcb1_s%d%s%s.json" % (seed, "r" if START else "", os.environ.get("PLACE_TAG", "")))
    json.dump({r: [round(it.u, 3), round(it.d, 3), it.rot, it.side] for r, it in items.items()}, open(outp, "w"), indent=0, sort_keys=True)
    print("wrote", outp)
