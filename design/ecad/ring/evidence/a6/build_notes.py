import re, csv, collections, os
R = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/")
DES = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/")
old = open(R + 'evidence/a6/sch-notes_before.md').read()

def lines(p):
    return open(p).read().split('\n')

def ln(path, pat, nth=1):
    k = 0
    for i, l in enumerate(lines(path), 1):
        if re.search(pat, l):
            k += 1
            if k == nth:
                return i
    raise SystemExit('no line for %r in %s' % (pat, path))

def lnr(path, pat):
    hit = [i for i, l in enumerate(lines(path), 1) if re.search(pat, l)]
    assert hit, (pat, path)
    return '%d to %d' % (hit[0], hit[-1]) if hit[-1] != hit[0] else str(hit[0])

MK, CK, GS = R + 'make_netlist.py', R + 'check_netlist.py', R + 'gen_sch.py'
BOM = DES + 'bom.csv'
V = {}
nl = list(csv.DictReader(open(R + 'netlist.csv')))
V['rows'] = len(nl); V['nets'] = len({r['net'] for r in nl if r['net']}); V['nc'] = sum(r['pin_type'] == 'no_connect' for r in nl)
V['parts'] = len(list(csv.DictReader(open(R + 'parts.csv'))))
V['syms'] = len({r['symbol'] for r in csv.DictReader(open(R + 'symbols.csv'))})
ad = collections.Counter(r['kind'] for r in csv.DictReader(open(R + 'additions.csv')))
V['added'] = ad['added']; V['np'] = ad['bom_not_placed']; V['tp'] = ad['testpad']
op = list(csv.DictReader(open(R + 'open-pins.csv')))
V['open'] = len(op)
oc = collections.Counter(r['reference'] for r in op)
V['open_u2'] = oc['U2'] - 1
V['open_pins'] = sum(1 for r in op if r['pin_number'])
V['open_other'] = len(op) - V['open_pins']
# line numbers
for k, (f, p) in {
    'mk_sym_u2': (MK, r"^SYM\['nPM1304_CSP35'\]"), 'mk_split': (MK, r'^BAND_SPLIT = \['), 'mk_u2': (MK, r"^part\('U2'"),
    'mk_u10': (MK, r"^part\('U10'"), 'mk_sym_u10': (MK, r"^SYM\['SN74AXC4T774_RSV'\]"), 'mk_u3': (MK, r"^part\('U3'"),
    'mk_sw': (MK, r'^for sw, line in'), 'mk_ja': (MK, r"^part\('J_BAND_A'"), 'mk_bt1': (MK, r"^part\('BT1'"),
    'mk_open_u2': (MK, r"^OPEN_ORDER_CODE"), 'mk_prov': (MK, r"'nPM1304_CSP35': \('A6"), 'mk_cp': (MK, r'^# pads from -Y to \+Y'),
    'gs_title': (GS, r"'Power: nPM1304'"), 'gs_rev': (GS, r'\(rev "A6"\)'),
    'ck_a61': (CK, r'^# A6-1 '), 'ck_a62': (CK, r'^# A6-2 '), 'ck_a63': (CK, r'^# A6-3 '), 'ck_a67': (CK, r'^# A6-7 '),
    'ck_a64': (CK, r'^# A6-4 '), 'ck_a69': (CK, r'^# A6-9 '), 'ck_a610': (CK, r'^# A6-10 '), 'ck_func': (CK, r"'SD_SCK': \[\('U10'"),
    'bom_u2': (BOM, r',U2,'), 'bom_u3': (BOM, r',U3,'), 'bom_u10': (BOM, r',U10,'), 'bom_u5': (BOM, r',U5,U6,'), 'bom_sw': (BOM, r',SW1,SW3,SW4,SW5,'),
    'bom_sw2': (BOM, r',SW2,'), 'bom_cap1': (BOM, r',CAP1,'), 'bom_m1': (BOM, r',M1,'), 'bom_bt1': (BOM, r',BT1,'),
    'bom_cp': (BOM, r',CP1,CP2,CP3,CP4,'), 'bom_ja': (BOM, r',J_BAND_A,'), 'bom_jb': (BOM, r',J_BAND_B,'),
    'bom_f1': (BOM, r',FLEX1,'), 'bom_f2': (BOM, r',FLEX2,'), 'bom_r71': (BOM, r',R71,'), 'bom_r72': (BOM, r',R72,'),
    'bom_l7': (BOM, r',L71,L72,'), 'bom_c71': (BOM, r',C71,'), 'bom_rt1': (BOM, r',RT1,'), 'bom_c61': (BOM, r',C61,C72,C80,C81,C82,'),
    'bom_r41': (BOM, r',R41,'), 'bom_prt': (BOM, r',PRT1,'), 'bom_hsg': (BOM, r',HSG1,'), 'bom_u9': (BOM, r',U9,'),
}.items():
    if f == BOM and p.startswith(',') and p.endswith(','):
        p = ',"?' + p[1:-1] + '"?,'
    V[k] = ln(f, p)
