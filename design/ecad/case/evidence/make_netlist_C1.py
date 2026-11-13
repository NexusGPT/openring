#!/usr/bin/env python3
"""Writes the source tables of the charging-case schematic: netlist.csv, parts.csv,
symbols.csv, additions.csv, open-pins.csv. Contract: design/case/case-architecture.md
(version C1) and design/case/case-bom.csv. Pin numbers and names come from the
datasheet named next to each symbol; a number written P<n> or SH is provisional
and is listed in open-pins.csv."""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
SYM = {}

# ESP32-S3-MINI-1-N8: Table 3-1 Pin Definitions, case_esp32s3_mini1.pdf p.11-12
MINI = {1: 'GND', 2: 'GND', 3: '3V3', 4: 'IO0', 5: 'IO1', 6: 'IO2', 7: 'IO3', 8: 'IO4', 9: 'IO5',
        10: 'IO6', 11: 'IO7', 12: 'IO8', 13: 'IO9', 14: 'IO10', 15: 'IO11', 16: 'IO12', 17: 'IO13',
        18: 'IO14', 19: 'IO15', 20: 'IO16', 21: 'IO17', 22: 'IO18', 23: 'IO19', 24: 'IO20', 25: 'IO21',
        26: 'IO26', 27: 'IO47', 28: 'IO33', 29: 'IO34', 30: 'IO48', 31: 'IO35', 32: 'IO36', 33: 'IO37',
        34: 'IO38', 35: 'IO39', 36: 'IO40', 37: 'IO41', 38: 'IO42', 39: 'TXD0', 40: 'RXD0', 41: 'IO45',
        42: 'GND', 43: 'GND', 44: 'IO46', 45: 'EN'}
for n in range(46, 66):
    MINI[n] = 'GND'
SYM['ESP32-S3-MINI-1'] = [(str(n), MINI[n], 'power_in' if MINI[n] in ('GND', '3V3') else
                           ('input' if MINI[n] == 'EN' else 'bidirectional')) for n in range(1, 66)]
# BQ25895 RTW: Table 6-1, case_bq25895.pdf p.4-5 (SDA = 6 from Figure 6-1); PowerPAD number provisional
SYM['BQ25895'] = [('1', 'VBUS', 'power_in'), ('2', 'D+', 'bidirectional'), ('3', 'D-', 'bidirectional'),
                  ('4', 'STAT', 'open_collector'), ('5', 'SCL', 'input'), ('6', 'SDA', 'bidirectional'),
                  ('7', 'INT', 'open_collector'), ('8', 'OTG', 'input'), ('9', 'CE', 'input'),
                  ('10', 'ILIM', 'passive'), ('11', 'TS', 'input'), ('12', 'QON', 'input'),
                  ('13', 'BAT', 'passive'), ('14', 'BAT', 'passive'), ('15', 'SYS', 'power_out'),
                  ('16', 'SYS', 'passive'), ('17', 'PGND', 'power_in'), ('18', 'PGND', 'power_in'),
                  ('19', 'SW', 'passive'), ('20', 'SW', 'passive'), ('21', 'BTST', 'passive'),
                  ('22', 'REGN', 'power_out'), ('23', 'PMID', 'power_out'), ('24', 'DSEL', 'open_collector'),
                  ('PAD', 'PowerPAD', 'passive')]
# TPS63802 DLA: Table 7-1, case_tps63802.pdf p.4
SYM['TPS63802'] = [('1', 'EN', 'input'), ('2', 'MODE', 'input'), ('3', 'AGND', 'power_in'), ('4', 'FB', 'input'),
                   ('5', 'PG', 'open_collector'), ('6', 'VOUT', 'power_out'), ('7', 'L2', 'passive'),
                   ('8', 'GND', 'power_in'), ('9', 'L1', 'passive'), ('10', 'VIN', 'power_in')]
