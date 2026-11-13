#!/usr/bin/env python3
"""Writes the footprint library OpenRing.pretty (one .kicad_mod per distinct package of parts.csv) and
footprint-sources.csv (one row per part reference).  Plain python 3, no KiCad needed.
usage:  design/.venv/bin/python -I make_footprints.py

Frame of every footprint: millimetres, +x right, +y DOWN (KiCad), seen from the top of the board (X-ray through the
part), origin at the centre of the body or of the pad group.  Every number below is copied from the page named in the
footprint's description (the maker document is in design/datasheets); the measured ones come from
w1-evidence/u1-measured-pads.csv (measure_u1.py).  Nothing is written to the silkscreen layers: the board has no
silkscreen (pcb/board-notes.md); the reference and the pin-1 mark are on F.Fab.
"""
import csv, os, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
RING = os.path.dirname(HERE)
DESIGN = os.path.dirname(os.path.dirname(RING))
LIB = os.path.join(HERE, 'OpenRing.pretty')
os.makedirs(LIB, exist_ok=True)
VERSION = '20260206'                    # file format of KiCad 10.0.8 (copied from its own library files)

FOOTPRINTS = {}                          # name -> dict(descr, tags, pads, body, crt, extra, meta)


def f(v):
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


class Pad:
    def __init__(self, num, x, y, w, h=None, shape='rect', poly=None, layers='top', rratio=0.25, drill=None):
        self.num, self.x, self.y, self.w, self.h = str(num), x, y, w, (w if h is None else h)
        self.shape, self.poly, self.layers, self.rratio, self.drill = shape, poly, layers, rratio, drill

    def text(self):
        lay = '"F.Cu" "F.Mask" "F.Paste"' if self.layers == 'top' else '"F.Cu" "F.Mask"'
        if self.shape == 'poly':
            pts = ' '.join('(xy %s %s)' % (f(px - self.x), f(py - self.y)) for px, py in self.poly)
            return ('\t(pad "%s" smd custom\n\t\t(at %s %s)\n\t\t(size 0.05 0.05)\n\t\t(layers %s)\n'
                    '\t\t(options\n\t\t\t(clearance outline)\n\t\t\t(anchor circle)\n\t\t)\n'
                    '\t\t(primitives\n\t\t\t(gr_poly\n\t\t\t\t(pts %s)\n\t\t\t\t(width 0)\n\t\t\t\t(fill yes)\n\t\t\t)\n\t\t)\n\t)\n'
                    % (self.num, f(self.x), f(self.y), lay, pts))
        s = '\t(pad "%s" smd %s\n\t\t(at %s %s)\n\t\t(size %s %s)\n\t\t(layers %s)\n' % (
            self.num, self.shape, f(self.x), f(self.y), f(self.w), f(self.h), lay)
        if self.shape == 'roundrect':
            s += '\t\t(roundrect_rratio %s)\n' % f(self.rratio)
        return s + '\t)\n'


def define(name, descr, tags, pads, body, margin=0.1, pin1=None, extra_fab=None, crt=None, port=None):
    """body = (w, h) centred at the origin, or (x0, y0, x1, y1).  crt overrides the courtyard (x0,y0,x1,y1)."""
    if len(body) == 2:
        bx0, by0, bx1, by1 = -body[0] / 2, -body[1] / 2, body[0] / 2, body[1] / 2
    else:
        bx0, by0, bx1, by1 = body
    xs = [bx0, bx1]; ys = [by0, by1]
    for p in pads:
        if p.shape == 'poly':
            xs += [q[0] for q in p.poly]; ys += [q[1] for q in p.poly]
        else:
            xs += [p.x - p.w / 2, p.x + p.w / 2]; ys += [p.y - p.h / 2, p.y + p.h / 2]
    cx0, cy0, cx1, cy1 = crt if crt else (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)
    FOOTPRINTS[name] = dict(descr=descr, tags=tags, pads=pads, body=(bx0, by0, bx1, by1), crt=(cx0, cy0, cx1, cy1),
                            pin1=pin1, extra=extra_fab or [])
    return name


