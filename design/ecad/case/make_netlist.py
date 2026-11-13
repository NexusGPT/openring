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
# BQ25895 RTW: Table 6-1, case_bq25895.pdf p.4-5 (SDA = 6 from Figure 6-1); PowerPAD = pad 25 (TI numbers none; 25 = pin count + 1, closed in closed-pins.csv)
SYM['BQ25895'] = [('1', 'VBUS', 'power_in'), ('2', 'D+', 'bidirectional'), ('3', 'D-', 'bidirectional'),
                  ('4', 'STAT', 'open_collector'), ('5', 'SCL', 'input'), ('6', 'SDA', 'bidirectional'),
                  ('7', 'INT', 'open_collector'), ('8', 'OTG', 'input'), ('9', 'CE', 'input'),
                  ('10', 'ILIM', 'passive'), ('11', 'TS', 'input'), ('12', 'QON', 'input'),
                  ('13', 'BAT', 'passive'), ('14', 'BAT', 'passive'), ('15', 'SYS', 'power_out'),
                  ('16', 'SYS', 'passive'), ('17', 'PGND', 'power_in'), ('18', 'PGND', 'power_in'),
                  ('19', 'SW', 'passive'), ('20', 'SW', 'passive'), ('21', 'BTST', 'passive'),
                  ('22', 'REGN', 'power_out'), ('23', 'PMID', 'power_out'), ('24', 'DSEL', 'open_collector'),
                  ('25', 'PowerPAD', 'passive')]
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
# USB4105-GF-A: pin/signal table, case_usb4105.pdf p.1 drawing rev B4; the maker's table names the shell 'SHELL' with no number: pin SH, all four shell pads carry it
SYM['USB4105'] = [('A1', 'GND', 'passive'), ('A4', 'VBUS', 'power_out'), ('A5', 'CC1', 'passive'),
                  ('A6', 'Dp1', 'passive'), ('A7', 'Dn1', 'passive'), ('A8', 'SBU1', 'passive'),
                  ('A9', 'VBUS', 'passive'), ('A12', 'GND', 'passive'), ('B1', 'GND', 'passive'),
                  ('B4', 'VBUS', 'passive'), ('B5', 'CC2', 'passive'), ('B6', 'Dp2', 'passive'),
                  ('B7', 'Dn2', 'passive'), ('B8', 'SBU2', 'passive'), ('B9', 'VBUS', 'passive'),
                  ('B12', 'GND', 'passive'), ('SH', 'SHELL', 'passive')]
# Zetta SD NAND ZDSD64GLQEAG-R: signal names from sdnand_zetta_family_atta.pdf p.4 section 5 (SD 4-bit mode); the maker numbers no land, so the pin numbers
# 1 to 8 are ours, in the order of the maker's figure (left group top to bottom, then right group), see closed-pins.csv and the footprint LGA16_9x10_ZDSD
SD = [('DAT2', 'bidirectional'), ('CD/DAT3', 'bidirectional'), ('CLK', 'input'), ('GND', 'power_in'),
      ('VDD', 'power_in'), ('DAT1', 'bidirectional'), ('DAT0', 'bidirectional'), ('CMD', 'bidirectional')]
