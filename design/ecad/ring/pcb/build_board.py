#!/usr/bin/env python3
"""build_board.py [placement.csv] -- writes ring.kicad_pcb, ring.kicad_pro and ring.kicad_dru: the ring main board, placed,
with its outline, 4-layer stack, rules, net classes, rule areas and ground zones (no track: route_fixed.py adds the
scripted copper, the router the rest; make_board.sh runs every step).

Run with KiCad's own Python: ./run_kipy.sh build_board.py

Sources (design/wiring/ring-board-plan.md, "the plan"):
  stack c.2 (Plan A: 4 copper layers 0.018, dielectrics 0.065 prepreg / core / prepreg, 0.30 finished),
  rules c.5, antenna keep-out e.3 with the lead's Y 2.90 (wiring/lead-decisions.md, 2026-11-13 00:39), outline e.7
  (27.2 x 12.6, corners r 0.8, no notch), tail keep-outs f.1 / band-interface.md section 2, placement: the plan's
  round 2 table ring-board-plan-work/placement-plan.csv (reference, footprint, side, x_mm, y_mm, rotation_deg).
Coordinates: model (0,0) = KiCad (100,100), no mirror; F.Cu is the populated face (toward the floor), B.Cu faces the screen.
Every footprint comes from OpenRing.pretty or OpenRingBand.pretty unchanged; this script draws none.
"""
import csv, json, math, os, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
RING = os.path.dirname(HERE)
DESIGN = os.path.dirname(os.path.dirname(RING))
# round 2 of the board (board-notes-r2.md): the plan's current table design/wiring/ring-board-plan-work/placement-plan.csv
# (round 4, 02:41) with the board's own moves, written in full to placement-final.csv (same columns); every rotation and
# position the board uses is a row of that file (round 1's override lists are folded into it), so the table is the one truth
PLAN_TABLE = os.path.join(HERE, "placement-final.csv")
LIBS = {"OpenRing": os.path.join(HERE, "OpenRing.pretty"),
        "OpenRingBand": os.path.join(DESIGN, "ecad", "band", "OpenRingBand.pretty")}
OUT = os.path.join(HERE, "ring.kicad_pcb")
OX, OY = 100.0, 100.0
BX, BY, RC = 27.2, 12.6, 0.8
BAND_ONLY = {"RT1", "BT1", "SW1", "SW2", "SW3", "SW4", "SW5", "M1", "CP1", "CP2", "CP3", "CP4", "DISP1"}

# stack, plan c.2
CU_T, DI_T, MASK_T = 0.018, 0.065, 0.0165          # 4 x 0.018 + 3 x 0.065 = 0.267; masks bring it to 0.300
THICK = 0.30
# keep-outs (model mm): antenna (plan e.3, Y from the lead's decision), tail lands (band-interface.md section 2)
ANT_KO = [(-13.60, 3.10), (-9.20, 3.10), (-9.20, 3.30), (-8.75, 3.30), (-8.75, 6.30), (-13.60, 6.30)]   # plan R2.0 (lead's ruling)
TAIL_A_KO = (-3.50, -5.60, -1.00, -3.40)
TAIL_B_KO = (-3.50, 3.40, -1.00, 5.60)
EDGE_BAND = 0.15                                    # plan g.4: router keep-out band inside the outline

NETCLASS = {   # plan c.5 and d.5
    "RF": ["ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED", "ANT_TRIM"],
    "USB": ["USB_DP", "USB_DN"],
    "PWR": ["VBUS", "VBAT", "VSYS", "SW1", "SW2", "VDD_1V8", "VDD_3V0", "VMOT"],
}


def mm(v): return FromMM(v)
def P(x, y): return VECTOR2I(mm(OX + x), mm(OY + y))
def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


table_path = sys.argv[1] if len(sys.argv) > 1 else PLAN_TABLE
parts = {p["reference"]: p for p in rows(os.path.join(RING, "parts.csv"))}
net_rows = rows(os.path.join(RING, "netlist.csv"))
pin_net = {(r["reference"], r["pin_number"]): r["net"] for r in net_rows}
board_refs = [r for r in parts if r not in BAND_ONLY]

ROT_OVERRIDE = {}       # round 1's corrections are rows of placement-final.csv now (board-notes-r2.md, step 2)
PLACE_OVERRIDE = {}
place = {}
for r in rows(table_path):
    if r["reference"] in place:
        print("note: placement table repeats", r["reference"], "(first row kept)")
        continue
    place[r["reference"]] = r
missing = [r for r in board_refs if r not in place]
extra = [r for r in place if r not in board_refs]
if missing or extra:
    raise SystemExit("placement table %s: parts without a row %s, rows without a part %s" % (table_path, missing, extra))

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(mm(THICK))

