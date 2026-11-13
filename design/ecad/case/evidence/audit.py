#!/usr/bin/env python3
"""Final audit of the case unit: re-measures every count stated in sch-notes.md."""
import csv, re, json
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/case")
E = R + '/evidence'
out = []
def claim(t, ok, m): out.append('%s | %s | measured: %s' % ('MATCH' if ok else 'MISMATCH', t, m))
rows = list(csv.DictReader(open(R + '/netlist.csv')))
nets = {r['net'] for r in rows if r['pin_type'] != 'no_connect'}
claim('279 pin rows', len(rows) == 279, len(rows))
claim('61 nets', len(nets) == 61, len(nets))
nc = sum(1 for r in rows if r['pin_type'] == 'no_connect')
claim('17 no-connect pins', nc == 17, nc)
parts = list(csv.DictReader(open(R + '/parts.csv')))
claim('89 parts', len(parts) == 89, len(parts))
snap = list(csv.DictReader(open(R + '/bom_refs_snapshot.csv')))
claim('89 snapshot designators', len(snap) == 89, len(snap))
adds = list(csv.DictReader(open(R + '/additions.csv')))
na = [a['reference'] for a in adds if a['kind'] == 'added']
claim('0 added', len(na) == 0, len(na))
claim('nothing not placed', [a['reference'] for a in adds if a['kind'] == 'bom_not_placed'] == [], [a['reference'] for a in adds if a['kind'] == 'bom_not_placed'])
op = list(csv.DictReader(open(R + '/open-pins.csv')))
claim('12 open-pin rows', len(op) == 12, len(op))
for ref, n in (('U4', 8), ('BT1', 2), ('U2', 1), ('J1', 1)):
    k = sum(1 for o in op if o['reference'] == ref); claim('open pins %s = %d' % (ref, n), k == n, k)
erc = open(R + '/erc-report.txt').read()
claim('ERC 0 violations', len(re.findall(r'^\[', erc, re.M)) == 0, len(re.findall(r'^\[', erc, re.M)))
j = json.load(open(R + '/erc-report.json'))
ne = sum(1 for s in j.get('sheets', []) for v in s.get('violations', []))
claim('ERC json 0 violations', ne == 0, ne)
ex = open(E + '/broken/exits.txt').read()
claim('2 broken copies exit 1', ex.count('exit 1') == 2, ex.count('exit 1'))
claim('ERC probe 1 power_pin_not_driven', '1 [power_pin_not_driven]' in ex, True)
import fitz
claim('PDF 7 pages', len(fitz.open(R + '/case-schematic.pdf')) == 7, len(fitz.open(R + '/case-schematic.pdf')))
claim('0 overlapping word pairs', 'TOTAL overlapping word pairs 0' in open(E + '/render_c2.log').read(), True)
ck = open(E + '/check_c2.log').read()
claim('14 C2 checks ok', ck.count('ok   C2:') == 14, ck.count('ok   C2:'))
claim('89 placed, 0 added', '89 case-bom electrical, 89 placed, 0 not placed, 0 added' in ck, True)
bx = open(E + '/broken_c2_exits.txt').read()
claim('8 case broken copies exit 1', sum(1 for l in bx.splitlines() if l.startswith('case ') and ' exit 1 ' in l) == 8, sum(1 for l in bx.splitlines() if l.startswith('case ') and ' exit 1 ' in l))
claim('ring P3.05 copy exit 1', 'ring p305_on_light exit 1' in bx, True)
import hashlib
h = lambda q: hashlib.md5(open(q, 'rb').read()).hexdigest()
ch = [i for i in range(1, 8) if h(E + '/pdf_c1_p%d.png' % i) != h(E + '/pdf_c2_p%d.png' % i)]
claim('every page changed c1->c2 (title C2)', ch == list(range(1, 8)), ch)
claim('notes: conflicts left open none', 'Conflicts left open: none.' in open(R + '/sch-notes.md').read(), True)
claim('65 of 65 U1 pins', '65 of 65' in ck, True)
claim('7 rails each one source', ck.count('ok   rail') == 7, ck.count('ok   rail'))
dw = open(E + '/done_when.log').read().strip().splitlines()
claim('done-when exit 0', dw[-1] == 'done_when exit 0', dw[-1])
notes = open(R + '/sch-notes.md').read().strip().splitlines()
claim('notes last line RESULT', notes[-1].startswith('RESULT: done'), notes[-1])
print('\n'.join(out))
print('claims checked', len(out), 'mismatches', sum(1 for o in out if o.startswith('MISMATCH')))
