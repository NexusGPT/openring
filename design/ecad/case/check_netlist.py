#!/usr/bin/env python3
"""Checks the case netlist.csv against case-architecture.md (C1) section 6 pin plan,
case-bom.csv (designators frozen in bom_refs_snapshot.csv), the power tree, and the
netlist KiCad exports from case.kicad_sch. Exit 0 only when every check passes.
usage: check_netlist.py [netlist.csv]"""
import csv, os, re, subprocess, sys, collections
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, '..', '..'))
KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
NETFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'netlist.csv')
FAIL = []
def fail(m): FAIL.append(m); print('FAIL', m)
def ok(m): print('ok  ', m)

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
    rr = pin_of.get((ref, pin), [])
    if len(rr) != 1: return 'MISSING'
    return None if rr[0]['pin_type'] == 'no_connect' else rr[0]['net']
def ep(net): return {(r['reference'], r['pin_name']) for r in nets.get(net, [])}
def refs(net): return {r['reference'] for r in nets.get(net, [])}

# ---------------------------------------------------------------- (a) pin plan of U1, section 6
arch = open(os.path.join(DESIGN, 'case', 'case-architecture.md')).read()
sec6 = arch.split('## 6.')[1].split('## 7.')[0]
plan = []
for l in sec6.splitlines():
    if not l.startswith('| ') or l.startswith('| Module pin') or l.startswith('|---'):
        continue
    c = [x.strip() for x in l.strip('|').split('|')]
    pins = []
    for tok in c[0].split(','):
        tok = tok.strip()
        if '-' in tok:
            a, b = tok.split('-'); pins += list(range(int(a), int(b) + 1))
        else:
            pins.append(int(tok))
    names = [n.strip() for n in c[1].split(',')]
    plan.append((pins, names, c[2]))
FUNC = {
    'CC1_SENSE': [('R6', '~')], 'CC2_SENSE': [('R7', '~')], 'RING_TOUCH': [('E1', '1')],
    'VRING_SENSE': [('R12', '~'), ('R13', '~')], 'CHG_OTG': [('U2', 'OTG'), ('R27', '~')], 'CHG_INT_N': [('U2', 'INT'), ('R16', '~')],
    'I2C_SDA': [('U2', 'SDA'), ('R14', '~')], 'SD_D3': [('U4', 'CD/DAT3'), ('R30', '~')], 'SD_D2': [('U4', 'DAT2'), ('R29', '~')],
    'SD_CMD': [('U4', 'CMD'), ('R18', '~')], 'SD_CLK': [('R26', '~')], 'SD_D0': [('U4', 'DAT0'), ('R19', '~')],
    'SD_D1': [('U4', 'DAT1'), ('R20', '~')], 'VRING_EN': [('U5', 'EN'), ('R25', '~')],
    'VRING_FAULT_N': [('U5', 'FAULT'), ('R17', '~')], 'I2C_SCL': [('U2', 'SCL'), ('R15', '~')],
    'CHG_CE_N': [('U2', 'CE'), ('R21', '~')], 'USB_D-': [('U6', 'D1-'), ('P2', '1')], 'USB_D+': [('U6', 'D1+'), ('P3', '1')],
    'LED_R': [('R8', '~')], 'LED_G': [('R9', '~')], 'LED_B': [('R10', '~')], 'EN': [('R23', '~'), ('C30', '~')],
    '3V3': [('U3', 'VOUT'), ('C9', '~'), ('C10', '~')], 'GND': [('U2', 'PGND')],
}
npin = 0
for pins, names, netcol in plan:
    for i, pn in enumerate(pins):
        got = net_at('U1', str(pn))
        if got == 'MISSING':
            fail('U1 pin %d missing' % pn); continue
        if netcol.startswith('not connected'):
            good = got is None
        elif 'test pad' in netcol:
            good = got is not None and bool(refs(got) & testpads)
            if netcol.startswith('BOOT'):
                good = good and got == 'BOOT' and ('R22', '~') in ep(got)
        else:
            want = FUNC.get(netcol)
            good = got == netcol and want is not None and all(e in ep(got) for e in want)
        if good:
            npin += 1
        else:
            fail('pin plan: U1 pin %d (%s) net %r does not meet %r' % (pn, names[min(i, len(names) - 1)], got, netcol))
total = sum(len(p) for p, _, _ in plan)
ok('pin plan: %d of %d U1 pins as section 6' % (npin, total)) if npin == total else fail('pin plan %d of %d' % (npin, total))
# "Other pins" sentence: STAT 10k to 3V3, DSEL open, QON test pad, ILIM 260 ohm to GND, D+/D- to J1
other = [(('U2', '4'), lambda n: n and ('R24', '~') in ep(n) and parts['R24']['value'] == '10k'),
         (('U2', '24'), lambda n: n and ('R28', '~') in ep(n)),
         (('U2', '12'), lambda n: n and bool(refs(n) & testpads)),
         (('U2', '10'), lambda n: n and ('R11', '~') in ep(n) and parts['R11']['value'] == '260R'),
         (('U2', '2'), lambda n: n is None), (('U2', '3'), lambda n: n is None),
         (('J1', 'A6'), lambda n: n is None), (('J1', 'B6'), lambda n: n is None),
         (('J1', 'A7'), lambda n: n is None), (('J1', 'B7'), lambda n: n is None)]
