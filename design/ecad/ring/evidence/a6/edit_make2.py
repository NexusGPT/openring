P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s = open(P).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)

rep("# ---- power (nPM1300; passives from the DK PCA10184 page 6)",
    "# ---- power (A6: nPM1304, architecture 17.13; the passives are the nPM1300 DK PCA10184 page 6 ones: the nPM1304 page\n"
    "# that would confirm each is not in parts/research-npm1304.md, so every one is 'to confirm against the nPM1304\n"
    "# product specification' (S18))")
rep("part('U2', 'nPM1300_CAAA', 'nPM1300', 'NPM1300-CAAA-R', 'ring:WLCSP-35_nPM1300', P, npm)",
    "part('U2', 'nPM1304_CSP35', 'nPM1304', '', 'ring:WLCSP-35_nPM1304', P, npm)")
rep("two('RT1', 'NTC', '10k NTC', 'OPEN 12.2', 'ring:R_0402', BD, 'NTC', 'GND')  # in the band at the cell (A5 17.3)",
    "two('RT1', 'NTC', '10k NTC', 'OPEN 12.2', 'ring:R_0402', BD, 'NTC', 'GND')  # in the band at the cell (A5 17.3)")
rep("part('BT1', 'CELL', '4.35V 20-26mAh curved', 'Grepow custom', 'ring:CELL_TABS', BD, {'+': 'VBAT', '-': 'GND'})",
    "part('BT1', 'CELL', '4.35V 15-20mAh curved', 'Grepow custom', 'ring:CELL_TABS', BD, {'+': 'VBAT', '-': 'GND'})  # 17.10 capacity (was 20-26 mAh of 17.3: review K4)")

# storage with the level shifter
old = s[s.index("# ---- storage (W3)"):s.index("# ---- screen and its supply")]
new = '''# ---- storage (W3) and its level shifter (A6, review F07)
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

'''
s = s.replace(old, new)

rep("# A5 17.3: the five switches and the motor are in the band, reached through the two flex tails J_BAND_A and\n# J_BAND_B (sheet \"band\"); each switch is one SKTAAAE010 between its line and ground.\n# SW1 UP, SW2 record (keeps the bom.csv designator), SW3 DOWN, SW4 LEFT, SW5 RIGHT.",
    "# A6 17.11: the five switches and the motor are in the band, reached through the two flex tails J_BAND_A and\n# J_BAND_B (sheet \"band\"; which tail carries which line: BAND_SPLIT at the top); each switch is one SKTAAAE010\n# between its line and ground. SW1 UP, SW3 DOWN, SW4 LEFT, SW5 RIGHT; SW2 (BTN_REC) is the switch under the centre of\n# the joystick nub (no record button, no record cap).")
rep("part('J_BAND_A', 'BAND_PADS_A', 'flex tail A (thumb side) 6 pads', '', 'ring:FLEX_PADS_1x6', BD,",
    "part('J_BAND_A', 'BAND_PADS_A', 'flex tail A (joystick side) %d pads' % len(BAND_A), '', 'ring:FLEX_PADS_1x%d' % len(BAND_A), BD,")
rep("part('J_BAND_B', 'BAND_PADS_B', 'flex tail B 9 pads', '', 'ring:FLEX_PADS_1x9', BD,",
    "part('J_BAND_B', 'BAND_PADS_B', 'flex tail B (other side) %d pads' % len(BAND_B), '', 'ring:FLEX_PADS_1x%d' % len(BAND_B), BD,")
rep("# pads from -Y to +Y: VBUS, D-, D+, GND (case design, lead 2026-11-10); in the band, outside, reach the board by J_BAND_B",
    "# pads from -Y to +Y: VBUS, D-, D+, GND (case design, lead 2026-11-10); on the INSIDE face of the band, in the resin liner\n# (architecture 17.12), they touch the skin; they reach the board by the tail the BAND_SPLIT table gives them")