V['u2_rows'] = lnr(R + 'netlist.csv', r',U2,')
V['u10_rows'] = lnr(R + 'netlist.csv', r',U10,')
V['ja_rows'] = lnr(R + 'netlist.csv', r',J_BAND_A,')
V['jb_rows'] = lnr(R + 'netlist.csv', r',J_BAND_B,')
V['pu2'] = ln(R + 'parts.csv', r'^U2,'); V['pu10'] = ln(R + 'parts.csv', r'^U10,'); V['pbt1'] = ln(R + 'parts.csv', r'^BT1,')
V['pja'] = ln(R + 'parts.csv', r'^J_BAND_A,'); V['pjb'] = ln(R + 'parts.csv', r'^J_BAND_B,')
V['sym_u2'] = lnr(R + 'symbols.csv', r'^nPM1304_CSP35,'); V['sym_u10'] = lnr(R + 'symbols.csv', r'^SN74AXC4T774_RSV,')
V['op_u2'] = lnr(R + 'open-pins.csv', r'^U2,'); V['op_ja'] = lnr(R + 'open-pins.csv', r'^J_BAND_A,'); V['op_jb'] = lnr(R + 'open-pins.csv', r'^J_BAND_B,')
V['op_order'] = ln(R + 'open-pins.csv', r'^U2,,order code')
V['ad_u10'] = lnr(R + 'additions.csv', r'^(U10|C81|C82),'); V['ad_ja'] = lnr(R + 'additions.csv', r'^J_BAND_[AB],')
V['bom_cap2_was'] = ln(R + 'evidence/a6/bom_before.csv', r',CAP2,')
V['arch_68'] = ln(DES + 'architecture.md', r'^\| Microphone x2')
V['arch_chg'] = ln(DES + 'architecture.md', r'^- Charge voltage 4\.40 V')
V['arch_pc'] = ln(DES + 'architecture.md', r'^\| Power chip \| nPM1300')
V['arch_rec'] = ln(DES + 'architecture.md', r'^\| Record button \| 1 x SKTAAAE010 under its own cap, on the band at \+62')
V['arch_joy'] = ln(DES + 'architecture.md', r'^\| Joystick \| 4 x SKTAAAE010 under one cap, on the band at \+38')
V['arch_mot'] = ln(DES + 'architecture.md', r'^\| Vibration motor \| VC0720B088L, coin, flat cable tail, in the band at -38')
V['arch_wire'] = ln(DES + 'architecture.md', r'^- Wiring: two flex tails')
V['arch_cell2'] = ln(DES + 'architecture.md', r'^\| Cell \| custom curved cell')
V['bn_u1'] = ln(R + 'pcb/board-notes.md', r'^- U1 \(61 balls\)')
V['pl_u1'] = ln(DES + 'mech/thin/placement.csv', r'^main_chip,U1')
V['mcu68'] = ln(DES + 'parts/mcu.md', r'^- Not found\. The reference PCB PDF')
V['sch55'] = ln(DES + 'parts/nordic-ref-text/caaa_schematic.txt', r'^VDD:nRF supplied by 1\.8 V to 3\.6 V')
V['rn_ord'] = ln(DES + 'parts/research-npm1304.md', r'^\| Orderable part numbers')
V['rn_pin'] = ln(DES + 'parts/research-npm1304.md', r'^\| Pin or footprint compatibility')
V['rn_435'] = ln(DES + 'parts/research-npm1304.md', r'^\| Is 4\.35 V an option')
E6 = R + 'evidence/a6/'
V['cs_vcc'] = ln(E6 + 'slim2_cs-sdnand-20230403.txt', r'Power supply: Vcc = 2\.7V')
V['cs_vih'] = ln(E6 + 'slim2_cs-sdnand-20230403.txt', r'^VIH ')
V['nrf_abs'] = ln(E6 + 'mcu_nrf54l15_ds_v2.2.txt', r'VDD\+0\.3')
V['ti_ord'] = ln(E6 + 'ti_sn74axc4t774.txt', r'^SN74AXC4T774RSVR$')
V['ti_pin'] = ln(E6 + 'ti_sn74axc4t774.txt', r'Table 4-1\. Pin Functions')
V['ti_iso'] = ln(E6 + 'ti_sn74axc4t774.txt', r'^7\.3\.4 VCC Isolation')
V['ti_fn'] = ln(E6 + 'ti_sn74axc4t774.txt', r'Table 7-1\. Function Table')
V['ti_bp'] = ln(E6 + 'ti_sn74axc4t774.txt', r'^0\.1 µF$')
TL = DES + 'parts/codes_tpd4e05u06_text.log'
V['tpd_esd'] = ln(TL, r'^IEC 61000-4-2 level 4'); V['tpd_vr'] = ln(TL, r'^VRWM'); V['tpd_leak'] = ln(TL, r'^ILEAK'); V['tpd_cap'] = ln(TL, r'^IO capacitance')
V['mic_snr'] = ln(DES + 'datasheets/mic-research/im68d128b-brief.txt', r'Signal-to-noise ratio \(SNR\)')

