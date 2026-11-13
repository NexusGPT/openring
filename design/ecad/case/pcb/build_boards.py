#!/usr/bin/env python3
"""Builds the two case boards from the netlist, the footprint library and the case model.

Run with KiCad's own Python:   design/ecad/ring/pcb/run_kipy.sh design/ecad/case/pcb/build_boards.py <stage> [args]
Stages
  unrouted   write work/case_main_unrouted.kicad_pcb and work/case_pins_unrouted.kicad_pcb (outline, parts at the placement, nets, rules, zones)
  dsn        write work/case_main.dsn (the router input) for PCB1
  finish     read work/case_main.ses (router result), tune the USB pair, pour zones, save pcb/case_main.kicad_pcb;
             also route and save pcb/case_pins.kicad_pcb (PCB2 is routed here by rule, 5 short tracks)
  all        unrouted + dsn (the router step itself is route_main.sh) + finish
Frames, the line or key of every model number: geom.py.  Rules: board-notes.md section 'Board technology'."""
import csv, json, math, os, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
import geom

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)
LIB = os.path.join(HERE, "OpenRingCase.pretty")
WORK = os.path.join(HERE, "work")
os.makedirs(WORK, exist_ok=True)
OX, OY = 100.0, 100.0          # PCB1 origin on the KiCad sheet
OX2, OY2 = 100.0, 100.0        # PCB2 origin

# ---------------------------------------------------------------- rules (board-notes.md): JLCPCB capability page, w5_jlcpcb_capabilities.html
TRACK = 0.15                   # default track width and clearance (page: 0.10 / 0.10 mm for 1 oz, so 0.15 is inside standard)
CLEAR = 0.15
VIA_D, VIA_P = 0.3, 0.6        # via drill / pad (page: min via hole 0.15 mm, annular ring >= 0.15 mm absolute minimum multilayer; ours 0.15)
EDGE_CLEAR = 0.2               # page: copper clearance from routed board edges >= 0.2 mm
HOLE_CLEAR = 0.25
if os.environ.get("CASE_FINE") == "1":      # round 2, main board only: signal track and gap 0.10 mm, via 0.20 / 0.50 mm (capability page, multilayer minimum 0.09 mm, via hole 0.15 mm / 0.25 mm, ring 0.15 mm)
    TRACK, CLEAR, VIA_D, VIA_P, HOLE_CLEAR = 0.10, 0.10, 0.20, 0.50, 0.20
P_WIDE = 0.40                  # power class: VBUS_IN, SYS, BAT, SW, PMID, U3_L1, U3_L2 (design current 1.5 A, IPC-2221 outer 1 oz 10 K rise needs 0.40 mm, see power_width.py)
P_MED = 0.30                   # SYS BAT SW PMID U3_L1 U3_L2 (neck-down limited by the 0.5 mm pitch pins of U2 and U3)
P_3V3 = 0.20                   # 3V3 (U1 peak 355 mA needs 0.072 mm)
WIDE_NETS = ["VBUS_IN"]
MED_NETS = ["SYS", "BAT", "SW", "PMID", "U3_L1", "U3_L2"]
NET_3V3 = ["VRING"]          # 0.20 mm class (3V3 is a plane in round 2)
PCB1_CLASSES = [("pwr_wide", P_WIDE, WIDE_NETS), ("pwr_med", P_MED, MED_NETS), ("pwr_3v3", P_3V3, NET_3V3)]
PCB2_CLASSES = [("pwr", 0.4, ["VRING", "GND"])]


def mm(v):
    return FromMM(v)


def pt1(u, d):
    return VECTOR2I(mm(OX + u), mm(OY + d))


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


parts = {r["reference"]: r for r in rows(os.path.join(CASE, "parts.csv"))}
netrows = rows(os.path.join(CASE, "netlist.csv"))
pinnet = {(r["reference"], r["pin_number"]): r["net"] for r in netrows}
PCB2_REFS = ["P1", "P2", "P3", "P4", "E1"]
# PCB2 ends of the wires (not in the netlist: each wire is one pin part on PCB1; the other end sits on PCB2): ref -> (netlist wire, net)
WIRE_ENDS = {"WP1": "W1", "WP2": "W2", "WP3": "W3", "WP4": "W4", "WP7": "W7"}


