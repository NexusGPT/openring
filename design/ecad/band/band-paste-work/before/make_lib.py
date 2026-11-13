#!/usr/bin/env python3
"""Writes the footprint library OpenRingBand.pretty (run with KiCad's own Python: ../ring/pcb/run_kipy.sh make_lib.py).
Each footprint description names the document and page its numbers come from."""
import os, sys, shutil
import pcbnew
from pcbnew import VECTOR2I, FromMM

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import band_layout as L

LIB = os.path.join(HERE, "OpenRingBand.pretty")
KICAD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
if os.path.isdir(LIB):
    shutil.rmtree(LIB)
os.makedirs(LIB)
board = pcbnew.BOARD()
IO = pcbnew.PCB_IO_KICAD_SEXPR()
mm = FromMM


def new_fp(name, descr, tags=""):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID("OpenRingBand", name))
    fp.SetReference("REF**")
    fp.SetValue(name)
    fp.SetLibDescription(descr)
    fp.SetKeywords(tags)
    fp.SetAttributes(pcbnew.FP_SMD)
    return fp


def add_pad(fp, num, x, y, w, h, shape="rect", side="F", mask_margin=0.05):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE if shape == "circle" else pcbnew.PAD_SHAPE_RECT)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    ls = pcbnew.LSET()
    if side == "F":
        ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.F_Mask)
    else:
        ls.AddLayer(pcbnew.B_Cu); ls.AddLayer(pcbnew.B_Mask)
    pad.SetLayerSet(ls)
    pad.SetSize(VECTOR2I(mm(w), mm(h)))
    pad.SetPosition(VECTOR2I(mm(x), mm(y)))
    pad.SetLocalSolderMaskMargin(mm(mask_margin))
    fp.Add(pad)
    return pad


def rect(fp, x0, y0, x1, y1, layer, w=0.05):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_RECT); s.SetLayer(layer); s.SetFilled(False)
    s.SetStart(VECTOR2I(mm(x0), mm(y0))); s.SetEnd(VECTOR2I(mm(x1), mm(y1))); s.SetWidth(mm(w))
    fp.Add(s)


def circle(fp, x, y, r, layer, w=0.05):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetLayer(layer); s.SetFilled(False)
    s.SetStart(VECTOR2I(mm(x), mm(y))); s.SetEnd(VECTOR2I(mm(x + r), mm(y))); s.SetWidth(mm(w))
    fp.Add(s)


def line(fp, x0, y0, x1, y1, layer, w=0.05):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(layer)
    s.SetStart(VECTOR2I(mm(x0), mm(y0))); s.SetEnd(VECTOR2I(mm(x1), mm(y1))); s.SetWidth(mm(w))
    fp.Add(s)


def finish(fp, ref_xy=(0, -2.0)):
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Reference().SetTextSize(VECTOR2I(mm(0.4), mm(0.4)))
    fp.Reference().SetTextThickness(mm(0.06))
    fp.Reference().SetPosition(VECTOR2I(mm(ref_xy[0]), mm(ref_xy[1])))
    fp.Value().SetVisible(False)
    IO.FootprintSave(LIB, fp)
    return fp


ALPS = ("Alps Alpine SKTAAAE010 tact switch, 2.6 x 1.6 x 0.53 mm. Land pattern from the Alps Alpine SKTA series catalog "
        "design/datasheets/w4_alps_skta_catalog.pdf page 2, Drawing No.1: 'Land Dimensions' (outer span 3.2, inner span 2.1, overall height 1.3, gap 0.2: "
        "four lands 0.55 x 0.55 at +-1.325 and +-0.375 from the centre). Terminal numbers as Alps gives them in the 'Dimensions' view on the same page "
        "(seen from above): 1 top left, 2 top right, 3 bottom left, 4 bottom right; 'Circuit Diagram': terminals 1 and 3 are joined, 2 and 4 are joined, "
        "the contact is between the two pairs. Reflow profile: product specification slim_alps-skta-aaae010-orwin.pdf page 4 (peak 260 C max 3 s).")

# ---- 1. switch, 4 lands
fp = new_fp("Alps_SKTAAAE010_4pad", ALPS + " This variant has all four lands (centre switch SW2).", "switch tact SKTA")
for n, (x, y) in {1: (-1.325, -0.375), 2: (1.325, -0.375), 3: (-1.325, 0.375), 4: (1.325, 0.375)}.items():
    add_pad(fp, n, x, y, 0.55, 0.55)
rect(fp, -1.3, -0.8, 1.3, 0.8, pcbnew.F_Fab)
circle(fp, -1.0, -0.5, 0.1, pcbnew.F_Fab)
rect(fp, -1.6, -0.65, 1.6, 0.65, pcbnew.F_CrtYd, 0.01)
finish(fp)

