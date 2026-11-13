#!/usr/bin/env python3
"""Writes OpenRingCase.pretty: one exact footprint per distinct package of the case boards.
Run with KiCad's own Python:  design/ecad/ring/pcb/run_kipy.sh design/ecad/case/pcb/make_footprints.py
Every pad position and size below comes from the maker document and page named in the description of its footprint.
Pad numbers are the maker's pin numbers (or, where the maker gives none, the numbers stated in open-pins.csv).
Frame of every footprint: top view of the board (x right, y down), origin at the package centre unless said otherwise."""
import os
import pcbnew
from pcbnew import VECTOR2I, FromMM

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "OpenRingCase.pretty")
os.makedirs(LIB, exist_ok=True)
for _f in os.listdir(LIB):                      # rebuild the library from scratch: the files below are the whole library
    if _f.endswith(".kicad_mod"):
        print("removing previous", _f)
        os.remove(os.path.join(LIB, _f))
BOARD = pcbnew.BOARD()
CY = 0.10          # courtyard margin around pads/body (assembly spacing)
FPS = {}           # name -> (description, tags)


def mm(v):
    return FromMM(v)


def new(name, desc, tags, smd=True):
    fp = pcbnew.FOOTPRINT(BOARD)
    fp.SetFPID(pcbnew.LIB_ID("", name))
    fp.SetReference("REF**")
    fp.SetValue(name)
    fp.SetLibDescription(desc)
    fp.SetKeywords(tags)
    fp.SetAttributes(pcbnew.FP_SMD if smd else pcbnew.FP_THROUGH_HOLE)
    fp.Reference().SetLayer(pcbnew.F_SilkS)
    fp.Value().SetLayer(pcbnew.F_Fab)
    for t in (fp.Reference(), fp.Value()):
        t.SetTextSize(VECTOR2I(mm(0.8), mm(0.8)))
        t.SetTextThickness(mm(0.12))
    return fp


def smd(fp, num, x, y, w, h, rr=0.2, shape="roundrect", paste=True):
    p = pcbnew.PAD(fp)
    p.SetNumber(str(num))
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    if shape == "rect":
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
    elif shape == "circle":
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    else:
        p.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
        p.SetRoundRectRadiusRatio(rr)
    p.SetSize(VECTOR2I(mm(w), mm(h)))
    p.SetPosition(VECTOR2I(mm(x), mm(y)))
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.F_Mask)
    if paste:
        ls.AddLayer(pcbnew.F_Paste)
    p.SetLayerSet(ls)
    fp.Add(p)
    return p


def pth(fp, num, x, y, dia, drill, oval=None):
    p = pcbnew.PAD(fp)
    p.SetNumber(str(num))
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    if oval:
        p.SetShape(pcbnew.PAD_SHAPE_OVAL)
        p.SetSize(VECTOR2I(mm(oval[0]), mm(oval[1])))
        p.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
        p.SetDrillSize(VECTOR2I(mm(drill[0]), mm(drill[1])))
    else:
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        p.SetSize(VECTOR2I(mm(dia), mm(dia)))
        p.SetDrillSize(VECTOR2I(mm(drill), mm(drill)))
    p.SetPosition(VECTOR2I(mm(x), mm(y)))
    p.SetLayerSet(pcbnew.PAD.PTHMask())
    fp.Add(p)
    return p


def npth(fp, x, y, drill):
    p = pcbnew.PAD(fp)
    p.SetNumber("")
    p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(VECTOR2I(mm(drill), mm(drill)))
    p.SetDrillSize(VECTOR2I(mm(drill), mm(drill)))
    p.SetPosition(VECTOR2I(mm(x), mm(y)))
    p.SetLayerSet(pcbnew.PAD.UnplatedHoleMask())
    fp.Add(p)
    return p


