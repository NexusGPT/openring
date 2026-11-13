"""A7 edit of check_netlist.py. Each replacement must hit exactly once."""
import sys
F = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/check_netlist.py")
s = open(F).read()
R = []
# R41 value: architecture 17.21 replaces the W5 value (W5 row still says 680 ohm; 17.21 "R41 becomes 820 ohm")
R.append(("""# recording light (A3 section 9 and W5): R41 value from the W5 row, no chip pin on the light
m = re.search(r'\\| W5 \\|[^\\n]*R41 = (\\d+) ohm', arch)
want_r41 = (m.group(1) + 'R') if m else None
got_r41 = parts.get('R41', {}).get('value')
ok('R41 = %s (W5)' % got_r41) if want_r41 and got_r41 == want_r41 else fail('R41 is %r, W5 says %r' % (got_r41, want_r41))""",
"""# recording light: R41 value read from architecture 17.21 ("R41 becomes N ohm"), which replaces the W5 value (A7)
m = re.search(r'### 17\\.21 [^\\n]*\\n(?:[^\\n]*\\n)*?[^\\n]*R41 becomes (\\d+) ohm', arch)
want_r41 = (m.group(1) + 'R') if m else None
got_r41 = parts.get('R41', {}).get('value')
ok('R41 = %s (17.21)' % got_r41) if want_r41 and got_r41 == want_r41 else fail('R41 is %r, 17.21 says %r' % (got_r41, want_r41))"""))
# A5-1 -> A7-3 microphones
R.append(("""# A5-1 microphones: two IM68D128B on the A pair, SELECT to ground and to VDD_MIC, 100 ohm on DATA, decoupling
mic_refs = sorted(r for r, sy in sym_of.items() if sy == 'IM68D128B')
okm = mic_refs == ['U5', 'U6'] and not [r for r, sy in sym_of.items() if sy.startswith('IM73D')]
okm = okm and all(netof(u, p) == n for u, p, n in (
    ('U5', 'P1', 'MIC_A_CLK'), ('U6', 'P1', 'MIC_A_CLK'), ('U5', 'P5', 'GND'), ('U6', 'P5', 'VDD_MIC'),
    ('U5', 'P2', 'VDD_MIC'), ('U6', 'P2', 'VDD_MIC'), ('U5', 'P3', 'GND'), ('U6', 'P3', 'GND')))
okm = okm and net_at('U1', 'F1') == 'MIC_A_CLK' and net_at('U1', 'F2') == 'MIC_A_DATA'
okm = okm and all(netof(r, '1') in ('MIC1_DATA', 'MIC2_DATA') and netof(r, '2') == 'MIC_A_DATA' for r in ('R31', 'R32'))
okm = okm and all((netof(c, '1'), netof(c, '2')) == ('VDD_MIC', 'GND') for c in ('C31', 'C32', 'C35', 'C36'))
a5('A5-1', okm, 'two IM68D128B (U5 SELECT GND, U6 SELECT VDD_MIC) on MIC_A_CLK F1 and MIC_A_DATA F2, R31 R32 100R, C31 C32 C35 C36',
   'microphones wrong: %s' % mic_refs)""",
"""# A7-3 (was A5-1) microphones: two Knowles SPK0641HT4H-1 (architecture 17.19), 8 pins numbered as the Knowles pin table
# (sheet 6, read here from the saved text copy), SELECT of U5 to ground and of U6 to VDD_MIC, 100 ohm on DATA, decoupling
mic_refs = sorted(r for r, sy in sym_of.items() if sy == 'SPK0641HT4H_1')
bad3 = [] if mic_refs == ['U5', 'U6'] else ['microphone parts %s' % mic_refs]
bad3 += ['old microphone symbol %s' % r for r, sy in sym_of.items() if sy.startswith('IM73D') or sy.startswith('IM68D')]
try:
    kt = open(os.path.join(DESIGN, 'mech', 'mic-path', 'datasheets', 'knowles-spk0641ht4h-1_chipsmall.txt')).read()
    kn = {m.group(1): m.group(2) for m in re.finditer(r'^\\s+([1-8])\\s+(DATA|CLOCK|SELECT|Vdd|GROUND)\\s', kt, re.M)}
except Exception as e:
    kt = ''; kn = {}; bad3.append('cannot read the Knowles text copy: %s' % e)
mine3 = {sp['pin_number']: sp['pin_name'] for sp in syms['SPK0641HT4H_1']}
if len(kn) != 8 or {k: v.upper() for k, v in kn.items()} != mine3:
    bad3.append('symbol pins %s against the Knowles table %s' % (mine3, kn))
for u, sel, dl in (('U5', 'GND', 'MIC1_DATA'), ('U6', 'VDD_MIC', 'MIC2_DATA')):
    want = {'1': dl, '2': 'MIC_A_CLK', '3': sel, '4': 'VDD_MIC', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND'}
    bad3 += ['%s pin %s on %s want %s' % (u, k, netof(u, k), v) for k, v in want.items() if netof(u, k) != v]
    bad3 += ['%s value or part %r %r' % (u, parts[u]['value'], parts[u]['mpn'])] if (parts.get(u, {}).get('value'), parts.get(u, {}).get('mpn')) != ('SPK0641HT4H-1', 'SPK0641HT4H-1') else []
bad3 += [] if net_at('U1', 'F1') == 'MIC_A_CLK' and net_at('U1', 'F2') == 'MIC_A_DATA' else ['F1 F2 not on MIC_A_CLK MIC_A_DATA']
bad3 += ['%s not between MICn_DATA and MIC_A_DATA' % r for r in ('R31', 'R32') if not (netof(r, '1') in ('MIC1_DATA', 'MIC2_DATA') and netof(r, '2') == 'MIC_A_DATA')]
bad3 += ['%s not VDD_MIC to GND' % c for c in ('C31', 'C32', 'C35', 'C36') if (netof(c, '1'), netof(c, '2')) != ('VDD_MIC', 'GND')]
bad3 += ['%s value %r is not marked Class 1 (Knowles sheet 4)' % (c, parts[c]['value']) for c in ('C35', 'C36') if 'Class 1' not in parts[c]['value']]
bad3 += ['microphone rows left in open-pins.csv'] if any(r.startswith('U5,') or r.startswith('U6,') for r in open(os.path.join(HERE, 'open-pins.csv')).read().split('\\n')) else []
a5('A7-3', not bad3, 'two SPK0641HT4H-1, 8 pins equal the Knowles table (1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5-8 GROUND all on GND), U5 SELECT GND, U6 SELECT VDD_MIC, CLOCK on MIC_A_CLK F1, DATA through R31 R32 to MIC_A_DATA F2, C31 C32 C35 C36, C35 C36 Class 1, no microphone pin open',
   'microphones wrong: %s' % bad3)"""))
