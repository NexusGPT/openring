# B1 completeness, own enumeration: every pin of a part that is not soldered on the board it belongs
# to (off-board parts, band-circuit parts, the interface lands, the case's off-board parts and wire pads)
# must be an end of at least one product-wiring.csv line. Prints pins with no line.
import csv, re
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
lines = list(csv.DictReader(open(f'{R}/design/wiring/product-wiring.csv')))
ends = set()
for L in lines:
    for s in ('A', 'B'):
        m = re.match(r'\s*([A-Za-z0-9+\-]+)', L[f'end_{s}_pin'] or '')
        ends.add((L[f'end_{s}_ref'], m.group(1) if m else ''))
        for x in re.findall(r'land (J_BAND_[AB]):(\d+)', L[f'end_{s}_pin'] or ''):
            ends.add(x)
want = []
for r in csv.DictReader(open(f'{R}/design/ecad/ring/netlist.csv')):
    if re.match(r'^(DISP1|BT1|RT1|M1|CP\d|SW\d|J_BAND_[AB]|J1)$', r['reference']):
        want.append(('ring', r['reference'], r['pin_number'], r['net']))
for r in csv.DictReader(open(f'{R}/design/ecad/case/netlist.csv')):
    if re.match(r'^(BT1|TH1|P\d|E1|W\d)$', r['reference']):
        want.append(('case', r['reference'], r['pin_number'], r['net']))
for p in ('WP1', 'WP2', 'WP3', 'WP4', 'WP7'):
    want.append(('case_pins board', p, '1', ''))
for t in ('1', '2', '3'):
    want.append(('flex2 board', 'PRT1', t, ''))
miss = [w for w in want if (w[1], w[2]) not in ends]
print('interface pins enumerated', len(want), 'covered', len(want) - len(miss))
for m in miss:
    print('NO LINE', m)