SYM['ZDSD64GLQEAG'] = [('%d' % (i + 1), n, t) for i, (n, t) in enumerate(SD)]
# APTF1616SEEZGQBDC: package drawing p.1: pin 1 common anode, 2 red, 3 green, 4 blue cathodes
SYM['APTF1616'] = [('1', 'A', 'passive'), ('2', 'K_R', 'passive'), ('3', 'K_G', 'passive'), ('4', 'K_B', 'passive')]
SYM['CELL'] = [('1', '+', 'power_out'), ('2', '-', 'passive')]   # lead 1 = red (+), lead 2 = black (-): a requirement on the cell order, see closed-pins.csv
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
part('U1', 'ESP32-S3-MINI-1', 'ESP32-S3-MINI-1-N8', 'ESP32-S3-MINI-1-N8', 'OpenRingCase:ESP32-S3-MINI-1', M, u1, by='number')
two('C9', 'C', '10uF', 'OpenRingCase:SMD_0603', M, '3V3', 'GND')
two('C10', 'C', '100nF', 'OpenRingCase:SMD_0402', M, '3V3', 'GND')
two('R23', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'EN', '3V3')
two('C30', 'C', '1uF', 'OpenRingCase:SMD_0402', M, 'EN', 'GND')
two('R22', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'BOOT', '3V3')
two('R14', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'I2C_SDA', '3V3')
two('R15', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'I2C_SCL', '3V3')
two('R16', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'CHG_INT_N', '3V3')
two('R17', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'VRING_FAULT_N', '3V3')
two('R21', 'R', '10k', 'OpenRingCase:SMD_0402', M, 'CHG_CE_N', '3V3')  # sim finding 2: CE pulled HIGH at power-on (charger off until U1 allows it)
#
two('R25', 'R', '100k', 'OpenRingCase:SMD_0402', M, 'VRING_EN', 'GND')
two('R8', 'R', '510R', 'OpenRingCase:SMD_0402', M, 'LED_R', 'LED_KR')
two('R9', 'R', '270R', 'OpenRingCase:SMD_0402', M, 'LED_G', 'LED_KG')
two('R10', 'R', '270R', 'OpenRingCase:SMD_0402', M, 'LED_B', 'LED_KB')
part('LED1', 'APTF1616', 'RGB', 'APTF1616SEEZGQBDC', 'OpenRingCase:LED_APTF1616', M,
     {'A': 'SYS', 'K_R': 'LED_KR', 'K_G': 'LED_KG', 'K_B': 'LED_KB'})

# ---- power: BQ25895 (Figure 9-1 and Table 6-1), TPS63802 (Figure 10-1), cell
part('U2', 'BQ25895', 'BQ25895', 'BQ25895RTWR', 'OpenRingCase:WQFN-24_RTW_4x4', PW,
     {'1': 'VBUS_IN', '2': None, '3': None,  # C2: D+/D- not connected (no 9/12 V handshake)
      '4': 'CHG_STAT', '5': 'I2C_SCL', '6': 'I2C_SDA',
      '7': 'CHG_INT_N', '8': 'CHG_OTG', '9': 'CHG_CE_N', '10': 'ILIM', '11': 'TS', '12': 'QON',
      '13': 'BAT', '14': 'BAT', '15': 'SYS', '16': 'SYS', '17': 'GND', '18': 'GND', '19': 'SW', '20': 'SW',
      '21': 'BTST', '22': 'REGN', '23': 'PMID', '24': 'CHG_DSEL', '25': 'GND'}, by='number')