# A5-6 -> A7-2 motor
R.append(("""# A5-6 motor: M1 = VC0720B088L, circuit of W6 unchanged
om = parts.get('M1', {}).get('value') == 'VC0720B088L' and parts.get('M1', {}).get('mpn') == 'VC0720B088L'
om = om and (netof('M1', 'P1'), netof('M1', 'P2')) == ('VDD_3V0', 'MOTOR_DRV')
om = om and (netof('Q1', 'D'), netof('Q1', 'S'), netof('Q1', 'G')) == ('MOTOR_DRV', 'GND', 'MOTOR_G')
om = om and (netof('D1', '1'), netof('D1', '2')) == ('VDD_3V0', 'MOTOR_DRV')
om = om and (netof('R61', '1'), netof('R61', '2')) == ('MOTOR', 'MOTOR_G') and (netof('R62', '1'), netof('R62', '2')) == ('MOTOR_G', 'GND')
om = om and net_at('U1', 'F6') == 'MOTOR' and parts['R61']['value'] == '100R' and parts['R62']['value'] == '100k'
a5('A5-6', om, 'M1 = VC0720B088L; W6 circuit unchanged (F6 - R61 - Q1 gate, R62, D1 across M1, M1+ on VDD_3V0)', 'motor wrong')""",
"""# A7-2 (was A5-6) motor: architecture 17.16 and 17.22, motor-drive.md 2.1: M1 W0525AB001D between VMOT and GND; U11
# TLV75530PDQNR IN on VBAT, OUT on VMOT, EN on MOT_EN (R61 from MOTOR F6, R62 to GND); C83 VBAT-GND, C84 VMOT-GND; no Q1, no D1
bad2 = []
bad2 += [] if (parts.get('M1', {}).get('value'), parts.get('M1', {}).get('mpn')) == ('W0525AB001D', 'W0525AB001D') else ['M1 part %r' % parts.get('M1')]
bad2 += [] if (netof('M1', 'P1'), netof('M1', 'P2')) == ('VMOT', 'GND') else ['M1 on %s %s' % (netof('M1', 'P1'), netof('M1', 'P2'))]
u11 = {'1': 'VMOT', '2': 'GND', '3': 'MOT_EN', '4': 'VBAT', 'EP': 'GND'}
bad2 += [] if parts.get('U11', {}).get('mpn') == 'TLV75530PDQNR' else ['U11 part %r' % parts.get('U11')]
bad2 += ['U11 pin %s on %s want %s' % (k, netof('U11', k), v) for k, v in u11.items() if netof('U11', k) != v]
bad2 += [] if {sp['pin_number']: sp['pin_name'] for sp in syms['TLV75530P_DQN']} == {'1': 'OUT', '2': 'GND', '3': 'EN', '4': 'IN', 'EP': 'PAD'} else ['U11 symbol pins']
bad2 += ['%s not %s to GND' % (c, n) for c, n in (('C83', 'VBAT'), ('C84', 'VMOT')) if (netof(c, '1'), netof(c, '2')) != (n, 'GND')]
bad2 += ['%s value %r' % (c, parts.get(c, {}).get('value')) for c in ('C83', 'C84') if parts.get(c, {}).get('value') != '10uF']
bad2 += [] if (netof('R61', '1'), netof('R61', '2')) == ('MOTOR', 'MOT_EN') and (netof('R62', '1'), netof('R62', '2')) == ('MOT_EN', 'GND') else ['R61 R62 wiring']
bad2 += [] if net_at('U1', 'F6') == 'MOTOR' and parts['R61']['value'] == '100R' and parts['R62']['value'] == '100k' else ['F6 or R61 R62 values']
bad2 += [] if refs_on('MOT_EN') == {'R61', 'R62', 'U11'} and refs_on('MOTOR') == {'U1', 'R61'} else ['MOT_EN %s MOTOR %s' % (sorted(refs_on('MOT_EN')), sorted(refs_on('MOTOR')))]
bad2 += [] if refs_on('VMOT') == {'U11', 'C84', 'M1', 'J_BAND_A'} else ['VMOT members %s' % sorted(refs_on('VMOT'))]
bad2 += ['%s still present' % r for r in ('Q1', 'D1') if r in parts or any(x['reference'] == r for x in rows)]
bad2 += ['net %s still present' % n for n in ('MOTOR_DRV', 'MOTOR_G') if n in nets]
bad2 += ['M1 or the motor regulator on VDD_3V0'] if refs_on('VDD_3V0') & {'M1', 'U11', 'C84'} else []
a5('A7-2', not bad2, 'M1 W0525AB001D on VMOT and GND; U11 TLV75530PDQNR (1 OUT VMOT, 2 GND, 3 EN MOT_EN, 4 IN VBAT, pad GND); R61 MOTOR-MOT_EN 100R, R62 MOT_EN-GND 100k; C83 VBAT, C84 VMOT 10uF; Q1, D1, MOTOR_DRV, MOTOR_G absent',
   'motor drive wrong: %s' % bad2)"""))