# TPS2553 DBV (SOT-23): Table 5-1, case_tps2553.pdf p.3-4
SYM['TPS2553'] = [('1', 'IN', 'power_in'), ('2', 'GND', 'power_in'), ('3', 'EN', 'input'),
                  ('4', 'FAULT', 'open_collector'), ('5', 'ILIM', 'passive'), ('6', 'OUT', 'power_out')]
# TPD4E05U06 DQA: Table 4-2, case_tpd4e05u06.pdf
SYM['TPD4E05U06'] = [('1', 'D1+', 'passive'), ('2', 'D1-', 'passive'), ('3', 'GND', 'power_in'),
                     ('4', 'D2+', 'passive'), ('5', 'D2-', 'passive'), ('6', 'NC', 'no_connect'),
                     ('7', 'NC', 'no_connect'), ('8', 'GND', 'power_in'), ('9', 'NC', 'no_connect'),
                     ('10', 'NC', 'no_connect')]
# USB4105-GF-A: pin/signal table, case_usb4105.pdf drawing rev B4; shell pad number provisional
SYM['USB4105'] = [('A1', 'GND', 'passive'), ('A4', 'VBUS', 'power_out'), ('A5', 'CC1', 'passive'),
                  ('A6', 'Dp1', 'passive'), ('A7', 'Dn1', 'passive'), ('A8', 'SBU1', 'passive'),
                  ('A9', 'VBUS', 'passive'), ('A12', 'GND', 'passive'), ('B1', 'GND', 'passive'),
                  ('B4', 'VBUS', 'passive'), ('B5', 'CC2', 'passive'), ('B6', 'Dp2', 'passive'),
                  ('B7', 'Dn2', 'passive'), ('B8', 'SBU2', 'passive'), ('B9', 'VBUS', 'passive'),
                  ('B12', 'GND', 'passive'), ('SH', 'SHELL', 'passive')]
# Zetta SD NAND, SD mode names from sdnand_zetta_family_atta.pdf section 5; numbers provisional (S3)
SD = [('CLK', 'input'), ('CMD', 'bidirectional'), ('DAT0', 'bidirectional'), ('DAT1', 'bidirectional'),
      ('DAT2', 'bidirectional'), ('CD/DAT3', 'bidirectional'), ('VDD', 'power_in'), ('GND', 'power_in')]
