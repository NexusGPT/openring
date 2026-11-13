#!/usr/bin/env python3
"""Checks netlist.csv against the architecture (A5-draft, sections 7, 14, 16, 17 with 17.11 to 17.13: A6) and bom.csv, and against the
netlist KiCad exports from ring.kicad_sch. Exit 0 only when every check passes.
usage: check_netlist.py [netlist.csv [sheet_folder]]   (a second file lets a broken copy be tested; a folder holding
ring*.kicad_sch and ring-schematic.pdf lets check A6-10 test a broken copy)"""
import csv, os, re, subprocess, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, '..', '..'))
KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
NETFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'netlist.csv')
SCHDIR = sys.argv[2] if len(sys.argv) > 2 else HERE
FAIL = []
import make_netlist as MK  # BAND_SPLIT: the one table that says which flex tail carries which line


def fail(msg):
    FAIL.append(msg)
    print('FAIL', msg)


def ok(msg):
    print('ok  ', msg)


rows = list(csv.DictReader(open(NETFILE)))
parts = {p['reference']: p for p in csv.DictReader(open(os.path.join(HERE, 'parts.csv')))}
syms = collections.defaultdict(list)
for r in csv.DictReader(open(os.path.join(HERE, 'symbols.csv'))):
    syms[r['symbol']].append(r)
adds = list(csv.DictReader(open(os.path.join(HERE, 'additions.csv'))))
added = {a['reference'] for a in adds if a['kind'] == 'added'}
not_placed = {a['reference'] for a in adds if a['kind'] == 'bom_not_placed'}
testpads = {a['reference'] for a in adds if a['kind'] == 'testpad'}

nets = collections.defaultdict(list)
pin_of = collections.defaultdict(list)
for r in rows:
    pin_of[(r['reference'], r['pin_number'])].append(r)
    if r['pin_type'] != 'no_connect':
        nets[r['net']].append(r)


def net_at(ref, pin):
    rr = [r for r in pin_of.get((ref, pin), []) if r['pin_type'] != 'no_connect']
    return rr[0]['net'] if len(rr) == 1 else None


def endpoints(net):
    return {(r['reference'], r['pin_name']) for r in nets.get(net, [])}

# ---------------------------------------------------------------- (a) section 7 pin plan
arch = open(os.path.join(DESIGN, 'architecture.md')).read()
sec7 = arch.split('## 7.')[1].split('## 8.')[0]
table = [l for l in sec7.splitlines() if l.startswith('| ') and not l.startswith('| Signal') and not l.startswith('|---')]
plan = []
for l in table:
    c = [x.strip() for x in l.strip('|').split('|')]
    sig, pin, ball = c[0], c[1], c[2]
    if sig.startswith('Spare'):
        for pn in [p.strip() for p in pin.split(',')]:
            plan.append(('SPARE_' + pn.replace('.', '_'), pn, None))
        continue
    if ball in ('n/a', ''):
        continue
    sigs = [s.strip() for s in sig.split('/')]
    balls = [b.strip() for b in ball.split('/')]
    pins = [p.strip() for p in pin.split('/')]
    if len(sigs) != len(balls):
        fail('cannot parse section 7 row: %s' % l); continue
    for i, (s, b) in enumerate(zip(sigs, balls)):
        plan.append((s, pins[i] if i < len(pins) else pin, b))