# the table of pads, from the split
import sys
sys.path.insert(0, R)
import make_netlist as MK_
pa = ', '.join('%d %s (%s)' % (i + 1, p, n) for i, (n, p) in enumerate(zip(MK_.BAND_A, MK_.BAND_A_NAMES)))
pb = ', '.join('%d %s (%s)' % (i + 1, p, n) for i, (n, p) in enumerate(zip(MK_.BAND_B, MK_.BAND_B_NAMES)))
V['pads_a'] = pa; V['pads_b'] = pb; V['na'] = len(MK_.BAND_A); V['nb'] = len(MK_.BAND_B)

s = old
def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (a[:80], s.count(a))
    s = s.replace(a, b)

rep("then sections 7 and 14) and `design/bom.csv`.", "then sections 7 and 14) and `design/bom.csv`. A6 (2026-11-10, later): sections 17.11, 17.12 and 17.13 are read too; section 11 lists the A6 changes.")
rep("(365 rows, 91 nets, 15 no-connect pins)", "(@@rows@@ rows, @@nets@@ nets, @@nc@@ no-connect pins)")
rep("(113 parts)", "(@@parts@@ parts)")
rep("pins of each of the 26 part symbols (ring.kicad_sym adds PWR_FLAG: 27 symbols)", "pins of each of the @@syms@@ part symbols (ring.kicad_sym adds PWR_FLAG: @@syms1@@ symbols)")
rep("designators added against bom.csv (34), bom.csv lines not placed (20), test pads (22)", "designators added against bom.csv (@@added@@), bom.csv designators not placed (@@np@@), test pads (@@tp@@)")
rep("every provisional pin number and every OPEN part number (89 rows)", "every provisional pin number and every OPEN part number or order code (@@open@@ rows)")
rep("title block Rev A5 on each", "title block Rev A6 on each")
rep("| `make_netlist.py` | writes the source tables below; every pin assignment is in this one file, with its source named next to it |",
    "| `make_netlist.py` | writes the source tables below; every pin assignment is in this one file, with its source named next to it; the table `BAND_SPLIT` at its top says which flex tail carries which line |")