def write_all():
    for name, d in FOOTPRINTS.items():
        bx0, by0, bx1, by1 = d['body']; cx0, cy0, cx1, cy1 = d['crt']
        t = ['(footprint "%s"\n\t(version %s)\n\t(generator "openring_make_footprints")\n\t(generator_version "1")\n\t(layer "F.Cu")\n'
             % (name, VERSION)]
        t.append('\t(descr "%s")\n\t(tags "%s")\n' % (d['descr'].replace('"', "'"), d['tags']))
        font = '(effects\n\t\t\t(font\n\t\t\t\t(size 0.5 0.5)\n\t\t\t\t(thickness 0.08)\n\t\t\t)\n\t\t)'
        t.append('\t(property "Reference" "REF**"\n\t\t(at 0 %s 0)\n\t\t(layer "F.Fab")\n\t\t%s\n\t)\n' % (f(cy0 - 0.4), font))
        t.append('\t(property "Value" "%s"\n\t\t(at 0 %s 0)\n\t\t(layer "F.Fab")\n\t\t%s\n\t)\n' % (name, f(cy1 + 0.4), font))
        t.append('\t(attr smd)\n')
        t.append('\t(fp_rect\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.05)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.CrtYd")\n\t)\n'
                 % (f(cx0), f(cy0), f(cx1), f(cy1)))
        t.append('\t(fp_rect\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.08)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.Fab")\n\t)\n'
                 % (f(bx0), f(by0), f(bx1), f(by1)))
        if d['pin1']:
            px, py = d['pin1']
            t.append('\t(fp_circle\n\t\t(center %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.06)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.Fab")\n\t)\n'
                     % (f(px), f(py), f(px + 0.08), f(py)))
        for (kind, a) in d['extra']:
            if kind == 'circle':
                t.append('\t(fp_circle\n\t\t(center %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.06)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "F.Fab")\n\t)\n'
                         % (f(a[0]), f(a[1]), f(a[0] + a[2] / 2), f(a[1])))
            elif kind == 'line':
                t.append('\t(fp_line\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.06)\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "F.Fab")\n\t)\n'
                         % tuple(f(v) for v in a))
        for p in d['pads']:
            t.append(p.text())
        t.append(')\n')
        with open(os.path.join(LIB, name + '.kicad_mod'), 'w') as fh:
            fh.write(''.join(t))


# =====================================================================================================================
# 1. U1  nRF54LM20A-CAAA, WLCSP-61, balls A1..H10 as Nordic's reference schematic
rows_ = list(csv.DictReader(open(os.path.join(HERE, 'w1-evidence', 'u1-measured-pads.csv'))))
define('WLCSP-61_nRF54LM20A-CAAA',
       'Nordic nRF54LM20A-CAAA WLCSP-61, body 3.020 x 2.430. Land centres measured from Nordic nRF54LM20x-CAAA reference layout rev 0.2 '
       '(nrf54lm20x_caaa_ref_pcb_0_2.pdf p1 pads, 0.2 mm round, pitch 0.325; p11 and p12 body outline 3.020 x 2.430); ball names from '
       'nrf54lm20x_caaa_ref_schematic_0_2.pdf p1; top view, A1 top left. 59 balls on the 0.325 grid (rows A B D E F G H, columns 1 2 4 to 10), '
       'C1 (ANT) and D3 (VSS) off the grid. Nordic package drawing (HTML only, behind a bot check) not obtained: ball height and tolerance not read',
       'WLCSP nordic nRF54LM20A CAAA 0.325mm',
       [Pad(r['ball'], float(r['x_mm']), float(r['y_mm']), 0.2, shape='circle') for r in rows_],
       (3.02, 2.43), margin=0.1, pin1=(-1.302, -0.978))

# 2. U2  nPM1304-CAAA, CSP-35, 7 x 5, pitch 0.419 (x) and 0.44 (y)
pads = []
for ri, row in enumerate('ABCDE'):
    for ci in range(1, 8):
        pads.append(Pad('%s%d' % (row, ci), (ci - 4) * 0.419, (ri - 2) * 0.44, 0.225, shape='circle'))
define('WLCSP-35_nPM1304-CAAA',
       'Nordic nPM1304-CAAA CSP-35, body D 3.0775 x E 2.3775 (npm1304_datasheet_v1_0.pdf p155 Figure 55 and Table 35): 7 x 5 balls, pitch d 0.419 along the 7 columns, '
       'e 0.44 along the 5 rows, ball b 0.225 nominal (0.195 to 0.255); balls A1..E7 as p153 Table 33 and p152 Figure 53 top view (A1 top left). '
       'The document gives no land drawing: land diameter = nominal ball b',
       'CSP nordic nPM1304 35 balls',
       pads, (3.0775, 2.3775), margin=0.1, pin1=(-1.257, -0.88))

# 3. U4  SGM38046 WLCSP-2x2-16B, 4 x 4, pitch 0.5, land dia 0.25 to 0.27
pads = []
for ri, row in enumerate('ABCD'):
    for ci in range(1, 5):
        pads.append(Pad('%s%d' % (row, ci), (ci - 2.5) * 0.5, (ri - 1.5) * 0.5, 0.26, shape='circle'))
define('WLCSP-16_SGM38046_2.0x2.0_P0.5',
       'SG Micro SGM38046 WLCSP-2x2-16B, body 2.005 x 2.005, 4 x 4 balls pitch 0.5, recommended land 16 x dia 0.25 to 0.27 (0.26 nominal) '
       '(p3_sgm38046.pdf PDF p18 package outline and recommended land pattern; pin names PDF p3); A1 top left of the top view',
       'WLCSP sgmicro SGM38046 16 balls 0.5mm',
       pads, (2.005, 2.005), margin=0.1, pin1=(-0.75, -0.75))