# ball of spare pins from the ball list
balls_csv = {r['pin_name_as_printed']: r['ball'] for r in csv.DictReader(open(os.path.join(DESIGN, 'parts', 'nrf54lm20a-csp61-pins.csv')))}
NAME = {'USB D-': 'USB_DN', 'D+': 'USB_DP', 'nRESET': 'NRESET', 'XL1': 'XL1', 'XL2': 'XL2'}
# function each signal must reach (from sections 5, 7, 9 and 14)
FUNC = {
    'MIC_A_CLK': [('U5', 'CLOCK'), ('U6', 'CLOCK')],
    'MIC_A_DATA': [('R31', '~'), ('R32', '~')],
    'XL1': [('X2', 'X1')], 'XL2': [('X2', 'X2')],
    'SD_SCK': [('U10', 'A1')], 'SD_MOSI': [('U10', 'A2')], 'SD_MISO': [('U10', 'A4')], 'SD_CS': [('U10', 'A3')],  # A6 F07: through U10
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
n7 = 0
for sig, pin, ball in plan:
    s = NAME.get(sig, sig)
    if ball is None:
        ball = balls_csv.get(pin)
        want = [(t, '1') for t in testpads]
    else:
        want = FUNC.get(s)
    if s in A5_SPARE:
        netname = net_at('U1', ball)
        mem = {r['reference'] for r in nets.get(netname, [])}
        if netname != s or mem != {'U1', A5_SPARE[s]}:
            fail('A5 section 17: %s ball %s net %r members %s, want only U1 and %s' % (s, ball, netname, sorted(mem), A5_SPARE[s])); continue
        n7 += 1; continue
    if s in ('VBUS',):
        netname = net_at('U1', ball)  # H9 reaches VBUS through Nordic's R1
        ep = endpoints(netname) | endpoints('VBUS') if netname else set()
        if netname != 'U1_VBUS' or ('R1', '~') not in ep:
            fail('VBUS ball %s not on U1_VBUS through R1' % ball)
    else:
        netname = net_at('U1', ball)
        if s != 'ANT' and netname != s:
            fail('section 7: %s ball %s is on net %r' % (s, ball, netname)); continue
        ep = endpoints(netname)
    if want is None:
        fail('no expected function for %s' % s); continue
    if s.startswith('SPARE'):
        if not any(e in ep for e in want):
            fail('spare %s ball %s has no test pad' % (pin, ball)); continue
    elif not all(e in ep for e in want):
        fail('section 7: %s ball %s misses %s' % (s, ball, [e for e in want if e not in ep])); continue
    n7 += 1
ok('section 7 rows checked: %d of %d' % (n7, len(plan))) if n7 == len(plan) else fail('section 7 %d of %d' % (n7, len(plan)))
# second level: mic data resistors reach the mic DATA pins
for r, u in (('R31', 'U5'), ('R32', 'U6')):
    if (u, 'DATA') not in endpoints(net_at(r, '1')) | endpoints(net_at(r, '2')):
        fail('%s does not reach %s DATA' % (r, u))
# (removed in A5: the check that each JOY line passes the joystick wire link J2-wire-J3; J2, J3 and W5 to W10
# no longer exist, check A5-9 below checks the flex tail J_BAND_A instead)

# contact pad order from -Y to +Y: VBUS, D-, D+, GND (case design, lead 2026-11-10)
for cp, want in (('CP1', 'VBUS'), ('CP2', 'USB_DN'), ('CP3', 'USB_DP'), ('CP4', 'GND')):
    got = net_at(cp, '1')
    fail('%s on %s, want %s' % (cp, got, want)) if got != want else ok('%s on %s' % (cp, want))
# recording light (A3 section 9 and W5): R41 value from the W5 row, no chip pin on the light
m = re.search(r'\| W5 \|[^\n]*R41 = (\d+) ohm', arch)
want_r41 = (m.group(1) + 'R') if m else None
got_r41 = parts.get('R41', {}).get('value')
ok('R41 = %s (W5)' % got_r41) if want_r41 and got_r41 == want_r41 else fail('R41 is %r, W5 says %r' % (got_r41, want_r41))
light = set()
for n in ('LED_A', 'LED_K'):
    light |= refs_ if False else {r['reference'] for r in nets.get(n, [])}
fail('a chip pin touches the light: %s' % sorted(light)) if 'U1' in light else ok('no U1 pin on LED_A or LED_K')
p305 = net_at('U1', 'G4')
mem = sorted((r['reference'], r['pin_number']) for r in nets.get(p305, []))
ok('P3.05 (G4) is a spare: %s %s' % (p305, mem)) if p305 == 'SPARE_P3_05' and mem == [('TP16', '1'), ('U1', 'G4')] else fail('P3.05 net %r members %s' % (p305, mem))
# ---------------------------------------------------------------- (b) designators vs bom.csv
MECH = re.compile(r'^(PCB|HSG|SCR|GSK|GL|ADH|FOAM|MEM)\d+$')
# Designator list frozen from bom.csv as first read (lead's instruction, 2026-11-10: bom.csv changes
# while the lead fills maker codes; the check must not fail on that). bom_refs_snapshot.csv holds it.
# R51 to R56 are in it and excluded below: wiring decision W1 drops the six joystick/button pull-ups.
# CBL1 is replaced by wires W5-W10 and pad connectors J2, J3 (lead, 2026-11-10).
bomrefs = {r['reference'] for r in csv.DictReader(open(os.path.join(HERE, 'bom_refs_snapshot.csv')))}
live = set()
for r in csv.DictReader(open(os.path.join(DESIGN, 'bom.csv'))):
    for ref in [x.strip() for x in r['reference'].split(',')]:
        if ref and not MECH.match(ref):
            live.add(ref)
if live != bomrefs:
    print('info bom.csv now differs from the snapshot (not a failure): only in live %s, only in snapshot %s' % (
        sorted(live - bomrefs), sorted(bomrefs - live)))
inet = {r['reference'] for r in rows}
miss = sorted(bomrefs - inet - not_placed)
extra = sorted(inet - bomrefs - added - testpads)
bad_np = sorted(not_placed - bomrefs)
if miss: fail('bom.csv electrical designators missing from netlist: %s' % miss)
if extra: fail('netlist designators in neither bom.csv nor additions: %s' % extra)
if bad_np: fail('not-placed list names designators absent from bom.csv: %s' % bad_np)
if not (miss or extra or bad_np):
    ok('designators: %d bom electrical, %d placed, %d not placed (listed), %d added' % (
        len(bomrefs), len(inet), len(not_placed), len(added)))

# ---------------------------------------------------------------- (c) every pin exactly once
nerr = 0
for ref, p in parts.items():
    for sp in syms[p['symbol']]:
        k = (ref, sp['pin_number'])
        if len(pin_of.get(k, [])) != 1:
            fail('pin %s.%s appears %d times' % (ref, sp['pin_number'], len(pin_of.get(k, [])))); nerr += 1
for k in pin_of:
    if k[0] not in parts:
        fail('netlist part %s not in parts.csv' % k[0]); nerr += 1
    elif k[1] not in {sp['pin_number'] for sp in syms[parts[k[0]]['symbol']]}:
        fail('netlist pin %s.%s not on its symbol' % k); nerr += 1
if not nerr:
    ok('every pin of %d parts appears exactly once (%d pin rows)' % (len(parts), len(rows)))

# ---------------------------------------------------------------- (d) single-pin nets
single = [n for n, rr in nets.items() if len(rr) < 2 and not (rr and rr[0]['reference'] in testpads)]
fail('single-pin nets: %s' % single) if single else ok('no single-pin net (%d nets)' % len(nets))

# ---------------------------------------------------------------- (e) rails of section 3
sec3 = arch.split('## 3.')[1].split('## 4.')[0]
rails = []
for l in sec3.splitlines():
    if l.startswith('| ') and not l.startswith('| Rail') and not l.startswith('|---'):
        rails += [x.strip() for x in l.strip('|').split('|')[0].split('/')]
for rail in rails:
    src = [r for r in nets.get(rail, []) if r['pin_type'] == 'power_out']
    if len(src) != 1:
        fail('rail %s has %d power_out sources: %s' % (rail, len(src), [(r['reference'], r['pin_name']) for r in src]))
    else:
        ok('rail %s source %s.%s' % (rail, src[0]['reference'], src[0]['pin_name']))

# ---------------------------------------------------------------- (f) microphone SELECT (was LR)
for u, want in (('U5', 'GND'), ('U6', 'VDD_MIC')):
    n = [r['net'] for r in rows if r['reference'] == u and r['pin_name'] == 'SELECT']
    fail('%s SELECT on %s, want %s' % (u, n, want)) if n != [want] else ok('%s SELECT on %s' % (u, want))

# ---------------------------------------------------------------- (g) ball H8
h8 = net_at('U1', 'H8')
others = [r for r in nets.get(h8, []) if not (r['reference'] == 'U1' and r['pin_number'] == 'H8')]
if len(others) == 1 and parts[others[0]['reference']]['symbol'] == 'C':
    c = others[0]['reference']
    other_net = [r['net'] for r in rows if r['reference'] == c and r['net'] != h8]
    fail('H8 capacitor %s not to GND' % c) if other_net != ['GND'] else ok('H8 connects only to %s, to GND' % c)
else:
    fail('ball H8 net %s has %s' % (h8, [(r['reference'], r['pin_number']) for r in others]))

# ---------------------------------------------------------------- (i) A5 changes (architecture 16.4, 16.6, 17.3, 17.4)
def refs_on(net):
    return {r['reference'] for r in nets.get(net, [])}


def netof(ref, pin):
    return net_at(ref, pin)


def a5(tag, cond, good, bad):
    ok('%s %s' % (tag, good)) if cond else fail('%s %s' % (tag, bad))


sym_of = {ref: p['symbol'] for ref, p in parts.items()}

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

TAILS = {'J_BAND_A', 'J_BAND_B'}


def tail_of(net):
    t = refs_on(net) & TAILS
    return next(iter(t)) if len(t) == 1 else None


# A5-3 joystick: no 5-way part; four SKTAAAE010, each between its line and ground, no pull-up or protection part
oj = not [r for r, sy in sym_of.items() if sy == 'SKRHADE010']
for sw, line, ball in (('SW1', 'JOY_UP', 'H1'), ('SW3', 'JOY_DOWN', 'G2'), ('SW4', 'JOY_LEFT', 'G1'), ('SW5', 'JOY_RIGHT', 'G10')):
    oj = oj and sym_of.get(sw) == 'SKTAAAE010' and netof(sw, 'P1') == line and netof(sw, 'P2') == 'GND'
    oj = oj and net_at('U1', ball) == line and tail_of(line) is not None and refs_on(line) == {'U1', tail_of(line), sw}
a5('A5-3', oj, 'no SKRHADE010; SW1 UP, SW3 DOWN, SW4 LEFT, SW5 RIGHT each line to GND, each line holds only U1, one flex tail and its switch (no pull-up, no protection part, as the old lines)',
   'joystick wrong (5-way part, switch wiring, or a part on a JOY line)')

# A5-4 JOY_CENTER H4 on a test pad only
a5('A5-4', net_at('U1', 'H4') == 'JOY_CENTER' and refs_on('JOY_CENTER') == {'U1', 'TP22'},
   'JOY_CENTER (H4) reaches only test pad TP22', 'JOY_CENTER not on a test pad only: %s' % sorted(refs_on('JOY_CENTER')))

# A5-5 (A6, 17.11) the centre switch SW2 under the joystick nub on BTN_REC, no record button; EVPAVAA1A gone, five SKTAAAE010 in all
n_sk = sorted(r for r, sy in sym_of.items() if sy == 'SKTAAAE010')
orb = sym_of.get('SW2') == 'SKTAAAE010' and netof('SW2', 'P1') == 'BTN_REC' and netof('SW2', 'P2') == 'GND'
orb = orb and net_at('U1', 'H2') == 'BTN_REC' and tail_of('BTN_REC') is not None and refs_on('BTN_REC') == {'U1', tail_of('BTN_REC'), 'SW2'}
orb = orb and not [r for r, sy in sym_of.items() if sy == 'EVPAVAA1A'] and n_sk == ['SW1', 'SW2', 'SW3', 'SW4', 'SW5']
a5('A5-5', orb, 'SW2 SKTAAAE010 (joystick centre switch) BTN_REC (H2) to GND, no EVPAVAA1A, 5 SKTAAAE010 in all', 'centre switch SW2 wrong: %s' % n_sk)

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
SDNET = {'1': 'SD_DAT2', '2': 'SDC_CS', '3': 'SDC_SCK', '4': 'GND', '5': 'SDC_MOSI', '6': 'SDC_MISO', '7': 'SD_DAT1', '8': 'VDD_SD'}
os_ = parts.get('U3', {}).get('value') == 'CSNP32GCR01-BOW' and parts['U3']['symbol'] == 'CSNP32GCR01_BOW'
os_ = os_ and all(netof('U3', k) == v for k, v in SDNET.items()) and len(syms['CSNP32GCR01_BOW']) == 8
os_ = os_ and {sp['pin_number']: sp['pin_name'] for sp in syms['CSNP32GCR01_BOW']} == SD
for r, n in (('R60', 'SDC_MISO'), ('R63', 'SD_DAT1'), ('R64', 'SD_DAT2'), ('R65', 'SDC_CS')):
    os_ = os_ and {netof(r, '1'), netof(r, '2')} == {n, 'VDD_SD'}
try:
    import fitz
    txt = fitz.open(os.path.join(DESIGN, 'datasheets', 'slim2_cs-sdnand-20230403.pdf'))[4].get_text()
    docname = {'1': 'SDD2', '2': 'CD/SDD3', '3': 'SCLK', '4': 'VSS', '5': 'CMD', '6': 'SDD0', '7': 'SDD1', '8': 'VCC'}
    bad_doc = [k for k, v in docname.items() if not re.search(r'\n%s\s*\n\s*%s' % (k, re.escape(v)), txt)]
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

# A6-9 the two flex tails (architecture 17.8 as replaced by 17.11 and 17.12). The split of lines between the tails is the
# table BAND_SPLIT in make_netlist.py; the rules below do not depend on which tail is which, except that the lead's
# confirmation of the motor's tail is left open (the motor pair may be on either tail, but both lines on the same one).
split = MK.BAND_SPLIT
want_a = [n for n, _, sd in split if sd == 'A']
want_b = [n for n, _, sd in split if sd == 'B']
ja = [netof('J_BAND_A', str(i + 1)) for i in range(len(syms['BAND_PADS_A']))]
jb = [netof('J_BAND_B', str(i + 1)) for i in range(len(syms['BAND_PADS_B']))]
o9 = ja == want_a and jb == want_b and len(ja) == len(want_a) and len(jb) == len(want_b)
o9 = o9 and [sp['pin_name'] for sp in syms['BAND_PADS_A']] == [p for _, p, sd in split if sd == 'A']
o9 = o9 and [sp['pin_name'] for sp in syms['BAND_PADS_B']] == [p for _, p, sd in split if sd == 'B']
side = {}
for n, _, sd in split:
    side.setdefault(n, set()).add(sd)
JOYSET = ['JOY_UP', 'JOY_DOWN', 'JOY_LEFT', 'JOY_RIGHT', 'BTN_REC']
CELLSET = ['VBAT', 'NTC', 'VBUS', 'USB_DN', 'USB_DP']
one = lambda names: len(set(x for n in names for x in side.get(n, {'?'}))) == 1 and all(len(side.get(n, {'?', '!'})) == 1 for n in names)
o9 = o9 and one(JOYSET) and one(CELLSET) and one(['MOTOR_DRV', 'VDD_3V0'])
o9 = o9 and side['JOY_UP'] != side['VBAT']                       # joystick side and cell side are different tails
o9 = o9 and all(side[n] == side['JOY_UP'] for n in ('BTN_REC',))   # the centre switch is on the joystick's tail
o9 = o9 and {n for n in side if len(side[n]) > 1} == {'GND'}      # only ground is on both tails
o9 = o9 and 'GND' in want_a and 'GND' in want_b
band_parts = ['SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'M1', 'BT1', 'RT1', 'CP1', 'CP2', 'CP3', 'CP4']
for bp in band_parts:
    for sp in syms[parts[bp]['symbol']]:
        n = netof(bp, sp['pin_number'])
        o9 = o9 and n is not None and (TAILS & refs_on(n)) != set()
o9 = o9 and all(parts[b]['sheet'] == 'band' for b in band_parts + ['J_BAND_A', 'J_BAND_B'])
old = [r for r in ('J2', 'J3', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', 'CAP2') if r in parts]
o9 = o9 and not old
a5('A6-9', o9, 'J_BAND_A %d pads and J_BAND_B %d pads equal the BAND_SPLIT table; joystick lines and SW2 on one tail, cell/NTC/VBUS/D-/D+ on the other, motor pair together, only GND on both; every pin of SW1-SW5, M1, BT1, RT1, CP1-CP4 is on a net with a tail pad; J2 J3 W1-W10 absent' % (len(ja), len(jb)),
   'flex tails wrong: A %s B %s want A %s B %s old parts %s' % (ja, jb, want_a, want_b, old))

# A6-10 title block A6 in every sheet file and on every PDF page
files = sorted(f for f in os.listdir(SCHDIR) if f.startswith('ring') and f.endswith('.kicad_sch'))
notA6 = [f for f in files if '(rev "A6")' not in open(os.path.join(SCHDIR, f)).read()]
try:
    import fitz
    pdf = fitz.open(os.path.join(SCHDIR, 'ring-schematic.pdf'))
    pg = [i + 1 for i, p in enumerate(pdf) if not re.search(r'Rev:?\s*A6', p.get_text())]
    npg = len(pdf)
except Exception as e:
    pg, npg = ['cannot read pdf: %s' % e], -1
a5('A6-10', not notA6 and not pg and npg == len(files), 'rev A6 in %d sheet files and on all %d PDF pages' % (len(files), npg),
   'title block not A6: files %s pdf pages %s (pdf %d pages, %d files)' % (notA6, pg, npg, len(files)))

# A6-1 (a) U2 is the nPM1304 35-ball CSP; no order code is invented; every ball is listed provisional
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
   'U2 not the nPM1304 as required (symbol %r value %r mpn %r; listed %d of %d pins)' % (u2.get('symbol'), u2.get('value'), u2.get('mpn'), len(listed), len(u2pins)))

# A6-2 (b) one control: SW2 stays (BTN_REC), CAP2 gone, CAP1 kept, no line names a record cap or pill
bt = ' '.join(' '.join(r.values()) for r in bomrows)
caps = [r['reference'] for r in bomrows if r['reference'] in ('CAP1', 'CAP2')]
o2 = caps == ['CAP1'] and not re.search(r'Record button cap|record pill|record cap|CAP2|pill 4\.4|over the record switch', bt)
o2 = o2 and 'CAP2' not in parts and sym_of.get('SW2') == 'SKTAAAE010' and netof('SW2', 'P1') == 'BTN_REC'
a5('A6-2', o2, 'SW2 kept on BTN_REC; bom.csv keeps CAP1 and has no CAP2, record cap or record pill', 'one-control rule broken: caps %s' % caps)

# A6-3 (c) the charging pads touch the skin: VBUS is an input only on the ring, D- and D+ hold only the chip and U9
vb = [(r['reference'], r['pin_name']) for r in nets.get('VBUS', []) if r['pin_type'] == 'power_out']
o3 = vb == [('CP1', '1')]
o3 = o3 and refs_on('USB_DN') == {'U1', 'U9', 'CP2', tail_of('USB_DN')} and refs_on('USB_DP') == {'U1', 'U9', 'CP3', tail_of('USB_DP')}
o3 = o3 and {r['reference'] for r in nets['VBUS']} == {'CP1', 'U2', 'U9', 'R1', 'C71', 'C72', tail_of('VBUS')}
o3 = o3 and not ({r['reference'] for r in nets.get('VBUSOUT', [])} & {'CP1', 'U9', tail_of('VBUS')})
a5('A6-3', o3, 'VBUS: the only source is the pad CP1 (the case); U2 VBUS and U1 (through R1) are inputs; VBUSOUT is a separate net not on a pad; D- and D+ hold only U1, U9, their pad and the tail (no resistor, no other driver)',
   'pad nets wrong: VBUS sources %s, USB_DN %s, USB_DP %s' % (vb, sorted(refs_on('USB_DN')), sorted(refs_on('USB_DP'))))

# A6-7 (d, review F07) storage bus: no line joins the 1.8 V chip ball and the 3.0 V storage pad directly
o7 = True
bad7 = []
for sig, csig, a, b in (('SD_SCK', 'SDC_SCK', '1', '12'), ('SD_MOSI', 'SDC_MOSI', '2', '11'), ('SD_CS', 'SDC_CS', '3', '10'), ('SD_MISO', 'SDC_MISO', '4', '9')):
    if refs_on(sig) != {'U1', 'U10'} or refs_on(csig) - {'U3', 'U10', 'R60', 'R65'} or netof('U10', a) != sig or netof('U10', b) != csig:
        bad7.append(sig)
    if 'U1' in refs_on(csig) or 'U3' in refs_on(sig):
        bad7.append(sig + ' direct')
want_u10 = {'5': 'VDD_1V8', '6': 'GND', '7': 'GND', '8': 'GND', '13': 'VDD_SD', '14': 'VDD_1V8', '15': 'VDD_1V8', '16': 'VDD_1V8'}
bad7 += ['U10 pin %s on %s want %s' % (k, netof('U10', k), v) for k, v in want_u10.items() if netof('U10', k) != v]
bad7 += ['pull-up on the 1.8 V side: %s' % r for r in ('R60', 'R63', 'R64', 'R65') if 'VDD_SD' in (netof(r, '1'), netof(r, '2')) and not ({netof(r, '1'), netof(r, '2')} & {'SDC_MISO', 'SDC_CS', 'SD_DAT1', 'SD_DAT2'})]
bad7 += ['U10 supply capacitor %s' % c for c, n in (('C81', 'VDD_1V8'), ('C82', 'VDD_SD')) if {netof(c, '1'), netof(c, '2')} != {n, 'GND'}]
# U10 pin table against the saved TI datasheet text (SCES898C Table 4-1, column RSV)
try:
    tt = open(os.path.join(HERE, 'evidence', 'a6', 'ti_sn74axc4t774.txt')).read()
    blk = tt.split('Table 4-1. Pin Functions')[1].split('www.ti.com')[0].split('\n')
    toks = [x.strip() for x in blk if x.strip()]
    ti = {}
    for k, tok in enumerate(toks):
        if re.fullmatch(r'(A[1-4]|B[1-4]|DIR[1-4]|OE|GND|VCCA|VCCB)', tok) and k + 3 < len(toks) and all(re.fullmatch(r'\d+', toks[k + j]) for j in (1, 2, 3)):
            ti[tok] = toks[k + 2]
    got = {sp['pin_name']: sp['pin_number'] for sp in syms['SN74AXC4T774_RSV']}
    bad7 += ['U10 pin %s is %s, TI RSV column says %s' % (n, got.get(n), ti.get(n)) for n in sorted(set(got) | set(ti)) if got.get(n) != ti.get(n)]
    bad7 += ([] if len(ti) == 16 else ['TI text gave %d of 16 pins' % len(ti)])
except Exception as e:
    bad7.append('cannot read the saved TI datasheet text: %s' % e)
a5('A6-7', not bad7, 'F07: SD_SCK, SD_MOSI, SD_CS, SD_MISO reach the card only through U10 (VCCA VDD_1V8, VCCB VDD_SD, DIR1-3 high, DIR4 low, OE low), pull-ups on the card side, U10 pin numbers equal the RSV column of the TI table',
   'storage level shift wrong: %s' % bad7)

# A6-4 (h) microphone figure and (f) charge settings in the files this task owns
bim = [r for r in bomrows if r['reference'] == 'U5,U6']
brief = open(os.path.join(DESIGN, 'datasheets', 'mic-research', 'im68d128b-brief.txt')).read()
o4 = len(bim) == 1 and '67.5 dB(A)' in bim[0]['key_figures'] and '68 dB' not in ' '.join(bim[0].values()) and re.search(r'Signal-to-noise ratio \(SNR\)\s+67\.5 dB\(A\)', brief) is not None
a5('A6-4', o4, 'microphone line says 67.5 dB(A) as the IM68D128B brief, no 68 dB', 'microphone figure wrong')
OLD = re.compile(r'(\b32 mA|\b68 mA|\b4\.40 V|\b4\.4 V\b|\b4\.45 V|\b800 mA)')
hits = []
for fn in ('bom.csv',):
    for k, l in enumerate(open(os.path.join(DESIGN, fn)).read().split('\n'), 1):
        if OLD.search(l): hits.append((fn, k, OLD.search(l).group(1)))
for fn in ('parts.csv', 'additions.csv', 'open-pins.csv', 'netlist.csv', 'sch-notes.md'):
    for k, l in enumerate(open(os.path.join(HERE, fn)).read().split('\n'), 1):
        if OLD.search(l) and 'WAS:' not in l: hits.append((fn, k, OLD.search(l).group(1)))
a5('A6-5', not hits, 'no charge setting other than 15 mA and 4.35 V in bom.csv, parts.csv, additions.csv, open-pins.csv, netlist.csv, sch-notes.md (lines marked WAS: excepted)',
   'old charge setting found: %s' % hits)

# ---------------------------------------------------------------- (h) KiCad's own netlist
xml = os.path.join(HERE, 'ring-kicad.xml')
lg = open(os.path.join(HERE, 'evidence', 'kicad_netlist_export.log'), 'w')
rc = subprocess.call([KICAD_CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', xml,
                      os.path.join(HERE, 'ring.kicad_sch')], stdout=lg, stderr=lg)
if rc != 0 or not os.path.exists(xml):
    fail('kicad-cli export netlist exit %d' % rc)
else:
    kn = {}
    knc = set()
    for n in ET.parse(xml).getroot().iter('net'):
        nodes = {(x.get('ref'), x.get('pin')) for x in n.iter('node') if not x.get('ref').startswith('#')}
        name = n.get('name').lstrip('/')
        if name.startswith('unconnected-'):
            knc |= nodes
        elif nodes:
            kn[name] = nodes
    mine = {n: {(r['reference'], r['pin_number']) for r in rr} for n, rr in nets.items()}
    mnc = {(r['reference'], r['pin_number']) for r in rows if r['pin_type'] == 'no_connect'}
    d1 = sorted(set(mine) ^ set(kn))
    d2 = sorted(n for n in set(mine) & set(kn) if mine[n] != kn[n])
    if d1: fail('net names differ between netlist.csv and KiCad export: %s' % d1)
    if d2: fail('net members differ: %s' % [(n, sorted(mine[n] ^ kn[n])) for n in d2])
    if mnc != knc: fail('no-connect pins differ: %s' % sorted(mnc ^ knc))
    if not (d1 or d2 or mnc != knc):
        ok('KiCad export matches netlist.csv: %d nets, %d no-connect pins' % (len(kn), len(knc)))

print('RESULT', 'FAIL %d' % len(FAIL) if FAIL else 'PASS', 'netlist', os.path.basename(NETFILE))
sys.exit(1 if FAIL else 0)