rep("U2 nPM1300 with its passives C71 to C80, L71, L72, R71, R72, R57, R58, as in A3.",
    "U2 nPM1304 (A6, architecture 17.13) with the passives of the nPM1300 kit design C71 to C80, L71, L72, R71, R72, R57, R58, each marked in bom.csv 'to confirm against the nPM1304 product specification' (S18); no order code for U2.")
rep(", 2 DAT3 = SD_CS (D9), 3 CLK = SD_SCK (A9), 4 VSS, 5 CMD = SD_MOSI (B10), 6 DAT0 = SD_MISO (D10), 7 DAT1, 8 VCC = VDD_SD. 47 kohm pull-ups to VDD_SD on DAT0 (R60), DAT1 (R63), DAT2 (R64), DAT3/CS (R65); C60 4.7 uF and C61 100 nF on VDD_SD (W3, unchanged).",
    ", 2 DAT3 = SDC_CS, 3 CLK = SDC_SCK, 4 VSS, 5 CMD = SDC_MOSI, 6 DAT0 = SDC_MISO, 7 DAT1, 8 VCC = VDD_SD. A6: the four bus lines no longer join the chip balls directly: U10 (SN74AXC4T774RSVR) carries SD_SCK (A9), SD_MOSI (B10), SD_CS (D9) from the 1.8 V side to the card side nets SDC_SCK, SDC_MOSI, SDC_CS and SDC_MISO back to SD_MISO (D10); see section 11, F07. 47 kohm pull-ups to VDD_SD on DAT0 (R60 on SDC_MISO), DAT1 (R63), DAT2 (R64), DAT3/CS (R65 on SDC_CS); C60 4.7 uF and C61 100 nF on VDD_SD (W3).")