# ---- 2. switch, lands 3 and 4 only (the two lands on the side of the head centre)
fp = new_fp("Alps_SKTAAAE010_pads34", ALPS + " This variant has only lands 3 and 4 (bottom side): the head of the joystick tail is 6.4 mm wide and the outer lands "
            "1 and 2 of the four outer switches would lie 0.15 mm from the cut edge (copper to edge needs 0.30, JLCPCB flexible PCB capabilities, row FPC Outline). "
            "Terminals 3 and 4 are the two ends of the contact, so the switch works with lands 3 and 4 alone; terminals 1 and 2 float (they are joined to 3 and 4 inside).",
            "switch tact SKTA")
for n, (x, y) in {3: (-1.325, 0.375), 4: (1.325, 0.375)}.items():
    add_pad(fp, n, x, y, 0.55, 0.55)
rect(fp, -1.3, -0.8, 1.3, 0.8, pcbnew.F_Fab)
circle(fp, -1.0, -0.5, 0.1, pcbnew.F_Fab)
line(fp, -1.6, -0.375, -1.05, -0.375, pcbnew.F_Fab, 0.03)
rect(fp, -1.6, 0.1, 1.6, 0.65, pcbnew.F_CrtYd, 0.01)
finish(fp)

# ---- 3. motor lead lands, pitch 1.0 along the tail
fp = new_fp("W0525AB001D_Lands", "Lands for the two lead wires of the Jinlong W0525AB001D coin vibration motor (5.0 dia x 2.5, BLDC, 3.0 V). "
            "Source: design/datasheets/slim2_jinlong-w0525ab001d.pdf page 9 (drawing): 'Lead Wire (AWG32) Red(+)' and 'Black(or Blue)(-)', lead length 30 +-1.5, "
            "stripped end 1.5 +-0.5; page 14 item 9-2 (red to +, blue or black to -). Pad 1 = red lead (+, net VMOT, ring netlist M1 pin 1) at the foot side, pad 2 = blue lead (-, net GND, M1 pin 2) "
            "1.0 mm nearer the head. Each land is 0.30 along the tail x 0.80 across (long side toward the motor, which stands on the +X side of the tail). One AWG32 lead (bare diameter 0.20 mm) arrives across the tail from the motor, is stripped 0.6 mm and laid along the 0.80 side, then soldered by hand; pad centre is 0.13 mm toward -y of the footprint origin (FLEX1 frame, y = -v).",
            "motor leads")
add_pad(fp, "1", -0.5, -0.13, 0.30, 0.80)
add_pad(fp, "2", 0.5, -0.13, 0.30, 0.80)
rect(fp, -0.7, -0.53, 0.7, 0.27, pcbnew.F_Fab)
rect(fp, -0.75, -0.58, 0.75, 0.32, pcbnew.F_CrtYd, 0.01)
finish(fp)

# ---- 4. protection circuit output lands on FLEX2
fp = new_fp("PRT1_Tabs", "Three lands on FLEX2 for the three output tabs of the cell's protection circuit PRT1 (custom part; its interface is fixed by "
            "design/ecad/band/band-interface.md section 5, not by a maker sheet). Pad 1 'P+' = cell positive output (net VBAT, ring pin BT1 P1), pad 3 'NTC' = temperature "
            "sensor RT1 pin 1 (net NTC), pad 2 'P-' = cell negative output and RT1 pin 2 (net GND, ring pins BT1 P2 and RT1 2). Lands 0.26 along the tail x 0.45 across, pitch 0.43 "
            "along the tail in the order 1, 3, 2 (pad 2 farthest from the slot). The PRT1 tabs are nickel strips 0.30 wide x 0.10 thick lying on the lands; solder by hand.",
            "cell protection tabs")
for n, x in ((1, -0.43), (3, 0.0), (2, 0.43)):
    add_pad(fp, n, x, 0.0, 0.26, 0.45)
rect(fp, -0.7, -0.4, 0.7, 0.4, pcbnew.F_Fab)
rect(fp, -0.8, -0.5, 0.8, 0.5, pcbnew.F_CrtYd, 0.01)
finish(fp)

# ---- 5. charging pad land, on the inner face (B.Cu)
fp = new_fp("CP_Pad_1.6", "Charging pad land on the inner face (B.Cu) of FLEX2: round 1.6 mm. A gold-plated disc 1.6 dia bonded on it is the pad (architecture 17.12: 1.6 mm gold discs; "
            "design/mfg/specs/band-flex-tails.md critical dimensions: diameter 1.6, pitch 2.4 along the arc, order VBUS, D-, D+, GND). Land copper 1.6, coverlay opening 1.8. "
            "Disc: see design/ecad/band/band-interface.md section 8.", "charging pad")
add_pad(fp, 1, 0, 0, 1.6, 1.6, shape="circle", side="B", mask_margin=0.10)
circle(fp, 0, 0, 0.8, pcbnew.B_Fab)
circle(fp, 0, 0, 0.95, pcbnew.B_CrtYd, 0.01)
finish(fp)