# 4. U3  CS Semiconductor CSNP32GCR01-BOW, LGA-8 8.0 x 6.2 (pads from the package drawing, pin numbers from the pin table)
pads = []
ys = [-1.905, -0.635, 0.635, 1.905]
for i, y in enumerate(ys):                       # pins 1 to 4 down the left column
    pads.append(Pad(i + 1, -3.5, y, 0.8, 0.7))
for i, y in enumerate(reversed(ys)):             # pins 5 to 8 up the right column, 5 at the bottom
    pads.append(Pad(5 + i, 3.5, y, 0.8, 0.7))
pads.append(Pad('9', 0.0, 2.6, 0.7, 0.8))        # drawn on the package drawing, no pin in the pin table
define('LGA-9_CSNP32GCR01-BOW_8.0x6.2',
       'CS Semiconductor CSNP32GCR01-BOW LGA-8, body D 8.0 x E 6.2 (slim2_cs-sdnand-20230403.pdf PDF p5 (printed p2) package drawing, table PDF p6 (printed p3): pad L 0.8 x b 0.7, '
       'pitch B 1.27, column centres C 7.00 apart, bottom pad N 2.6 below the centre); pin numbers 1 to 8 as the pin table on PDF p5 (1 SDD2 to 4 VSS down the left, '
       '5 CMD up to 8 VCC on the right). Pad 9 (bottom centre) is on the drawing but has no pin in the table: unconnected land',
       'LGA sdnand CS 8 pads',
       pads, (8.0, 6.2), margin=0.1, pin1=(-3.0, -2.6))

# 5. U5, U6  Knowles SPK0641HT4H-1, 4.00 x 3.00 x 1.00, 8 pads
kn = [(1, -0.425, 0.675, 0.45, 0.95), (2, -0.425, -0.675, 0.45, 0.95), (3, 0.425, -0.675, 0.45, 0.95), (4, 0.425, 0.675, 0.45, 0.95),
      (5, 0.0, 1.7125, 1.3, 0.325), (6, -1.2125, 0.0, 0.325, 2.3), (7, 0.0, -1.7125, 1.3, 0.325), (8, 1.2125, 0.0, 0.325, 2.3)]
define('LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0',
       'Knowles SPK0641HT4H-1 top-port microphone, body W 3.00 x L 4.00 x 1.00 (Datasheet SPK0641HT4H-1 Rev A, p6, in design/mech/mic-path/datasheets/'
       'knowles-spk0641ht4h-1_chipsmall.pdf, PDF p7 = printed p6). Example land pattern of the same page: '
       'overall 2.750 x 3.750, tall pads 2 x 2.300 x 0.325, wide pads 2 x 1.300 x 0.325, inner pads 4 x 0.450 x 0.950, gaps 0.400; pin table: 1 DATA, 2 CLOCK, '
       '3 SELECT, 4 Vdd, 5 to 8 GROUND. Land view = top view (mirror of the maker bottom view). Port dia 0.25 at 1.500 from the left edge and 1.030 from the top edge. '
       'The 8 corner chamfers 0.1 x 45 of the example are not drawn',
       'LGA knowles microphone SiSonic 8 pads',
       [Pad(n, x, y, w, h) for (n, x, y, w, h) in kn], (3.0, 4.0), margin=0.1, pin1=(-1.2, 1.5),
       extra_fab=[('circle', (0.0, -0.97, 0.25))])

# 6. U9  TI TPD4E05U06DQA, USON-10, pitch 0.5
pads = []
for i, y in enumerate([-1.0, -0.5, 0.0, 0.5, 1.0]):
    pads.append(Pad(i + 1, -0.4175, y, 0.565, 0.4 if i == 2 else 0.2))
for i, y in enumerate([1.0, 0.5, 0.0, -0.5, -1.0]):
    pads.append(Pad(6 + i, 0.4175, y, 0.565, 0.4 if i == 2 else 0.2))
define('USON-10_TPD4E05U06DQA',
       'TI TPD4E05U06DQA USON-10 (DQA0010A), body 1.0 x 2.5 x 0.55 (codes_tpd4e05u06.pdf PDF p28 package outline 0.9 to 1.1 x 2.4 to 2.6; PDF p29 example board layout: '
       '10 x 0.565 long pads, 8 x 0.2 wide, pins 3 and 8 0.4 wide, pitch 0.5, column centres 0.835 apart); pins 1 to 5 down the left, 6 to 10 up the right (TI numbering, pin 1 top left)',
       'USON TI 10 pads 0.5mm',
       pads, (1.0, 2.5), margin=0.1, pin1=(-0.3, -1.1))