two('C1', 'C', '1uF', 'OpenRingCase:SMD_0603', PW, 'VBUS_IN', 'GND')
two('C2', 'C', '22uF', 'OpenRingCase:SMD_0805', PW, 'PMID', 'GND')
two('C3', 'C', '22uF', 'OpenRingCase:SMD_0805', PW, 'PMID', 'GND')
two('C4', 'C', '10uF', 'OpenRingCase:SMD_0603', PW, 'SYS', 'GND')
two('C5', 'C', '10uF', 'OpenRingCase:SMD_0603', PW, 'SYS', 'GND')
two('C6', 'C', '10uF', 'OpenRingCase:SMD_0603', PW, 'BAT', 'GND')
two('C7', 'C', '47nF', 'OpenRingCase:SMD_0402', PW, 'BTST', 'SW')
two('C8', 'C', '4.7uF 10V', 'OpenRingCase:SMD_0603', PW, 'REGN', 'GND')
two('L1', 'L', '1uH', 'OpenRingCase:L_XFL40xx_4x4', PW, 'SW', 'SYS')
two('R11', 'R', '260R', 'OpenRingCase:SMD_0402', PW, 'ILIM', 'GND')
two('RT1', 'R', '5.23k', 'OpenRingCase:SMD_0402', PW, 'REGN', 'TS')
two('RT2', 'R', '30.1k', 'OpenRingCase:SMD_0402', PW, 'TS', 'GND')
two('TH1', 'NTC', '10k 103AT', 'OpenRingCase:NTC_wired', PW, 'TS', 'GND')
two('R24', 'R', '10k', 'OpenRingCase:SMD_0402', PW, 'CHG_STAT', '3V3')
two('R28', 'R', '10k', 'OpenRingCase:SMD_0402', PW, 'CHG_DSEL', '3V3')  # C2
two('R27', 'R', '100k', 'OpenRingCase:SMD_0402', PW, 'CHG_OTG', 'GND')  # C2
part('U3', 'TPS63802', 'TPS63802', 'TPS63802DLAR', 'OpenRingCase:DFN-10_DLA_2x3', PW,
     {'1': 'SYS', '2': 'GND', '3': 'GND', '4': 'FB', '5': None, '6': '3V3', '7': 'U3_L2', '8': 'GND',
      '9': 'U3_L1', '10': 'SYS'}, by='number')
two('L2', 'L', '0.47uH', 'OpenRingCase:L_XFL40xx_4x4', PW, 'U3_L1', 'U3_L2')
two('R3', 'R', '511k', 'OpenRingCase:SMD_0402', PW, '3V3', 'FB')
two('R4', 'R', '91k', 'OpenRingCase:SMD_0402', PW, 'FB', 'GND')
two('C11', 'C', '10uF', 'OpenRingCase:SMD_0603', PW, 'SYS', 'GND')
two('C12', 'C', '22uF', 'OpenRingCase:SMD_0603', PW, '3V3', 'GND')
part('BT1', 'CELL', '700mAh 3.7V', 'DNK852338', 'OpenRingCase:CELL_LEADS', PW, {'+': 'BAT', '-': 'GND'})
part('W5', 'PIN1', 'cell lead +', '', 'OpenRingCase:WIRE_PTH_0.7', PW, {'1': 'BAT'}, by='number')
part('W6', 'PIN1', 'cell lead -', '', 'OpenRingCase:WIRE_PTH_0.7', PW, {'1': 'GND'}, by='number')

# ---- USB-C input
j1 = {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND', 'A4': 'VBUS_IN', 'A9': 'VBUS_IN',
      'B4': 'VBUS_IN', 'B9': 'VBUS_IN', 'A5': 'CC1', 'B5': 'CC2', 'A6': None, 'B6': None,
      'A7': None, 'B7': None, 'A8': None, 'B8': None}  # C2: D+/D- not connected
part('J1', 'USB4105', 'USB-C', 'USB4105-GF-A', 'OpenRingCase:USB4105-GF-A', U, j1, by='number')
two('R1', 'R', '5.1k', 'OpenRingCase:SMD_0402', U, 'CC1', 'GND')
two('R2', 'R', '5.1k', 'OpenRingCase:SMD_0402', U, 'CC2', 'GND')
two('R6', 'R', '100k', 'OpenRingCase:SMD_0402', U, 'CC1', 'CC1_SENSE')
two('R7', 'R', '100k', 'OpenRingCase:SMD_0402', U, 'CC2', 'CC2_SENSE')

# ---- ring link: switch, ESD, spring pins, presence electrode
part('U5', 'TPS2553', 'TPS2553', 'TPS2553DBVR', 'OpenRingCase:SOT-23-6_DBV', RL,
     {'1': 'PMID', '2': 'GND', '3': 'VRING_EN', '4': 'VRING_FAULT_N', '5': 'U5_ILIM', '6': 'VRING'}, by='number')