for (ref, pn), f in other:
    n = net_at(ref, pn)
    ok('other pins: %s.%s on %s' % (ref, pn, n)) if f(n) else fail('other pins: %s.%s on %r' % (ref, pn, n))
# spring pin order along Y: P1 VBUS, P2 D-, P3 D+, P4 GND
for p, want in (('P1', 'VRING'), ('P2', 'USB_D-'), ('P3', 'USB_D+'), ('P4', 'GND')):
    n = net_at(p, '1')
    ok('%s on %s' % (p, want)) if n == want else fail('%s on %r, want %s' % (p, n, want))
# USB-C sink: 5.1 kohm from each CC to GND
for cc, r in (('A5', 'R1'), ('B5', 'R2')):
    n = net_at('J1', cc)
    other_end = [x['net'] for x in rows if x['reference'] == r and x['net'] != n]
    good = n and (r, '~') in ep(n) and parts[r]['value'] == '5.1k' and other_end == ['GND']
    ok('J1 %s: %s 5.1k to GND' % (cc, r)) if good else fail('J1 %s: %s not 5.1k to GND' % (cc, r))
# TS divider and VRING switch per the power tree
tsn = net_at('U2', '11')
ok('TS divider RT1/RT2/TH1') if {('RT1', '~'), ('RT2', '~'), ('TH1', '~')} <= ep(tsn) and ('RT1', '~') in ep('REGN') else fail('TS divider wrong')
ok('U5 IN on PMID, OUT on VRING') if net_at('U5', '1') == 'PMID' and net_at('U5', '6') == 'VRING' else fail('U5 IN/OUT wrong')

# C2 change list (case-architecture.md line 3, case-notes.md "Changes the schematic must take")
def other_end(ref, net):
    return [x['net'] for x in rows if x['reference'] == ref and x['net'] != net]
def val(ref): return parts.get(ref, {}).get('value')
c2 = [
    ('TPS2553 EN pin 3 = VRING_EN', net_at('U5', '3') == 'VRING_EN'),
    ('TPS2553 FAULT pin 4 = VRING_FAULT_N', net_at('U5', '4') == 'VRING_FAULT_N'),
    ('TPS2553 GND pin 2 = GND', net_at('U5', '2') == 'GND'),
    ('LED1 common anode pin 1 on SYS (sim finding 3)', net_at('LED1', '1') == 'SYS'),
    ('CE pulled up: R21 10k from CHG_CE_N to 3V3 (sim finding 2)', val('R21') == '10k' and other_end('R21', 'CHG_CE_N') == ['3V3']),
    ('LED1 cathodes 2/3/4 through R8/R9/R10 to LED_R/G/B',
     all((r, '~') in ep(net_at('LED1', pn)) and other_end(r, net_at('LED1', pn)) == [g]
         for pn, r, g in (('2', 'R8', 'LED_R'), ('3', 'R9', 'LED_G'), ('4', 'R10', 'LED_B')))),
    ('DSEL R28 10k to 3V3', val('R28') == '10k' and other_end('R28', net_at('U2', '24')) == ['3V3']),
    ('CHG_OTG R27 100k to GND', val('R27') == '100k' and other_end('R27', 'CHG_OTG') == ['GND']),
    ('SD_D2 R29 10k to 3V3', val('R29') == '10k' and other_end('R29', 'SD_D2') == ['3V3']),
    ('SD_D3 R30 10k to 3V3', val('R30') == '10k' and other_end('R30', 'SD_D3') == ['3V3']),
    ('USB-C D+/D- reach no U2 pin', not any(net_at('U2', p) for p in ('2', '3')) and not any(net_at('J1', p) for p in ('A6', 'B6', 'A7', 'B7'))),
    ('divider R3 511k 3V3-FB, R4 91k FB-GND', val('R3') == '511k' and val('R4') == '91k' and other_end('R3', 'FB') == ['3V3'] and other_end('R4', 'FB') == ['GND']),
    ('TS divider RT1 5.23k, RT2 30.1k', val('RT1') == '5.23k' and val('RT2') == '30.1k'),
    ('L1 1uH SW-SYS', val('L1') == '1uH' and sorted(x['net'] for x in rows if x['reference'] == 'L1') == ['SW', 'SYS']),
    ('W7 on RING_TOUCH with E1', {'W7', 'E1'} <= refs('RING_TOUCH')),
]
for name, good in c2:
    ok('C2: ' + name) if good else fail('C2: ' + name)