def net_of(ref, pin):
    return pinnet.get((ref, pin), "")


def load_fp(name):
    return pcbnew.FootprintLoad(LIB, name)


def get_net(board, cache, name):
    if not name:
        return None
    if name not in cache:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        cache[name] = ni
    return cache[name]


def add_part(board, cache, ref, fpname, value, pos, rot, side="F", netfn=None, text_layer=pcbnew.F_Fab):
    fp = load_fp(fpname)
    fp.SetReference(ref)
    fp.SetValue(value)
    board.Add(fp)
    fp.SetPosition(pos)
    if side == "B":
        fp.Flip(pos, False)
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetLayer(pcbnew.F_Fab if side == "F" else pcbnew.B_Fab)
    fp.Reference().SetTextSize(VECTOR2I(mm(0.5), mm(0.5)))
    fp.Reference().SetTextThickness(mm(0.08))
    fp.Value().SetVisible(False)
    for p in fp.Pads():
        n = netfn(ref, p.GetNumber()) if netfn else ""
        if n:
            p.SetNet(get_net(board, cache, n))
    return fp


def setup_rules(board, layers, thickness):
    board.SetCopperLayerCount(layers)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(thickness))
    ds.m_TrackMinWidth = mm(TRACK)
    ds.m_MinClearance = mm(CLEAR)
    ds.m_ViasMinSize = mm(VIA_P)
    ds.m_ViasMinAnnulus = mm(0.15)
    ds.m_MinThroughDrill = mm(VIA_D)
    ds.m_CopperEdgeClearance = mm(EDGE_CLEAR)
    ds.m_HoleToHoleMin = mm(HOLE_CLEAR)
    ds.m_HoleClearance = mm(CLEAR)
    ds.m_MinSilkClearance = mm(0.15)
    ds.m_SolderMaskMinWidth = mm(0.1)
    ds.m_SolderMaskExpansion = mm(0.05)
    ds.m_SolderMaskToCopperClearance = mm(0.05)
    ds.m_MinResolvedSpokes = 2
    ds.m_MinConn = mm(0.15)
    ds.m_ViasMinAnnulus = mm(0.15)
    ds.m_MinThroughDrill = mm(VIA_D)
    ns = ds.m_NetSettings
    dc = ns.GetDefaultNetclass()
    dc.SetClearance(mm(CLEAR))
    dc.SetTrackWidth(mm(TRACK))
    dc.SetViaDiameter(mm(VIA_P))
    dc.SetViaDrill(mm(VIA_D))
    dc.SetDiffPairWidth(mm(TRACK))
    dc.SetDiffPairGap(mm(0.15))
    return ds


CLASSES = {}   # board id -> list of (name, width, nets)


def add_netclass(board, name, width, nets):
    CLASSES.setdefault(id(board), []).append((name, width, nets))
    ns = board.GetDesignSettings().m_NetSettings
    nc = pcbnew.NETCLASS(name)
    nc.SetClearance(mm(CLEAR))
    nc.SetTrackWidth(mm(width))
    nc.SetViaDiameter(mm(VIA_P))
    nc.SetViaDrill(mm(VIA_D))
    ns.SetNetclass(name, nc)
    for n in nets:
        ns.SetNetclassPatternAssignment(n, name)