nets = {}
for n in sorted({r["net"] for r in net_rows if r["net"]}):
    ni = pcbnew.NETINFO_ITEM(board, n); board.Add(ni); nets[n] = ni

# ---------------------------------------------------------------- outline: 27.2 x 12.6, corners r 0.8, no notch
def edge_seg(a, b):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(P(*a)); s.SetEnd(P(*b)); s.SetWidth(mm(0.05)); board.Add(s)
def edge_arc(c, a0, a1):
    pt = lambda a: (c[0] + RC * math.cos(math.radians(a)), c[1] + RC * math.sin(math.radians(a)))
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetArcGeometry(P(*pt(a0)), P(*pt((a0 + a1) / 2)), P(*pt(a1))); s.SetWidth(mm(0.05)); board.Add(s)
hx, hy = BX / 2, BY / 2
edge_seg((-hx + RC, -hy), (hx - RC, -hy)); edge_arc((hx - RC, -hy + RC), -90, 0)
edge_seg((hx, -hy + RC), (hx, hy - RC)); edge_arc((hx - RC, hy - RC), 0, 90)
edge_seg((hx - RC, hy), (-hx + RC, hy)); edge_arc((-hx + RC, hy - RC), 90, 180)
edge_seg((-hx, hy - RC), (-hx, -hy + RC)); edge_arc((-hx + RC, -hy + RC), 180, 270)

# ---------------------------------------------------------------- footprints
fps = {}
for ref in board_refs:
    p = parts[ref]; t = place[ref]
    lib, name = p["footprint"].split(":", 1)
    if t["footprint"] != p["footprint"]:
        raise SystemExit("%s: placement table footprint %s, parts.csv %s" % (ref, t["footprint"], p["footprint"]))
    fp = pcbnew.FootprintLoad(LIBS[lib], name)
    if fp is None:
        raise SystemExit("footprint %s not found" % p["footprint"])
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetReference(ref); fp.SetValue(p["value"] or p["symbol"])
    if p["dnp"] == "yes":
        fp.SetDNP(True); fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True)
    fp.SetField("MPN", p["mpn"])
    for pad in fp.Pads():
        n = pin_net.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(nets[n])
    x, y, rot = float(t["x_mm"]), float(t["y_mm"]), float(t["rotation_deg"])
    if ref in PLACE_OVERRIDE:
        print("position override", ref, (x, y), "->", PLACE_OVERRIDE[ref][0], ":", PLACE_OVERRIDE[ref][1])
        x, y = PLACE_OVERRIDE[ref][0]
    if ref in ROT_OVERRIDE:
        if rot != {"FB1": 90, "C1": 90, "R71": 90, "C2": 90}.get(ref, 0):
            raise SystemExit("%s: table rotation %s differs from the one the override was written for" % (ref, rot))
        print("rotation override", ref, rot, "->", ROT_OVERRIDE[ref][0], ":", ROT_OVERRIDE[ref][1])
        rot = ROT_OVERRIDE[ref][0]
    board.Add(fp)
    fp.SetPosition(P(x, y))
    fp.SetOrientationDegrees(rot)
    if t["side"] == "B":
        fp.Flip(P(x, y), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetOrientationDegrees(rot)
    fps[ref] = fp

# ---------------------------------------------------------------- rule areas and zones
def rect_outline(z, r):
    pts = r if isinstance(r, list) else [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    o = z.Outline(); o.NewOutline()
    for (x, y) in pts:
        o.Append(P(x, y))

def rule_area(name, r, tracks, vias, zones, layers):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True); z.SetZoneName(name)
    ls = pcbnew.LSET()
    for l in layers: ls.AddLayer(l)
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowZoneFills(zones)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    rect_outline(z, r); board.Add(z); return z

CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
# antenna keep-out: no via and no zone on any layer; tracks are limited by ring.kicad_dru (only the antenna's own stubs on F.Cu)
rule_area("ANT_KEEPOUT", ANT_KO, False, True, True, CU)
# tail land keep-outs: no via (band-interface.md: "every through hole"; plan f.3: no via inside)
rule_area("TAIL_A_KEEPOUT", TAIL_A_KO, False, True, False, CU)
# chip exit of the antenna line (U1 C1 to L2, inside and beside the ball field): the RF 0.20 gap does not apply there, the
# board gap does (Nordic's own layout has B2's track 0.15 from it); used by ring.kicad_dru
rule_area("RF_CHIP_EXIT", (1.90, -0.75, 2.80, -0.05), False, False, False, [pcbnew.F_Cu])
# chip exit of the USB pair (H6, H7 to the lane): the H-row neighbours stand 0.325 apart, the 0.20 pair gap starts past it
rule_area("USB_CHIP_EXIT", (3.80, 0.80, 4.75, 1.95), False, False, False, [pcbnew.F_Cu])
rule_area("TAIL_B_KEEPOUT", TAIL_B_KO, False, True, False, CU)
# router keep-out band along the edge (plan g.4): no track, no via; zones are kept off the edge by the copper-to-edge rule
e = EDGE_BAND
for i, r in enumerate(((-hx, -hy, hx, -hy + e), (-hx, hy - e, hx, hy), (-hx, -hy, -hx + e, hy), (hx - e, -hy, hx, hy))):
    rule_area("EDGE_BAND_%d" % i, r, True, True, False, CU)

def gnd_zone(layer, prio):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer); z.SetNet(nets["GND"]); z.SetZoneName("GND_" + board.GetLayerName(layer))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(mm(0.1)); z.SetMinThickness(mm(0.1))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    rect_outline(z, (-hx, -hy, hx, hy)); board.Add(z); return z
gnd_zone(pcbnew.B_Cu, 0)        # L4: ground plane (plan c.2)
gnd_zone(pcbnew.In1_Cu, 0)      # L2: ground copper everywhere the escape and signals leave room
gnd_zone(pcbnew.F_Cu, 0)        # L1: ground copper in free areas
gnd_zone(pcbnew.In2_Cu, 0)      # L3: ground copper in free areas (between the power tracks)

