#!/usr/bin/env python3
"""Writes the source tables of the ring schematic: netlist.csv, parts.csv,
additions.csv, open-pins.csv. Every pin number and name below is copied from
the source named next to it; a pin number written P<n> is provisional and is
listed in open-pins.csv."""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- symbols
# symbol name -> list of (pin_number, pin_name, pin_type)
SYM = {}

# nRF54LM20A CAAA: ball names from parts/nrf54lm20a-csp61-pins.csv (Nordic CAAA reference schematic)
def _u1_type(name):
    if name == 'VDD': return 'power_in'
    if name == 'VSS': return 'power_in'
    if name in ('DCC', 'DECD', 'DECA', 'DECRF', 'TXRTUNE', 'XC1', 'XC2', 'ANT'): return 'passive'
    if name == 'DECUSB': return 'power_out'
    if name == 'VBUS': return 'power_in'
    if name in ('SWDCLK', 'nRESET'): return 'input'
    return 'bidirectional'
_balls = list(csv.DictReader(open(os.path.join(HERE, '../../parts/nrf54lm20a-csp61-pins.csv'))))
SYM['nRF54LM20A_CAAA'] = [(b['ball'], b['pin_name_as_printed'], _u1_type(b['pin_name_as_printed'])) for b in _balls]

# A7 (architecture 17.18): U2 is the Nordic nPM1304-CAAA, 35-ball CSP. Ball numbers and names are read from
# npm1304-balls.csv, the copy of Nordic's nPM1304 Product Specification v1.0 Table 33, page 153
# (design/datasheets/npm1304_datasheet_v1_0.pdf). VBUS (B1, B2), VSYS (C1, C2) and VBAT (D1, D2) have two balls each;
# the package has no GPIO4. Pin type per name below (schematic choice; the second VSYS ball is 'passive' so that the
# net VSYS has one power output for KiCad's ERC).
NPM_TYPE = {'VBUS': 'power_in', 'CC1': 'bidirectional', 'CC2': 'bidirectional', 'VBAT': 'power_in', 'NTC': 'passive',
            'GPIO0': 'bidirectional', 'GPIO1': 'bidirectional', 'GPIO2': 'bidirectional', 'GPIO3': 'bidirectional',
            'LED0': 'open_collector', 'LED1': 'open_collector', 'LED2': 'open_collector',
            'VSET1': 'passive', 'VSET2': 'passive', 'SHPHLD': 'input', 'SCL': 'input', 'SDA': 'bidirectional',
            'VDDIO': 'power_in', 'VBUSOUT': 'power_out', 'VSYS': 'power_out', 'PVDD': 'power_in',
            'VOUT1': 'power_out', 'SW1': 'passive', 'PVSS1': 'power_in', 'VOUT2': 'power_out', 'SW2': 'passive',
            'PVSS2': 'power_in', 'LSIN1/VINLDO1': 'power_in', 'LSIN2/VINLDO2': 'power_in',
            'LSOUT1/VOUTLDO1': 'power_out', 'LSOUT2/VOUTLDO2': 'power_out', 'AVSS': 'power_in'}
NPM_BALLS = list(csv.DictReader(open(os.path.join(HERE, 'npm1304-balls.csv'))))
SYM['nPM1304_CSP35'] = [(b['ball'], b['name'], 'passive' if b['ball'] == 'C2' else NPM_TYPE[b['name']]) for b in NPM_BALLS]

# CS Semiconductor CSNP32GCR01-BOW, LGA-8: pad numbers and names from the maker spec V1.0 p5 table 2.1
# (design/datasheets/slim2_cs-sdnand-20230403.pdf): 1 SDD2, 2 SDD3 (SPI CS), 3 SCLK, 4 VSS, 5 CMD (SPI DI),
# 6 SDD0 (SPI DO), 7 SDD1, 8 VCC. Names kept as the SD names of wiring decision W3.
SYM['CSNP32GCR01_BOW'] = [('1', 'DAT2', 'bidirectional'), ('2', 'DAT3', 'bidirectional'), ('3', 'CLK', 'input'),
                          ('4', 'VSS', 'power_in'), ('5', 'CMD', 'bidirectional'), ('6', 'DAT0', 'bidirectional'),
                          ('7', 'DAT1', 'bidirectional'), ('8', 'VCC', 'power_in')]

# A6 review F07: TI SN74AXC4T774, 4-bit dual-supply translator, RSV package (UQFN-16, 2.6 x 1.8 mm).
# Pin numbers: TI datasheet SCES898C Table 4-1 column RSV (saved: evidence/a6/ti_sn74axc4t774.txt).
SYM['SN74AXC4T774_RSV'] = [('1', 'A1', 'bidirectional'), ('2', 'A2', 'bidirectional'), ('3', 'A3', 'bidirectional'),
                           ('4', 'A4', 'bidirectional'), ('5', 'DIR3', 'input'), ('6', 'DIR4', 'input'),
                           ('7', 'OE', 'input'), ('8', 'GND', 'power_in'), ('9', 'B4', 'bidirectional'),
                           ('10', 'B3', 'bidirectional'), ('11', 'B2', 'bidirectional'), ('12', 'B1', 'bidirectional'),
                           ('13', 'VCCB', 'power_in'), ('14', 'VCCA', 'power_in'), ('15', 'DIR1', 'input'),
                           ('16', 'DIR2', 'input')]

# SGM38046 balls: datasheet p3_sgm38046.pdf p3 pin description
SYM['SGM38046'] = [
    ('A1', 'PVIN', 'power_in'), ('A2', 'AVIN', 'passive'), ('A3', 'AGND', 'power_in'),
    ('A4', 'C1P', 'passive'), ('B1', 'SW1', 'passive'), ('B2', 'PGND', 'power_in'),
    ('B3', 'CPGND', 'power_in'), ('B4', 'C1N', 'passive'), ('C1', 'SW2', 'passive'),
    ('C2', 'AVDDEN', 'input'), ('C3', 'SWIRE', 'input'), ('C4', 'VON', 'power_out'),
    ('D1', 'VOUT', 'power_out'), ('D2', 'AVDD', 'power_out'), ('D3', 'OVDD', 'power_out'),
    ('D4', 'OVSS', 'power_out')]