R.append(("o9 = o9 and one(JOYSET) and one(CELLSET) and one(['MOTOR_DRV', 'VDD_3V0'])",
          "o9 = o9 and one(JOYSET) and one(CELLSET) and one(['VMOT'])  # A7: motor return is a ground pad (motor-drive.md W2)"))
R.append(("o9 = o9 and side['JOY_UP'] != side['VBAT']                       # joystick side and cell side are different tails",
          "o9 = o9 and side['JOY_UP'] != side['VBAT']                       # joystick side and cell side are different tails\no9 = o9 and side['VMOT'] == side['JOY_UP']                       # A7 (17.16): the motor is on tail A, the joystick side"))
R.append(("""a5('A6-9', o9, 'J_BAND_A %d pads and J_BAND_B %d pads equal the BAND_SPLIT table; joystick lines and SW2 on one tail, cell/NTC/VBUS/D-/D+ on the other, motor pair together, only GND on both;""",
          """o9 = o9 and len(ja) == 8 and len(jb) == 7 and ja.count('GND') == 2  # A7: 8 and 7 pads (17.14), MOT- and GND on ground (W2)
a5('A6-9', o9, 'J_BAND_A %d pads and J_BAND_B %d pads equal the BAND_SPLIT table; joystick lines, SW2 and VMOT on one tail, cell/NTC/VBUS/D-/D+ on the other, only GND on both, two GND pads on A;"""))
# A6-10 -> A7-10
R.append(("""# A6-10 title block A6 in every sheet file and on every PDF page
files = sorted(f for f in os.listdir(SCHDIR) if f.startswith('ring') and f.endswith('.kicad_sch'))
notA6 = [f for f in files if '(rev "A6")' not in open(os.path.join(SCHDIR, f)).read()]""",
"""# A7-10 (was A6-10) title block A7 in every sheet file and on every PDF page
files = sorted(f for f in os.listdir(SCHDIR) if f.startswith('ring') and f.endswith('.kicad_sch'))
notA6 = [f for f in files if '(rev "A7")' not in open(os.path.join(SCHDIR, f)).read()]"""))
R.append(("""    pg = [i + 1 for i, p in enumerate(pdf) if not re.search(r'Rev:?\\s*A6', p.get_text())]""",
          """    pg = [i + 1 for i, p in enumerate(pdf) if not re.search(r'Rev:?\\s*A7', p.get_text())]"""))
