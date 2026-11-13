# Own check of product-wiring.csv against the board pad dumps (pads/*.csv, made by dump_pads.py
# with KiCad's Python) and the two netlists. Prints one line per check and a tally.
# Usage: python3 check_lines.py > check_lines.log
import csv, re, collections
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = R + '/design/wiring/review-work'
SIZES = [7, 8, 9, 10, 11, 12, 13]

def load_pads(name):
    d = {}
    for r in csv.DictReader(open(f'{W}/pads/{name}.csv')):
        d.setdefault((r['ref'], r['pad']), []).append(r)
    return d

PADS = {n: load_pads(n) for n in ['ring', 'case_main', 'case_pins'] + [f'flex{f}-us{s}' for f in (1, 2) for s in SIZES]}
NET = {}
for nl in ('ring', 'case'):
    for r in csv.DictReader(open(f'{R}/design/ecad/{nl}/netlist.csv')):
        NET[(nl, r['reference'], r['pin_number'])] = r['net']

import os
lines = list(csv.DictReader(open(os.environ.get('WCSV', f'{R}/design/wiring/product-wiring.csv'))))
tally = collections.Counter()
out = []

def boards_for(board_text):
    t = board_text.lower()
    if t.startswith('ring main board'): return ['ring']
    if t.startswith('flex1'): return [f'flex1-us{s}' for s in SIZES]
    if t.startswith('flex2'): return [f'flex2-us{s}' for s in SIZES]
    if 'case main board' in t: return ['case_main']
    if 'case pin board' in t: return ['case_pins']
    return []

def pin_of(text):
    m = re.match(r'\s*([A-Za-z0-9+\-]+)', text or '')
    return m.group(1) if m else ''

def pad_net(board, ref, pin):
    rows = PADS[board].get((ref, pin))
    if not rows: return None, None
    nets = {r['net'] for r in rows}
    return '|'.join(sorted(nets)), rows[0]['cluster']

def rec(kind, lid, ok, msg):
    tally[(kind, 'pass' if ok else 'FAIL')] += 1
    out.append(f"{'PASS' if ok else 'FAIL'} {kind} {lid} {msg}")