two('R5', 'R', '59.0k', 'OpenRingCase:SMD_0402', RL, 'U5_ILIM', 'GND')
two('C16', 'C', '100nF', 'OpenRingCase:SMD_0402', RL, 'PMID', 'GND')
two('C15', 'C', '10uF', 'OpenRingCase:SMD_0603', RL, 'VRING', 'GND')
two('R12', 'R', '100k', 'OpenRingCase:SMD_0402', RL, 'VRING', 'VRING_SENSE')
two('R13', 'R', '47k', 'OpenRingCase:SMD_0402', RL, 'VRING_SENSE', 'GND')
part('U6', 'TPD4E05U06', 'TPD4E05U06', 'TPD4E05U06DQAR', 'OpenRingCase:USON-10_DQA_1x2.5', RL,
     {'1': 'USB_D+', '2': 'USB_D-', '3': 'GND', '4': 'VRING', '5': 'VRING', '6': None, '7': None, '8': 'GND',
      '9': None, '10': None}, by='number')
# spring pins along Y: P1 VBUS (-3.81), P2 D- (-1.27), P3 D+ (+1.27), P4 GND (+3.81); wire k on pin k
for p, w, net in (('P1', 'W1', 'VRING'), ('P2', 'W2', 'USB_D-'), ('P3', 'W3', 'USB_D+'), ('P4', 'W4', 'GND')):
    part(p, 'PIN1', 'spring pin', 'P70-6000045R', 'OpenRingCase:HARWIN_P70_6000045R', RL, {'1': net}, by='number')
    part(w, 'PIN1', 'wire 30AWG', '', 'OpenRingCase:WIRE_PTH_0.7', RL, {'1': net}, by='number')
# pin-board ends of the five wires (pads WP1 WP2 WP3 WP4 WP7 of PCB2, footprint WIRE_SMD_0.9x1.1): the other end of each wire Wk is the plated hole Wk on PCB1;
# same net as Wk, so the netlist records which pin-board pad each wire starts from (review 2026-11-13 minor m4)
for w, net in (('W1', 'VRING'), ('W2', 'USB_D-'), ('W3', 'USB_D+'), ('W4', 'GND'), ('W7', 'RING_TOUCH')):
    part('WP' + w[1:], 'PIN1', 'wire 30AWG pin-board end of ' + w, '', 'OpenRingCase:WIRE_SMD_0.9x1.1', RL, {'1': net}, by='number')
part('E1', 'PIN1', 'touch electrode 6x3', '', 'OpenRingCase:TOUCH_E1_front', RL, {'1': 'RING_TOUCH'}, by='number')
part('W7', 'PIN1', 'wire 30AWG', '', 'OpenRingCase:WIRE_PTH_0.7', RL, {'1': 'RING_TOUCH'}, by='number')

# ---- storage (SD 4-bit)
part('U4', 'ZDSD64GLQEAG', 'ZDSD64GLQEAG-R', 'ZDSD64GLQEAG-R', 'OpenRingCase:LGA16_9x10_ZDSD', S,
     {'CLK': 'SD_CLK_U4', 'CMD': 'SD_CMD', 'DAT0': 'SD_D0', 'DAT1': 'SD_D1', 'DAT2': 'SD_D2',
      'CD/DAT3': 'SD_D3', 'VDD': '3V3', 'GND': 'GND'})
two('R26', 'R', '22R', 'OpenRingCase:SMD_0402', S, 'SD_CLK', 'SD_CLK_U4')
two('R18', 'R', '10k', 'OpenRingCase:SMD_0402', S, 'SD_CMD', '3V3')
two('R19', 'R', '10k', 'OpenRingCase:SMD_0402', S, 'SD_D0', '3V3')
two('R20', 'R', '10k', 'OpenRingCase:SMD_0402', S, 'SD_D1', '3V3')
two('R29', 'R', '10k', 'OpenRingCase:SMD_0402', S, 'SD_D2', '3V3')  # C2
two('R30', 'R', '10k', 'OpenRingCase:SMD_0402', S, 'SD_D3', '3V3')  # C2
two('C13', 'C', '100nF', 'OpenRingCase:SMD_0402', S, '3V3', 'GND')
two('C14', 'C', '4.7uF', 'OpenRingCase:SMD_0603', S, '3V3', 'GND')