# ---------------------------------------------------------------- fab text: board name and stack, on F.Fab
t = pcbnew.PCB_TEXT(board); t.SetLayer(pcbnew.Dwgs_User)
t.SetText("Ring main board W2: 4 copper layers any-layer HDI, 0.30 +-0.025 mm finished, laser microvias 0.10/0.20 filled and plated over, ENIG-P (ENEPIG), stack in ring.kicad_pcb setup and fab/stackup.txt")
t.SetTextSize(VECTOR2I(mm(0.3), mm(0.3))); t.SetPosition(P(0, -7.2)); board.Add(t)

for fp in fps.values():
    for fld in fp.GetFields():
        if fld.GetName() != "Reference":
            fld.SetVisible(False)
    fp.Reference().SetLayer(pcbnew.F_Fab if not fp.IsFlipped() else pcbnew.B_Fab)
    fp.Reference().SetTextSize(VECTOR2I(mm(0.25), mm(0.25))); fp.Reference().SetTextThickness(mm(0.04))
    for it in list(fp.GraphicalItems()):
        if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            fp.Remove(it)     # silk removed: no room for it on 0201 parts; references are on the fab layer

# design rules (c.5) in the board settings too (they are written again into ring.kicad_pro below)
ds.m_TrackMinWidth = mm(0.065)
ds.m_MinClearance = mm(0.065)
ds.m_ViasMinSize = mm(0.2)
ds.m_MinThroughDrill = mm(0.1)
ds.m_MicroViasMinSize = mm(0.2)
ds.m_MicroViasMinDrill = mm(0.1)
ds.m_CopperEdgeClearance = mm(0.1)
ds.m_HoleToHoleMin = mm(0.2)
ds.m_HoleClearance = mm(0.075)
ds.m_ViasMinAnnularWidth = mm(0.05)

pcbnew.SaveBoard(OUT, board)

# ---------------------------------------------------------------- stack text (pcbnew Python has no stackup writer)
lines = ["\t\t(stackup", '\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))', '\t\t\t(layer "F.Paste" (type "Top Solder Paste"))',
         '\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness %s))' % MASK_T]
cu_names = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
diel = [("prepreg", "106 prepreg"), ("core", "core"), ("prepreg", "106 prepreg")]
for i, n in enumerate(cu_names):
    lines.append('\t\t\t(layer "%s" (type "copper") (thickness %s))' % (n, CU_T))
    if i < 3:
        lines.append('\t\t\t(layer "dielectric %d" (type "%s") (thickness %s) (material "%s") (epsilon_r 4.1) (loss_tangent 0.02))'
                     % (i + 1, diel[i][0], DI_T, diel[i][1]))
lines += ['\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness %s))' % MASK_T,
          '\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))', '\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))',
          '\t\t\t(copper_finish "ENEPIG")', '\t\t\t(dielectric_constraints no)', "\t\t)"]
txt = open(OUT).read()
assert "\t(setup\n" in txt and "(stackup" not in txt
txt = txt.replace("\t(setup\n", "\t(setup\n" + "\n".join(lines) + "\n", 1)
open(OUT, "w").write(txt)