R.append(("""a5('A6-10', not notA6 and not pg and npg == len(files), 'rev A6 in %d sheet files and on all %d PDF pages' % (len(files), npg),
   'title block not A6: files %s pdf pages %s (pdf %d pages, %d files)' % (notA6, pg, npg, len(files)))""",
          """a5('A7-10', not notA6 and not pg and npg == len(files), 'rev A7 in %d sheet files and on all %d PDF pages' % (len(files), npg),
   'title block not A7: files %s pdf pages %s (pdf %d pages, %d files)' % (notA6, pg, npg, len(files)))"""))
# A6-1 -> A7-1
R.append(("""# A6-1 (a) U2 is the nPM1304 35-ball CSP; no order code is invented; every ball is listed provisional
openrows = list(csv.DictReader(open(os.path.join(HERE, 'open-pins.csv'))))
u2 = parts.get('U2', {})
o1 = u2.get('symbol') == 'nPM1304_CSP35' and u2.get('value') == 'nPM1304' and u2.get('mpn') == '' and 'nPM1300' not in ' '.join(u2.values())
u2pins = {sp['pin_number'] for sp in syms['nPM1304_CSP35']}
listed = {r['pin_number'] for r in openrows if r['reference'] == 'U2' and r['pin_number']}
o1 = o1 and listed == u2pins and len(u2pins) > 0
o1 = o1 and any(r['reference'] == 'U2' and r['pin_name'] == 'order code' and 'S18' in r['why_open'] for r in openrows)
bomrows = list(csv.DictReader(open(os.path.join(DESIGN, 'bom.csv'))))
bu2 = [r for r in bomrows if r['reference'] == 'U2']
o1 = o1 and len(bu2) == 1 and bu2[0]['maker_part_number'] == '' and 'S18' in bu2[0]['open_action'] and 'nPM1304' in bu2[0]['key_figures']
a5('A6-1', o1, 'U2 nPM1304 CSP-35 (symbol, value), order code empty in parts.csv and bom.csv with open action S18, all %d U2 balls listed provisional in open-pins.csv' % len(u2pins),
   'U2 not the nPM1304 as required (symbol %r value %r mpn %r; listed %d of %d pins)' % (u2.get('symbol'), u2.get('value'), u2.get('mpn'), len(listed), len(u2pins)))""",
"""# A7-1 (was A6-1) U2 nPM1304-CAAA: every ball number and name equals npm1304-balls.csv (Nordic Table 33, page 153);
# no placeholder P<n>; no GPIO4; no U2 row left in open-pins.csv; order code nPM1304-CAAA-R7 (Table 50, page 168)
openrows = list(csv.DictReader(open(os.path.join(HERE, 'open-pins.csv'))))
u2 = parts.get('U2', {})
bad1 = [] if (u2.get('symbol'), u2.get('value'), u2.get('mpn')) == ('nPM1304_CSP35', 'nPM1304', 'nPM1304-CAAA-R7') else ['U2 part %r' % u2]
nordic = [(r['ball'], r['name']) for r in csv.DictReader(open(os.path.join(HERE, 'npm1304-balls.csv')))]
mine1 = [(sp['pin_number'], sp['pin_name']) for sp in syms['nPM1304_CSP35']]
bad1 += [] if sorted(mine1) == sorted(nordic) and len(nordic) == 35 else ['U2 pins differ from Table 33: only mine %s only Nordic %s' % (sorted(set(mine1) - set(nordic)), sorted(set(nordic) - set(mine1)))]
bad1 += ['placeholder pin %s' % p for p, _ in mine1 if re.fullmatch(r'P\\d+', p)]
bad1 += ['GPIO4 present'] if any(n == 'GPIO4' for _, n in mine1) or any(r['reference'] == 'U2' and r['pin_name'] == 'GPIO4' for r in rows) else []
bad1 += ['U2 rows in open-pins.csv: %d' % len([r for r in openrows if r['reference'] == 'U2'])] if any(r['reference'] == 'U2' for r in openrows) else []
WANT_U2 = {'B1': 'VBUS', 'B2': 'VBUS', 'C1': 'VSYS', 'C2': 'VSYS', 'C7': 'VSYS', 'D1': 'VBAT', 'D2': 'VBAT', 'D3': 'NTC', 'D4': 'SHPHLD',
           'D6': 'PMIC_INT', 'E3': 'PMIC_SCL', 'E5': 'PMIC_SDA', 'E4': 'VDD_1V8', 'C3': 'VBUSOUT', 'B6': 'VDD_1V8', 'B7': 'SW1',
           'A7': 'GND', 'C6': 'VDD_3V0', 'D7': 'SW2', 'E7': 'GND', 'B4': 'VDD_1V8', 'B5': 'VDD_3V0', 'A4': 'VDD_MIC', 'A5': 'VDD_SD',
           'A6': 'GND', 'E2': 'VSET1', 'E1': 'VSET2', 'A1': None, 'A2': None, 'A3': None, 'B3': None, 'C4': None, 'C5': None, 'D5': None, 'E6': None}
bad1 += ['U2 ball %s on %s want %s' % (b, netof('U2', b), n) for b, n in WANT_U2.items() if netof('U2', b) != n]
bomrows = list(csv.DictReader(open(os.path.join(DESIGN, 'bom.csv'))))
bu2 = [r for r in bomrows if r['reference'] == 'U2']
bad1 += [] if len(bu2) == 1 and bu2[0]['maker_part_number'] == 'nPM1304-CAAA-R7' else ['bom.csv U2 order code %r' % [r['maker_part_number'] for r in bu2]]
a5('A7-1', not bad1, 'U2 nPM1304-CAAA-R7: %d balls equal npm1304-balls.csv (Table 33 p153), no P<n> placeholder, no GPIO4, no U2 row in open-pins.csv, every ball on its A6 net' % len(mine1),
   'U2 wrong: %s' % bad1)

# A7-4 power chip passives against Nordic's reference (npm1304-reference.md D1 to D4)
bad4 = []
bad4 += [] if parts['C71']['value'] == '1.0uF 25V' and (netof('C71', '1'), netof('C71', '2')) == ('VBUS', 'GND') else ['C71 %r on %s' % (parts['C71']['value'], (netof('C71', '1'), netof('C71', '2')))]
bc71 = [r for r in bomrows if r['reference'] == 'C71']
bad4 += [] if len(bc71) == 1 and '25 V' in bc71[0]['value'] and bc71[0]['maker_part_number'] != 'GRM155R60J475ME47D' else ['bom.csv C71 %r' % [(r['value'], r['maker_part_number']) for r in bc71]]
for c, n, v in (('C85', 'VBAT', '2.2uF'), ('C86', 'VDD_MIC', '1.0uF'), ('C87', 'VDD_SD', '1.0uF'), ('C88', 'VSYS', '10uF')):
    bad4 += [] if parts.get(c, {}).get('value') == v and (netof(c, '1'), netof(c, '2')) == (n, 'GND') else ['%s %r on %s want %s %s' % (c, parts.get(c, {}).get('value'), (netof(c, '1'), netof(c, '2')), v, n)]
bad4 += [] if len([r for r in nets.get('VSYS', []) if r['reference'].startswith('C') and parts[r['reference']]['value'] == '10uF']) == 3 else ['VSYS does not hold three 10 uF']
a5('A7-4', not bad4, 'C71 1.0 uF 25 V on VBUS (not the 6.3 V part), C85 2.2 uF on VBAT, C86 1.0 uF on VDD_MIC, C87 1.0 uF on VDD_SD, three 10 uF on VSYS (C74, C75, C88)',
   'power chip passives wrong: %s' % bad4)

# A7-5 recording light: R41 820 ohm (17.21) and LED1 pad 1 = cathode on LED_K, pad 2 = anode on LED_A (maker p1)
bad5 = [] if parts['R41']['value'] == '820R' and (netof('R41', '1'), netof('R41', '2')) == ('VDD_3V0', 'LED_A') else ['R41 %r' % parts['R41']['value']]
bad5 += [] if {sp['pin_number']: sp['pin_name'] for sp in syms['LED_KPG1005']} == {'1': 'K', '2': 'A'} else ['LED symbol pins']
bad5 += [] if (netof('LED1', '1'), netof('LED1', '2')) == ('LED_K', 'LED_A') else ['LED1 pad 1 %s pad 2 %s' % (netof('LED1', '1'), netof('LED1', '2'))]
bad5 += [] if (netof('Q2', 'D'), netof('Q2', 'S'), netof('Q2', 'G')) == ('LED_K', 'GND', 'VDD_MIC') else ['Q2 wiring']
bad5 += ['LED1 rows in open-pins.csv'] if any(r['reference'] == 'LED1' for r in openrows) else []
br41 = [r for r in bomrows if r['reference'] == 'R41']
bad5 += [] if len(br41) == 1 and br41[0]['value'].startswith('820 ohm') else ['bom.csv R41 %r' % [r['value'] for r in br41]]
bad5 += [] if {r['reference'] for r in bomrows} >= {'LG1', 'LP1'} else ['bom.csv has no LG1 or LP1 line']
a5('A7-5', not bad5, 'R41 820R from VDD_3V0 to LED_A; LED1 pad 1 K on LED_K, pad 2 A on LED_A; Q2 gate VDD_MIC; LED1 not provisional; bom.csv R41 820 ohm, LG1 and LP1 lines',
   'recording light wrong: %s' % bad5)

# A7-8 decisions re-checked: cell value (17.15, 17.17), one control (no switch beyond SW1 to SW5), U10 C81 C82
bad8 = [] if '20-27mAh' in parts['BT1']['value'] and '18.2mAh' in parts['BT1']['value'] else ['BT1 value %r' % parts['BT1']['value']]
bbt = [r for r in bomrows if r['reference'] == 'BT1']
bad8 += [] if len(bbt) == 1 and '20 to 27 mAh' in bbt[0]['value'] and '18.2 mAh' in bbt[0]['key_figures'] else ['bom.csv BT1']
bad8 += ['switch beyond the joystick: %s' % r for r, sy in sym_of.items() if sy == 'SKTAAAE010' and r not in ('SW1', 'SW2', 'SW3', 'SW4', 'SW5')]
bad8 += ['part %s present' % r for r in ('U10', 'C81', 'C82') if r not in parts]
a5('A7-8', not bad8, 'BT1 20 to 27 mAh at US 9 with 18.2 mAh at US 7 (netlist and bom.csv); only SW1 to SW5; U10, C81, C82 present (their wiring: A6-7)',
   'kept decisions wrong: %s' % bad8)"""))