# ---- test pads
TPS = ['BOOT', 'EN', 'TXD0', 'RXD0', 'QON'] + ['SPARE_IO%d' % i for i in range(33, 43)] + ['GND']
for i, n in enumerate(TPS):
    part('TP%d' % (i + 1), 'PIN1', 'pad', '', 'OpenRingCase:TESTPAD_1.0', T, {'1': n}, by='number')

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
       ('WP1', 'pin-board end of wire W1 (pad on PCB2; review m4)'), ('WP2', 'pin-board end of wire W2 (pad on PCB2; review m4)'),
       ('WP3', 'pin-board end of wire W3 (pad on PCB2; review m4)'), ('WP4', 'pin-board end of wire W4 (pad on PCB2; review m4)'),
       ('WP7', 'pin-board end of wire W7 (pad on PCB2; review m4)'),
       ('TP1', 'test pad BOOT'), ('TP2', 'test pad EN'), ('TP3', 'test pad TXD0'), ('TP4', 'test pad RXD0'),
       ('TP5', 'test pad QON')] + [('TP%d' % (i + 6), 'test pad spare IO%d' % (33 + i)) for i in range(10)] + [
       ('TP16', 'test pad GND')]
NOT_PLACED = []  # C2 case-bom.csv lists C1-C16 itself; the C-set line is gone
TESTPAD_REFS = ['TP%d' % (i + 1) for i in range(len(TPS))]
PROV = {}   # every pin number is now real or fixed as a stated requirement: see CLOSED below
CLOSED = [
    ('U2', '25', 'PowerPAD', 'TI BQ25895 Table 6-1 gives the exposed pad no number (case_bq25895.pdf p.4-5; RTW drawing p.62-64: "thermal pad")',
     'numbered 25 = pin count + 1 in footprint WQFN-24_RTW_4x4 (thermal land 3.1 x 3.1 mm, case_bq25895.pdf p.64)'),
    ('BT1', '1', '+', 'cell datasheet gives terminal codes WC and FL only (case_cell_dnk852338.pdf p.1)',
     'requirement on the cell order: flying leads FL, lead 1 red = +, lead 2 black = -, cut to 40 mm at the board (CL = 100 mm as supplied)'),
    ('BT1', '2', '-', 'same', 'same: lead 2 black = -'),
    ('J1', 'SH', 'SHELL', 'the pin table of case_usb4105.pdf p.1 lists the shell as SHELL without a number',
     'pin SH kept; the four shell tabs are four plated slots, all numbered SH in footprint USB4105-GF-A (drawing p.1 Recommended PCB Layout)'),
]
for i, (n, nm) in enumerate((('DAT2', 'DAT2'), ('CD/DAT3', 'CD/DAT3'), ('CLK', 'CLK'), ('GND', 'GND'), ('VDD', 'VDD'), ('DAT1', 'DAT1'), ('DAT0', 'DAT0'), ('CMD', 'CMD'))):
    CLOSED.append(('U4', str(i + 1), n, 'the package drawing numbers no land (sdnand_zetta_family_atta.pdf p.15); signal names p.4 section 5',
                   'pin %d = %s: numbers follow the maker figure p.4 (left group top to bottom, then right group); each signal has an outer and an inner land with the same number '
                   '(footprint LGA16_9x10_ZDSD, p.15 dimensions)' % (i + 1, n)))