# A7 (architecture 17.19): Knowles SPK0641HT4H-1, top port, 4.00 x 3.00 x 1.00. Pin table from the datasheet copy
# design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf sheet 6 (text copy lines 351 to 359):
# 1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5 to 8 GROUND ("All Ground pins must be connected to ground", sheet 4).
SYM['SPK0641HT4H_1'] = [('1', 'DATA', 'output'), ('2', 'CLOCK', 'input'), ('3', 'SELECT', 'input'),
                        ('4', 'VDD', 'power_in'), ('5', 'GROUND', 'power_in'), ('6', 'GROUND', 'power_in'),
                        ('7', 'GROUND', 'power_in'), ('8', 'GROUND', 'power_in')]
# A7 (architecture 17.22): TI TLV75530PDQNR, X2SON-4 (DQN). Pin numbers: TI SBVS320D Table 4-1, DQN column
# (design/datasheets/motor_tlv755p.pdf p3; text copy design/ecad/motor-drive/src_tlv755p.txt): OUT 1, GND 2, EN 3,
# IN 4; the thermal pad has no number in TI's table ("internally connected to GND"): drawn as pin EP on GND.
SYM['TLV75530P_DQN'] = [('1', 'OUT', 'power_out'), ('2', 'GND', 'power_in'), ('3', 'EN', 'input'),
                        ('4', 'IN', 'power_in'), ('EP', 'PAD', 'passive')]

# Screen TOH095XVT-01, 15 contacts, names in the order printed in the table of parts/slim.md section 1.3
# (maker p6; the table prints pin 4 twice and no pin 3: position k here = k-th entry as printed)
DISP_PINS = [('ELVSS', 'power_in'), ('ELVDD', 'power_in'), ('MTP', 'passive'), ('VCI', 'power_in'),
             ('IOVCC', 'power_in'), ('SWIRE', 'output'), ('TE', 'output'), ('RESX', 'input'),
             ('CS', 'input'), ('SCL', 'input'), ('RS', 'input'), ('SDA', 'input'),
             ('GND', 'power_in'), ('GND', 'power_in'), ('GND', 'power_in')]
SYM['TOH095XVT-01'] = [(str(i + 1), n, t) for i, (n, t) in enumerate(DISP_PINS)]
# J1 board connector Hirose FH35C-15S-0.3SHW(50), 15 positions: position numbers provisional (drawing not read); names follow the tail
SYM['FPC_15'] = [('P%d' % (i + 1), n, 'passive') for i, (n, _) in enumerate(DISP_PINS)]

# TPD4E05U06 DQA: TI datasheet SLVSBO7O Table 4-2
SYM['TPD4E05U06'] = [('1', 'D1+', 'passive'), ('2', 'D1-', 'passive'), ('3', 'GND', 'power_in'),
                     ('4', 'D2+', 'passive'), ('5', 'D2-', 'passive'), ('6', 'NC', 'no_connect'),
                     ('7', 'NC', 'no_connect'), ('8', 'GND', 'power_in'), ('9', 'NC', 'no_connect'),
                     ('10', 'NC', 'no_connect')]
# Alps SKTAAAE010: 1 pole 1 throw tact switch (maker spec KTA-601 p1); the spec shows no terminal numbers
# (drawing not in the copy): two terminals P1, P2, provisional
SYM['SKTAAAE010'] = [('P1', '~', 'passive'), ('P2', '~', 'passive')]
# DMN2450UFB4: names from Diodes DS40239 p1 (D, S, G); pad numbers provisional
SYM['DMN2450UFB4'] = [('G', 'G', 'input'), ('S', 'S', 'passive'), ('D', 'D', 'passive')]
# A7 (architecture 17.21): Kingbright KPG-1005SURC-TT, pad 1 = cathode, pad 2 = anode (maker sheet p1 symbol,
# design/datasheets/light_kb_KPG-1005SURC-TT_rs-copy.pdf; light-path.md section 3 and 6)
SYM['LED_KPG1005'] = [('1', 'K', 'passive'), ('2', 'A', 'passive')]
# A7 (architecture 17.16): Jinlong W0525AB001D, two lead wires, red + and blue - (architecture 17.16 'Part', citing spec S-525113 rev 0 pages 2, 4, 6, 8,
# design/datasheets/slim2_jinlong-w0525ab001d.pdf); the maker gives colours, not numbers: P1, P2 are this schematic's
SYM['MOTOR'] = [('P1', '+', 'passive'), ('P2', '-', 'passive')]
# Cell: custom, tab order open (12.7)
SYM['CELL'] = [('P1', '+', 'power_out'), ('P2', '-', 'passive')]
# Johanson 2450AT18D0100: datasheet terminal configuration (pin 1 feed, 2-4 GND)
SYM['2450AT18D0100'] = [('1', 'FEED', 'passive'), ('2', 'GND', 'passive'), ('3', 'GND', 'passive'),
                        ('4', 'GND', 'passive')]
