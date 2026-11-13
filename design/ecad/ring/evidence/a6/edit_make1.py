import re
P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s = open(P).read()

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)

# (a) U2 symbol
rep("""# nPM1300: names from nRF54LM20 DK schematic PCA10184 v0.5.4 page 6 (U3 nPM1300-QEAA).
# Ball numbers of the CAAA (WLCSP-35) package are not readable: provisional P1..P32.""",
"""# A6 (architecture 17.13): U2 is the Nordic nPM1304, 35-ball CSP 3.1 x 2.4 mm (package code CA).
# The nPM1304 ball map is NOT read: Nordic states no pin or footprint compatibility with the nPM1300
# (parts/research-npm1304.md section 2). The pin NAMES below are those of the nPM1300 as drawn in the nRF54LM20 DK
# schematic PCA10184 v0.5.4 page 6 (U3 nPM1300-QEAA); they are an assumption for the nPM1304. Every ball number
# is provisional: P1..P33 are placeholders, not balls (open item S18).""")
rep("SYM['nPM1300_CAAA'] = ", "SYM['nPM1304_CSP35'] = ")

# SD level shifter symbol (after the CSNP symbol block)
rep("""# SGM38046 balls: datasheet p3_sgm38046.pdf p3 pin description""",
"""# A6 review F07: TI SN74AXC4T774, 4-bit dual-supply translator, RSV package (UQFN-16, 2.6 x 1.8 mm).
# Pin numbers: TI datasheet SCES898C Table 4-1 column RSV (saved: evidence/a6/ti_sn74axc4t774.txt).
SYM['SN74AXC4T774_RSV'] = [('1', 'A1', 'bidirectional'), ('2', 'A2', 'bidirectional'), ('3', 'A3', 'bidirectional'),
                           ('4', 'A4', 'bidirectional'), ('5', 'DIR3', 'input'), ('6', 'DIR4', 'input'),
                           ('7', 'OE', 'input'), ('8', 'GND', 'power_in'), ('9', 'B4', 'bidirectional'),
                           ('10', 'B3', 'bidirectional'), ('11', 'B2', 'bidirectional'), ('12', 'B1', 'bidirectional'),
                           ('13', 'VCCB', 'power_in'), ('14', 'VCCA', 'power_in'), ('15', 'DIR1', 'input'),
                           ('16', 'DIR2', 'input')]

# SGM38046 balls: datasheet p3_sgm38046.pdf p3 pin description""")

# band: split table
old_band = s[s.index("# band-side connection groups on the main board"):s.index("# ---------------------------------------------------------------- parts")]
new_band = '''# ---------------------------------------------------------------- band split (ONE TABLE: edit this to move a signal)
# The two flex tails leave the main board into the two shoulders of the band. Which tail carries which line is this
# table and nothing else: change a row's side ('A' or 'B') and run this script; the netlist, the parts list, the open-pins
# file and the pad counts follow, and check_netlist.py checks the result against the rules in its A6-9 block.
# Architecture 17.8 as replaced by 17.11 and 17.12 (A6):
#   side A = the joystick side: the four direction switches, the centre switch (SW2, BTN_REC) and, until the lead
#            confirms the inside model (sch-notes A6 changes, open point), the motor;
#   side B = the other side: cell tabs, temperature sensor and the four charging pads.
# columns: net on the main board, pad name on the tail, side
BAND_SPLIT = [
    ('JOY_UP', 'UP', 'A'),
    ('JOY_DOWN', 'DOWN', 'A'),
    ('JOY_LEFT', 'LEFT', 'A'),
    ('JOY_RIGHT', 'RIGHT', 'A'),
    ('BTN_REC', 'CENTRE', 'A'),
    ('MOTOR_DRV', 'MOT-', 'A'),
    ('VDD_3V0', 'MOT+', 'A'),
    ('GND', 'GND', 'A'),
    ('VBAT', 'CELL+', 'B'),
    ('GND', 'CELL-', 'B'),
    ('NTC', 'NTC', 'B'),
    ('VBUS', 'VBUS', 'B'),
    ('USB_DN', 'D-', 'B'),
    ('USB_DP', 'D+', 'B'),
    ('GND', 'GND', 'B'),
]
BAND_A = [n for n, _, sd in BAND_SPLIT if sd == 'A']
BAND_A_NAMES = [p for _, p, sd in BAND_SPLIT if sd == 'A']
BAND_B = [n for n, _, sd in BAND_SPLIT if sd == 'B']
BAND_B_NAMES = [p for _, p, sd in BAND_SPLIT if sd == 'B']
# pad numbers of the two tails are this schematic's own definition (order of the table), not a maker pin
SYM['BAND_PADS_A'] = [(str(i + 1), n, 'passive') for i, n in enumerate(BAND_A_NAMES)]
SYM['BAND_PADS_B'] = [(str(i + 1), n, 'passive') for i, n in enumerate(BAND_B_NAMES)]

'''
s = s.replace(old_band, new_band)
open(P, 'w').write(s)
print('ok')