# Orderable part numbers chosen by W5 for the lines that case-bom.csv leaves as "choose maker part" (case-bom.csv column open_action).
# Resistors: Yageo RC0402FR-07<value>L (1 %, thick film, 0402). Capacitors: Murata GRM series, X5R/X7R, rating chosen for the rail (5 V rails 10 V or more).
# Inductors: Coilcraft XFL4020-102MEC (1 uH, Isat 5.1 A) and XFL4015-471MEC (0.47 uH, the part TI lists in case_tps63802.pdf Table 10-2).
# R11: 260 ohm is not an E96 value; the nearest E96 value 261 ohm is ordered (ILIM cap 355/261 = 1.36 A).
RES = {'R1': '5K1', 'R2': '5K1', 'R3': '511K', 'R4': '91K', 'R5': '59K', 'R6': '100K', 'R7': '100K', 'R8': '510R', 'R9': '270R', 'R10': '270R',
       'R11': '261R', 'R12': '100K', 'R13': '47K', 'R14': '10K', 'R15': '10K', 'R16': '10K', 'R17': '10K', 'R18': '10K', 'R19': '10K', 'R20': '10K',
       'R21': '10K', 'R22': '10K', 'R23': '10K', 'R24': '10K', 'R25': '100K', 'R26': '22R', 'R27': '100K', 'R28': '10K', 'R29': '10K', 'R30': '10K',
       'RT1': '5K23', 'RT2': '30K1'}
MPN = {r: 'RC0402FR-07%sL' % v for r, v in RES.items()}
MPN.update({'C1': 'GRM188R61A105KA61D', 'C2': 'GRM21BR61A226ME44L', 'C3': 'GRM21BR61A226ME44L',
            'C4': 'GRM188R61A106KE69D', 'C5': 'GRM188R61A106KE69D', 'C6': 'GRM188R61A106KE69D', 'C7': 'GRM155R71C473KA01D',
            'C8': 'GRM188R61A475KE15D', 'C9': 'GRM188R60J106ME47D', 'C10': 'GRM155R71C104KA88D', 'C11': 'GRM188R61A106KE69D',
            'C12': 'GRM188R60J226MEA0D', 'C13': 'GRM155R71C104KA88D', 'C14': 'GRM188R61A475KE15D', 'C15': 'GRM188R61A106KE69D',
            'C16': 'GRM155R71C104KA88D', 'C30': 'GRM155R61A105KE15D',
            'L1': 'XFL4020-102MEC', 'L2': 'XFL4015-471MEC', 'TH1': '103AT-2', 'BT1': 'DNK852338',
            'P1': 'P70-6000045R', 'P2': 'P70-6000045R', 'P3': 'P70-6000045R', 'P4': 'P70-6000045R'})
MAKER = {'RES': 'Yageo', 'GRM': 'Murata', 'XFL': 'Coilcraft', '103AT-2': 'Semitec', 'DNK': 'DNK Power', 'P70': 'Harwin'}


def main():
    for p_ in PARTS:
        if p_['reference'] in MPN:
            p_['mpn'] = MPN[p_['reference']]
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
    snap = {r['reference'] for r in csv.DictReader(open(os.path.join(HERE, 'bom_refs_snapshot.csv')))}
    with open(os.path.join(HERE, 'additions.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['reference', 'kind', 'why'])
        for r, why in ADD:
            w.writerow([r, 'added' if r not in snap else 'in_bom_now', why])
        for r, why in NOT_PLACED: w.writerow([r, 'bom_not_placed', why])
        for r in TESTPAD_REFS: w.writerow([r, 'testpad', 'single-pin net allowed'])
    n = 0
    with open(os.path.join(HERE, 'open-pins.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['reference', 'pin_number', 'pin_name', 'why_open', 'closed_by'])
    with open(os.path.join(HERE, 'closed-pins.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['reference', 'pin_number', 'pin_name', 'why_it_was_open', 'how_closed'])
        for row in CLOSED:
            w.writerow(row)
    print('open pin rows', n, 'closed rows', len(CLOSED))
    print('netlist rows', len(rows), 'parts', len(PARTS), 'nets', len(set(r['net'] for r in rows if r['net'])))


if __name__ == '__main__':
    main()