# additions
rep("('J_BAND_A', 'A5 17.3 flex tail A (thumb side): 5 switch lines and ground, 6 pads on the main board'),\n    ('J_BAND_B', 'A5 17.3 flex tail B: motor 2, cell 2, temperature 1, charging pads 4 = 9 pads on the main board'),",
    "('J_BAND_A', 'A6 flex tail A (joystick side, BAND_SPLIT): 4 direction switches, centre switch, motor 2, ground = %d pads on the main board' % len(BAND_A)),\n    ('J_BAND_B', 'A6 flex tail B (other side, BAND_SPLIT): cell 2, temperature 1, charging pads 4 = %d pads on the main board' % len(BAND_B)),\n    ('U10', 'A6 review F07: level shifter SN74AXC4T774RSVR between the 1.8 V main chip and the 3.0 V storage part (TI SCES898C)'),\n    ('C81', 'A6 U10 VCCA 100 nF (TI SCES898C section 8, 0.1 uF)'), ('C82', 'A6 U10 VCCB 100 nF (TI SCES898C section 8, 0.1 uF)'),")
rep("('CP1', 'case contact pad VBUS, first from -Y (architecture 6, 8; order from the case design)')",
    "('CP1', 'charging pad VBUS, first from -Y, inside face of the band (architecture 17.12; order from the case design)')")
rep("('RT1', 'nPM1300 NTC thermistor 10 kohm beside the cell (lead 2026-11-10); part code OPEN')",
    "('RT1', 'NTC thermistor 10 kohm in the band at the cell (lead 2026-11-10); part code OPEN')")
rep("('TP19', 'test pad on nPM1300 SHPHLD (factory wake from ship mode)')", "('TP19', 'test pad on the power chip SHPHLD (factory wake from ship mode)')")
for a, b in (("'nPM1300 VBUS 4.7 uF (DK PCA10184 C36)'", "'U2 VBUS 4.7 uF (nPM1300 DK PCA10184 C36; confirm against the nPM1304 specification, S18)'"),
             ("'nPM1300 VBUS 100 nF (DK C37)'", "'U2 VBUS 100 nF (nPM1300 DK C37; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VBUSOUT 1.0 uF (DK C39)'", "'U2 VBUSOUT 1.0 uF (nPM1300 DK C39; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VSYS 10 uF (DK C40)'", "'U2 VSYS 10 uF (nPM1300 DK C40; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VSYS 10 uF (DK C41)'", "'U2 VSYS 10 uF (nPM1300 DK C41; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VSYS 1.0 nF (DK C42)'", "'U2 VSYS 1.0 nF (nPM1300 DK C42; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VSYS 1.0 nF (DK C43)'", "'U2 VSYS 1.0 nF (nPM1300 DK C43; confirm for the nPM1304, S18)'"),
             ("'nPM1300 buck 1 inductor 2.2 uH (DK L7)'", "'U2 buck 1 inductor 2.2 uH (nPM1300 DK L7; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VOUT1 10 uF (DK C46)'", "'U2 VOUT1 10 uF (nPM1300 DK C46; confirm for the nPM1304, S18)'"),
             ("'nPM1300 buck 2 inductor 2.2 uH (DK L6)'", "'U2 buck 2 inductor 2.2 uH (nPM1300 DK L6; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VOUT2 10 uF (DK C48)'", "'U2 VOUT2 10 uF (nPM1300 DK C48; confirm for the nPM1304, S18)'"),
             ("'nPM1300 VDDIO 100 nF (DK C54)'", "'U2 VDDIO 100 nF (nPM1300 DK C54; confirm for the nPM1304, S18)'")):
    rep(a, b)
rep("('SW3', 'A5 16.4 joystick switch DOWN (SKTAAAE010)')", "('SW3', 'A5 16.4 joystick switch DOWN (SKTAAAE010)')")
open(P, 'w').write(s)
print('ok')