def write_pro(classes, path, default_width=TRACK):
    """The rules live in the project file (kicad-cli drc and the DSN export read it), not in the .kicad_pcb"""
    cl = [{"name": "Default", "clearance": CLEAR, "track_width": default_width, "via_diameter": VIA_P, "via_drill": VIA_D,
           "microvia_diameter": 0.2, "microvia_drill": 0.1, "diff_pair_width": TRACK, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.25, "priority": 2147483647}]
    pats = []
    for (name, width, nets) in classes:
        cl.append({"name": name, "clearance": CLEAR, "track_width": width, "via_diameter": VIA_P, "via_drill": VIA_D,
                   "microvia_diameter": 0.2, "microvia_drill": 0.1, "diff_pair_width": TRACK, "diff_pair_gap": 0.15, "diff_pair_via_gap": 0.25, "priority": 0})
        for n in nets:
            pats.append({"netclass": name, "pattern": n})
    pro = {
        "board": {"design_settings": {
            "rules": {"min_clearance": CLEAR, "min_copper_edge_clearance": EDGE_CLEAR, "min_track_width": TRACK, "min_via_diameter": VIA_P,
                      "min_through_hole_diameter": VIA_D, "min_via_annular_width": 0.15, "min_hole_clearance": CLEAR, "min_hole_to_hole": HOLE_CLEAR,
                      "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1, "min_silk_clearance": 0.15, "min_text_height": 0.8, "min_text_thickness": 0.12,
                      "min_connection": 0.1 if os.environ.get("CASE_FINE") != "1" else 0.0, "min_resolved_spokes": 2, "solder_mask_clearance": 0.05, "solder_mask_min_width": 0.1,
                      "solder_mask_to_copper_clearance": 0.05, "min_groove_width": 0.0},
            "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.5, "copper_text_size_v": 1.5,
                         "silk_line_width": 0.12, "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15,
                         "other_line_width": 0.1, "fab_line_width": 0.1, "courtyard_line_width": 0.05},
            "track_widths": [0.0, TRACK, 0.2, 0.3, 0.4], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": VIA_P, "drill": VIA_D}],
        }},
        "net_settings": {"classes": cl, "netclass_patterns": pats, "meta": {"version": 4}},
        "meta": {"filename": os.path.basename(path), "version": 3},
    }
    json.dump(pro, open(path, "w"), indent=2)


def outline(board, polys):
    for poly in polys:
        n = len(poly)
        for i in range(n):
            s = pcbnew.PCB_SHAPE(board)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(mm(0.1))
            s.SetStart(poly[i])
            s.SetEnd(poly[(i + 1) % n])
            board.Add(s)


def text(board, layer, s, pos, size=0.8, rot=0.0, justify=None):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetLayer(layer)
    t.SetPosition(pos)
    t.SetTextSize(VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(max(0.12, size * 0.15)))
    t.SetTextAngleDegrees(rot)
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab, pcbnew.B_Cu):
        t.SetMirrored(True)
    board.Add(t)


def zone(board, layer, polygon, net=None, rule_area=False, clearance=None, minw=0.2, name=""):
    z = pcbnew.ZONE(board)
    if isinstance(layer, (list, tuple)):
        ls = pcbnew.LSET()
        for l in layer:
            ls.AddLayer(l)
        z.SetLayerSet(ls)
    else:
        z.SetLayer(layer)
    if net is not None:
        z.SetNet(net)
    z.SetZoneName(name)
    o = z.Outline()
    o.NewOutline()
    for p in polygon:
        o.Append(p.x, p.y)
    if rule_area:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
    else:
        z.SetMinThickness(mm(minw))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(mm(0.2))
        z.SetThermalReliefSpokeWidth(mm(0.25))
        if clearance:
            z.SetLocalClearance(mm(clearance))
    board.Add(z)
    return z


def track(board, a, b, layer, width, net):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(a)
    t.SetEnd(b)
    t.SetLayer(layer)
    t.SetWidth(mm(width))
    t.SetNet(net)
    board.Add(t)
    return t