def rect(fp, layer, x0, y0, x1, y1, w=0.05):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(VECTOR2I(mm(x0), mm(y0)))
    s.SetEnd(VECTOR2I(mm(x1), mm(y1)))
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    s.SetFilled(False)
    fp.Add(s)


def line(fp, layer, x0, y0, x1, y1, w=0.12):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(VECTOR2I(mm(x0), mm(y0)))
    s.SetEnd(VECTOR2I(mm(x1), mm(y1)))
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    fp.Add(s)


def circle(fp, layer, x, y, r, w=0.12, fill=False):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetStart(VECTOR2I(mm(x), mm(y)))
    s.SetEnd(VECTOR2I(mm(x + r), mm(y)))
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    s.SetFilled(fill)
    fp.Add(s)


def pads_bbox(fp):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for p in fp.Pads():
        pos = p.GetPosition()
        sz = p.GetSize()
        xs0.append(pos.x - sz.x // 2); xs1.append(pos.x + sz.x // 2)
        ys0.append(pos.y - sz.y // 2); ys1.append(pos.y + sz.y // 2)
    return min(xs0), min(ys0), max(xs1), max(ys1)


def finish(fp, body=None, court=None, mark=None):
    """body = (w, h) fab outline; court = (x0, y0, x1, y1) in mm, default pads bbox + CY"""
    if body:
        rect(fp, pcbnew.F_Fab, -body[0] / 2, -body[1] / 2, body[0] / 2, body[1] / 2, 0.1)
    if court is None:
        x0, y0, x1, y1 = pads_bbox(fp)
        court = (pcbnew.ToMM(x0) - CY, pcbnew.ToMM(y0) - CY, pcbnew.ToMM(x1) + CY, pcbnew.ToMM(y1) + CY)
        if body:
            court = (min(court[0], -body[0] / 2 - CY), min(court[1], -body[1] / 2 - CY),
                     max(court[2], body[0] / 2 + CY), max(court[3], body[1] / 2 + CY))
    rect(fp, pcbnew.F_CrtYd, *court, w=0.05)
    if mark:
        # pin-1 mark: silkscreen circle at the body corner on the side of pad `mark` when it keeps 0.25 mm from every pad of this footprint (the part body hides it
        # after assembly, so it only helps a builder placing the part); otherwise a circle on F.Fab outside the courtyard (never over copper)
        pad1 = [p for p in fp.Pads() if p.GetNumber() == str(mark)][0]
        px, py = pcbnew.ToMM(pad1.GetPosition().x), pcbnew.ToMM(pad1.GetPosition().y)
        bw, bh = body if body else (2 * abs(court[0]), 2 * abs(court[1]))
        sx = -1 if px < 0 else 1
        sy = -1 if py < 0 else 1
        mx, my = sx * (bw / 2 - 0.25), sy * (bh / 2 - 0.25)
        clear = True
        for q in fp.Pads():
            qx, qy = pcbnew.ToMM(q.GetPosition().x), pcbnew.ToMM(q.GetPosition().y)
            qw, qh = pcbnew.ToMM(q.GetSize().x), pcbnew.ToMM(q.GetSize().y)
            if abs(mx - qx) < qw / 2 + 0.25 + 0.15 and abs(my - qy) < qh / 2 + 0.25 + 0.15:
                clear = False
        if clear:
            circle(fp, pcbnew.F_SilkS, mx, my, 0.12, 0.12, True)
        else:
            ox = court[0] - 0.3 if px < 0 else court[2] + 0.3
            circle(fp, pcbnew.F_Fab, ox if abs(px) >= abs(py) else px, py if abs(px) >= abs(py) else (court[1] - 0.3 if py < 0 else court[3] + 0.3), 0.12, 0.1, True)
    t = fp.Reference()
    t.SetPosition(VECTOR2I(0, mm(court[1] - 0.8)))
    v = fp.Value()
    v.SetPosition(VECTOR2I(0, mm(court[3] + 0.8)))
    name = fp.GetFPID().GetLibItemName()
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    path = os.path.join(LIB, str(name) + ".kicad_mod")
    if os.path.exists(path):
        os.remove(path)
    io.FootprintSave(LIB, fp)


# ---------------------------------------------------------------- chip parts
# IPC-7351B nominal land patterns for the three chip sizes (the standard; the passives' maker documents give only the body size)
def chip(name, pad_w, pad_h, pitch_c, body, desc):
    fp = new(name, desc, "chip 0402 0603 0805 smd")
    smd(fp, 1, -pitch_c / 2, 0, pad_w, pad_h)
    smd(fp, 2, pitch_c / 2, 0, pad_w, pad_h)
    finish(fp, body=body)


chip("SMD_0402", 0.58, 0.62, 0.96, (1.0, 0.5),
     "Chip 0402 (1005 metric), body 1.0 x 0.5 mm; pads 0.58 x 0.62 mm at 0.96 mm pitch (IPC-7351B nominal). Used for R and C 0402. "
     "Body size: Murata GRM155 / Yageo RC0402 outline; land pattern: IPC-7351B.")
chip("SMD_0603", 0.80, 0.95, 1.65, (1.6, 0.8),
     "Chip 0603 (1608 metric), body 1.6 x 0.8 mm; pads 0.80 x 0.95 mm at 1.65 mm pitch (IPC-7351B nominal). Used for C 0603. "
     "Body size: Murata GRM188 outline (size 0603 (1608) named in case_tps63802.pdf Table 10-3 p.20); land pattern: IPC-7351B.")
chip("SMD_0805", 1.025, 1.40, 1.825, (2.0, 1.25),
     "Chip 0805 (2012 metric), body 2.0 x 1.25 mm; pads 1.025 x 1.40 mm at 1.825 mm pitch (IPC-7351B nominal). Used for C2 and C3 (PMID). "
     "Body size: Murata GRM21B outline; land pattern: IPC-7351B.")

# ---------------------------------------------------------------- inductors: Coilcraft XFL4015 (L2) and XFL4020 (L1): same land pattern
fp = new("L_XFL40xx_4x4",
         "Coilcraft XFL4015 / XFL4020 shielded inductor, body 4.0 x 4.0 mm (height 1.6 max XFL4015, 2.1 max XFL4020). Two pads 0.98 x 3.4 mm, "
         "2.37 mm between pads (pad centres 3.35 mm apart). Source: w5_coilcraft_xfl4015.pdf (Coilcraft document 769-2) page 2 'Recommended Land Pattern'; "
         "w5_coilcraft_xfl4020.pdf (document 745-3) page 3, same pattern. Pad 1 on the side of the dash number marking.",
         "inductor coilcraft xfl4015 xfl4020")
smd(fp, 1, -1.675, 0, 0.98, 3.4, rr=0.1)
smd(fp, 2, 1.675, 0, 0.98, 3.4, rr=0.1)
finish(fp, body=(4.0, 4.0), mark=1)

# ---------------------------------------------------------------- U1 ESP32-S3-MINI-1 (case_esp32s3_mini1.pdf Figure 11-1 p.45, Figure 3-1 p.10, Figure 10-1 p.42)
fp = new("ESP32-S3-MINI-1",
         "Espressif ESP32-S3-MINI-1 module 15.4 x 20.5 mm, 65 pins. Land pattern: case_esp32s3_mini1.pdf Figure 11-1 (p.45): 60 pads 0.4 x 0.8 mm, "
         "4 corner pads 0.8 x 0.8 mm, pitch 0.85 mm, pad ring 14 x 14 mm between corner pad centres, centre ground pad of 3 x 3 squares 1.2 mm at 1.65 mm pitch (all pin 61). "
         "Pin numbers: Figure 3-1 (p.10) top view: left column 1 to 15 top to bottom, bottom row 16 to 30 left to right, right column 45 (top) to 31 (bottom), "
         "top row 60 to 46 left to right, corners 62 (top left), 65 (top right), 63 (bottom left), 64 (bottom right). Antenna area 5.05 mm above the top pad row (Figure 11-1). "
         "Origin: module body centre; antenna at the top (negative y).",
         "esp32 module espressif antenna")
P = 0.85
for k in range(15):
    smd(fp, 1 + k, -7.0, -3.75 + P * k, 0.8, 0.4, rr=0.25)            # left column pins 1..15
    smd(fp, 16 + k, -5.95 + P * k, 9.2, 0.4, 0.8, rr=0.25)            # bottom row pins 16..30
    smd(fp, 45 - k, 7.0, -3.75 + P * k, 0.8, 0.4, rr=0.25)            # right column pins 45..31 top to bottom
    smd(fp, 60 - k, -5.95 + P * k, -4.8, 0.4, 0.8, rr=0.25)           # top row pins 60..46 left to right
for num, x, y in ((62, -7.0, -4.8), (65, 7.0, -4.8), (63, -7.0, 9.2), (64, 7.0, 9.2)):
    smd(fp, num, x, y, 0.8, 0.8, rr=0.2)
for ix in (-1, 0, 1):
    for iy in (-1, 0, 1):
        smd(fp, 61, 1.65 * ix, 2.2 + 1.65 * iy, 1.2, 1.2, rr=0.1)
rect(fp, pcbnew.F_Fab, -7.7, -10.25, 7.7, 10.25, 0.1)
rect(fp, pcbnew.F_CrtYd, -7.8, -10.35, 7.8, 10.35, 0.05)
fp.Reference().SetPosition(VECTOR2I(0, mm(-11.3)))
fp.Value().SetPosition(VECTOR2I(0, mm(11.3)))
circle(fp, pcbnew.F_Fab, -8.5, -3.75, 0.2, 0.1, True)          # pin 1 mark on the fab layer (the silk position would sit on the neighbouring copper)
io = pcbnew.PCB_IO_KICAD_SEXPR()
io.FootprintSave(LIB, fp)

# ---------------------------------------------------------------- U2 BQ25895 RTW WQFN-24 (case_bq25895.pdf p.62 outline, p.63 thermal pad, p.64 land pattern)
fp = new("WQFN-24_RTW_4x4",
         "TI RTW (S-PWQFN-N24) 4 x 4 mm, 0.5 mm pitch. Land pattern: case_bq25895.pdf p.64 'Example Board Layout': pads 0.28 x 0.85 mm (outer span 4.8 mm), "
         "thermal land 2.6 x 2.6 mm (TI shows 3.1 mm, which touches the pin pads: its inner edge is 1.55 mm from the centre, the same as the pin pads' inner ends; 2.6 mm is the smallest exposed pad of the package, 2.7 +-0.1 mm on p.63, and leaves 0.2 mm to every pin pad) with 9 vias dia 0.3 mm on a 0.9 mm grid; paste: four 1.1 mm windows (stencil figure). Pin order p.62 (outline, bottom view) mirrored to the top view: "
         "pins 1 to 6 on the top row right to left, 7 to 12 on the left column, 13 to 18 on the bottom row, 19 to 24 on the right column. "
         "Exposed pad = pad 25 (TI numbers none; 25 = pin count + 1, requirement closed in open-pins.csv).",
         "bq25895 wqfn qfn rtw ti")
for k in range(6):
    smd(fp, 1 + k, 1.25 - 0.5 * k, -1.975, 0.28, 0.85, rr=0.5)
    smd(fp, 7 + k, -1.975, -1.25 + 0.5 * k, 0.85, 0.28, rr=0.5)
    smd(fp, 13 + k, -1.25 + 0.5 * k, 1.975, 0.28, 0.85, rr=0.5)
    smd(fp, 19 + k, 1.975, 1.25 - 0.5 * k, 0.85, 0.28, rr=0.5)
ep = smd(fp, 25, 0, 0, 2.6, 2.6, rr=0.05, paste=False)
for ix in (-1, 0, 1):
    for iy in (-1, 0, 1):
        pth(fp, 25, 0.9 * ix, 0.9 * iy, 0.6, 0.3)
for sx in (-0.7, 0.7):
    for sy in (-0.7, 0.7):
        q = pcbnew.PAD(fp)
        q.SetNumber("")
        q.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        q.SetShape(pcbnew.PAD_SHAPE_RECT)
        q.SetSize(VECTOR2I(mm(1.1), mm(1.1)))
        q.SetPosition(VECTOR2I(mm(sx), mm(sy)))
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Paste); q.SetLayerSet(ls)
        fp.Add(q)
finish(fp, body=(4.0, 4.0), court=(-2.55, -2.55, 2.55, 2.55), mark=1)

# ---------------------------------------------------------------- U3 TPS63802 DLA VSON-HR 10 (case_tps63802.pdf p.35 outline, p.36 land pattern)
fp = new("DFN-10_DLA_2x3",
         "TI DLA0010A VSON-HR 10 pin, 2.0 x 3.0 mm, 0.5 mm pitch. Land pattern: case_tps63802.pdf p.36 'Example Board Layout' (top view): pins 1 to 5 on the left at x = -0.9 mm, "
         "pads 0.6 x 0.25 mm; pins 6, 7, 9, 10 on the right at x = +0.75 mm, pads 0.9 x 0.25 mm; pin 8 (GND) long pad 1.3 x 0.25 mm centred at x = +0.55 mm. "
         "Pin order from the outline p.35 (bottom view) mirrored: 1 to 5 down the left side, 6 at the bottom right up to 10 at the top right.",
         "tps63802 dfn vson ti")
for k in range(5):
    smd(fp, 1 + k, -0.9, -1.0 + 0.5 * k, 0.6, 0.25, rr=0.2)
for n, y in ((6, 1.0), (7, 0.5), (9, -0.5), (10, -1.0)):
    smd(fp, n, 0.75, y, 0.9, 0.25, rr=0.2)
smd(fp, 8, 0.55, 0.0, 1.3, 0.25, rr=0.2)
finish(fp, body=(2.0, 3.0), mark=1)

# ---------------------------------------------------------------- U5 TPS2553 DBV SOT-23-6 (case_tps2553.pdf p.43 outline, p.44 land pattern DBV0006A)
fp = new("SOT-23-6_DBV",
         "TI DBV0006A SOT-23 6 pin, body 2.9 x 1.6 mm, pitch 0.95 mm. Land pattern: case_tps2553.pdf p.44 'Example Board Layout' DBV0006A: 6 pads 1.1 x 0.6 mm, "
         "columns 2.6 mm apart. Pins 1 to 3 on the left top to bottom, 4 to 6 on the right bottom to top.",
         "tps2553 sot-23 dbv ti")
for k in range(3):
    smd(fp, 1 + k, -1.3, -0.95 + 0.95 * k, 1.1, 0.6, rr=0.15)
    smd(fp, 4 + k, 1.3, 0.95 - 0.95 * k, 1.1, 0.6, rr=0.15)
finish(fp, body=(2.9, 1.6), mark=1)

# ---------------------------------------------------------------- U6 TPD4E05U06 DQA USON-10 (case_tpd4e05u06.pdf p.28 outline, p.29 land pattern DQA0010A)
fp = new("USON-10_DQA_1x2.5",
         "TI DQA0010A USON 10 pin, 1.0 x 2.5 mm, 0.5 mm pitch. Land pattern: case_tpd4e05u06.pdf p.29 'Example Board Layout' DQA0010A: pads 0.565 x 0.2 mm, "
         "pins 3 and 8 (GND) 0.565 x 0.4 mm, columns 0.835 mm apart. Pins 1 to 5 on the left top to bottom, 6 to 10 on the right bottom to top. "
         "DQA0010B (p.32) has the same pad grid with 0.3 mm centre pads; the 0.4 mm pads here cover both.",
         "tpd4e05u06 uson dqa ti esd")
for k in range(5):
    h = 0.4 if k == 2 else 0.2
    smd(fp, 1 + k, -0.4175, -1.0 + 0.5 * k, 0.565, h, rr=0.2)
    smd(fp, 6 + k, 0.4175, 1.0 - 0.5 * k, 0.565, h, rr=0.2)
finish(fp, body=(1.0, 2.5), mark=1)

# ---------------------------------------------------------------- J1 USB4105-GF-A (case_usb4105.pdf p.1 drawing rev B4, 'Recommended PCB Layout')
fp = new("USB4105-GF-A",
         "GCT USB4105-GF-A USB Type-C receptacle, top mount, 16 contacts on 12 pads, 8.94 x 7.35 x 3.31 mm. Land pattern: case_usb4105.pdf p.1 'Recommended PCB Layout' "
         "(rev B4, component side view): 12 pads 1.15 mm long at y = -3.68 mm; wide pads 0.6 mm (A1/B12 x -3.2, A4/B9 x -2.4, B4/A9 x +2.4, A12/B1 x +3.2), "
         "narrow pads 0.3 mm (B8 -1.75, A5 -1.25, B7 -0.75, A6 -0.25, A7 +0.25, B6 +0.75, A8 +1.25, B5 +1.75); two holes dia 0.65 mm at x +-2.89 y -2.605; "
         "four shell slots at x +-4.32: y -3.105 (pad 1.0 x 2.1 mm, drill 0.6 x 1.7) and y +1.075 (pad 1.0 x 1.8 mm, drill 0.6 x 1.4). "
         "Pin table (p.1): A1, A12, B1, B12 GND, A4, A9, B4, B9 VBUS, A5 CC1, B5 CC2, A6 Dp1, A7 Dn1, B6 Dp2, B7 Dn2, A8 SBU1, B8 SBU2, SHELL (no number: the four shell pads are all numbered SH). "
         "Two contacts share each wide pad, so both pad numbers sit on the same copper. Mating face at y = +4.18 mm (courtyard line of the drawing).",
         "usb type-c receptacle gct usb4105")
for num, x, w in (("A1", -3.2, 0.6), ("B12", -3.2, 0.6), ("A4", -2.4, 0.6), ("B9", -2.4, 0.6), ("B8", -1.75, 0.3), ("A5", -1.25, 0.3),
                  ("B7", -0.75, 0.3), ("A6", -0.25, 0.3), ("A7", 0.25, 0.3), ("B6", 0.75, 0.3), ("A8", 1.25, 0.3), ("B5", 1.75, 0.3),
                  ("B4", 2.4, 0.6), ("A9", 2.4, 0.6), ("B1", 3.2, 0.6), ("A12", 3.2, 0.6)):
    smd(fp, num, x, -3.68, w, 1.15, rr=0.15)
npth(fp, -2.89, -2.605, 0.65)
npth(fp, 2.89, -2.605, 0.65)
for sx in (-4.32, 4.32):
    pth(fp, "SH", sx, -3.105, 1.0, (0.6, 1.7), oval=(1.0, 2.1))
    pth(fp, "SH", sx, 1.075, 1.0, (0.6, 1.4), oval=(1.0, 1.8))
rect(fp, pcbnew.F_Fab, -4.47, -3.17, 4.47, 4.18, 0.1)
rect(fp, pcbnew.F_CrtYd, -5.32, -4.4, 5.32, 4.18, 0.05)
fp.Reference().SetPosition(VECTOR2I(0, mm(-5.2)))
fp.Value().SetPosition(VECTOR2I(0, mm(5.2)))
io.FootprintSave(LIB, fp)

# ---------------------------------------------------------------- LED1 APTF1616SEEZGQBDC (case_kb_aptf1616.pdf p.1)
fp = new("LED_APTF1616",
         "Kingbright APTF1616SEEZGQBDC RGB LED 1.6 x 1.6 x 0.7 mm. Land pattern: case_kb_aptf1616.pdf p.1 'Recommended Soldering Pattern': pads 0.85 x 0.5 mm, "
         "0.9 mm between pads in x, 0.5 mm in y (2.6 x 1.5 mm overall). Pin numbers from the package drawing (top view): 3 top left (green), 4 top right (blue), "
         "2 bottom left (red), 1 bottom right (common anode); polarity mark at pin 2.",
         "led rgb kingbright aptf1616")
smd(fp, 3, -0.875, -0.5, 0.85, 0.5, rr=0.15)
smd(fp, 4, 0.875, -0.5, 0.85, 0.5, rr=0.15)
smd(fp, 2, -0.875, 0.5, 0.85, 0.5, rr=0.15)
smd(fp, 1, 0.875, 0.5, 0.85, 0.5, rr=0.15)
finish(fp, body=(1.6, 1.6), mark=2)

# ---------------------------------------------------------------- U4 Zetta ZDSD64GLQEAG-R LGA16 9 x 10 (sdnand_zetta_family_atta.pdf p.15 package, p.4 pin assignment)
fp = new("LGA16_9x10_ZDSD",
         "Zetta ZDSD64GLQEAG-R SD NAND, LGA 9.00 x 10.00 mm (E x D), 16 lands for 8 signals. Source: sdnand_zetta_family_atta.pdf p.15 'Package Dimensions' bottom view: "
         "lands L x b = 0.80 x 0.60 mm (outer columns) and 0.80 x 0.80 mm (inner columns, b1), row pitch 1.27 mm, inner columns 1.1 to 1.9 mm from the package ends, "
         "outer columns 0 to 0.8 mm. Each signal has one outer and one inner land (same pad number). Signals p.4 section 5 (left group of the bottom view, top to bottom): "
         "1 DAT2, 2 CD/DAT3, 3 CLK, 4 GND; right group: 5 VDD, 6 DAT1, 7 DAT0, 8 CMD. The maker numbers no land: pin numbers 1 to 8 are ours (open-pins.csv), in the order of the maker's figure. "
         "This footprint is the top view (bottom view mirrored); pin 1 marker at the top right. Package long axis along x.",
         "sd nand lga zetta zdsd64")
rows = (-1.905, -0.635, 0.635, 1.905)
for r, y in enumerate(rows):
    smd(fp, 1 + r, 4.6, y, 0.8, 0.6, rr=0.15)     # outer left-group column (bottom view) -> right side here
    smd(fp, 1 + r, 3.5, y, 0.8, 0.8, rr=0.15)
    smd(fp, 5 + r, -3.5, y, 0.8, 0.8, rr=0.15)
    smd(fp, 5 + r, -4.6, y, 0.8, 0.6, rr=0.15)
finish(fp, body=(10.0, 9.0), mark=1)

# ---------------------------------------------------------------- P1 to P4 Harwin P70-6000045R (p3_harwin_p70_chipdip.pdf p.1, 2.8 mm free height)
fp = new("HARWIN_P70_6000045R",
         "Harwin P70-6000045R spring contact, SMT with peg, free height 2.80 mm, barrel dia 1.50 mm, 1.85 mm long, peg dia 1.00 mm. Land pattern: p3_harwin_p70_chipdip.pdf p.1 "
         "'Recommended PC Board Pattern' for the 2.8 mm pin: solder pad dia 1.70 mm, hole dia 1.10 mm (plated here, the pad ring also on the back).",
         "harwin p70 pogo spring pin", smd=False)
pth(fp, 1, 0, 0, 1.7, 1.1)
circle(fp, pcbnew.F_Fab, 0, 0, 0.75, 0.1)
finish(fp, court=(-0.9, -0.9, 0.9, 0.9))

# ---------------------------------------------------------------- wire pads
fp = new("WIRE_PTH_0.7",
         "Solder pad for one flying wire (30 AWG, conductor 0.25 mm; or a cell lead): plated hole dia 0.70 mm, pad dia 1.30 mm (annular ring 0.30 mm). "
         "Wire is pushed through from the board side that faces the wire and soldered on the top face. Hole and ring sizes: ours; capability page in board-notes.md (JLCPCB: PTH ring recommended 0.2 mm, minimum 0.15 mm).",
         "wire solder pad", smd=False)
pth(fp, 1, 0, 0, 1.3, 0.7)
finish(fp, court=(-0.75, -0.75, 0.75, 0.75))
fp = new("WIRE_SMD_0.9x1.1",
         "Solder pad for one flying wire (30 AWG) laid flat: SMD pad 0.9 x 1.1 mm, no paste. Size: ours (3 times the 0.25 mm conductor width).",
         "wire solder pad smd")
smd(fp, 1, 0, 0, 0.9, 1.1, rr=0.2, paste=False)
finish(fp, court=(-0.55, -0.7, 0.55, 0.7))
fp = new("NTC_wired",
         "Two plated holes dia 0.70 mm (pads dia 1.30 mm, 2.0 mm apart) for the two leads of the cell-face thermistor TH1 (Semitec 103AT-2 recommended in case_bq25895.pdf p.5 Table 6-1 pin TS). "
         "Pad 1 and 2 are the two leads (no polarity).", "ntc thermistor wired", smd=False)
pth(fp, 1, -1.0, 0, 1.3, 0.7)
pth(fp, 2, 1.0, 0, 1.3, 0.7)
finish(fp, court=(-1.75, -0.75, 1.75, 0.75))
fp = new("CELL_LEADS",
         "Off-board part: the DNK852338 cell (40.0 x 23.0 x 8.5 mm, case_cell_dnk852338.pdf p.1 'Mechanical Data') lies under PCB1; its two flying leads (terminal code FL, lead length CL 100 mm "
         "as supplied, cut to 40 mm) end in the pads of W5 (+, red lead) and W6 (-, black lead). Drawn on F.Fab only, no pads, excluded from the position file.",
         "cell battery virtual")
fp.SetAttributes(pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)
rect(fp, pcbnew.F_Fab, -11.5, -20.0, 11.5, 20.0, 0.1)
fp.Reference().SetPosition(VECTOR2I(0, 0))
io.FootprintSave(LIB, fp)

# ---------------------------------------------------------------- test pad and touch electrode
fp = new("TESTPAD_1.0", "Round test pad dia 1.0 mm, bare copper with a mask opening, no paste (size from case-bom.csv lines 60 to 75: 'copper pad on PCB1, 1.0 dia').", "test pad")
smd(fp, 1, 0, 0, 1.0, 1.0, shape="circle", paste=False)
finish(fp, court=(-0.65, -0.65, 0.65, 0.65))
fp = new("TOUCH_E1_front",
         "Touch electrode E1, front part: copper rectangle 3.9 x 1.15 mm on the front face of the pin board inner island (case-bom.csv line 24: copper electrode, area 6 x 3 mm = 18 mm2, "
         "built here as this front part plus a back copper pour of the same net with vias). Mask open or covered: covered (no paste).", "touch electrode copper")
smd(fp, 1, 0, 0, 3.9, 1.15, rr=0.05, shape="rect", paste=False)
finish(fp, court=(-1.95, -0.575, 1.95, 0.575))

print("footprints written:", sorted(f for f in os.listdir(LIB)))
print("count", len([f for f in os.listdir(LIB) if f.endswith('.kicad_mod')]))