SYM['ZDSD64GLQEAG'] = [('P%d' % (i + 1), n, t) for i, (n, t) in enumerate(SD)]
# APTF1616SEEZGQBDC: package drawing p.1: pin 1 common anode, 2 red, 3 green, 4 blue cathodes
SYM['APTF1616'] = [('1', 'A', 'passive'), ('2', 'K_R', 'passive'), ('3', 'K_G', 'passive'), ('4', 'K_B', 'passive')]
SYM['CELL'] = [('P1', '+', 'power_out'), ('P2', '-', 'passive')]
SYM['R'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['C'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['L'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['NTC'] = [('1', '~', 'passive'), ('2', '~', 'passive')]
SYM['PIN1'] = [('1', '1', 'passive')]

PARTS, CONN = [], {}


def part(ref, sym, value, mpn, fp, sheet, conn, by='name', dnp=False):
    PARTS.append(dict(reference=ref, symbol=sym, value=value, mpn=mpn, footprint=fp, sheet=sheet,
                      dnp='yes' if dnp else 'no'))
    CONN[ref] = (by, conn)


def two(ref, sym, value, fp, sheet, n1, n2, mpn=''):
    part(ref, sym, value, mpn, fp, sheet, {'1': n1, '2': n2}, by='number')


M, PW, U, RL, S, T = 'main', 'power', 'usbc', 'ringlink', 'storage', 'test'

# ---- U1 per case-architecture.md section 6
u1 = {}
for n, name in MINI.items():
    if name == 'GND':
        u1[str(n)] = 'GND'
plan = {3: '3V3', 4: 'BOOT', 5: 'CC1_SENSE', 6: 'CC2_SENSE', 7: None, 8: 'RING_TOUCH', 9: 'VRING_SENSE',
        10: 'CHG_OTG', 11: 'CHG_INT_N', 12: 'I2C_SDA', 13: 'SD_D3', 14: 'SD_D2', 15: 'SD_CMD', 16: 'SD_CLK',
        17: 'SD_D0', 18: 'SD_D1', 19: 'VRING_EN', 20: 'VRING_FAULT_N', 21: 'I2C_SCL', 22: 'CHG_CE_N',
        23: 'USB_D-', 24: 'USB_D+', 25: 'LED_R', 26: None, 27: 'LED_G', 30: 'LED_B',
        28: 'SPARE_IO33', 29: 'SPARE_IO34', 31: 'SPARE_IO35', 32: 'SPARE_IO36', 33: 'SPARE_IO37',
        34: 'SPARE_IO38', 35: 'SPARE_IO39', 36: 'SPARE_IO40', 37: 'SPARE_IO41', 38: 'SPARE_IO42',
        39: 'TXD0', 40: 'RXD0', 41: None, 44: None, 45: 'EN'}
for n, net in plan.items():
    u1[str(n)] = net
part('U1', 'ESP32-S3-MINI-1', 'ESP32-S3-MINI-1-N8', 'ESP32-S3-MINI-1-N8', 'case:ESP32-S3-MINI-1', M, u1, by='number')
two('C9', 'C', '10uF', 'case:C_0603', M, '3V3', 'GND')
two('C10', 'C', '100nF', 'case:C_0402', M, '3V3', 'GND')
two('R23', 'R', '10k', 'case:R_0402', M, 'EN', '3V3')
two('C30', 'C', '1uF', 'case:C_0402', M, 'EN', 'GND')
two('R22', 'R', '10k', 'case:R_0402', M, 'BOOT', '3V3')
two('R14', 'R', '10k', 'case:R_0402', M, 'I2C_SDA', '3V3')
two('R15', 'R', '10k', 'case:R_0402', M, 'I2C_SCL', '3V3')
two('R16', 'R', '10k', 'case:R_0402', M, 'CHG_INT_N', '3V3')
two('R17', 'R', '10k', 'case:R_0402', M, 'VRING_FAULT_N', '3V3')
two('R21', 'R', '10k', 'case:R_0402', M, 'CHG_CE_N', 'GND')
two('R25', 'R', '100k', 'case:R_0402', M, 'VRING_EN', 'GND')
two('R8', 'R', '470R', 'case:R_0402', M, 'LED_R', 'LED_KR')
two('R9', 'R', '150R', 'case:R_0402', M, 'LED_G', 'LED_KG')
two('R10', 'R', '150R', 'case:R_0402', M, 'LED_B', 'LED_KB')
part('LED1', 'APTF1616', 'RGB', 'APTF1616SEEZGQBDC', 'case:LED_1616', M,
     {'A': '3V3', 'K_R': 'LED_KR', 'K_G': 'LED_KG', 'K_B': 'LED_KB'})

# ---- power: BQ25895 (Figure 9-1 and Table 6-1), TPS63802 (Figure 10-1), cell
part('U2', 'BQ25895', 'BQ25895', 'BQ25895RTWR', 'case:WQFN-24_RTW', PW,
     {'1': 'VBUS_IN', '2': 'USB_C_DP', '3': 'USB_C_DN', '4': 'CHG_STAT', '5': 'I2C_SCL', '6': 'I2C_SDA',
      '7': 'CHG_INT_N', '8': 'CHG_OTG', '9': 'CHG_CE_N', '10': 'ILIM', '11': 'TS', '12': 'QON',
      '13': 'BAT', '14': 'BAT', '15': 'SYS', '16': 'SYS', '17': 'GND', '18': 'GND', '19': 'SW', '20': 'SW',
      '21': 'BTST', '22': 'REGN', '23': 'PMID', '24': None, 'PAD': 'GND'}, by='number')
two('C1', 'C', '1uF', 'case:C_0603', PW, 'VBUS_IN', 'GND')
two('C2', 'C', '22uF', 'case:C_0805', PW, 'PMID', 'GND')
two('C3', 'C', '22uF', 'case:C_0805', PW, 'PMID', 'GND')
two('C4', 'C', '10uF', 'case:C_0603', PW, 'SYS', 'GND')
two('C5', 'C', '10uF', 'case:C_0603', PW, 'SYS', 'GND')
two('C6', 'C', '10uF', 'case:C_0603', PW, 'BAT', 'GND')
two('C7', 'C', '47nF', 'case:C_0402', PW, 'BTST', 'SW')
two('C8', 'C', '4.7uF 10V', 'case:C_0603', PW, 'REGN', 'GND')
two('L1', 'L', '1uH', 'case:L_0420', PW, 'SW', 'SYS')
two('R11', 'R', '260R', 'case:R_0402', PW, 'ILIM', 'GND')
two('RT1', 'R', '5.21k', 'case:R_0402', PW, 'REGN', 'TS')
two('RT2', 'R', '29.87k', 'case:R_0402', PW, 'TS', 'GND')
two('TH1', 'NTC', '10k 103AT', 'case:NTC_wired', PW, 'TS', 'GND')
two('R24', 'R', '10k', 'case:R_0402', PW, 'CHG_STAT', '3V3')
part('U3', 'TPS63802', 'TPS63802', 'TPS63802DLAR', 'case:DFN-10_DLA', PW,
     {'1': 'SYS', '2': 'GND', '3': 'GND', '4': 'FB', '5': None, '6': '3V3', '7': 'U3_L2', '8': 'GND',
      '9': 'U3_L1', '10': 'SYS'}, by='number')
two('L2', 'L', '0.47uH', 'case:L_4x4', PW, 'U3_L1', 'U3_L2')
two('R3', 'R', '560k', 'case:R_0402', PW, '3V3', 'FB')
two('R4', 'R', '100k', 'case:R_0402', PW, 'FB', 'GND')
two('C11', 'C', '10uF', 'case:C_0603', PW, 'SYS', 'GND')
two('C12', 'C', '22uF', 'case:C_0603', PW, '3V3', 'GND')
part('BT1', 'CELL', '700mAh 3.7V', 'DNK852338', 'case:CELL_LEADS', PW, {'+': 'BAT', '-': 'GND'})
part('W5', 'PIN1', 'cell lead +', '', 'case:SOLDER_1', PW, {'1': 'BAT'}, by='number')
part('W6', 'PIN1', 'cell lead -', '', 'case:SOLDER_1', PW, {'1': 'GND'}, by='number')

# ---- USB-C input
j1 = {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND', 'A4': 'VBUS_IN', 'A9': 'VBUS_IN',
      'B4': 'VBUS_IN', 'B9': 'VBUS_IN', 'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_C_DP', 'B6': 'USB_C_DP',
      'A7': 'USB_C_DN', 'B7': 'USB_C_DN', 'A8': None, 'B8': None}
part('J1', 'USB4105', 'USB-C', 'USB4105-GF-A', 'case:USB4105', U, j1, by='number')
two('R1', 'R', '5.1k', 'case:R_0402', U, 'CC1', 'GND')
two('R2', 'R', '5.1k', 'case:R_0402', U, 'CC2', 'GND')
two('R6', 'R', '100k', 'case:R_0402', U, 'CC1', 'CC1_SENSE')
two('R7', 'R', '100k', 'case:R_0402', U, 'CC2', 'CC2_SENSE')

# ---- ring link: switch, ESD, spring pins, presence electrode
part('U5', 'TPS2553', 'TPS2553', 'TPS2553DBVR', 'case:SOT-23-6', RL,
     {'1': 'PMID', '2': 'GND', '3': 'VRING_EN', '4': 'VRING_FAULT_N', '5': 'U5_ILIM', '6': 'VRING'}, by='number')
two('R5', 'R', '59.0k', 'case:R_0402', RL, 'U5_ILIM', 'GND')
two('C16', 'C', '100nF', 'case:C_0402', RL, 'PMID', 'GND')
two('C15', 'C', '10uF', 'case:C_0603', RL, 'VRING', 'GND')
two('R12', 'R', '100k', 'case:R_0402', RL, 'VRING', 'VRING_SENSE')
two('R13', 'R', '47k', 'case:R_0402', RL, 'VRING_SENSE', 'GND')
part('U6', 'TPD4E05U06', 'TPD4E05U06', 'TPD4E05U06DQAR', 'case:USON-10_DQA', RL,
     {'1': 'USB_D+', '2': 'USB_D-', '3': 'GND', '4': 'VRING', '5': 'VRING', '6': None, '7': None, '8': 'GND',
      '9': None, '10': None}, by='number')
# spring pins along Y: P1 VBUS (-3.81), P2 D- (-1.27), P3 D+ (+1.27), P4 GND (+3.81); wire k on pin k
for p, w, net in (('P1', 'W1', 'VRING'), ('P2', 'W2', 'USB_D-'), ('P3', 'W3', 'USB_D+'), ('P4', 'W4', 'GND')):
    part(p, 'PIN1', 'spring pin', '0981-0-15-20-87-14-11-0', 'case:MillMax_0981', RL, {'1': net}, by='number')
    part(w, 'PIN1', 'wire 30AWG', '', 'case:SOLDER_1', RL, {'1': net}, by='number')
part('E1', 'PIN1', 'touch electrode 6x3', '', 'case:COPPER_6x3', RL, {'1': 'RING_TOUCH'}, by='number')
part('W7', 'PIN1', 'wire 30AWG', '', 'case:SOLDER_1', RL, {'1': 'RING_TOUCH'}, by='number')

# ---- storage (SD 4-bit)
part('U4', 'ZDSD64GLQEAG', 'ZDSD64GLQEAG-R', 'ZDSD64GLQEAG-R', 'case:LGA8x2_9x10', S,
     {'CLK': 'SD_CLK_U4', 'CMD': 'SD_CMD', 'DAT0': 'SD_D0', 'DAT1': 'SD_D1', 'DAT2': 'SD_D2',
      'CD/DAT3': 'SD_D3', 'VDD': '3V3', 'GND': 'GND'})
two('R26', 'R', '22R', 'case:R_0402', S, 'SD_CLK', 'SD_CLK_U4')
two('R18', 'R', '10k', 'case:R_0402', S, 'SD_CMD', '3V3')
two('R19', 'R', '10k', 'case:R_0402', S, 'SD_D0', '3V3')
two('R20', 'R', '10k', 'case:R_0402', S, 'SD_D1', '3V3')
two('C13', 'C', '100nF', 'case:C_0402', S, '3V3', 'GND')
two('C14', 'C', '4.7uF', 'case:C_0603', S, '3V3', 'GND')

# ---- test pads
TPS = ['BOOT', 'EN', 'TXD0', 'RXD0', 'QON'] + ['SPARE_IO%d' % i for i in range(33, 43)] + ['GND']
for i, n in enumerate(TPS):
    part('TP%d' % (i + 1), 'PIN1', 'pad', '', 'case:TESTPAD_1.0', T, {'1': n}, by='number')

ADD = [('C1', 'C-set: VBUS 1 uF (BQ25895 Table 6-1)'), ('C2', 'C-set: PMID 22 uF'), ('C3', 'C-set: PMID 22 uF (44 uF >= 40 uF with OTG)'),
       ('C4', 'C-set: SYS 10 uF'), ('C5', 'C-set: SYS 10 uF (20 uF)'), ('C6', 'C-set: BAT 10 uF'),
       ('C7', 'C-set: BTST 47 nF'), ('C8', 'C-set: REGN 4.7 uF 10 V'), ('C9', 'C-set: U1 10 uF'),
       ('C10', 'C-set: U1 0.1 uF'), ('C11', 'C-set: U3 input 10 uF (TPS63802 Figure 10-1 C1)'),
       ('C12', 'C-set: U3 output 22 uF (Figure 10-1 C2)'), ('C13', 'C-set: U4 0.1 uF'), ('C14', 'C-set: U4 4.7 uF'),
       ('C15', 'C-set: VRING 10 uF'), ('C16', 'TPS2553 IN 0.1 uF (Table 5-1 IN pin)'),
       ('R24', 'BQ25895 STAT 10 kohm pull-up (architecture section 6 "Other pins")'),
       ('R25', 'VRING_EN 100 kohm pull-down (architecture section 6, IO15)'),
       ('R26', 'SD_CLK 22 ohm series (architecture section 6, IO12)'),
       ('W7', 'fifth pin-board wire for the touch electrode E1 (PCB2 line says 4 wires)'),
       ('TP1', 'test pad BOOT'), ('TP2', 'test pad EN'), ('TP3', 'test pad TXD0'), ('TP4', 'test pad RXD0'),
       ('TP5', 'test pad QON')] + [('TP%d' % (i + 6), 'test pad spare IO%d' % (33 + i)) for i in range(10)] + [
       ('TP16', 'test pad GND')]
NOT_PLACED = [('C-set', 'placeholder line, split into C1-C16 (additions)')]
TESTPAD_REFS = ['TP%d' % (i + 1) for i in range(len(TPS))]
PROV = {
    'ZDSD64GLQEAG': ('SD-mode names from the Zetta family datasheet section 5; pad numbers of the LGA8x2 9x10 package not in a text-readable drawing', 'Zetta package drawing of ZDSD64GLQEAG-R (case supplier item S3)'),
    'CELL': ('cell leads: datasheet gives terminals WC/FL only', 'DNK cell order with leads (S1)'),
    'BQ25895': ('PowerPAD has no number in Table 6-1', 'footprint step: TI RTW land pattern'),
    'USB4105': ('shell tabs have no number in the pin table', 'footprint step: GCT USB4105 land pattern'),
}


def main():
    rows = []
    for p in PARTS:
        by, conn = CONN[p['reference']]
        keys = set()
        for num, name, typ in SYM[p['symbol']]:
            key = num if by == 'number' else name
            keys.add(key)
            if key not in conn:
                raise SystemExit('pin %s %s of %s not assigned' % (num, name, p['reference']))
            net = conn[key]
            rows.append(dict(net='' if (net is None or typ == 'no_connect') else net, reference=p['reference'],
                             pin_number=num, pin_name=name,
                             pin_type='no_connect' if (net is None or typ == 'no_connect') else typ))
        if set(conn) - keys:
            raise SystemExit('unknown pins %s on %s' % (set(conn) - keys, p['reference']))
    rows.sort(key=lambda r: (r['net'] == '', r['net'], r['reference'], r['pin_number']))
    with open(os.path.join(HERE, 'netlist.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['net', 'reference', 'pin_number', 'pin_name', 'pin_type']); w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, 'parts.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['reference', 'symbol', 'value', 'mpn', 'footprint', 'sheet', 'dnp']); w.writeheader(); w.writerows(PARTS)
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
    n = 0
    with open(os.path.join(HERE, 'open-pins.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['reference', 'pin_number', 'pin_name', 'why_open', 'closed_by'])
        for p in PARTS:
            if p['symbol'] in PROV:
                for num, name, typ in SYM[p['symbol']]:
                    if p['symbol'] in ('BQ25895', 'USB4105') and num not in ('PAD', 'SH'):
                        continue
                    w.writerow([p['reference'], num, name] + list(PROV[p['symbol']])); n += 1
    print('open pin rows', n)
    print('netlist rows', len(rows), 'parts', len(PARTS), 'nets', len(set(r['net'] for r in rows if r['net'])))


if __name__ == '__main__':
    main()