# 7. U10  TI SN74AXC4T774RSV, UQFN-16, pitch 0.4
pads = [Pad(1, -0.75, -0.6, 0.7, 0.2)]
for i, y in enumerate([-0.2, 0.2, 0.6]):
    pads.append(Pad(2 + i, -0.8, y, 0.6, 0.2))
for i, x in enumerate([-0.6, -0.2, 0.2, 0.6]):
    pads.append(Pad(5 + i, x, 1.2, 0.2, 0.6))
for i, y in enumerate([0.6, 0.2, -0.2, -0.6]):
    pads.append(Pad(9 + i, 0.8, y, 0.6, 0.2))
for i, x in enumerate([0.6, 0.2, -0.2, -0.6]):
    pads.append(Pad(13 + i, x, -1.2, 0.2, 0.6))
define('UQFN-16_SN74AXC4T774RSV_1.8x2.6',
       'TI SN74AXC4T774RSV UQFN-16 (RSV0016A), body 1.8 x 2.6 x 0.55 (w1_ti_sn74axc4t774.pdf p40 package outline, p41 example board layout: 15 pads 0.6 x 0.2, '
       'pad 1 0.7 x 0.2, pitch 0.4, column centres 1.6 apart, row centres 2.4 apart); pins 1 to 4 down the left, 5 to 8 along the bottom, 9 to 12 up the right, '
       '13 to 16 along the top (pin 1 top left of the left column)',
       'UQFN TI 16 pads 0.4mm',
       pads, (1.8, 2.6), margin=0.1, pin1=(-0.55, -0.95))

# 8. U11  TI TLV75530PDQNR, X2SON-4 with a 45 degree thermal pad
r2 = 0.48 * math.sqrt(2) / 2
define('X2SON-4_TLV755xxPDQN_1.0x1.0',
       'TI TLV75530PDQN X2SON-4 (DQN0004A), body 1.0 x 1.0 x 0.4 (motor_tlv755p.pdf PDF p41 package outline 0.95 to 1.05; PDF p42 example board layout: pads 0.36 x 0.21, '
       'pad centres 0.86 apart across and 0.65 apart down, thermal pad a 0.48 square turned 45 degrees). Pins 1 top left, 2 bottom left, 3 bottom right, 4 top right; '
       'pad 5 is the thermal pad (the land drawing numbers it 5). The inner corner cuts of the four small pads are not drawn: the cut size is not dimensioned on the page',
       'X2SON TI 4 pads thermal pad',
       [Pad(1, -0.43, -0.325, 0.36, 0.21), Pad(2, -0.43, 0.325, 0.36, 0.21), Pad(3, 0.43, 0.325, 0.36, 0.21), Pad(4, 0.43, -0.325, 0.36, 0.21),
        Pad(5, 0.0, 0.0, 0.05, 0.05, shape='poly', poly=[(0, -r2), (r2, 0), (0, r2), (-r2, 0)])],
       (1.0, 1.0), margin=0.1, pin1=(-0.3, -0.3))

# 9. ANT1  Johanson 2450AT18D0100001E
define('ANT_Johanson_2450AT18D0100001E_3.2x1.6',
       'Johanson 2450AT18D0100001E chip antenna EIA 1206, body L 3.20 x W 1.60 x T 1.20 (antenna_johanson_2450AT18D0100001E.pdf PDF p2: terminals b 0.50 x a 0.30 at the four '
       'corners, pin 1 FEED, pins 2 to 4 GND); lands 1.0 x 0.6 at 2.0 gap and 0.7 gap (evaluation board mounting p3); top view, pin 1 top left, pin 2 top right (along the length), '
       'pin 4 bottom left. The p3 ground clearance (4.0 wide, 6.0 long) is a board rule, not drawn here',
       'antenna 2.4GHz 1206 johanson',
       [Pad(1, -1.5, -0.65, 1.0, 0.6), Pad(2, 1.5, -0.65, 1.0, 0.6), Pad(3, 1.5, 0.65, 1.0, 0.6), Pad(4, -1.5, 0.65, 1.0, 0.6)],
       (3.2, 1.6), margin=0.1, pin1=(-1.1, -0.45))

# 10. X1  Kyocera CX2016DB
define('XTAL_Kyocera_CX2016DB_2.0x1.6',
       'Kyocera CX2016DB crystal 2.00 x 1.60 x 0.40 (w1_kyocera_cx2016db_catalog_page10.pdf p1 (page 9 of the 77-page Kyocera crystal units catalogue cry_e.pdf): dimensions, recommended land pattern four 0.9 x 0.8 pads, '
       'centres 1.4 across and 1.1 down; connection (top view): crystal on #1 and #3, #2 marked GND, #4 not connected). Top view: #4 top left, #3 top right, #1 bottom left, #2 bottom right',
       'crystal 32MHz kyocera 2016',
       [Pad(1, -0.7, 0.55, 0.9, 0.8), Pad(2, 0.7, 0.55, 0.9, 0.8), Pad(3, 0.7, -0.55, 0.9, 0.8), Pad(4, -0.7, -0.55, 0.9, 0.8)],
       (2.0, 1.6), margin=0.1, pin1=(-0.6, 0.45))

