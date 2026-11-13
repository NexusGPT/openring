P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/check_netlist.py")
s = open(P).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)

rep('"""Checks netlist.csv against the architecture (A5-draft, sections 7, 14, 16, 17) and bom.csv, and against the',
    '"""Checks netlist.csv against the architecture (A5-draft, sections 7, 14, 16, 17 with 17.11 to 17.13: A6) and bom.csv, and against the')
rep('ring*.kicad_sch and ring-schematic.pdf lets check A5-10 test a broken copy)"""', 'ring*.kicad_sch and ring-schematic.pdf lets check A6-10 test a broken copy)"""')
rep("import csv, os, re, subprocess, sys, collections\n", "import csv, os, re, subprocess, sys, collections\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n")
# the split table is read from make_netlist.py (one place); the rules below are written here, not read from it
rep("FAIL = []\n", "FAIL = []\nimport make_netlist as MK  # BAND_SPLIT: the one table that says which flex tail carries which line\n")

# SD functions: the chip lines reach the level shifter A side, the card side reaches U3
rep("""    'SD_SCK': [('U3', 'CLK')], 'SD_MOSI': [('U3', 'CMD')], 'SD_MISO': [('U3', 'DAT0')], 'SD_CS': [('U3', 'DAT3')],""",
    """    'SD_SCK': [('U10', 'A1')], 'SD_MOSI': [('U10', 'A2')], 'SD_MISO': [('U10', 'A4')], 'SD_CS': [('U10', 'A3')],  # A6 F07: through U10""")
rep("""# A5-3 joystick""", """TAILS = {'J_BAND_A', 'J_BAND_B'}


def tail_of(net):
    t = refs_on(net) & TAILS
    return next(iter(t)) if len(t) == 1 else None


# A5-3 joystick""")
rep("    oj = oj and net_at('U1', ball) == line and refs_on(line) == {'U1', 'J_BAND_A', sw}",
    "    oj = oj and net_at('U1', ball) == line and tail_of(line) is not None and refs_on(line) == {'U1', tail_of(line), sw}")
rep("each line holds only U1, J_BAND_A and its switch (no pull-up", "each line holds only U1, one flex tail and its switch (no pull-up")
rep("orb = orb and net_at('U1', 'H2') == 'BTN_REC' and refs_on('BTN_REC') == {'U1', 'J_BAND_A', 'SW2'}",
    "orb = orb and net_at('U1', 'H2') == 'BTN_REC' and tail_of('BTN_REC') is not None and refs_on('BTN_REC') == {'U1', tail_of('BTN_REC'), 'SW2'}")
rep("# A5-5 record button: one SKTAAAE010 on BTN_REC, EVPAVAA1A gone, five SKTAAAE010 in all",
    "# A5-5 (A6, 17.11) the centre switch SW2 under the joystick nub on BTN_REC, no record button; EVPAVAA1A gone, five SKTAAAE010 in all")
rep("'record button wrong: %s' % n_sk", "'centre switch SW2 wrong: %s' % n_sk")
rep("'SW2 SKTAAAE010 BTN_REC (H2) to GND, no EVPAVAA1A, 5 SKTAAAE010 in all'", "'SW2 SKTAAAE010 (joystick centre switch) BTN_REC (H2) to GND, no EVPAVAA1A, 5 SKTAAAE010 in all'")

# A5-7 card side nets
rep("SDNET = {'1': 'SD_DAT2', '2': 'SD_CS', '3': 'SD_SCK', '4': 'GND', '5': 'SD_MOSI', '6': 'SD_MISO', '7': 'SD_DAT1', '8': 'VDD_SD'}",
    "SDNET = {'1': 'SD_DAT2', '2': 'SDC_CS', '3': 'SDC_SCK', '4': 'GND', '5': 'SDC_MOSI', '6': 'SDC_MISO', '7': 'SD_DAT1', '8': 'VDD_SD'}")
rep("for r, n in (('R60', 'SD_MISO'), ('R63', 'SD_DAT1'), ('R64', 'SD_DAT2'), ('R65', 'SD_CS')):",
    "for r, n in (('R60', 'SDC_MISO'), ('R63', 'SD_DAT1'), ('R64', 'SD_DAT2'), ('R65', 'SDC_CS')):")

# replace A5-9 and A5-10 blocks by A6 ones
i0 = s.index("# A5-9 the two flex tails")
i1 = s.index("# ---------------------------------------------------------------- (h) KiCad's own netlist")
new = r'''# A6-9 the two flex tails (architecture 17.8 as replaced by 17.11 and 17.12). The split of lines between the tails is the
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
o3 = o3 and all(n.startswith('VBUS') is False for n in nets if n not in ('VBUS', 'VBUSOUT', 'U1_VBUS'))
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

'''
s = s[:i0] + new + s[i1:]
open(P, 'w').write(s)
print('ok')