# ---------------------------------------------------------------- project rules (c.5) and net classes
pro_path = os.path.join(HERE, "ring.kicad_pro")
pro = json.load(open(pro_path)) if os.path.exists(pro_path) else {}
pro.setdefault("board", {}).setdefault("design_settings", {})
dsj = pro["board"]["design_settings"]
dsj["rules"] = {
    "min_clearance": 0.065, "min_copper_edge_clearance": 0.1, "min_track_width": 0.065,
    "min_via_diameter": 0.2, "min_through_hole_diameter": 0.1, "min_via_annular_width": 0.05,
    "min_hole_clearance": 0.075, "min_hole_to_hole": 0.2, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
    "min_silk_clearance": 0.0, "min_text_height": 0.2, "min_text_thickness": 0.03,
    "allow_blind_buried_vias": True, "allow_microvias": True,
}
dsj["track_widths"] = [0.0, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.6]
dsj["via_dimensions"] = [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.2, "drill": 0.1}]
dsj["diff_pair_dimensions"] = [{"gap": 0.0, "via_gap": 0.0, "width": 0.0}, {"gap": 0.075, "via_gap": 0.0, "width": 0.1}]
def cls(name, clr, w, extra=None):
    c = {"name": name, "clearance": clr, "track_width": w, "via_diameter": 0.2, "via_drill": 0.1,
         "microvia_diameter": 0.2, "microvia_drill": 0.1, "diff_pair_width": 0.1, "diff_pair_gap": 0.075,
         "diff_pair_via_gap": 0.0, "wire_width": 6, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
         "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647 if name == "Default" else 1}
    return c
pro["net_settings"] = {
    "classes": [cls("Default", 0.075, 0.1), cls("RF", 0.075, 0.12), cls("USB", 0.075, 0.1), cls("PWR", 0.075, 0.15)],
    "meta": {"version": 4},
    "net_colors": None,
    "netclass_assignments": None,
    "netclass_patterns": [{"netclass": c, "pattern": n} for c, ns in NETCLASS.items() for n in ns],
}
pro["meta"] = {"filename": "ring.kicad_pro", "version": 3}
json.dump(pro, open(pro_path, "w"), indent=2)

# custom rules (c.5, d.1, d.2, e.3): written next to the board, KiCad reads ring.kicad_dru with ring.kicad_pro
dru = """(version 1)
# ring main board rules, design/wiring/ring-board-plan.md c.5 (written by build_board.py)
(rule "via land and ring"
  (condition "A.Type == 'Via'")
  (constraint via_diameter (min 0.2mm))
  (constraint hole_size (min 0.1mm))
  (constraint annular_width (min 0.05mm)))
(rule "hole to hole"
  (constraint hole_to_hole (min 0.2mm)))
(rule "RF line 0.20 to other copper (d.1)"
  (condition "A.NetClass == 'RF' && A.Type == 'Track' && B.NetClass != 'RF' && !A.intersectsArea('RF_CHIP_EXIT')")
  (constraint clearance (min 0.2mm)))
(rule "RF to zones (d.1)"
  (condition "A.NetClass == 'RF' && B.Type == 'Zone'")
  (constraint clearance (min 0.2mm)))
(rule "USB pair 0.20 to other tracks and vias (d.2)"
  (condition "A.NetClass == 'USB' && A.Type == 'Track' && B.NetClass != 'USB' && (B.Type == 'Track' || B.Type == 'Via') && !A.intersectsArea('USB_CHIP_EXIT')")
  (constraint clearance (min 0.2mm)))
(rule "USB to zones (d.2)"
  (condition "A.NetClass == 'USB' && B.Type == 'Zone'")
  (constraint clearance (min 0.2mm)))
(rule "PWR gap (c.5)"
  (condition "A.NetClass == 'PWR' && A.Type == 'Track' && B.Type == 'Track'")
  (constraint clearance (min 0.1mm)))
(rule "antenna keep-out (e.3): only the antenna's own tracks on F.Cu"
  (condition "A.Type == 'Track' && A.intersectsArea('ANT_KEEPOUT') && !(A.Layer == 'F.Cu' && (A.NetName == 'RF_FEED' || A.NetName == 'ANT_TRIM' || A.NetName == 'GND'))")
  (constraint disallow track))
"""
open(os.path.join(HERE, "ring.kicad_dru"), "w").write(dru)

# project footprint libraries: both libraries the board uses
open(os.path.join(HERE, "fp-lib-table"), "w").write(
    '(fp_lib_table\n  (version 7)\n'
    '  (lib (name "OpenRing")(type "KiCad")(uri "${KIPRJMOD}/OpenRing.pretty")(options "")(descr "OpenRing footprints, one per package of parts.csv (W1)"))\n'
    '  (lib (name "OpenRingBand")(type "KiCad")(uri "${KIPRJMOD}/../../band/OpenRingBand.pretty")(options "")(descr "band library (band-circuits): J_BAND_A_BOARD, J_BAND_B_BOARD"))\n)\n')

print("footprints:", len(fps), "nets:", len(nets), "placement table:", table_path, "written", OUT)