# 11. Chip passives: pad sizes measured on Nordic's reference layout (nrf54lm20x_caaa_ref_pcb_0_2.pdf p1) for the same parts
CHIP_SRC = ('Land sizes measured on the Nordic nRF54LM20x-CAAA reference layout (nrf54lm20x_caaa_ref_pcb_0_2.pdf p1, 12:1) for %s of the same parts list. ')
define('Chip_0201',
       'Chip 0201 (0.6 x 0.3) for C, R, L, ferrite. ' + CHIP_SRC % 'C1, C2, C5, C7, FB1, R2, L2 to L4' + 'Pads 0.27 along x 0.30 across, centres 0.57 apart',
       'chip 0201',
       [Pad(1, -0.285, 0, 0.27, 0.30), Pad(2, 0.285, 0, 0.27, 0.30)], (0.6, 0.3), margin=0.1)
define('Chip_0402',
       'Chip 0402 (1.0 x 0.5) for C and R. ' + CHIP_SRC % 'C4 (10 uF)' + 'Pads 0.425 along x 0.50 across, centres 0.92 apart',
       'chip 0402',
       [Pad(1, -0.46, 0, 0.425, 0.50), Pad(2, 0.46, 0, 0.425, 0.50)], (1.0, 0.5), margin=0.1)
define('Chip_0603',
       'Chip 0603 (1.6 x 0.8) for C, R, L. ' + CHIP_SRC % 'R1 (2.2 R)' + 'Pads 0.80 along x 0.85 across, centres 1.4 apart',
       'chip 0603',
       [Pad(1, -0.7, 0, 0.80, 0.85), Pad(2, 0.7, 0, 0.80, 0.85)], (1.6, 0.8), margin=0.1)

# 12. J1  Hirose FH35C-15S-0.3SHW(50): recommended land dimensions (catalogue p4, drawing CL580-2919-0-50 p1)
J1 = []
for k in range(1, 16):
    x = 2.1 - 0.3 * (k - 1)                    # pin 1 at +2.1 (right), pin 15 at -2.1, 0.3 apart
    if k % 2 == 1:
        J1.append(Pad(k, x, 1.4, 0.3, 0.8))      # odd pins: row of 8 pads, 0.8 long, bottom row
    else:
        J1.append(Pad(k, x, -1.475, 0.3, 0.65))  # even pins: row of 7 pads, 0.65 long, top row
J1.append(Pad('MP', -2.8, 1.125, 0.4, 0.95))
J1.append(Pad('MP', 2.8, 1.125, 0.4, 0.95))
define('FPC_Hirose_FH35C-15S-0.3SHW',
       'Hirose FH35C-15S-0.3SHW(50) FPC connector, 15 contacts 0.3 pitch in two staggered rows (w1_hirose_fh35c_series_catalog.pdf p3 dimensions A 6.1, B 3.6, C 4.2, '
       'p4 recommended land: pads 0.3 wide, 7 pads 0.65 long at 0.6 pitch (even pins) and 8 pads 0.8 long at 0.6 pitch (odd pins), rows 3.6 apart outer edge to outer edge, '
       'two metal-fitting pads 0.4 x 0.95 each 0.5 from the end pad centre; w1_hirose_fh35c-15s-0.3shw50_drawing.pdf p1: pin 1 is the right end of the odd row, pin 2 the right end of the even row, '
       'numbering goes left with 0.3 steps). Courtyard (W2, design/wiring/ring-board-plan.md f.4 and h.1): the closed housing, A 6.1 along the contact row (catalogue p3) by depth (3.35) '
       '(catalogue p3 top view, lever closed; the (4.2) of the p3 detail drawing is the lever standing open, only while the tail is plugged in before assembly), '
       'centred on the land pattern, and widened in depth to the outer land edges, B 3.6 (catalogue p4), because the land rows reach 0.125 beyond the 3.35 housing on each side: 6.1 x 3.6. Pads MP are the two mounting pads (no signal)',
       'connector FPC hirose 0.3mm 15 pin',
       J1, (6.1, 3.35), margin=0.1, crt=(-3.05, -1.8, 3.05, 1.8), pin1=(2.1, 0.5))

