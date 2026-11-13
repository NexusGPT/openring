#!/usr/bin/env python3
"""Final audit: re-measures every count stated in sch-notes.md and the final reply
from the delivered files, and prints a line per claim with its measured value."""
import csv, os, re, json, subprocess, sys, hashlib
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring")
E = R + '/evidence'
out = []
def claim(text, ok, measured):
    out.append('%s | %s | measured: %s' % ('MATCH' if ok else 'MISMATCH', text, measured))

rows = list(csv.DictReader(open(R + '/netlist.csv')))
nets = {r['net'] for r in rows if r['pin_type'] != 'no_connect'}
nc = [r for r in rows if r['pin_type'] == 'no_connect']
claim('netlist.csv 391 rows', len(rows) == 391, len(rows))
claim('93 nets', len(nets) == 93, len(nets))
claim('15 no-connect pins', len(nc) == 15, len(nc))
parts = list(csv.DictReader(open(R + '/parts.csv')))
claim('125 parts', len(parts) == 125, len(parts))
syms = {r['symbol'] for r in csv.DictReader(open(R + '/symbols.csv'))}
claim('27 part symbols in symbols.csv', len(syms) == 27, len(syms))
lib = open(R + '/ring.kicad_sym').read()
claim('ring.kicad_sym 28 symbols', len(re.findall(r'^\(symbol "[^"]+"$', lib, re.M)) == 28, len(re.findall(r'^\(symbol "[^"]+"$', lib, re.M)))
adds = list(csv.DictReader(open(R + '/additions.csv')))
na = [a['reference'] for a in adds if a['kind'] == 'added']
claim('37 added designators', len(na) == 37, len(na))
claim('not placed: R51-R56, CBL1, NPM-REF (8)', [a['reference'] for a in adds if a['kind'] == 'bom_not_placed'] == ['R51','R52','R53','R54','R55','R56','CBL1','NPM-REF'],
      [a['reference'] for a in adds if a['kind'] == 'bom_not_placed'])
op = list(csv.DictReader(open(R + '/open-pins.csv')))
pins = [o for o in op if o['pin_number']]
vals = [o for o in op if not o['pin_number']]
claim('72 provisional pin numbers', len(pins) == 72, len(pins))
claim('3 OPEN values (L71, L72, RT1)', sorted(o['reference'] for o in vals) == ['L71', 'L72', 'RT1'], [o['reference'] for o in vals])
for ref, n in (('U2', 33), ('U3', 8), ('J1', 15), ('Q1', 3), ('Q2', 3), ('LED1', 2), ('M1', 2), ('BT1', 2), ('X1', 2), ('X2', 2)):
    k = sum(1 for o in pins if o['reference'] == ref)
    claim('open pins %s = %d' % (ref, n), k == n, k)
erc = open(R + '/erc-report.txt').read()
nv = len(re.findall(r'^\[', erc, re.M))
claim('ERC 0 violations (errors and warnings)', nv == 0, nv)
j = json.load(open(R + '/erc-report.json'))
nerr = sum(1 for s in j.get('sheets', []) for v in s.get('violations', []) if v.get('severity') == 'error')
nwarn = sum(1 for s in j.get('sheets', []) for v in s.get('violations', []) if v.get('severity') == 'warning')
claim('ERC json errors 0, warnings 0', nerr == 0 and nwarn == 0, (nerr, nwarn))
t1 = open(E + '/erc-report_t1.txt').read()
claim('run t1 had 118 footprint_link_issues warnings', t1.count('[footprint_link_issues]') == 118 and len(re.findall(r'^\[', t1, re.M)) == 118,
      t1.count('[footprint_link_issues]'))
ex = open(E + '/broken/exits.txt').read()
claim('broken copies exit 1 (2 of 2)', ex.count('exit 1') == 2, ex.count('exit 1'))
claim('ERC probe: 2 power_pin_not_driven', '2 [power_pin_not_driven]' in ex, [l for l in ex.splitlines() if 'power_pin' in l])
import fitz
d = fitz.open(R + '/ring-schematic.pdf')
claim('PDF 8 pages', len(d) == 8, len(d))
r6 = open(E + '/render_t9.log').read()
claim('0 overlapping word pairs', 'TOTAL overlapping word pairs 0' in r6, r6.strip().splitlines()[-1])
def h(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
same = [i for i in range(3, 9) if h(E + '/pdf_t5_p%d.png' % i) == h(E + '/pdf_t6_p%d.png' % i)]
claim('pages 3 to 8 identical between t5 (read) and t6', same == list(range(3, 9)), same)
same7 = [i for i in range(1, 9) if h(E + '/pdf_t6_p%d.png' % i) == h(E + '/pdf_t7_p%d.png' % i)]
claim('t7 (final) equals t6 on pages 1-6 and 8; page 7 changed and was read', same7 == [1, 2, 3, 4, 5, 6, 8], same7)
snap = list(csv.DictReader(open(R + '/bom_refs_snapshot.csv')))
claim('snapshot 96 designators', len(snap) == 96, len(snap))
ck = open(E + '/check_t9.log').read().strip().splitlines()
claim('check_t9 last line exit 0', ck[-1] == 'check_netlist exit 0', ck[-1])
dw = open(E + '/done_when.log').read().strip().splitlines()
claim('done-when exit 0', dw[-1] == 'done_when exit 0', dw[-1])
notes = open(R + '/sch-notes.md').read().strip().splitlines()
claim('sch-notes last line is RESULT', notes[-1].startswith('RESULT: done'), notes[-1])
claim('sch-notes has questions_for_owner section', '## questions_for_owner' in notes, True)
# rails each one source
for l in open(E + '/check_t9.log'):
    if l.startswith('ok   rail'):
        out.append('INFO | ' + l.strip())
# reply claims
rep = E + '/final_reply.md'
if os.path.exists(rep):
    t = open(rep).read()
    for num in sorted(set(re.findall(r'\b\d+\b', t)), key=int):
        out.append('REPLY-NUMBER | %s | %s' % (num, 'in audit lines' if any(re.search(r'\b%s\b' % num, o) for o in out) else 'check by hand'))
ck9 = open(E + '/check_t9.log').read()
claim('R41 680R checked', 'ok   R41 = 680R (W5)' in ck9, True)
claim('P3.05 only TP16', "ok   P3.05 (G4) is a spare: SPARE_P3_05 [('TP16', '1'), ('U1', 'G4')]" in ck9, True)
claim('R41 value 680R in parts.csv', [p['value'] for p in parts if p['reference'] == 'R41'] == ['680R'], [p['value'] for p in parts if p['reference'] == 'R41'])
print('\n'.join(out))
print('claims checked', sum(1 for o in out if o.startswith(('MATCH', 'MISMATCH'))), 'mismatches', sum(1 for o in out if o.startswith('MISMATCH')))