# A6-4 microphone figure -> A7-6 (the part changed: 64.5 dB(A), Knowles sheet 2)
R.append(("""bim = [r for r in bomrows if r['reference'] == 'U5,U6']
brief = open(os.path.join(DESIGN, 'datasheets', 'mic-research', 'im68d128b-brief.txt')).read()
o4 = len(bim) == 1 and '67.5 dB(A)' in bim[0]['key_figures'] and '68 dB' not in ' '.join(bim[0].values()) and re.search(r'Signal-to-noise ratio \\(SNR\\)\\s+67\\.5 dB\\(A\\)', brief) is not None
a5('A6-4', o4, 'microphone line says 67.5 dB(A) as the IM68D128B brief, no 68 dB', 'microphone figure wrong')""",
"""bim = [r for r in bomrows if r['reference'] == 'U5,U6']
o4 = len(bim) == 1 and 'SNR 64.5 dB(A)' in bim[0]['key_figures'] and bim[0]['maker_part_number'] == 'SPK0641HT4H-1' and 'IM68D128B' not in ' '.join(bim[0].values())
o4 = o4 and re.search(r'Signal to Noise Ratio\\s+SNR\\s+94 dB SPL @ 1 kHz, A-weighted\\s+-\\s+64\\.5', kt) is not None
a5('A7-6', o4, 'microphone line names SPK0641HT4H-1 with SNR 64.5 dB(A) as the Knowles sheet 2 text, no IM68D128B', 'microphone line wrong')"""))
for old, new in R:
    n = s.count(old)
    print('hits', n, repr(old[:60]))
    if n != 1:
        sys.exit('replacement does not hit exactly once')
    s = s.replace(old, new)
s = s.replace('"""Checks netlist.csv against the architecture (A5-draft, sections 7, 14, 16, 17 with 17.11 to 17.13: A6)',
              '"""Checks netlist.csv against the architecture (A5-draft, sections 7, 14, 16, 17 with 17.11 to 17.13: A6; 17.16 to 17.22: A7)')
open(F, 'w').write(s)
print('done')