# 14. X2  TXC 9HT11-32.768KDZC-T (2 pads); land measured on Nordic's reference layout
define('XTAL_TXC_9HT11_2.0x1.2',
       'TXC 9HT11-32.768KDZC-T 32.768 kHz crystal, 2 pads, 2.0 x 1.2 x 0.6 (w1_txc_9ht11_datasheet.pdf p1, T11 series: "2 pads surface mount package"). Land measured on the Nordic nRF54LM20x-CAAA reference layout (nrf54lm20x_caaa_ref_pcb_0_2.pdf p1, X2: two pads 1.4 x 0.75, '
       'centres 1.45 apart; BOM nrf54lm20x_caaa BOM row X2 names this part and the footprint XTAL_2012). The one-page TXC sheet has no drawing, so the pad numbers are not printed: '
       'the two terminals of a crystal are interchangeable: pad 1 = X1 net, pad 2 = X2 net',
       'crystal 32.768kHz TXC 2012',
       [Pad(1, 0.0, -0.725, 1.4, 0.75), Pad(2, 0.0, 0.725, 1.4, 0.75)], (1.2, 2.0), margin=0.1, pin1=(0.0, -0.55))

# 15. L1  TDK MLZ1608 land as Nordic draws it for L1 MLZ1608M4R7WT000
define('L_TDK_MLZ1608_1.6x0.8',
       'TDK MLZ1608 inductor 1.6 x 0.8 (parts list L1 MLZ1608M4R7WT000, also L71 and L72 if chosen from the same series). Land measured on the Nordic nRF54LM20x-CAAA reference layout '
       '(nrf54lm20x_caaa_ref_pcb_0_2.pdf p1, L1: pads 0.75 along x 0.80 across, centres 1.35 apart; BOM names this exact part for L1)',
       'inductor 0603 1608 TDK',
       [Pad(1, -0.675, 0, 0.75, 0.80), Pad(2, 0.675, 0, 0.75, 0.80)], (1.6, 0.8), margin=0.1)

# 16. DISP1  mating contacts on the tail of the Tailor Pixels TOH095XVT-01
D1 = [Pad(k, 2.1 - 0.3 * (k - 1), 0.0, 0.15, 3.2) for k in range(1, 16)]
define('FPCtail_Tailor_TOH095XVT-01_15',
       'Contacts of the flexible tail of the Tailor Pixels TOH095XVT-01 screen module (display_TOH095XVT-01.pdf PDF p5: tail 4.8 wide, contact block 3.2 long, 15 contacts numbered 15 to 1 '
       'left to right seen from the contact side, so pin 1 at the right; pin table of the same page: 1 ELVSS, 2 ELVDD, 3 MTP, 4 VCC, 5 IOVCC, 6 SWIRE, 7 TE, 8 RESET, 9 CS, 10 SCL, 11 RS, 12 SDA, 13 to 15 GND). '
       'Pitch 0.3 (4.8 tail = Hirose FH35C-15 recommended FPC width F 4.8, w1_hirose_fh35c_series_catalog.pdf p5) and pad width 0.15 (half the pitch) are not printed on the Tailor page. '
       'Seen from the contact side. Not a board part: the module is not placed on the ring board',
       'FPC tail screen contacts',
       D1, (4.8, 3.2), margin=0.1, pin1=(2.1, -1.3))

# 17. L10  Murata 1269AS-H-2R2M=P2 (2.5 x 2.0 x 1.0)
define('L_Murata_1269AS-H_2.5x2.0',
       'Murata 1269AS-H-2R2M=P2 inductor (parts L10, L71, L72), body 2.5 x 2.0 x 1.0 max (w1b_murata_1269as-h-2r2m.pdf p1) and its recommended PCB pattern (p5): overall length 2.8, gap between pads 1.2, pad length across 2.0, so two pads 0.8 x 2.0 with centres 2.0 apart. '
       'Spec No. J(E)TE243A-0004A-01 lists this code on p2',
       'inductor 2520 murata',
       [Pad(1, -1.0, 0, 0.8, 2.0), Pad(2, 1.0, 0, 0.8, 2.0)], (2.5, 2.0), margin=0.1)

# ---- band parts (SW1 to SW5, M1, RT1, CP1 to CP4, BT1/PRT1, J_BAND_A, J_BAND_B) are drawn by band-circuits in ecad/band/OpenRingBand.pretty (lead, 2026-11-13)
define('TESTPAD_0.8',
       'Test pad 0.8 mm round, bare copper, no part (our own size, kept from the first draft: parts.csv footprint name TESTPAD_0.8; 22 pads TP1 to TP22 from the list TPS in make_netlist.py; see pcb/footprint-notes.md)',
       'test pad 0.8mm',
       [Pad(1, 0.0, 0.0, 0.8, shape='circle')], (0.8, 0.8), margin=0.05)