def via(board, pos, net, drill=VIA_D, dia=VIA_P):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pos)
    v.SetWidth(mm(dia))
    v.SetDrill(mm(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)
    return v


# ================================================================ PCB1
def pcb1_outline_points():
    h = geom.BOARD_H / 2
    d0, d1 = geom.BOARD_D0, geom.BOARD_D1
    t0 = geom.TAB_U0
    th = geom.TAB_HALF
    d_hi = -geom.J1_YC - 0.0            # tab centre d = -J1_YC
    # polygon (u, d), clockwise on the sheet, tab on the -d side (case +y side) at the left edge
    pts = [(0.0, d0), (geom.BOARD_W, d0), (geom.BOARD_W, d1), (0.0, d1), (0.0, d_hi + th), (t0, d_hi + th), (t0, d_hi - th), (0.0, d_hi - th)]
    return pts


def build_pcb1(placement):
    b = pcbnew.BOARD()
    setup_rules(b, 4, geom.BOARD_T)
    cache = {}
    # nets of PCB1
    names = sorted({r["net"] for r in netrows if r["net"]})
    for n in names:
        get_net(b, cache, n)
    # outline
    outline(b, [[pt1(u, d) for (u, d) in pcb1_outline_points()]])
    # parts
    placed = []
    for ref, (u, d, rot, side) in sorted(placement.items()):
        p = parts[ref]
        fpname = p["footprint"].split(":")[1]
        add_part(b, cache, ref, fpname, p["value"], pt1(u, d), rot, side, net_of)
        placed.append(ref)
    # BT1: virtual cell, drawn under the board (case_params / case.py cell box: x_c0 .. + 23, y +-20)
    cell_u = geom.PCB1_X0 * 0 + (-7.737067021407239 - geom.PCB1_X0)
    add_part(b, cache, "BT1", "CELL_LEADS", parts["BT1"]["value"], pt1(cell_u + 11.5, 0.0), 0, "F", net_of)
    return b, cache


def u1_ground_pattern(b, cache):
    """the nine centre pads of U1 (pin 61, ground) are tied by copper through their centres and four vias: three tracks 0.3 mm wide through the pad rows, one through the middle
    column, rows extended 0.9 mm beyond the block; four vias at the ends of the first and third row"""
    fp = [f for f in b.GetFootprints() if f.GetReference() == "U1"][0]
    pads = [p for p in fp.Pads() if p.GetNumber() == "61"]
    xs = sorted({round(ToMM(p.GetPosition().x), 3) for p in pads})
    ys = sorted({round(ToMM(p.GetPosition().y), 3) for p in pads})
    assert len(xs) == 3 and len(ys) == 3, (xs, ys)
    gnd = cache["GND"]
    ext = 0.9 + 0.6
    F = pcbnew.F_Cu
    for y in ys:
        track(b, VECTOR2I(mm(xs[0] - ext), mm(y)), VECTOR2I(mm(xs[2] + ext), mm(y)), F, 0.3, gnd)
    track(b, VECTOR2I(mm(xs[1]), mm(ys[0])), VECTOR2I(mm(xs[1]), mm(ys[2])), F, 0.3, gnd)
    for y in (ys[0], ys[2]):
        for x in (xs[0] - ext, xs[2] + ext):
            via(b, VECTOR2I(mm(x), mm(y)), gnd)


def antenna_keepout(b):
    u0, d0, u1, d1 = geom.ANT_KEEPOUT
    poly = [pt1(u0, d0), pt1(u1, d0), pt1(u1, d1), pt1(u0, d1)]
    zone(b, [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu], poly, rule_area=True, name="ANTENNA_KEEPOUT")


def board_inset_polygon(inset):
    """PCB1 outline inset by `inset` mm (the tab is included); built by hand for the two rectangles"""
    d0, d1 = geom.BOARD_D0 + inset, geom.BOARD_D1 - inset
    t0 = geom.TAB_U0 + inset
    th = geom.TAB_HALF - inset
    d_hi = -geom.J1_YC
    w = geom.BOARD_W - inset
    pts = [(inset, d0), (w, d0), (w, d1), (inset, d1), (inset, d_hi + th), (t0, d_hi + th), (t0, d_hi - th), (inset, d_hi - th)]
    return [pt1(u, d) for u, d in pts]


def add_pcb1_zones(b, cache):
    gnd = cache["GND"]
    poly = board_inset_polygon(0.2)
    zone(b, pcbnew.In1_Cu, poly, gnd, name="GND_In1")
    if "3V3" in cache and os.environ.get("CASE_FINE") == "1":
        zone(b, pcbnew.In2_Cu, poly, cache["3V3"], name="V33_In2")      # round 2: In2 is the 3V3 plane


def add_pcb1_outer_pours(b, cache):
    gnd = cache["GND"]
    poly = board_inset_polygon(0.2)
    layers = ((pcbnew.F_Cu, "GND_F"), (pcbnew.B_Cu, "GND_B")) if os.environ.get("CASE_FINE") == "1" else ((pcbnew.F_Cu, "GND_F"), (pcbnew.B_Cu, "GND_B"), (pcbnew.In2_Cu, "GND_In2"))
    for layer, nm in layers:
        zone(b, layer, poly, gnd, name=nm)


# ================================================================ PCB2
def kx(y):
    return OX2 - y


def ky(dz):
    return OY2 - dz


def pt2(y, dz):
    return VECTOR2I(mm(kx(y)), mm(ky(dz)))


def build_pcb2():
    b = pcbnew.BOARD()
    setup_rules(b, 2, geom.PCB2_T)
    cache = {}
    names = sorted({r["net"] for r in netrows if r["reference"] in PCB2_REFS and r["net"]})
    for n in names:
        get_net(b, cache, n)
    zh = geom.PCB2_Z_HALF
    ih = geom.PCB2_INNER_HALF
    wi, wo = geom.PCB2_WING_IN, geom.PCB2_WING_OUT
    # three pieces (inner island, wing of P1 at +y, wing of P4 at -y): front face seen from the pin side
    pieces = [(-ih, ih), (wi, wo), (-wo, -wi)]
    polys = []
    for (y0, y1) in pieces:
        polys.append([pt2(y0, zh), pt2(y1, zh), pt2(y1, -zh), pt2(y0, -zh)])
    outline(b, polys)
    ypin = geom.YPIN
    nets = {"P1": "VRING", "P2": "USB_D-", "P3": "USB_D+", "P4": "GND"}
    for k, ref in enumerate(["P1", "P2", "P3", "P4"]):
        add_part(b, cache, ref, "HARWIN_P70_6000045R", parts[ref]["value"], pt2(ypin[k], 0.0), 0, "F", net_of)
    wz = -1.75   # wire pads in the lower strip
    wire_y = {"WP1": ypin[0], "WP2": ypin[1], "WP3": ypin[2], "WP4": ypin[3], "WP7": 0.0}
    for wref, w in WIRE_ENDS.items():
        n = net_of(w, "1")
        add_part(b, cache, wref, "WIRE_SMD_0.9x1.1", "wire 30AWG pin-board end of " + w, pt2(wire_y[wref], wz), 0, "F", lambda r, p, n=n: n)
    # E1 front strip
    e1z = 1.70
    add_part(b, cache, "E1", "TOUCH_E1_front", parts["E1"]["value"], pt2(0.0, e1z), 0, "F", net_of)
    # tracks (front): pin pad to its wire pad, W7 to E1 between the two pin pads
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    for k, (pr, wr) in enumerate((("P1", "WP1"), ("P2", "WP2"), ("P3", "WP3"), ("P4", "WP4"))):
        n = cache[nets[pr]]
        track(b, pt2(ypin[k], 0.0), pt2(ypin[k], wz), F, 0.4 if pr == "P1" or pr == "P4" else 0.3, n)
    rt = cache["RING_TOUCH"]
    track(b, pt2(0.0, wz), pt2(0.0, e1z), F, 0.2, rt)
    # E1 back pour and its two vias
    for sy in (-1.4, 1.4):
        via(b, pt2(sy, e1z), rt)
    poly = [pt2(-(ih - 0.2), zh - 0.2), pt2(ih - 0.2, zh - 0.2), pt2(ih - 0.2, -(zh - 0.2)), pt2(-(ih - 0.2), -(zh - 0.2))]
    zone(b, B, poly, rt, clearance=0.2, name="E1_back_pour")
    add_netclass(b, "pwr", 0.4, ["VRING", "GND"])
    return b, cache


# ================================================================ main
def save(board, path):
    pcbnew.SaveBoard(path, board)


def fill_all(board):
    f = pcbnew.ZONE_FILLER(board)
    f.Fill(board.Zones())


# ================================================================ finish
import subprocess
KC = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")


def drc(path, out):
    rc = subprocess.call([KC, "pcb", "drc", "--severity-all", "--all-track-errors", "--format", "json", "-o", out, path],
                         stdout=open(out + ".log", "w"), stderr=subprocess.STDOUT)
    rep = json.load(open(out))
    return rc, len(rep.get("violations", [])), len(rep.get("unconnected_items", [])), rep


def net_length(b, netname):
    L = 0.0
    for t in b.GetTracks():
        if t.GetNetname() == netname:
            if t.Type() == pcbnew.PCB_VIA_T:
                L += ToMM(b.GetDesignSettings().GetBoardThickness()) if False else 0.0
            else:
                L += ToMM(t.GetLength())
    return L


def meander(b, netname, extra, layer_ok=(pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu), skip=0, h=0.8, w=0.30, pitch=0.60):
    """lengthen `netname` by about `extra` mm: replace the skip-th longest straight track of at least 3 mm by a square-wave bump train"""
    cands = [t for t in b.GetTracks() if t.GetNetname() == netname and t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() in layer_ok and ToMM(t.GetLength()) >= 1.6]
    cands.sort(key=lambda t: -t.GetLength())
    if skip >= len(cands):
        return False
    t = cands[skip]
    ax, ay = ToMM(t.GetStart().x), ToMM(t.GetStart().y)
    bx, by = ToMM(t.GetEnd().x), ToMM(t.GetEnd().y)
    L = math.hypot(bx - ax, by - ay)
    tx, ty = (bx - ax) / L, (by - ay) / L
    nx, ny = -ty, tx
    k = max(1, int(math.ceil(extra / (2 * h))))
    need = k * pitch + w
    if need > L - 0.7:
        k = int((L - 0.7 - w) / pitch)
        if k < 1:
            return False
    s0 = (L - (k * pitch + w)) / 2
    pts = [(ax, ay)]
    pos = s0
    pts.append((ax + tx * pos, ay + ty * pos))
    for i in range(k):
        x0, y0 = ax + tx * pos, ay + ty * pos
        pts += [(x0 + nx * h, y0 + ny * h), (x0 + nx * h + tx * w, y0 + ny * h + ty * w), (x0 + tx * w, y0 + ty * w)]
        pos += pitch
        pts.append((ax + tx * pos, ay + ty * pos))
    pts.append((bx, by))
    layer, width, net = t.GetLayer(), ToMM(t.GetWidth()), t.GetNet()
    b.Remove(t)
    for (p0, p1) in zip(pts[:-1], pts[1:]):
        if abs(p0[0] - p1[0]) + abs(p0[1] - p1[1]) < 1e-6:
            continue
        track(b, VECTOR2I(mm(p0[0]), mm(p0[1])), VECTOR2I(mm(p1[0]), mm(p1[1])), layer, width, net)
    return True


def finish_pcb1(ses):
    unr = os.path.join(WORK, "case_main_unrouted.kicad_pcb")
    b = pcbnew.LoadBoard(unr)
    ok = pcbnew.ImportSpecctraSES(b, ses)
    print("ses import", ok)
    cache = {}
    for ni in b.GetNetInfo().NetsByName().values() if hasattr(b.GetNetInfo().NetsByName(), "values") else []:
        cache[ni.GetNetname()] = ni
    if not cache:
        for code, ni in b.GetNetsByNetcode().items():
            cache[ni.GetNetname()] = ni
    # the router writes short pad-exit stubs narrower than the rule (0.1124 mm): set every track to at least the minimum width
    widened = 0
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_TRACE_T and ToMM(t.GetWidth()) < TRACK - 1e-6:
            t.SetWidth(mm(TRACK))
            widened += 1
    print("tracks widened to the minimum width:", widened)
    add_pcb1_outer_pours(b, cache)
    return b, cache


def pairs_length_report(b):
    return net_length(b, "USB_D+"), net_length(b, "USB_D-")


def remove_dangling(b, path, rounds=6):
    """removes tracks and vias that the router left unconnected at one end (DRC types track_dangling, via_dangling); returns the number removed"""
    removed = 0
    for rnd in range(rounds):
        pcbnew.SaveBoard(path, b)
        rc, nv, nu, rep = drc(path, path + ".tidy.json")
        ids = []
        for v in rep.get("violations", []):
            if v["type"] in ("track_dangling", "via_dangling"):
                ids += [i["uuid"] for i in v["items"]]
        if not ids:
            break
        byid = {t.m_Uuid.AsString(): t for t in b.GetTracks()}
        for u in ids:
            it = byid.get(u)
            if it is not None:
                b.Remove(it)
                removed += 1
        fill_all(b)
    return removed


def final_save_pcb1(b):
    out = os.path.join(HERE, "case_main.kicad_pcb")
    write_pro(PCB1_CLASSES, os.path.join(HERE, "case_main.kicad_pro"))
    fill_all(b)
    n = remove_dangling(b, out)
    print("dangling items removed:", n)
    pcbnew.SaveBoard(out, b)
    return out


def build_and_save_pcb2():
    b2, c2 = build_pcb2()
    fill_all(b2)
    write_pro(PCB2_CLASSES, os.path.join(HERE, "case_pins.kicad_pro"), default_width=0.3)
    out = os.path.join(HERE, "case_pins.kicad_pcb")
    pcbnew.SaveBoard(out, b2)
    return out


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "unrouted"
    TAG = os.environ.get("CASE_TAG", "")
    placement = json.load(open(os.environ.get("CASE_PLACEMENT", os.path.join(HERE, "placement_pcb1.json"))))
    if stage in ("unrouted", "all"):
        b1, c1 = build_pcb1(placement)
        antenna_keepout(b1)
        u1_ground_pattern(b1, c1)
        add_pcb1_zones(b1, c1)
        add_netclass(b1, "pwr_wide", P_WIDE, WIDE_NETS)
        add_netclass(b1, "pwr_med", P_MED, MED_NETS)
        add_netclass(b1, "pwr_3v3", P_3V3, NET_3V3)
        save(b1, os.path.join(WORK, "case_main_unrouted%s.kicad_pcb" % TAG))
        write_pro(PCB1_CLASSES, os.path.join(WORK, "case_main_unrouted%s.kicad_pro" % TAG))
        print("PCB1 unrouted: footprints", len(list(b1.GetFootprints())), "nets", len(c1))
    if stage == "pcb2":
        print("PCB2 saved", build_and_save_pcb2())
    if stage == "finish":
        b, cache = finish_pcb1(os.path.join(WORK, (sys.argv[2] if len(sys.argv) > 2 else "case_main") + ".ses"))
        lp, ln = pairs_length_report(b)
        print("USB lengths before tuning: D+ %.3f D- %.3f diff %.3f" % (lp, ln, abs(lp - ln)))
        write_pro(PCB1_CLASSES, os.path.join(HERE, "case_main.kicad_pro"))
        out = final_save_pcb1(b)
        print("PCB1 saved", out)
        print("PCB2 saved", build_and_save_pcb2())
    if stage == "grfinish":
        b = pcbnew.LoadBoard(sys.argv[2])
        cache = {n.GetNetname(): n for n in b.GetNetsByNetcode().values()}
        add_pcb1_outer_pours(b, cache)
        write_pro(PCB1_CLASSES, os.path.join(HERE, "case_main.kicad_pro"))
        out = final_save_pcb1(b)
        print("PCB1 saved", out)
        print("PCB2 saved", build_and_save_pcb2())
    if stage == "finish1":
        b, cache = finish_pcb1(os.path.join(WORK, "case_main.ses"))
        lp, ln = pairs_length_report(b)
        print("USB lengths before tuning: D+ %.3f D- %.3f diff %.3f" % (lp, ln, abs(lp - ln)))
        pcbnew.SaveBoard(os.path.join(WORK, "case_main_imported.kicad_pcb"), b)
    print("stage", stage, "done")