i0 = s.index("**Band (sheet 8, new).**"); i1 = s.index("**USB protection and test pads")
s = s[:i0] + ("**Band (sheet 8).** A6: the split of lines between the two tails is the table `BAND_SPLIT` at the top of `make_netlist.py` (section 11, change e). J_BAND_A (joystick side, @@na@@ pads): @@pads_a@@. J_BAND_B (other tail, @@nb@@ pads): @@pads_b@@. Behind them: SW1 UP, SW3 DOWN, SW4 LEFT, SW5 RIGHT, each one SKTAAAE010 with terminal P1 on its line and P2 on ground; SW2 on BTN_REC is the switch under the centre of the joystick nub (architecture 17.11; there is no record button); M1 VC0720B088L, + on VDD_3V0, - on MOTOR_DRV; BT1 the curved cell, + on VBAT, - on ground; RT1 10 kohm NTC from NTC to ground, in the band at the cell; CP1 to CP4 the charging pads, VBUS, D-, D+, GND in order from -Y to +Y, on the inside face of the band (architecture 17.12). The pad order and pad numbers of the two tails are this schematic's own definition (not a maker pin).\n\n") + s[i1:]
rep("Added designators (34), each with its reason", "Added designators (@@added@@), each with its reason")
rep("SW3, SW4, SW5. Test pads TP20", "SW3, SW4, SW5; U10, C81, C82 (A6). Test pads TP20")
i0 = s.index("For the lead: the live bom.csv still lists J2 and J3"); i1 = s.index("## 5. Open pins")
s = s[:i0] + "`make_netlist.py` copies maker part numbers from bom.csv where it names one (U5 and U6 read IM68D128BV01XTMA1 there). U2 has none on purpose (section 11, change a).\n\n" + s[i1:]
i0 = s.index("## 5. Open pins"); i1 = s.index("## 6. ERC result")
s = s[:i0] + """## 5. Open pins

`open-pins.csv` holds @@open@@ rows: @@open_pins@@ provisional pin numbers and @@open_other@@ rows for a part number or order code that is OPEN (L71, L72, RT1, the U2 order code):
- U2 nPM1304: @@open_u2@@ pins, every one (A6). The names are the nPM1300's from the DK schematic; the numbers P1 to P33 are placeholders, not balls (the CSP has 35 balls).
- J_BAND_A (@@na@@ pads) and J_BAND_B (@@nb@@ pads): the pad order is this schematic's own definition (A6 lists them: the split is confirmed by the lead after the inside model).
- U5, U6 IM68D128B: 5 pins each. Names Clock, VDD, Ground, Data, Select as given in the brief; the IM68D128B brief (`datasheets/mic-research/im68d128b-brief.txt`) gives no pin table. P1 to P5 are placeholders.
- SW1 to SW5 SKTAAAE010: 2 terminals each (10 pins); the Alps spec KTA-601 (7 pages) gives no terminal numbers or drawing (open item S9).
- J1: 15 positions; Hirose FH35C-15S-0.3SHW(50) selected, its drawing not read; position k assumed = tail contact k.
- DISP1 pins 3 (MTP) and 4 (VCI): the Tailor table prints "4 MTP, 4 VCI" and no pin 3; order kept as printed.
- Q1, Q2 (G, S, D pad numbers), LED1 (anode, cathode), M1 (plus, minus and tail contact numbers: VC0720B088L has an FPC tail, no polarity printed), BT1 (tabs), X1, X2.
- Not provisional: U10 (pin numbers equal the RSV column of the TI table, check A6-7), U3 (maker table, A5-7).

""" + s[i1:]
rep("Power flags unchanged: PWR_FLAG on GND (power sheet) and on U1_VBUS (main sheet).", "Power flags unchanged: PWR_FLAG on GND (power sheet) and on U1_VBUS (main sheet). A6 result: section 11, change (check 1).")
rep("Section 17 wins: J_BAND_A has 6 pads.", "Section 17 wins: J_BAND_A has 6 pads. A6: superseded by 17.11 and 17.12: J_BAND_A has @@na@@ pads and J_BAND_B @@nb@@ (section 11).")
rep("- Switch designators: SW1 UP, SW2 record (keeps the bom.csv designator), SW3 DOWN", "- Switch designators: SW1 UP, SW2 centre switch under the joystick nub (keeps the bom.csv designator), SW3 DOWN")
rep("10. The charger setting: 32 mA is above 1 C for a 20 to 26 mAh cell (architecture 17.5, open item S12).",
    "10. The charger setting: 15 mA and 4.35 V on the nPM1304 (architecture 17.13, 1 C of the smallest cell of the range) until Grepow states the cell's own limit (open item S12). WAS: the nPM1300 could not charge below 32 mA, above 1 C for this cell (architecture 17.5).")
rep("J_BAND_B pads 7 and 8", "J_BAND_B pads 5 and 6")
rep("13. Four tact switches closing in pairs for a centre press (B6): no schematic part; firmware.", "13. Centre press: SW2 under the nub's centre (architecture 17.11, first choice). Second choice, if it does not fit between the four direction switches: two opposite switches closing within 40 ms (B6), firmware only.")
rep("## 10. A5 changes\n", "## 10. A5 changes\n\nA6: rows 5, 9 and 10 of the table are superseded by checks A6-2, A6-9 and A6-10 (section 11). `prove_a5.sh` and `prove_fail.sh` describe the A5 and A3 states; they are not files of this task and were not rerun.\n")
i0 = s.index("RESULT: done, check_netlist.py exit 0")
s = s[:i0].rstrip('\n') + '\n'
s = s.replace('@@syms1@@', str(V['syms'] + 1))

new = open(R + 'evidence/a6/notes_a6_section.md').read()
s += '\n' + new
for k, v in V.items():
    s = s.replace('@@%s@@' % k, str(v))
left = re.findall(r'@@\w+@@', s)
assert not left, left
open(R + 'sch-notes.md', 'w').write(s)
print('written', len(s))