# =====================================================================================================================
# footprint-sources.csv : one row per part reference
# name -> (package, maker document file, page, pitch, pin-to-net map source, land source, document obtained)
NR_PCB = 'nrf54lm20x_caaa_ref_pcb_0_2.pdf'
SRC = {
 'WLCSP-61_nRF54LM20A-CAAA': ('WLCSP-61 (CAAA)', NR_PCB, 'p1 pads; p11 and p12 body outline (schematic names: nrf54lm20x_caaa_ref_schematic_0_2.pdf p1)', '0.325',
    'parts/nrf54lm20a-csp61-pins.csv (Nordic reference schematic p1) read by make_netlist.py SYM nRF54LM20A_CAAA; mapping checked 61 of 61 by measure_u1.py',
    'maker reference layout (measured)', 'Nordic package drawing not obtained (HTML behind a bot check); reference layout and schematic read'),
 'WLCSP-35_nPM1304-CAAA': ('CSP-35 (CAAA)', 'npm1304_datasheet_v1_0.pdf', 'p155 Figure 55 and Table 35; p152 Figure 53; p153 Table 33', '0.419 x 0.44',
    'ecad/ring/npm1304-balls.csv (Table 33 p153) read by make_netlist.py SYM nPM1304_CSP35', 'maker package drawing (no land drawing: land = nominal ball)', 'yes'),
 'WLCSP-16_SGM38046_2.0x2.0_P0.5': ('WLCSP-2x2-16B', 'p3_sgm38046.pdf', 'p18 (package outline and recommended land pattern); p3 (pins)', '0.5',
    'make_netlist.py SYM SGM38046 (p3 pin description)', 'maker recommended land pattern', 'yes'),
 'LGA-9_CSNP32GCR01-BOW_8.0x6.2': ('LGA-8 8.0 x 6.2 (9 pads drawn)', 'slim2_cs-sdnand-20230403.pdf', 'PDF p5-6 (printed p2-3)', '1.27 (side pads)',
    'make_netlist.py SYM CSNP32GCR01_BOW (pin table PDF p5); pad 9 has no pin in the table', 'maker package drawing (pads)', 'yes'),
 'LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0': ('LGA-8 4.0 x 3.0', 'design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf; second copy design/datasheets/w1b_knowles_spk0641ht4h-1_chipdip.pdf', 'PDF p7 (printed p6)', 'n/a (8 pads, gaps 0.4)',
    'make_netlist.py SYM SPK0641HT4H_1 (pin table PDF p7)', 'maker example land pattern', 'Knowles Datasheet Rev A: Chipsmall copy (on disk) and ChipDip copy https://static.chipdip.ru/lib/185/DOC011185940.pdf; the Knowles site returned no sheet'),
 'USON-10_TPD4E05U06DQA': ('USON-10 (DQA0010A)', 'codes_tpd4e05u06.pdf', 'PDF p28 outline, p29 example board layout', '0.5',
    'make_netlist.py SYM TPD4E05U06 (TI Table 4-2)', 'maker example board layout', 'yes'),
 'UQFN-16_SN74AXC4T774RSV_1.8x2.6': ('UQFN-16 (RSV0016A)', 'w1_ti_sn74axc4t774.pdf', 'PDF p40 outline, p41 example board layout', '0.4',
    'make_netlist.py SYM SN74AXC4T774_RSV (TI Table 4-1 RSV column, p3)', 'maker example board layout', 'yes'),
 'X2SON-4_TLV755xxPDQN_1.0x1.0': ('X2SON-4 (DQN0004A)', 'motor_tlv755p.pdf', 'PDF p41 outline, p42 example board layout', 'n/a (rows 0.65, columns 0.86)',
    'make_netlist.py SYM TLV75530P_DQN (TI Table 4-1 DQN column; pad 5 = thermal pad as the land drawing)', 'maker example board layout', 'yes'),
 'ANT_Johanson_2450AT18D0100001E_3.2x1.6': ('EIA 1206 chip antenna', 'antenna_johanson_2450AT18D0100001E.pdf', 'PDF p2 (terminals), p3 (mounting lands)', 'n/a (4 corner lands)',
    'make_netlist.py SYM 2450AT18D0100 (terminal table PDF p2)', 'maker evaluation-board lands', 'yes'),
 'XTAL_Kyocera_CX2016DB_2.0x1.6': ('2016 crystal, 4 pads', 'w1_kyocera_cx2016db_catalog_page10.pdf', 'p1', 'n/a (centres 1.4 x 1.1)',
    'make_netlist.py SYM XTAL_CX2016DB (connection diagram: crystal on 1 and 3, 2 GND, 4 not connected)', 'maker recommended land pattern', 'yes'),
 'XTAL_TXC_9HT11_2.0x1.2': ('2012 crystal, 2 pads', NR_PCB + ' and w1_txc_9ht11_datasheet.pdf', 'p1 (pads of X2); TXC p1 (2 pads, 2.0 x 1.2 x 0.6)', 'n/a (centres 1.45)',
    'make_netlist.py SYM XTAL_2PAD (two interchangeable terminals)', 'maker reference layout (measured)', 'TXC T11 sheet read (1 page: 2 pads, size, no drawing, no pad numbers)'),
 'Chip_0201': ('chip 0201', NR_PCB, 'p1 (C1, C2, C5, C7, FB1, R2, L2 to L4)', 'n/a (centres 0.57)', 'make_netlist.py SYM C, R, L, FB: pins 1 and 2', 'maker reference layout (measured)', 'yes (Nordic layout); passive maker sheets not obtained'),
 'Chip_0402': ('chip 0402', NR_PCB, 'p1 (C4)', 'n/a (centres 0.92)', 'make_netlist.py SYM C, R, NTC: pins 1 and 2', 'maker reference layout (measured)', 'yes (Nordic layout); passive maker sheets not obtained'),
 'Chip_0603': ('chip 0603', NR_PCB, 'p1 (R1)', 'n/a (centres 1.4)', 'make_netlist.py SYM C, R, L: pins 1 and 2', 'maker reference layout (measured)', 'yes (Nordic layout); passive maker sheets not obtained'),
 'L_TDK_MLZ1608_1.6x0.8': ('inductor 1608 (0603)', NR_PCB, 'p1 (L1)', 'n/a (centres 1.35)', 'make_netlist.py SYM L: pins 1 and 2', 'maker reference layout (measured)', 'yes (Nordic layout); TDK sheet not obtained'),
 'L_Murata_1269AS-H_2.5x2.0': ('inductor 2520', 'w1b_murata_1269as-h-2r2m.pdf', 'p1 (body), p5 (recommended PCB pattern), p2 (code)', 'n/a (centres 2.0)', 'make_netlist.py SYM L: pins 1 and 2', 'maker recommended land pattern', 'Murata spec J(E)TE243A-0004A-01 copy from cdn.eicom.ru (distributor host, Murata-printed)'),
 'FPC_Hirose_FH35C-15S-0.3SHW': ('FPC connector 15 contacts', 'w1_hirose_fh35c_series_catalog.pdf', 'p3 dimensions, p4 recommended land; w1_hirose_fh35c-15s-0.3shw50_drawing.pdf p1 (numbering)', '0.3 (0.6 per row)',
    'make_netlist.py SYM FPC_15: pins 1 to 15 in the order of the screen tail; MP = two mounting pads', 'maker recommended land pattern', 'yes'),
 'FPCtail_Tailor_TOH095XVT-01_15': ('screen tail contacts', 'display_TOH095XVT-01.pdf', 'PDF p5', '0.3 (derived, not printed)',
    'make_netlist.py SYM TOH095XVT-01 (table on PDF p5: 3 MTP, 4 VCC)', 'DERIVED pitch and width (tail 4.8 wide and Hirose F 4.8); contact block 3.2 long as printed', 'yes (pad width and pitch are not printed)'),
 'TESTPAD_0.8': ('test pad 0.8', 'pcb/footprint-notes.md', 'point a', 'n/a', 'make_netlist.py SYM TESTPAD: one pad', 'our own size', 'not applicable (our own)'),
}


