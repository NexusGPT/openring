p=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/check_netlist.py")
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
rep('"""Checks netlist.csv against the architecture (A2) and bom.csv,','"""Checks netlist.csv against the architecture (A5-draft, sections 7, 14, 16, 17) and bom.csv,')
# FUNC
a=s.index("FUNC = {"); b=s.index("n7 = 0")
s=s[:a]+'''FUNC = {
    'MIC_A_CLK': [('U5', 'CLOCK'), ('U6', 'CLOCK')],
    'MIC_A_DATA': [('R31', '~'), ('R32', '~')],
    'XL1': [('X2', 'X1')], 'XL2': [('X2', 'X2')],
    'SD_SCK': [('U3', 'CLK')], 'SD_MOSI': [('U3', 'CMD')], 'SD_MISO': [('U3', 'DAT0')], 'SD_CS': [('U3', 'DAT3')],
    'LCD_SCK': [('DISP1', 'SCL')], 'LCD_MOSI': [('DISP1', 'SDA')], 'LCD_CS': [('DISP1', 'CS')],
    'LCD_DCX': [('DISP1', 'RS')], 'LCD_RST': [('DISP1', 'RESX')], 'LCD_TE': [('DISP1', 'TE')],
    'PMIC_SDA': [('U2', 'SDA')], 'PMIC_SCL': [('U2', 'SCL')], 'PMIC_INT': [('U2', 'GPIO0')],
    'OLED_PWR_EN': [('U4', 'AVDDEN')],
    'BTN_REC': [('SW2', '~')], 'JOY_UP': [('SW1', '~')], 'JOY_DOWN': [('SW3', '~')],
    'JOY_LEFT': [('SW4', '~')], 'JOY_RIGHT': [('SW5', '~')],
    'MOTOR': [('R61', '~')], 'DBG_TX': [('TP1', '1')], 'DBG_RX': [('TP2', '1')],
    'USB_DN': [('CP2', '1'), ('U9', 'D1-')], 'USB_DP': [('CP3', '1'), ('U9', 'D1+')],
    'VBUS': [('CP1', '1')], 'SWDCLK': [('TP3', '1')], 'SWDIO': [('TP4', '1')], 'NRESET': [('TP5', '1')],
    'ANT': [('L2', '~')],
}
# A5 (architecture 16.6, 17.4): these three section 7 signals are spare pins on a test pad only
A5_SPARE = {'MIC_B_CLK': 'TP20', 'MIC_B_DATA': 'TP21', 'JOY_CENTER': 'TP22'}
'''+s[b:]
rep("    if s in ('VBUS',):\n","    if s in A5_SPARE:\n        netname = net_at('U1', ball)\n        mem = {r['reference'] for r in nets.get(netname, [])}\n        if netname != s or mem != {'U1', A5_SPARE[s]}:\n            fail('A5 section 17: %s ball %s net %r members %s, want only U1 and %s' % (s, ball, netname, sorted(mem), A5_SPARE[s])); continue\n        n7 += 1; continue\n    if s in ('VBUS',):\n")
# second level
a=s.index("# second level: mic data resistors"); b=s.index("# contact pad order from -Y")
s=s[:a]+'''# second level: mic data resistors reach the mic DATA pins
for r, u in (('R31', 'U5'), ('R32', 'U6')):
    if (u, 'DATA') not in endpoints(net_at(r, '1')) | endpoints(net_at(r, '2')):
        fail('%s does not reach %s DATA' % (r, u))
# (removed in A5: the check that each JOY line passes the joystick wire link J2-wire-J3; J2, J3 and W5 to W10
# no longer exist, check A5-9 below checks the flex tail J_BAND_A instead)

'''+s[b:]
# LR check
a=s.index("# ---------------------------------------------------------------- (f) microphone LR"); b=s.index("# ---------------------------------------------------------------- (g) ball H8")
s=s[:a]+'''# ---------------------------------------------------------------- (f) microphone SELECT (was LR)
for u, want in (('U5', 'GND'), ('U6', 'VDD_MIC')):
    n = [r['net'] for r in rows if r['reference'] == u and r['pin_name'] == 'SELECT']
    fail('%s SELECT on %s, want %s' % (u, n, want)) if n != [want] else ok('%s SELECT on %s' % (u, want))

'''+s[b:]
# A5 section
a=s.index("# ---------------------------------------------------------------- (h) KiCad's own netlist")
A5 = r'''# ---------------------------------------------------------------- (i) A5 changes (architecture 16.4, 16.6, 17.3, 17.4)
def refs_on(net):
    return {r['reference'] for r in nets.get(net, [])}


def netof(ref, pin):
    return net_at(ref, pin)


def a5(tag, cond, good, bad):
    ok('%s %s' % (tag, good)) if cond else fail('%s %s' % (tag, bad))


sym_of = {ref: p['symbol'] for ref, p in parts.items()}
band_a = ['JOY_UP', 'JOY_DOWN', 'JOY_LEFT', 'JOY_RIGHT', 'BTN_REC', 'GND']
band_b = ['MOTOR_DRV', 'VDD_3V0', 'VBAT', 'GND', 'NTC', 'VBUS', 'USB_DN', 'USB_DP', 'GND']

# A5-1 microphones: two IM68D128B on the A pair, SELECT to ground and to VDD_MIC, 100 ohm on DATA, decoupling
mic_refs = sorted(r for r, sy in sym_of.items() if sy == 'IM68D128B')
okm = mic_refs == ['U5', 'U6'] and not [r for r, sy in sym_of.items() if sy.startswith('IM73D')]
okm = okm and all(netof(u, p) == n for u, p, n in (
    ('U5', 'P1', 'MIC_A_CLK'), ('U6', 'P1', 'MIC_A_CLK'), ('U5', 'P5', 'GND'), ('U6', 'P5', 'VDD_MIC'),
    ('U5', 'P2', 'VDD_MIC'), ('U6', 'P2', 'VDD_MIC'), ('U5', 'P3', 'GND'), ('U6', 'P3', 'GND')))
okm = okm and net_at('U1', 'F1') == 'MIC_A_CLK' and net_at('U1', 'F2') == 'MIC_A_DATA'
okm = okm and all(netof(r, '1') in ('MIC1_DATA', 'MIC2_DATA') and netof(r, '2') == 'MIC_A_DATA' for r in ('R31', 'R32'))
okm = okm and all((netof(c, '1'), netof(c, '2')) == ('VDD_MIC', 'GND') for c in ('C31', 'C32', 'C35', 'C36'))
a5('A5-1', okm, 'two IM68D128B (U5 SELECT GND, U6 SELECT VDD_MIC) on MIC_A_CLK F1 and MIC_A_DATA F2, R31 R32 100R, C31 C32 C35 C36',
   'microphones wrong: %s' % mic_refs)

# A5-2 second pair and its decoupling gone; MIC_B_CLK E6 and MIC_B_DATA D7 only on test pads
gone = ['U7', 'U8', 'R33', 'R34', 'C33', 'C34', 'C37', 'C38']
left = [g for g in gone if g in parts or any(r['reference'] == g for r in rows)]
okb = not left and not {'MIC3_DATA', 'MIC4_DATA'} & set(nets)
okb = okb and refs_on('MIC_B_CLK') == {'U1', 'TP20'} and refs_on('MIC_B_DATA') == {'U1', 'TP21'}
okb = okb and net_at('U1', 'E6') == 'MIC_B_CLK' and net_at('U1', 'D7') == 'MIC_B_DATA'
a5('A5-2', okb, 'U7 U8 R33 R34 C33 C34 C37 C38 absent; E6 MIC_B_CLK and D7 MIC_B_DATA reach only test pads TP20 and TP21',
   'second microphone pair not removed or MIC_B not test pad only: still present %s' % left)

# A5-3 joystick: no 5-way part; four SKTAAAE010, each between its line and ground, no pull-up or protection part
oj = not [r for r, sy in sym_of.items() if sy == 'SKRHADE010']
for sw, line, ball in (('SW1', 'JOY_UP', 'H1'), ('SW3', 'JOY_DOWN', 'G2'), ('SW4', 'JOY_LEFT', 'G1'), ('SW5', 'JOY_RIGHT', 'G10')):
    oj = oj and sym_of.get(sw) == 'SKTAAAE010' and netof(sw, 'P1') == line and netof(sw, 'P2') == 'GND'
    oj = oj and net_at('U1', ball) == line and refs_on(line) == {'U1', 'J_BAND_A', sw}
a5('A5-3', oj, 'no SKRHADE010; SW1 UP, SW3 DOWN, SW4 LEFT, SW5 RIGHT each line to GND, each line holds only U1, J_BAND_A and its switch (no pull-up, no protection part, as the old lines)',
   'joystick wrong (5-way part, switch wiring, or a part on a JOY line)')

# A5-4 JOY_CENTER H4 on a test pad only
a5('A5-4', net_at('U1', 'H4') == 'JOY_CENTER' and refs_on('JOY_CENTER') == {'U1', 'TP22'},
   'JOY_CENTER (H4) reaches only test pad TP22', 'JOY_CENTER not on a test pad only: %s' % sorted(refs_on('JOY_CENTER')))

# A5-5 record button: one SKTAAAE010 on BTN_REC, EVPAVAA1A gone, five SKTAAAE010 in all
n_sk = sorted(r for r, sy in sym_of.items() if sy == 'SKTAAAE010')
orb = sym_of.get('SW2') == 'SKTAAAE010' and netof('SW2', 'P1') == 'BTN_REC' and netof('SW2', 'P2') == 'GND'
orb = orb and net_at('U1', 'H2') == 'BTN_REC' and refs_on('BTN_REC') == {'U1', 'J_BAND_A', 'SW2'}
orb = orb and not [r for r, sy in sym_of.items() if sy == 'EVPAVAA1A'] and n_sk == ['SW1', 'SW2', 'SW3', 'SW4', 'SW5']
a5('A5-5', orb, 'SW2 SKTAAAE010 BTN_REC (H2) to GND, no EVPAVAA1A, 5 SKTAAAE010 in all', 'record button wrong: %s' % n_sk)

# A5-6 motor: M1 = VC0720B088L, circuit of W6 unchanged
om = parts.get('M1', {}).get('value') == 'VC0720B088L' and parts.get('M1', {}).get('mpn') == 'VC0720B088L'
om = om and (netof('M1', 'P1'), netof('M1', 'P2')) == ('VDD_3V0', 'MOTOR_DRV')
om = om and (netof('Q1', 'D'), netof('Q1', 'S'), netof('Q1', 'G')) == ('MOTOR_DRV', 'GND', 'MOTOR_G')
om = om and (netof('D1', '1'), netof('D1', '2')) == ('VDD_3V0', 'MOTOR_DRV')
om = om and (netof('R61', '1'), netof('R61', '2')) == ('MOTOR', 'MOTOR_G') and (netof('R62', '1'), netof('R62', '2')) == ('MOTOR_G', 'GND')
om = om and net_at('U1', 'F6') == 'MOTOR' and parts['R61']['value'] == '100R' and parts['R62']['value'] == '100k'
a5('A5-6', om, 'M1 = VC0720B088L; W6 circuit unchanged (F6 - R61 - Q1 gate, R62, D1 across M1, M1+ on VDD_3V0)', 'motor wrong')

# A5-7 storage: CSNP32GCR01-BOW, 8 pads numbered as the maker table, W3 wiring
SD = {'1': 'DAT2', '2': 'DAT3', '3': 'CLK', '4': 'VSS', '5': 'CMD', '6': 'DAT0', '7': 'DAT1', '8': 'VCC'}
SDNET = {'1': 'SD_DAT2', '2': 'SD_CS', '3': 'SD_SCK', '4': 'GND', '5': 'SD_MOSI', '6': 'SD_MISO', '7': 'SD_DAT1', '8': 'VDD_SD'}
os_ = parts.get('U3', {}).get('value') == 'CSNP32GCR01-BOW' and parts['U3']['symbol'] == 'CSNP32GCR01_BOW'
os_ = os_ and all(netof('U3', k) == v for k, v in SDNET.items()) and len(syms['CSNP32GCR01_BOW']) == 8
os_ = os_ and {sp['pin_number']: sp['pin_name'] for sp in syms['CSNP32GCR01_BOW']} == SD
for r, n in (('R60', 'SD_MISO'), ('R63', 'SD_DAT1'), ('R64', 'SD_DAT2'), ('R65', 'SD_CS')):
    os_ = os_ and {netof(r, '1'), netof(r, '2')} == {n, 'VDD_SD'}
try:
    import fitz
    txt = fitz.open(os.path.join(DESIGN, 'datasheets', 'slim2_cs-sdnand-20230403.pdf'))[4].get_text()
    docname = {'1': 'SDD2', '2': 'CD/SDD3', '3': 'SCLK', '4': 'VSS', '5': 'CMD', '6': 'SDD0', '7': 'SDD1', '8': 'VCC'}
    bad_doc = [k for k, v in docname.items() if not re.search(r'\n%s\n%s' % (k, re.escape(v)), txt)]
except Exception as e:  # not a pass: recorded as a failure
    bad_doc = ['cannot read maker pdf: %s' % e]
a5('A5-7', os_ and not bad_doc, 'U3 CSNP32GCR01-BOW, 8 pads numbered as the maker table (p5), W3 wiring and 4 pull-ups',
   'storage wrong or pad numbers differ from the maker table: %s' % bad_doc)

# A5-8 screen connector: 15 positions, names and order as printed in parts/slim.md 1.3
slim = open(os.path.join(DESIGN, 'parts', 'slim.md')).read()
sec13 = slim.split('### 1.3')[1].split('### 1.4')[0]
line = [l for l in sec13.splitlines() if l.startswith('- Pin table')][0]
line = line.split('As printed')[0].split('15 pins:')[1]
printed = []
for m in re.finditer(r'\b(\d+)(?:-(\d+))? ([A-Z]{2,}[A-Z0-9]*)\b', line):
    hi = int(m.group(2) or m.group(1)); lo = int(m.group(1))
    printed += [m.group(3)] * (hi - lo + 1)
W9 = ['ELVSS', 'ELVDD', None, 'VDD_3V0', 'VDD_1V8', 'SWIRE', 'LCD_TE', 'LCD_RST', 'LCD_CS', 'LCD_SCK', 'LCD_DCX', 'LCD_MOSI', 'GND', 'GND', 'GND']
o8 = len(printed) == 15 and parts.get('J1', {}).get('value') == 'FH35C-15S-0.3SHW(50)' and len(syms['FPC_15']) == 15
o8 = o8 and [sp['pin_name'] for sp in syms['TOH095XVT-01']] == printed
for k in range(1, 16):
    nd, nj = netof('DISP1', str(k)), netof('J1', 'P%d' % k)
    o8 = o8 and nd == nj and nd == W9[k - 1]
    if W9[k - 1] is None:
        o8 = o8 and nd is None and netof('J1', 'P%d' % k) is None
openpins = open(os.path.join(HERE, 'open-pins.csv')).read()
o8 = o8 and 'DISP1,3,' in openpins and 'DISP1,4,' in openpins
a5('A5-8', o8, 'J1 FH35C-15S-0.3SHW(50) 15 positions = DISP1 15 contacts in the printed order %s; pin 4 listed provisional' % ','.join(printed),
   'screen connector wrong (printed order %s)' % printed)

# A5-9 the two flex tails: counts from architecture 17.3, pads, every band part reaches the board through them
wl = [l for l in arch.split('### 17.3')[1].splitlines() if l.startswith('- Wiring:')][0]
mt = re.search(r'Thumb side: (\d+) switch lines and ground\. Other side: motor (\d+), cell (\d+) plus its temperature sensor (\d+), charging pads (\d+)', wl)
na = int(mt.group(1)) + 1 if mt else -1
nb = sum(int(mt.group(i)) for i in range(2, 6)) if mt else -1
ja = [netof('J_BAND_A', str(i + 1)) for i in range(len(syms['BAND_PADS_A']))]
jb = [netof('J_BAND_B', str(i + 1)) for i in range(len(syms['BAND_PADS_B']))]
o9 = (na, nb) == (6, 9) and ja == band_a and jb == band_b and len(ja) == na and len(jb) == nb
band_parts = ['SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'M1', 'BT1', 'RT1', 'CP1', 'CP2', 'CP3', 'CP4']
for bp in band_parts:
    for sp in syms[parts[bp]['symbol']]:
        n = netof(bp, sp['pin_number'])
        o9 = o9 and n is not None and ({'J_BAND_A', 'J_BAND_B'} & refs_on(n)) != set()
o9 = o9 and all(parts[b]['sheet'] == 'band' for b in band_parts + ['J_BAND_A', 'J_BAND_B'])
old = [r for r in ('J2', 'J3', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10') if r in parts]
o9 = o9 and not old
a5('A5-9', o9, 'J_BAND_A %d pads, J_BAND_B %d pads (counts from architecture 17.3); every pin of SW1-SW5, M1, BT1, RT1, CP1-CP4 is on a net with a tail pad; J2 J3 W1-W10 absent' % (na, nb),
   'flex tails wrong: A %s B %s counts %s %s old parts %s' % (ja, jb, na, nb, old))

# A5-10 title block A5 in every sheet file and on every PDF page
files = sorted(f for f in os.listdir(HERE) if f.startswith('ring') and f.endswith('.kicad_sch'))
notA5 = [f for f in files if '(rev "A5")' not in open(os.path.join(HERE, f)).read() or '(rev "A3")' in open(os.path.join(HERE, f)).read()]
try:
    import fitz
    pdf = fitz.open(os.path.join(HERE, 'ring-schematic.pdf'))
    pg = [i + 1 for i, p in enumerate(pdf) if not re.search(r'Rev:?\s*A5', p.get_text())]
    npg = len(pdf)
except Exception as e:
    pg, npg = ['cannot read pdf: %s' % e], -1
a5('A5-10', not notA5 and not pg and npg == len(files), 'rev A5 in %d sheet files and on all %d PDF pages' % (len(files), npg),
   'title block not A5: files %s pdf pages %s (pdf %d pages, %d files)' % (notA5, pg, npg, len(files)))

'''
s=s[:a]+A5+s[a:]
open(p,'w').write(s)