# ---------------------------------------------------------------- (b) designators vs case-bom.csv snapshot
bomrefs = {r['reference'] for r in csv.DictReader(open(os.path.join(HERE, 'bom_refs_snapshot.csv')))}
MECH = re.compile(r'^(PCB|MECH)\d+$')
def expand(cell):
    out = []
    for t in [x.strip() for x in cell.split(',')]:
        m = re.match(r'^([A-Z]+)(\d+)-([A-Z]+)?(\d+)$', t)
        if m:
            out += ['%s%d' % (m.group(1), i) for i in range(int(m.group(2)), int(m.group(4)) + 1)]
        elif t:
            out.append(t)
    return out
live = set()
for r in csv.DictReader(open(os.path.join(DESIGN, 'case', 'case-bom.csv'))):
    live |= {x for x in expand(r['reference']) if not MECH.match(x)}
if live != bomrefs:
    print('info case-bom.csv differs from the snapshot (not a failure): only live %s, only snapshot %s' % (sorted(live - bomrefs), sorted(bomrefs - live)))
inet = {r['reference'] for r in rows}
miss = sorted(bomrefs - inet - not_placed)
extra = sorted(inet - bomrefs - added - testpads)
if miss: fail('case-bom designators missing: %s' % miss)
if extra: fail('designators in neither case-bom nor additions: %s' % extra)
if not (miss or extra):
    ok('designators: %d case-bom electrical, %d placed, %d not placed, %d added' % (len(bomrefs), len(inet), len(not_placed), len(added)))

# ---------------------------------------------------------------- (c) every pin once, (d) single-pin nets
nerr = 0
for ref, p in parts.items():
    for sp in syms[p['symbol']]:
        if len(pin_of.get((ref, sp['pin_number']), [])) != 1:
            fail('pin %s.%s count %d' % (ref, sp['pin_number'], len(pin_of.get((ref, sp['pin_number']), [])))); nerr += 1
for k in pin_of:
    if k[0] not in parts or k[1] not in {sp['pin_number'] for sp in syms[parts[k[0]]['symbol']]}:
        fail('netlist pin %s.%s not on a symbol' % k); nerr += 1
if not nerr: ok('every pin of %d parts exactly once (%d rows)' % (len(parts), len(rows)))
single = [n for n, rr in nets.items() if len(rr) < 2 and not (rr and rr[0]['reference'] in testpads)]
fail('single-pin nets %s' % single) if single else ok('no single-pin net (%d nets)' % len(nets))

# ---------------------------------------------------------------- (e) rails of section 4
sec4 = arch.split('## 4.')[1].split('## 5.')[0]
rails = [l.strip('|').split('|')[0].strip() for l in sec4.splitlines() if l.startswith('| ') and not l.startswith('| Rail') and not l.startswith('|---')]
for rail in rails:
    src = [r for r in nets.get(rail, []) if r['pin_type'] == 'power_out']
    ok('rail %s source %s.%s' % (rail, src[0]['reference'], src[0]['pin_name'])) if len(src) == 1 else fail('rail %s has %d sources %s' % (rail, len(src), [(r['reference'], r['pin_name']) for r in src]))

# ---------------------------------------------------------------- (f) KiCad export
xml = os.path.join(HERE, 'case-kicad.xml')
lg = open(os.path.join(HERE, 'evidence', 'kicad_netlist_export.log'), 'w')
rc = subprocess.call([KICAD_CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', xml, os.path.join(HERE, 'case.kicad_sch')], stdout=lg, stderr=lg)
if rc != 0 or not os.path.exists(xml):
    fail('kicad-cli export netlist exit %d' % rc)
else:
    kn, knc = {}, set()
    for n in ET.parse(xml).getroot().iter('net'):
        nodes = {(x.get('ref'), x.get('pin')) for x in n.iter('node') if not x.get('ref').startswith('#')}
        name = n.get('name').lstrip('/')
        if name.startswith('unconnected-'): knc |= nodes
        elif nodes: kn[name] = nodes
    mine = {n: {(r['reference'], r['pin_number']) for r in rr} for n, rr in nets.items()}
    mnc = {(r['reference'], r['pin_number']) for r in rows if r['pin_type'] == 'no_connect'}
    d1 = sorted(set(mine) ^ set(kn)); d2 = sorted(n for n in set(mine) & set(kn) if mine[n] != kn[n])
    if d1: fail('net names differ: %s' % d1)
    if d2: fail('net members differ: %s' % [(n, sorted(mine[n] ^ kn[n])) for n in d2])
    if mnc != knc: fail('no-connect pins differ: %s' % sorted(mnc ^ knc))
    if not (d1 or d2 or mnc != knc): ok('KiCad export matches netlist.csv: %d nets, %d no-connect pins' % (len(kn), len(knc)))
print('RESULT', 'FAIL %d' % len(FAIL) if FAIL else 'PASS', 'netlist', os.path.basename(NETFILE))
sys.exit(1 if FAIL else 0)