def write_sources():
    parts = list(csv.DictReader(open(os.path.join(RING, 'parts.csv'))))
    used = set()
    out = os.path.join(HERE, 'footprint-sources.csv')
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['reference', 'package', 'footprint', 'maker_document_file', 'page', 'pad_count', 'pitch', 'pin_to_net_map_source', 'land_source', 'document_obtained'])
        for p in parts:
            lib, name = p['footprint'].split(':', 1)
            if lib == 'OpenRingBand':
                bf = os.path.join(DESIGN, 'ecad', 'band', 'OpenRingBand.pretty', name + '.kicad_mod')
                cnt = len(re.findall(r'\(pad "', open(bf).read())) if os.path.exists(bf) else ''
                w.writerow([p['reference'], 'band part (drawn by band-circuits)', name, 'design/ecad/band/band-interface.md', 'band-circuits sections for this part',
                            cnt, 'see band-interface.md', 'netlist pin names kept as before W1 (band_layout.py maps them to pads)',
                            'band-circuits library design/ecad/band/OpenRingBand.pretty/' + name + '.kicad_mod', 'not mine (band-circuits)'])
                continue
            if name not in FOOTPRINTS:
                raise SystemExit('parts.csv footprint %s of %s is not in the library' % (p['footprint'], p['reference']))
            if name not in SRC:
                raise SystemExit('no source row for %s' % name)
            used.add(name)
            package, doc, page, pitch, pinmap, land, got = SRC[name]
            w.writerow([p['reference'], package, name, doc, page, len(FOOTPRINTS[name]['pads']), pitch, pinmap, land, got])
    unused = sorted(set(FOOTPRINTS) - used)
    if unused:
        raise SystemExit('footprints in the library that no part uses: %s' % unused)
    print('footprint-sources.csv: %d rows, %d footprints used' % (len(parts), len(used)))

if __name__ == '__main__':
    write_all()
    write_sources()
    print('wrote', len(FOOTPRINTS), 'footprints to', LIB)