# crystals: crystal data sheets not on disk: provisional terminals
SYM['XTAL'] = [('P1', 'X1', 'passive'), ('P2', 'X2', 'passive')]
SYM['R'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['C'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['L'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['FB'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['NTC'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['TESTPAD'] = [('1', '1', 'passive')]
SYM['CONTACTPAD'] = [('1', '1', 'passive')]
SYM['CONTACTPAD_VBUS'] = [('1', '1', 'power_out')]
# ---------------------------------------------------------------- band split (ONE TABLE: edit this to move a signal)
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
    ('GND', 'MOT-', 'A'),        # A7 motor-drive.md W2: the motor's return is its own ground pad
    ('VMOT', 'MOT+', 'A'),       # A7 motor-drive.md W1: the motor is fed by U11 on net VMOT
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

# ---------------------------------------------------------------- parts
PARTS = []  # ref, symbol, value, mpn, footprint, sheet, dnp
CONN = {}   # ref -> {pin_name_or_number: net}

def part(ref, sym, value, mpn, fp, sheet, conn, dnp=False, by='name'):
    PARTS.append(dict(reference=ref, symbol=sym, value=value, mpn=mpn, footprint=fp, sheet=sheet,
                      dnp='yes' if dnp else 'no'))
    CONN[ref] = (by, conn)

def two(ref, sym, value, mpn, fp, sheet, n1, n2, dnp=False):
    part(ref, sym, value, mpn, fp, sheet, {'1': n1, '2': n2}, dnp, by='number')

M = 'main'; P = 'power'; A = 'mics'; S = 'storage'; D = 'screen'; K = 'controls'; T = 'contacts'; BD = 'band'

# ---- main chip and radio (Nordic CAAA reference, config 1)
u1 = {
    'A4': 'VDD_1V8', 'E10': 'VDD_1V8', 'A7': 'GND', 'D3': 'GND', 'E1': 'GND', 'F10': 'GND',
    'A5': 'DCC', 'A6': 'DECD', 'A8': 'DECA', 'B2': 'DECA', 'H8': 'VDD_USB_3V3', 'H9': 'U1_VBUS',
    'A2': 'XC1', 'A1': 'XC2', 'G6': 'TXRTUNE', 'C1': 'ANT1_NODE', 'H6': 'USB_DN', 'H7': 'USB_DP',
    'D5': 'SWDCLK', 'E4': 'SWDIO', 'E2': 'NRESET',
    'F1': 'MIC_A_CLK', 'F2': 'MIC_A_DATA', 'E6': 'MIC_B_CLK', 'D7': 'MIC_B_DATA',
    'B6': 'XL1', 'B7': 'XL2',
    'A9': 'SD_SCK', 'B10': 'SD_MOSI', 'D10': 'SD_MISO', 'D9': 'SD_CS',
    'G9': 'LCD_SCK', 'G8': 'LCD_MOSI', 'F7': 'LCD_CS', 'G7': 'LCD_DCX', 'H5': 'LCD_RST', 'D6': 'LCD_TE',
    'B8': 'PMIC_SDA', 'E7': 'PMIC_SCL', 'D8': 'PMIC_INT', 'E9': 'OLED_PWR_EN',
    'H2': 'BTN_REC', 'H4': 'JOY_CENTER', 'H1': 'JOY_UP', 'G2': 'JOY_DOWN', 'G1': 'JOY_LEFT', 'G10': 'JOY_RIGHT',
    'F6': 'MOTOR', 'B4': 'DBG_TX', 'B5': 'DBG_RX',
    'H10': 'SPARE_P1_00', 'E8': 'SPARE_P1_01', 'F8': 'SPARE_P1_02', 'F4': 'SPARE_P1_14', 'E5': 'SPARE_P1_19',
    'F9': 'SPARE_P1_30', 'A10': 'SPARE_P2_00', 'B9': 'SPARE_P2_03', 'F5': 'SPARE_P3_03', 'G5': 'SPARE_P3_04',
    'G4': 'SPARE_P3_05',
}
part('U1', 'nRF54LM20A_CAAA', 'nRF54LM20A', 'NRF54LM20A-CAAA-R7', 'ring:WLCSP-61_CAAA', M, u1, by='number')
two('C4', 'C', '10uF', '', 'ring:C_0402', M, 'VDD_1V8', 'GND')
two('C5', 'C', '100nF', '', 'ring:C_0201', M, 'VDD_1V8', 'GND')
two('C1', 'C', '100nF', '', 'ring:C_0201', M, 'VDD_1V8', 'GND')
two('C2', 'C', '100nF', '', 'ring:C_0201', M, 'VDD_1V8', 'GND')
two('L1', 'L', '4.7uH', 'MLZ1608M4R7WT000', 'ring:L_0603', M, 'DCC', 'DECD')
two('C6', 'C', '4.7uF', 'GRM035R60J475ME15J', 'ring:C_0201', M, 'DECD', 'GND')
two('FB1', 'FB', '120R@100MHz', 'BLM03AG121SN1D', 'ring:L_0201', M, 'DECD', 'DECA')
two('C7', 'C', '2.2uF', 'GRM033D80E225ME47D', 'ring:C_0201', M, 'DECA', 'GND')
two('C14', 'C', '2.2uF', 'GRM033D80E225ME47D', 'ring:C_0201', M, 'DECA', 'GND')
two('C10', 'C', '2.2uF', 'GRM033D80E225ME47D', 'ring:C_0201', M, 'VDD_USB_3V3', 'GND')
two('R1', 'R', '2.2R', '', 'ring:R_0603', M, 'VBUS', 'U1_VBUS')
two('C11', 'C', '4.7uF', 'GRM155R61A475MEAAD', 'ring:C_0402', M, 'U1_VBUS', 'GND')
two('R2', 'R', '220R', '', 'ring:R_0201', M, 'TXRTUNE', 'GND')
part('X1', 'XTAL', '32MHz', 'CX2016DB32000D0WZRC1', 'ring:XTAL_2016', M, {'X1': 'XC1', 'X2': 'XC2'})
part('X2', 'XTAL', '32.768kHz', '9HT11-32.768KDZC-T', 'ring:XTAL_2012', M, {'X1': 'XL1', 'X2': 'XL2'})
two('L2', 'L', '3.6nH', 'LQP03HQ3N6B02', 'ring:L_0201', M, 'ANT1_NODE', 'ANT2_NODE')
two('C3', 'C', '1.2pF', 'GJM0335C1H1R2WB01D', 'ring:C_0201', M, 'ANT2_NODE', 'GND')
two('L3', 'L', '4.7nH', 'LQP03HQ4N7H02', 'ring:L_0201', M, 'ANT2_NODE', 'ANT3_NODE')
two('C12', 'C', '0.5pF', 'GJM0335C1ER50WB01D', 'ring:C_0201', M, 'ANT3_NODE', 'GND')
two('L4', 'L', '3.3nH', 'LQP03HQ3N3B02', 'ring:L_0201', M, 'ANT3_NODE', 'RF_FEED')
two('C13', 'C', 'DNP', '', 'ring:C_0201', M, 'RF_FEED', 'GND', dnp=True)
part('ANT1', '2450AT18D0100', '2450AT18D0100001E', '2450AT18D0100001E', 'ring:ANT_1206_Johanson', M,
     {'1': 'RF_FEED', '2': 'GND', '3': 'GND', '4': 'GND'}, by='number')

# ---- power (A6: nPM1304, architecture 17.13; the passives are the nPM1300 DK PCA10184 page 6 ones: the nPM1304 page
# that would confirm each is not in parts/research-npm1304.md, so every one is 'to confirm against the nPM1304
# product specification' (S18))
npm_net = {'VBUS': 'VBUS', 'CC1': None, 'CC2': None, 'VBAT': 'VBAT', 'NTC': 'NTC',
           'GPIO0': 'PMIC_INT', 'GPIO1': None, 'GPIO2': None, 'GPIO3': None,
           'LED0': None, 'LED1': None, 'LED2': None, 'VSET1': 'VSET1', 'VSET2': 'VSET2',
           'SHPHLD': 'SHPHLD', 'SCL': 'PMIC_SCL', 'SDA': 'PMIC_SDA', 'VDDIO': 'VDD_1V8',
           'VBUSOUT': 'VBUSOUT', 'VSYS': 'VSYS', 'PVDD': 'VSYS', 'VOUT1': 'VDD_1V8', 'SW1': 'SW1',
           'PVSS1': 'GND', 'VOUT2': 'VDD_3V0', 'SW2': 'SW2', 'PVSS2': 'GND',
           'LSIN1/VINLDO1': 'VDD_1V8', 'LSIN2/VINLDO2': 'VDD_3V0',
           'LSOUT1/VOUTLDO1': 'VDD_MIC', 'LSOUT2/VOUTLDO2': 'VDD_SD', 'AVSS': 'GND'}
npm = {b['ball']: npm_net[b['name']] for b in NPM_BALLS}  # every ball by its number (Table 33, p153)
# order code nPM1304-CAAA-R7: Nordic spec Table 50, page 168 (architecture 17.18)
part('U2', 'nPM1304_CSP35', 'nPM1304', 'nPM1304-CAAA-R7', 'ring:WLCSP-35_nPM1304', P, npm, by='number')
# A7 D1 (npm1304-reference.md): VBUS capacitor 1.0 uF X5R 25 V as Nordic C1 (spec Table 37, page 157)
two('C71', 'C', '1.0uF 25V', '', 'ring:C_0402', P, 'VBUS', 'GND')
# A7 D2: 2.2 uF X5R 10 V at the VBAT balls D1, D2 as Nordic C6 (Table 37, page 157); C21 serves U4, not U2
two('C85', 'C', '2.2uF', '', 'ring:C_0402', P, 'VBAT', 'GND')
# A7 D3: third 10 uF on VSYS/PVDD as Nordic C2, C3, C4 (Table 37, page 157; X5R 16 V)
two('C88', 'C', '10uF', '', 'ring:C_0402', P, 'VSYS', 'GND')
# A7 D4: load switch mode outputs: Nordic configuration 2 (one LOADSW in load switch mode) puts C14 1.0 uF on LSOUT1
# (spec Figure 59 page 158, Table 38 page 159: X5R 10 V); chapter 6.4 itself gives no capacitor rule (tSS is
# specified with 10 uF, Table 20 page 69). Applied to both outputs: C86 at ball A4 (VDD_MIC), C87 at ball A5 (VDD_SD)
two('C86', 'C', '1.0uF', '', 'ring:C_0201', P, 'VDD_MIC', 'GND')
two('C87', 'C', '1.0uF', '', 'ring:C_0201', P, 'VDD_SD', 'GND')
two('C72', 'C', '100nF', '', 'ring:C_0201', P, 'VBUS', 'GND')
two('C73', 'C', '1.0uF', '', 'ring:C_0201', P, 'VBUSOUT', 'GND')
two('C74', 'C', '10uF', '', 'ring:C_0402', P, 'VSYS', 'GND')
two('C75', 'C', '10uF', '', 'ring:C_0402', P, 'VSYS', 'GND')
two('C76', 'C', '1.0nF', '', 'ring:C_0201', P, 'VSYS', 'GND')
two('C77', 'C', '1.0nF', '', 'ring:C_0201', P, 'VSYS', 'GND')
two('L71', 'L', '2.2uH', 'OPEN 12.2', 'ring:L_0806', P, 'SW1', 'VDD_1V8')
two('C78', 'C', '10uF', '', 'ring:C_0402', P, 'VDD_1V8', 'GND')
two('L72', 'L', '2.2uH', 'OPEN 12.2', 'ring:L_0806', P, 'SW2', 'VDD_3V0')
two('C79', 'C', '10uF', '', 'ring:C_0402', P, 'VDD_3V0', 'GND')
two('C80', 'C', '100nF', '', 'ring:C_0201', P, 'VDD_1V8', 'GND')
two('R71', 'R', '47k', '', 'ring:R_0201', P, 'VSET1', 'GND')
two('R72', 'R', '150k', '', 'ring:R_0201', P, 'VSET2', 'GND')
two('RT1', 'NTC', '10k NTC', 'OPEN 12.2', 'ring:R_0402', BD, 'NTC', 'GND')  # in the band at the cell (A5 17.3)
part('BT1', 'CELL', '4.35V 20-27mAh at US9 (17.6mAh min at US7) curved', 'Grepow custom', 'ring:CELL_TABS', BD, {'+': 'VBAT', '-': 'GND'})  # A7: architecture 17.15 and 17.17 (was 15-20 mAh of 17.10); cell sweep 2026-11-11: smallest 17.6 mAh per 17.26 (before it 18.2 mAh)
two('R57', 'R', '4.7k', '', 'ring:R_0201', P, 'PMIC_SDA', 'VDD_1V8')
two('R58', 'R', '4.7k', '', 'ring:R_0201', P, 'PMIC_SCL', 'VDD_1V8')

# ---- microphones (W4, A5 16.4 and 16.6: two microphones, one stereo input on the A pins)
mics = [('U5', 'MIC_A_CLK', 'MIC1_DATA', 'MIC_A_DATA', 'GND', 'R31', 'C31', 'C35'),
        ('U6', 'MIC_A_CLK', 'MIC2_DATA', 'MIC_A_DATA', 'VDD_MIC', 'R32', 'C32', 'C36')]
for u, clk, dl, bus, lr, r, c1, c2 in mics:
    # A7 (17.19, mic-path.md section 9 items 26 to 29): SPK0641HT4H-1, nets unchanged, all four GROUND pins on GND
    part(u, 'SPK0641HT4H_1', 'SPK0641HT4H-1', 'SPK0641HT4H-1', 'ring:Knowles_SPK0641HT4H_LGA8_4.0x3.0', A,
         {'1': dl, '2': clk, '3': lr, '4': 'VDD_MIC', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND'}, by='number')
    two(r, 'R', '100R', '', 'ring:R_0201', A, dl, bus)
    two(c1, 'C', '1uF', '', 'ring:C_0201', A, 'VDD_MIC', 'GND')
    # Knowles sheet 4 (Figure 4 and notes): 0.1 uF next to each Vdd pin, no Class 2 dielectric near the microphone
    two(c2, 'C', '100nF Class 1', '', 'ring:C_0201', A, 'VDD_MIC', 'GND')

# ---- storage (W3) and its level shifter (A6, review F07)
# U1 balls A9, B10, D10, D9 are on VDD (1.8 V): the chip has one supply for every I/O (balls A4 and E10, no separate I/O
# supply ball) and the storage part runs from 2.7 to 3.6 V with VIH min 0.625 x VCC = 1.875 V at 3.0 V (maker spec
# slim2_cs-sdnand-20230403.pdf p5 and p6). The four lines therefore pass U10, TI SN74AXC4T774RSVR: A side (SD_*) on
# VDD_1V8, B side (SDC_*, card side) on VDD_SD. DIR1 to DIR3 high = A to B (SCK, MOSI, CS); DIR4 low = B to A (MISO).
# OE low = enabled; with VDD_SD below 100 mV all ports are Hi-Z (datasheet "VCC isolation"). The pull-ups of W3 stay
# on the card side, on VDD_SD.
part('U3', 'CSNP32GCR01_BOW', 'CSNP32GCR01-BOW', 'CSNP32GCR01-BOW', 'ring:LGA-8_6.2x8', S,
     {'CLK': 'SDC_SCK', 'CMD': 'SDC_MOSI', 'DAT0': 'SDC_MISO', 'DAT1': 'SD_DAT1', 'DAT2': 'SD_DAT2',
      'DAT3': 'SDC_CS', 'VCC': 'VDD_SD', 'VSS': 'GND'})
part('U10', 'SN74AXC4T774_RSV', 'SN74AXC4T774', 'SN74AXC4T774RSVR', 'ring:UQFN-16_RSV_2.6x1.8', S,
     {'1': 'SD_SCK', '2': 'SD_MOSI', '3': 'SD_CS', '4': 'SD_MISO', '5': 'VDD_1V8', '6': 'GND', '7': 'GND',
      '8': 'GND', '9': 'SDC_MISO', '10': 'SDC_CS', '11': 'SDC_MOSI', '12': 'SDC_SCK', '13': 'VDD_SD',
      '14': 'VDD_1V8', '15': 'VDD_1V8', '16': 'VDD_1V8'}, by='number')
two('C81', 'C', '100nF', '', 'ring:C_0201', S, 'VDD_1V8', 'GND')
two('C82', 'C', '100nF', '', 'ring:C_0201', S, 'VDD_SD', 'GND')
two('R60', 'R', '47k', '', 'ring:R_0201', S, 'SDC_MISO', 'VDD_SD')
two('R63', 'R', '47k', '', 'ring:R_0201', S, 'SD_DAT1', 'VDD_SD')
two('R64', 'R', '47k', '', 'ring:R_0201', S, 'SD_DAT2', 'VDD_SD')
two('R65', 'R', '47k', '', 'ring:R_0201', S, 'SDC_CS', 'VDD_SD')
two('C60', 'C', '4.7uF', '', 'ring:C_0402', S, 'VDD_SD', 'GND')
two('C61', 'C', '100nF', '', 'ring:C_0201', S, 'VDD_SD', 'GND')

# ---- screen and its supply (W9, W10; SGM38046 typical application)
part('U4', 'SGM38046', 'SGM38046', 'SGM38046YG/TR', 'ring:WLCSP-2x2-16B', D,
     {'PVIN': 'VBAT', 'AVIN': 'SGM_AVIN', 'AGND': 'GND', 'C1P': 'SGM_C1P', 'SW1': 'SGM_SW1',
      'PGND': 'GND', 'CPGND': 'GND', 'C1N': 'SGM_C1N', 'SW2': 'SGM_SW2', 'AVDDEN': 'OLED_PWR_EN',
      'SWIRE': 'SWIRE', 'VON': 'SGM_VON', 'VOUT': 'SGM_VOUT', 'AVDD': 'SGM_AVDD', 'OVDD': 'ELVDD',
      'OVSS': 'ELVSS'})
two('L10', 'L', '2.2uH', '1269AS-H-2R2M=P2', 'ring:L_2520', D, 'SGM_SW1', 'SGM_SW2')
two('C21', 'C', '4.7uF', 'GRM188R61C475KAAJD', 'ring:C_0603', D, 'VBAT', 'GND')
two('C22', 'C', '10uF', 'GRM155R60J106ME15', 'ring:C_0402', D, 'SGM_AVIN', 'GND')
two('C23', 'C', '2.2uF', 'GRM155R60J225ME15', 'ring:C_0402', D, 'SGM_C1P', 'SGM_C1N')
two('C24', 'C', '10uF', 'GRM188R61C106KAALD', 'ring:C_0603', D, 'SGM_VOUT', 'GND')
two('C25', 'C', '10uF', 'GRM188R61C106KAALD', 'ring:C_0603', D, 'ELVDD', 'GND')
two('C26', 'C', '4.7uF', 'GRM188R61C475KAAJD', 'ring:C_0603', D, 'SGM_AVDD', 'GND')
two('C27', 'C', '4.7uF', 'GRM188R61C475KAAJD', 'ring:C_0603', D, 'SGM_VON', 'GND')
two('C28', 'C', '22uF', 'GRM155R60J226ME11D', 'ring:C_0402', D, 'ELVSS', 'GND')
two('C29', 'C', '22uF', 'GRM155R60J226ME11D', 'ring:C_0402', D, 'ELVSS', 'GND')
two('R66', 'R', '100k', '', 'ring:R_0201', D, 'OLED_PWR_EN', 'GND')
scr = ['ELVSS', 'ELVDD', None, 'VDD_3V0', 'VDD_1V8', 'SWIRE', 'LCD_TE', 'LCD_RST', 'LCD_CS',
       'LCD_SCK', 'LCD_DCX', 'LCD_MOSI', 'GND', 'GND', 'GND']
part('J1', 'FPC_15', 'FH35C-15S-0.3SHW(50)', 'FH35C-15S-0.3SHW(50)', 'ring:Hirose_FH35C-15S-0.3SHW', D,
     {'P%d' % (i + 1): n for i, n in enumerate(scr)}, by='number')
part('DISP1', 'TOH095XVT-01', 'TOH095XVT-01', 'TOH095XVT-01', 'ring:NONE_module_tail', D,
     {str(i + 1): n for i, n in enumerate(scr)}, by='number')

# ---- controls, motor, recording light (W1, W5, W6)
# A6 17.11: the five switches and the motor are in the band, reached through the two flex tails J_BAND_A and
# J_BAND_B (sheet "band"; which tail carries which line: BAND_SPLIT at the top); each switch is one SKTAAAE010
# between its line and ground. SW1 UP, SW3 DOWN, SW4 LEFT, SW5 RIGHT; SW2 (BTN_REC) is the switch under the centre of
# the joystick nub (no record button, no record cap).
part('J_BAND_A', 'BAND_PADS_A', 'flex tail A (joystick side) %d pads' % len(BAND_A), '', 'ring:FLEX_PADS_1x%d' % len(BAND_A), BD,
     {str(i + 1): n for i, n in enumerate(BAND_A)}, by='number')
part('J_BAND_B', 'BAND_PADS_B', 'flex tail B (other side) %d pads' % len(BAND_B), '', 'ring:FLEX_PADS_1x%d' % len(BAND_B), BD,
     {str(i + 1): n for i, n in enumerate(BAND_B)}, by='number')
for sw, line in (('SW1', 'JOY_UP'), ('SW2', 'BTN_REC'), ('SW3', 'JOY_DOWN'), ('SW4', 'JOY_LEFT'), ('SW5', 'JOY_RIGHT')):
    part(sw, 'SKTAAAE010', 'SKTAAAE010', 'SKTAAAE010', 'ring:Alps_SKTA', BD, {'P1': line, 'P2': 'GND'}, by='number')
# A7 (architecture 17.16, 17.22; motor-drive.md 2.1, W3 to W8): M1 W0525AB001D on VMOT and GND; U11 TLV75530PDQNR
# from VBAT, EN from MOTOR through R61 with R62 to ground; C83 at IN, C84 at OUT; Q1 and D1 removed
part('M1', 'MOTOR', 'W0525AB001D', 'W0525AB001D', 'ring:WIRE_LEADS_2', BD,
     {'+': 'VMOT', '-': 'GND'})
part('U11', 'TLV75530P_DQN', 'TLV75530P 3.0V', 'TLV75530PDQNR', 'ring:X2SON-4_DQN_1x1', K,
     {'1': 'VMOT', '2': 'GND', '3': 'MOT_EN', '4': 'VBAT', 'EP': 'GND'}, by='number')
two('C83', 'C', '10uF', 'GRM155R60J106ME15', 'ring:C_0402', K, 'VBAT', 'GND')
two('C84', 'C', '10uF', 'GRM155R60J106ME15', 'ring:C_0402', K, 'VMOT', 'GND')
two('R61', 'R', '100R', '', 'ring:R_0201', K, 'MOTOR', 'MOT_EN')
two('R62', 'R', '100k', '', 'ring:R_0201', K, 'MOT_EN', 'GND')
two('R41', 'R', '820R', '', 'ring:R_0201', K, 'VDD_3V0', 'LED_A')  # A7 architecture 17.21, light-path.md 6: 820 ohm
part('LED1', 'LED_KPG1005', 'red 631nm', 'KPG-1005SURC-TT', 'ring:LED_0402', K,
     {'A': 'LED_A', 'K': 'LED_K'})  # pin numbers: 1 = K (cathode), 2 = A (anode), maker p1
part('Q2', 'DMN2450UFB4', 'DMN2450UFB4', 'DMN2450UFB4-7B', 'ring:X2-DFN1006-3', K,
     {'G': 'VDD_MIC', 'S': 'GND', 'D': 'LED_K'})

# ---- charging pads, USB protection and test pads (W7, W12)
# pads from -Y to +Y: VBUS, D-, D+, GND (case design, lead 2026-11-10); on the INSIDE face of the band, in the resin liner
# (architecture 17.12), they touch the skin; they reach the board by the tail the BAND_SPLIT table gives them
for cp, net in (('CP1', 'VBUS'), ('CP2', 'USB_DN'), ('CP3', 'USB_DP'), ('CP4', 'GND')):
    part(cp, 'CONTACTPAD_VBUS' if net == 'VBUS' else 'CONTACTPAD', 'gold pad 1.0mm', '', 'ring:PAD_1.0',
         BD, {'1': net}, by='number')
part('U9', 'TPD4E05U06', 'TPD4E05U06', 'TPD4E05U06DQAR', 'ring:USON-10_DQA', T,
     {'1': 'USB_DP', '2': 'USB_DN', '3': 'GND', '4': 'VBUS', '5': 'VBUS', '6': None, '7': None,
      '8': 'GND', '9': None, '10': None}, by='number')
TPS = ['DBG_TX', 'DBG_RX', 'SWDCLK', 'SWDIO', 'NRESET', 'SPARE_P1_00', 'SPARE_P1_01', 'SPARE_P1_02',
       'SPARE_P1_14', 'SPARE_P1_19', 'SPARE_P1_30', 'SPARE_P2_00', 'SPARE_P2_03', 'SPARE_P3_03',
       'SPARE_P3_04', 'SPARE_P3_05', 'VDD_1V8', 'GND', 'SHPHLD', 'MIC_B_CLK', 'MIC_B_DATA', 'JOY_CENTER']
for i, n in enumerate(TPS):
    part('TP%d' % (i + 1), 'TESTPAD', 'pad', '', 'ring:TESTPAD_0.8', T, {'1': n}, by='number')

# ---------------------------------------------------------------- additions
ADD = [
    ('U9', 'W7 USB protection array TPD4E05U06 (parts/order-codes.md section 3 first choice; TI SLVSBO7O)'),
    ('CP1', 'charging pad VBUS, first from -Y, inside face of the band (architecture 17.12; order from the case design)'), ('CP2', 'case contact pad D-, second from -Y'),
    ('CP3', 'case contact pad D+, third from -Y'), ('CP4', 'case contact pad GND, fourth from -Y'),
    ('R61', 'motor regulator enable series resistor 100 ohm (motor-drive.md)'), ('R62', 'motor regulator enable pull-down 100 kohm (motor-drive.md)'),
    ('U11', 'motor 3.0 V regulator from VBAT, TLV75530PDQNR (motor-drive.md)'), ('C83', 'U11 input 10 uF'),
    ('C84', 'U11 output and motor 10 uF (Jinlong 9-4 asks 2 uF or more)'),
    ('C85', 'A7 D2: U2 VBAT 2.2 uF at balls D1, D2 (nPM1304 spec Table 37 C6, page 157)'),
    ('C86', 'A7 D4: U2 LSOUT1 (VDD_MIC) 1.0 uF at ball A4 (nPM1304 spec configuration 2, C14, pages 158 and 159)'),
    ('C87', 'A7 D4: U2 LSOUT2 (VDD_SD) 1.0 uF at ball A5 (nPM1304 spec configuration 2, C14, pages 158 and 159)'),
    ('C88', 'A7 D3: U2 VSYS/PVDD third 10 uF (nPM1304 spec Table 37 C2 to C4, page 157)'),
    ('R63', 'W3 pull-up DAT1 47 kohm'), ('R64', 'W3 pull-up DAT2 47 kohm'), ('R65', 'W3 pull-up DAT3/CS 47 kohm'),
    ('C61', 'W3 100 nF at storage supply'), ('R66', 'W10 AVDDEN pull-down 100 kohm'),
    ('C71', 'A7 D1: U2 VBUS 1.0 uF X5R 25 V (nPM1304 spec Table 37 C1, page 157)'), ('C72', 'U2 VBUS 100 nF (nPM1300 DK C37; confirm for the nPM1304, S18)'),
    ('C73', 'U2 VBUSOUT 1.0 uF (nPM1300 DK C39; confirm for the nPM1304, S18)'), ('C74', 'U2 VSYS 10 uF (nPM1300 DK C40; confirm for the nPM1304, S18)'),
    ('C75', 'U2 VSYS 10 uF (nPM1300 DK C41; confirm for the nPM1304, S18)'), ('C76', 'U2 VSYS 1.0 nF (nPM1300 DK C42; confirm for the nPM1304, S18)'),
    ('C77', 'U2 VSYS 1.0 nF (nPM1300 DK C43; confirm for the nPM1304, S18)'), ('L71', 'U2 buck 1 inductor 2.2 uH (nPM1300 DK L7; confirm for the nPM1304, S18)'),
    ('C78', 'U2 VOUT1 10 uF (nPM1300 DK C46; confirm for the nPM1304, S18)'), ('L72', 'U2 buck 2 inductor 2.2 uH (nPM1300 DK L6; confirm for the nPM1304, S18)'),
    ('C79', 'U2 VOUT2 10 uF (nPM1300 DK C48; confirm for the nPM1304, S18)'), ('C80', 'U2 VDDIO 100 nF (nPM1300 DK C54; confirm for the nPM1304, S18)'),
    ('RT1', 'NTC thermistor 10 kohm in the band at the cell (lead 2026-11-10); part code OPEN'),
    ('TP16', 'W12 test pad for the 11th spare pin P3.05 (bom.csv counts 10 spares, section 7 lists 11)'),
    ('TP17', 'W12 test pad VDD_1V8'), ('TP18', 'W12 test pad GND'),
    ('TP19', 'test pad on the power chip SHPHLD (factory wake from ship mode)'),
    ('J_BAND_A', 'A6 flex tail A (joystick side, BAND_SPLIT): 4 direction switches, centre switch, motor 2, ground = %d pads on the main board' % len(BAND_A)),
    ('J_BAND_B', 'A6 flex tail B (other side, BAND_SPLIT): cell 2, temperature 1, charging pads 4 = %d pads on the main board' % len(BAND_B)),
    ('U10', 'A6 review F07: level shifter SN74AXC4T774RSVR between the 1.8 V main chip and the 3.0 V storage part (TI SCES898C)'),
    ('C81', 'A6 U10 VCCA 100 nF (TI SCES898C section 8, 0.1 uF)'), ('C82', 'A6 U10 VCCB 100 nF (TI SCES898C section 8, 0.1 uF)'),
    ('SW3', 'A5 16.4 joystick switch DOWN (SKTAAAE010)'), ('SW4', 'A5 16.4 joystick switch LEFT (toward hand)'),
    ('SW5', 'A5 16.4 joystick switch RIGHT (toward fingertip)'),
]
# bom.csv designators intentionally not placed, with the decision that removes them
NOT_PLACED = [('R51', 'W1: no pull-ups on the board (lead, 2026-11-10)'), ('R52', 'W1'), ('R53', 'W1'),
              ('R54', 'W1'), ('R55', 'W1'), ('R56', 'W1'),
              ('CBL1', 'joystick cable removed: switches reach the board through flex tail J_BAND_A (A5 17.3)'),
              ('U7', 'A5 16.4: 2 microphones in place of 4'), ('U8', 'A5 16.4'), ('R33', 'A5 16.4 (decoupling of the removed pair)'), ('R34', 'A5 16.4'),
              ('C33', 'A5 16.4'), ('C34', 'A5 16.4'), ('C37', 'A5 16.4'), ('C38', 'A5 16.4'),
              ('W1', 'A5 17.3: contact board removed, the 4 charging pads reach the board through J_BAND_B'), ('W2', 'A5 17.3'), ('W3', 'A5 17.3'), ('W4', 'A5 17.3'),
              ('NPM-REF', 'placeholder line, split into C71-C80, L71, L72, RT1 (additions)'),
              ('Q1', 'A7 architecture 17.22, motor-drive.md W5: motor switch removed (the motor runs from U11)'),
              ('D1', 'A7 architecture 17.22, motor-drive.md W4: motor diode removed')]
# parts whose order code is empty on purpose (never invented): reference -> why
OPEN_ORDER_CODE = {
    'C71': ('A7 D1: 1.0 uF X5R 25 V 10 % (nPM1304 spec Table 37, page 157); no maker sheet of such a part is on file', 'a distributor or the electronics designer: a 1.0 uF 25 V X5R part in 0402 or 0603 with its maker sheet'),
    'C85': ('A7 D2: 2.2 uF X5R 10 V (nPM1304 spec Table 37, page 157); no maker sheet on file', 'a distributor or the electronics designer: the part code with its maker sheet'),
    'C86': ('A7 D4: 1.0 uF X5R 10 V (nPM1304 spec Table 38, page 159); no maker sheet of a 10 V part on file', 'a distributor or the electronics designer: the part code with its maker sheet'),
    'C87': ('A7 D4: 1.0 uF X5R 10 V (nPM1304 spec Table 38, page 159); no maker sheet of a 10 V part on file', 'a distributor or the electronics designer: the part code with its maker sheet'),
    'C88': ('A7 D3: 10 uF X5R 16 V (nPM1304 spec Table 37, page 157); no maker sheet of a 16 V part on file', 'a distributor or the electronics designer: the part code with its maker sheet'),
    'C35': ('A7: 100 nF next to the microphone Vdd pin, no Class 2 dielectric near the microphone (Knowles SPK0641HT4H-1 sheet 4); the old code CL03A104KP3NNNC is X5R (Class 2)', 'a distributor or the electronics designer: a 100 nF Class 1 (C0G/NP0) part that fits under the board, or the lead accepts a Class 2 part'),
    'C36': ('as C35', 'as C35'),
}
TESTPAD_REFS = ['TP%d' % (i + 1) for i in range(len(TPS))]


def main():
    # maker part numbers: bom.csv (the lead's file) wins where it names one
    bom = {}
    for r in csv.DictReader(open(os.path.join(HERE, '../../bom.csv'))):
        for ref in [x.strip() for x in r['reference'].split(',')]:
            if r['maker_part_number'].strip():
                bom[ref] = r['maker_part_number'].strip()
    for p in PARTS:
        if p['reference'] in bom and p['mpn'] != bom[p['reference']]:
            print('mpn from bom.csv', p['reference'], repr(p['mpn']), '->', bom[p['reference']])
            p['mpn'] = bom[p['reference']]
    rows = []
    for p in PARTS:
        by, conn = CONN[p['reference']]
        for num, name, typ in SYM[p['symbol']]:
            key = num if by == 'number' else name
            if key not in conn:
                raise SystemExit('pin %s %s of %s not assigned' % (num, name, p['reference']))
            net = conn[key]
            if net is None or typ == 'no_connect':
                rows.append(dict(net='', reference=p['reference'], pin_number=num, pin_name=name,
                                 pin_type='no_connect'))
            else:
                rows.append(dict(net=net, reference=p['reference'], pin_number=num, pin_name=name,
                                 pin_type=typ))
        used = set(SYM[p['symbol']][i][0 if by == 'number' else 1] for i in range(len(SYM[p['symbol']])))
        extra = set(conn) - used
        if extra:
            raise SystemExit('unknown pins %s on %s' % (extra, p['reference']))
    rows.sort(key=lambda r: (r['net'] == '', r['net'], r['reference'], r['pin_number']))
    with open(os.path.join(HERE, 'netlist.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['net', 'reference', 'pin_number', 'pin_name', 'pin_type'])
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, 'parts.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['reference', 'symbol', 'value', 'mpn', 'footprint', 'sheet', 'dnp'])
        w.writeheader(); w.writerows(PARTS)
    with open(os.path.join(HERE, 'symbols.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['symbol', 'pin_number', 'pin_name', 'pin_type'])
        for s, pins in SYM.items():
            for pin in pins:
                w.writerow([s] + list(pin))
    with open(os.path.join(HERE, 'additions.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['reference', 'kind', 'why'])
        for r, why in ADD: w.writerow([r, 'added', why])
        for r, why in NOT_PLACED: w.writerow([r, 'bom_not_placed', why])
        for r in TESTPAD_REFS: w.writerow([r, 'testpad', 'single-pin net allowed'])
    PROV = {
        'SKTAAAE010': ('Alps spec KTA-601 shows two terminals but no terminal numbers or drawing (open item S9)', 'Alps SKTAAAE010 assembly drawing (S9)'),
        'FPC_15': ('Hirose FH35C-15S-0.3SHW(50) selected (A5 16.4) but its drawing and position numbering are not read; tail contact k assumed on connector position k', 'Hirose FH35C drawing and the screen tail drawing (action 12.1, open item S8)'),
        'DMN2450UFB4': ('datasheet DS40239 p1 names terminals D, S, G but prints no pad numbers', 'footprint step: map G/S/D to the X2-DFN1006-3 land pattern of DS40239'),
        'BAND_PADS_A': ('pad numbers are this schematic\'s own order (BAND_SPLIT at the top of make_netlist.py), not a maker pin; the split of signals between the two tails is confirmed by the lead after the inside model (A6, sch-notes)', 'flex tail drawing from the flex maker and the inside model (open items S16 and the lead\'s confirmation)'),
        'BAND_PADS_B': ('as BAND_PADS_A', 'as BAND_PADS_A'),
        'MOTOR': ('Jinlong W0525AB001D has two lead wires, red + and blue - (architecture 17.16, spec S-525113 rev 0); the maker gives colours, not numbers: P1 (+) and P2 (-) are this schematic\'s names; the lead length is open item S10', 'Jinlong drawing of the leads (S10, S4)'),
        'CELL': ('custom curved cell 1.6 x 6.0 x 39.175 mm on its centre line at US 9 in the band (architecture 17.26; 33.936 mm at US 7); tab order and its protection circuit (on the tab, at -77 degrees) not drawn', 'Grepow cell drawing (action 12.7, open item S12)'),
        'XTAL': ('crystal maker datasheets not on disk; Nordic reference symbol shows two terminals only', 'Kyocera CX2016DB and TXC 9HT11 datasheets (pad numbers, case ground pads)'),
    }
    DISP1_PROV = {'3': 'MTP: the Tailor table (slim.md 1.3 p6) prints "4 MTP, 4 VCI": pin 3 is absent and pin 4 appears twice; order kept as printed, this entry is the 3rd printed',
                  '4': 'VCI: second printed "4" of the Tailor table (slim.md 1.3); number provisional'}
    with open(os.path.join(HERE, 'open-pins.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['reference', 'pin_number', 'pin_name', 'why_open', 'closed_by'])
        n = 0
        for p in PARTS:
            if p['symbol'] in PROV:
                for num, name, typ in SYM[p['symbol']]:
                    w.writerow([p['reference'], num, name] + list(PROV[p['symbol']])); n += 1
        for k, why in DISP1_PROV.items():
            nm = [x[1] for x in SYM['TOH095XVT-01'] if x[0] == k][0]
            w.writerow(['DISP1', k, nm, why, 'Tailor Pixels pin table correction (open item S8)']); n += 1
        for p in PARTS:
            if p['reference'] in OPEN_ORDER_CODE:
                w.writerow([p['reference'], '', 'order code'] + list(OPEN_ORDER_CODE[p['reference']]))
            if 'OPEN' in p['value'] or 'OPEN' in p['mpn']:
                w.writerow([p['reference'], '', 'value or part number', 'value=%s mpn=%s' % (p['value'], p['mpn']), 'Nordic nPM1300 reference BOM (action 12.2) / screen connector (12.1)'])
    print('open pin rows', n)
    print('netlist rows', len(rows), 'parts', len(PARTS), 'nets', len(set(r['net'] for r in rows if r['net'])))


if __name__ == '__main__':
    main()