# ---- 6. RT1 on the protection circuit board (0402)
src = pcbnew.FootprintLoad(os.path.join(KICAD_FP, "Resistor_SMD.pretty"), "R_0402_1005Metric")
fp = new_fp("RT1_NTC_0402", "Land pattern for the 10 kilo-ohm NTC thermistor RT1 (0402, 1005 metric), for the PRT1 board (RT1 sits on the cell's protection circuit, "
            "architecture 17.3 and 17.8). Pads copied from the KiCad standard footprint Resistor_SMD:R_0402_1005Metric (IPC-7351B nominal: 0.51 x 0.64 at +-0.51); "
            "ring parts.csv footprint field 'ring:R_0402'. Pad 1 = NTC signal (net NTC), pad 2 = ground (joined on the PRT1 board to the cell negative output, FLEX2 land 'P-').",
            "thermistor 0402")
for p in src.Pads():
    pos = p.GetPosition()
    sz = p.GetSize()
    add_pad(fp, p.GetNumber(), pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y), pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y), mask_margin=0.0)
rect(fp, -0.5, -0.25, 0.5, 0.25, pcbnew.F_Fab)
rect(fp, -1.05, -0.45, 1.05, 0.45, pcbnew.F_CrtYd, 0.01)
finish(fp)

# ---- 7. J_BAND on the main board and on the tail
def jband(table, side, name_board, name_tail, which):
    xc, yc = -2.25, side * 4.325
    fp = new_fp(name_board, f"Main board lands J_BAND_{which} (band tail {'FLEX1 joystick side' if which == 'A' else 'FLEX2 cell side'}), on the board underside, hot-bar soldered to the tail "
                f"foot. Pad numbers are the ring netlist's (design/ecad/ring/netlist.csv rows J_BAND_{which}). Positions, sizes and soldering method: "
                f"design/ecad/band/band-interface.md section 2 (land 0.30 x 0.55, column pitch 0.51, row pitch 0.90, X -3.015 to -1.485, |Y| 3.875 and 4.775; "
                f"free room from design/mfg/specs/band-flex-tails.md line 46). Footprint origin = middle of the pad group (X -2.250, Y {yc:+.3f}); coordinates are the ring model's X, Y "
                f"(ring board file: F.Cu = underside, no mirror).", "flex hot bar")
    for pin, (nm, net, row, col) in table.items():
        x, y = L.land_model_xy(table, pin, side)
        add_pad(fp, pin, x - xc, y - yc, L.BOARD_LAND[0], L.BOARD_LAND[1])
    ya, yb = sorted((side * 3.4 - yc, side * 5.6 - yc))       # keep-out X -3.50 to -1.00, |Y| 3.40 to 5.60 (band-interface.md section 2)
    rect(fp, -1.25, ya, 1.25, yb, pcbnew.F_CrtYd, 0.01)
    rect(fp, -1.6, -1.45, 1.6, 1.45, pcbnew.F_Fab)
    finish(fp, (0, -1.8))
    # tail end: tail frame, y = s * v ; origin at u 0.9, v 0.25
    s = side
    fp = new_fp(name_tail, f"Tail-end lands of band tail {'FLEX1' if which == 'A' else 'FLEX2'} that mate with J_BAND_{which}: same land centres seen on the tail (outer face F.Cu), "
                f"land 0.30 along the tail x 0.30 across, ENIG, coverlay opening 0.40 x 0.40. Tail frame: x = u along the tail from the end that goes under the board, "
                f"y = {'+' if s > 0 else '-'}v with v = X + 2.5. Origin at u 0.90, v 0.25 (middle of the foot). Source: design/ecad/band/band-interface.md sections 2 and 3.", "flex hot bar")
    for pin, (nm, net, row, col) in table.items():
        u, v = L.land_tail_uv(table, pin)
        add_pad(fp, pin, u - 0.9, s * (v - 0.25), L.LAND_U, L.LAND_V, mask_margin=0.05)
    rect(fp, -0.9, -1.35, 1.0, 1.35, pcbnew.F_CrtYd, 0.01)
    rect(fp, -0.9, -1.35, 1.0, 1.35, pcbnew.F_Fab)
    finish(fp, (0, -1.7))

jband(L.JBAND_A, -1, "J_BAND_A_BOARD", "J_BAND_A_TAIL", "A")
jband(L.JBAND_B, +1, "J_BAND_B_BOARD", "J_BAND_B_TAIL", "B")

with open(os.path.join(os.path.dirname(LIB), "fp-lib-table"), "w") as f:
    f.write('(fp_lib_table\n  (version 7)\n  (lib (name "OpenRingBand")(type "KiCad")(uri "${KIPRJMOD}/OpenRingBand.pretty")(options "")(descr "OpenRing band flexible circuit footprints"))\n)\n')
print("library", LIB, sorted(os.listdir(LIB)))