SIG_CASE = {'VBUS': 'VRING', 'USB_DN': 'USB_D-', 'USB_DP': 'USB_D+', 'GND': 'GND'}
for L in lines:
    lid = L['id']
    for side in ('A', 'B'):
        sig = L[f'signal_{side}']
        bds = boards_for(L[f'end_{side}_board'])
        ref = L[f'end_{side}_ref']
        pin = pin_of(L[f'end_{side}_pin'])
        if not bds or L[f'end_{side}_kind'] == 'node':
            continue
        for bd in bds:
            net, cl = pad_net(bd, ref, pin)
            rec('END_NET', lid, net == sig, f'end {side} {bd} {ref}:{pin} board net={net} line signal={sig}')
    # face of the end on the board
    for side in ('A', 'B'):
        bds = boards_for(L[f'end_{side}_board'])
        face = L[f'end_{side}_face']
        ref = L[f'end_{side}_ref']; pin = pin_of(L[f'end_{side}_pin'])
        if not bds or L[f'end_{side}_kind'] == 'node': continue
        for bd in bds:
            rows = PADS[bd].get((ref, pin))
            if not rows: continue
            layers = rows[0]['layers'].split('|')
            want = 'F.Cu' if face.startswith('F.Cu') else ('B.Cu' if face.startswith('B.Cu') else None)
            if want is None:
                continue
            ok = (len(layers) == 1 and layers[0] == want) or (len(layers) > 2)
            rec('END_FACE', lid, ok, f'end {side} {bd} {ref}:{pin} pad layers={rows[0]["layers"][:20]} line face={face}')
    # path: both ends on the same board through copper
    bA = boards_for(L['end_A_board']); bB = boards_for(L['end_B_board'])
    if L['carrier_kind'] == 'copper':
        if L['end_A_kind'] == 'node':
            m = re.search(r'land (J_BAND_[AB]):(\d+)', L['end_A_pin'])
            a_ref, a_pin = m.group(1), m.group(2)
            boards = bB
        elif bA == ['ring'] and bB and bB[0].startswith('flex'):
            a_ref, a_pin = L['end_A_ref'], pin_of(L['end_A_pin'])
            boards = bB
        else:
            a_ref, a_pin = L['end_A_ref'], pin_of(L['end_A_pin'])
            boards = bA
        b_ref, b_pin = L['end_B_ref'], pin_of(L['end_B_pin'])
        if L['end_B_kind'] == 'node':
            # node on the same board: named parts such as "C13:1 L4:2" or "ground"
            targets = re.findall(r'([A-Z]+[0-9A-Z_]*):(\w+)', L['end_B_pin'])
            if not targets and L['end_B_pin'] == 'ground':
                targets = [('LT1', '2')]
        else:
            targets = [(b_ref, b_pin)]
        for bd in boards:
            na, ca = pad_net(bd, a_ref, a_pin)
            for (tr, tp) in targets:
                nb, cb = pad_net(bd, tr, tp)
                rec('PATH', lid, ca is not None and ca == cb, f'{bd} {a_ref}:{a_pin}({na}) to {tr}:{tp}({nb}) same copper cluster={ca == cb}')
    # spring pins: both ends' nets and the netlist names
    if L['carrier_kind'] == 'spring pin':
        sigA, sigB = L['signal_A'], L['signal_B']
        rec('PAIR_NAME', lid, SIG_CASE.get(sigA) == sigB, f'ring {sigA} paired to case {sigB}')
    # wire lines: the pin board copper reaches the spring pin of the same signal
    if L['carrier_kind'] == 'wire':
        na, ca = pad_net('case_pins', L['end_A_ref'], '1')
        hits = [k for k, v in PADS['case_pins'].items() if v[0]['cluster'] == ca and k != (L['end_A_ref'], '1')]
        rec('PINBOARD_PATH', lid, len(hits) > 0, f'case_pins {L["end_A_ref"]}:1 ({na}) joined by copper to {hits}')
    # netlist rows cited for the ends
    for side in ('A', 'B'):
        ref = L[f'end_{side}_ref']; pin = pin_of(L[f'end_{side}_pin'])
        for nl in ('ring', 'case'):
            n = NET.get((nl, ref, pin))
            if n is not None and L[f'end_{side}_kind'] != 'node':
                if (nl == 'ring' and L['joint'].startswith('R')) or (nl == 'case' and L['joint'].startswith('C')) or (nl == 'case' and 'case' in L[f'end_{side}_board']):
                    rec('NETLIST', lid, n == L[f'signal_{side}'], f'{nl} netlist {ref}:{pin}={n} line signal_{side}={L["signal_"+side]}')

# exactly once: unordered end pairs
keys = collections.Counter()
for L in lines:
    a = (L['end_A_board'], L['end_A_ref'], pin_of(L['end_A_pin']))
    b = (L['end_B_board'], L['end_B_ref'], pin_of(L['end_B_pin']))
    keys[tuple(sorted([a, b]))] += 1
for k, v in keys.items():
    rec('ONCE', k[0][1] + ':' + k[0][2] + '-' + k[1][1] + ':' + k[1][2], v == 1, f'count {v}')

# size columns: every lead/wire/tab/part cable line has 7 cut lengths or a size note
for L in lines:
    if L['carrier_kind'] in ('lead', 'wire', 'tab', 'part cable'):
        cuts = [L[f'cut_mm_us{s}'] for s in SIZES]
        ok = all(c.strip() for c in cuts) or 'not size dependent' in L['cut_note']
        rec('CUT', L['id'], ok and bool(L['carrier_marking'].strip()), f'cuts={cuts} note={L["cut_note"]!r} marking={L["carrier_marking"]!r}')
    if L['carrier_kind'] == 'copper' and L['end_B_board'].startswith('FLEX'):
        cps = [L[f'copper_mm_us{s}'] for s in SIZES]
        rec('COPPER_LEN', L['id'], all(c.strip() for c in cps), f'copper per size={cps}')

for o in out:
    print(o)
print('TALLY', dict(sorted(tally.items())))
print('lines read', len(lines))
