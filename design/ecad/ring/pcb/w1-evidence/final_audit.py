#!/usr/bin/env python3
"""Final audit of the W1 reply (final_reply.txt) and of footprint-notes.md.
1. every number in the reply is looked up in the saved evidence (first matching line printed);
2. every quoted string in the reply must occur verbatim in a saved file;
3. every path in the reply must exist;
4. every count the reply states is recomputed here with its own command;
5. statements about the same thing in reply and notes are compared.
Prints the number of claims checked and every failure.  Exit 1 on any failure.
Run: design/.venv/bin/python -I final_audit.py"""
import csv, glob, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.dirname(HERE)
RING = os.path.dirname(PCB)
DESIGN = os.path.dirname(os.path.dirname(RING))
reply = open(os.path.join(HERE, 'final_reply.txt')).read()
notes = open(os.path.join(PCB, 'footprint-notes.md')).read()

fails, checked = [], 0


def ok(what, cond, ev=''):
    global checked
    checked += 1
    print(('ok   ' if cond else 'FAIL ') + what + ('  <- ' + ev if ev else ''))
    if not cond:
        fails.append(what)


# ---- corpus of saved evidence lines
corpus_files = (glob.glob(os.path.join(HERE, '*.log')) + glob.glob(os.path.join(HERE, '*.csv')) + glob.glob(os.path.join(HERE, '*.txt'))
                + glob.glob(os.path.join(HERE, '*.diff')) + glob.glob(os.path.join(HERE, '*.md')) + glob.glob(os.path.join(HERE, '*.py'))
                + [os.path.join(PCB, 'footprint-notes.md'), os.path.join(PCB, 'footprint-sources.csv'), os.path.join(PCB, 'custom-part-interfaces.md'),
                   os.path.join(RING, 'parts.csv'), os.path.join(RING, 'netlist.csv'), os.path.join(RING, 'open-pins.csv'),
                   os.path.join(DESIGN, 'bom.csv'), os.path.join(DESIGN, 'mech', 'thin', 'placement.csv')]
                + glob.glob(os.path.join(PCB, 'OpenRing.pretty', '*.kicad_mod')))
corpus_files = [f for f in corpus_files if os.path.basename(f) not in ('final_reply.txt', 'final_audit.log', 'final_audit.py')]
corpus = []
for f in corpus_files:
    try:
        for i, l in enumerate(open(f, errors='replace'), 1):
            corpus.append((os.path.relpath(f, DESIGN), i, l.rstrip('\n')))
    except OSError:
        pass

# ---- 1. numbers
print('== 1. numbers in the reply')
body = re.sub(r'`[^`]*`', ' ', reply)
nums = []
for m in re.finditer(r'(?<![\w./-])(\d+(?:\.\d+)?)(?![\w/-])', body):
    nums.append(m.group(1))
seen = []
for n in nums:
    if n in seen:
        continue
    seen.append(n)
    pat = re.compile(r'(?<![\d.])' + re.escape(n) + r'(?![\d])')
    hit = next(((f, i, l) for f, i, l in corpus if pat.search(l)), None)
    ok('number %s' % n, hit is not None, '%s:%d %s' % (hit[0], hit[1], hit[2][:90].strip()) if hit else '')

# ---- 2. quoted strings
print('== 2. quoted strings')
for q in re.findall(r'"([^"]{6,})"', reply):
    hit = next(((f, i, l) for f, i, l in corpus if q in l), None)
    ok('quote "%s"' % q[:70], hit is not None, '%s:%d' % (hit[0], hit[1]) if hit else '')

# ---- 3. paths
print('== 3. paths')
paths = set(re.findall(r'(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:md|csv|py|log|sh|pretty|txt))\b', reply)) | set(re.findall(r'(design/[\w./-]+|pcb/[\w./-]+)', reply))
for p in sorted(paths):
    p = p.rstrip('./')
    cands = [os.path.join(DESIGN, p), os.path.join(os.path.dirname(DESIGN), p), os.path.join(RING, p), os.path.join(PCB, p), os.path.join(HERE, p)]
    found = next((c for c in cands if os.path.exists(c)), None)
    if not found:
        g = [x for x in glob.glob(os.path.join(DESIGN, '**', os.path.basename(p)), recursive=True) if '/review/' not in x and '/.venv/' not in x and 'sandbox' not in x]
        found = g[0] if g else None
    ok('path %s exists' % p, found is not None, os.path.relpath(found, os.path.dirname(DESIGN)) if found else '')

# ---- 4. recomputed counts
print('== 4. counts recomputed')
lib = os.path.join(PCB, 'OpenRing.pretty')
n_fp = len([f for f in os.listdir(lib) if f.endswith('.kicad_mod')])
parts = list(csv.DictReader(open(os.path.join(RING, 'parts.csv'))))
src = list(csv.DictReader(open(os.path.join(PCB, 'footprint-sources.csv'))))
net = list(csv.DictReader(open(os.path.join(RING, 'netlist.csv'))))
ok('19 footprints in OpenRing.pretty (ls count %d)' % n_fp, n_fp == 19)
ok('118 parts in parts.csv (count %d)' % len(parts), len(parts) == 118)
ok('footprint-sources.csv has 118 rows (count %d)' % len(src), len(src) == 118)
ok('netlist has 410 rows (count %d)' % len(net), len(net) == 410)
grep = subprocess.run(['grep', '-ril', 'PROVISIONAL', lib], capture_output=True, text=True)
ok('no file of OpenRing.pretty holds PROVISIONAL (grep -ril)', grep.stdout.strip() == '', grep.stdout.strip())
op_now = len(open(os.path.join(RING, 'open-pins.csv')).read().splitlines()) - 1
op_before = len(open(os.path.join(HERE, 'open-pins_before.csv')).read().splitlines()) - 1
ok('open-pins.csv holds 0 data rows (%d), was 60 (%d)' % (op_now, op_before), op_now == 0 and op_before == 60)
pm = {p['reference']: p for p in parts}
band = [p['reference'] for p in parts if p['footprint'].startswith('OpenRingBand:')]
ok('14 band parts name OpenRingBand (count %d)' % len(band), len(band) == 14)
ok('footprint-sources.csv rows of the band parts name the band library', all('OpenRingBand' in [r for r in src if r['reference'] == b][0]['land_source'] for b in band))
ok('C60 is 2.2uF 0402ZC225KAT2A in parts.csv', pm['C60']['value'] == '2.2uF' and pm['C60']['mpn'] == '0402ZC225KAT2A')
exp = {'C71': 'GRM155R61E105KA12D', 'C86': 'GRM155R61E105KA12D', 'C87': 'GRM155R61E105KA12D', 'C85': '0402ZC225KAT2A', 'C60': '0402ZC225KAT2A', 'C35': '04025A102JAT2A', 'C36': '04025A102JAT2A', 'L71': '1269AS-H-2R2M=P2', 'L72': '1269AS-H-2R2M=P2', 'RT1': 'NCP15XH103F03RC', 'L10': '1269AS-H-2R2M=P2'}
ok('closed refs carry the AVX codes of the reply', all(pm[k]['mpn'] == v for k, v in exp.items()))
bomtxt = open(os.path.join(DESIGN, 'bom.csv')).read()
ok('C88 is GRT188R61A106KE13D, Chip_0603', pm['C88']['mpn'] == 'GRT188R61A106KE13D' and pm['C88']['footprint'].endswith('Chip_0603'))
ok('bom.csv has no NOT CLOSED line', bomtxt.count('NOT CLOSED') == 0)
bomtxt = open(os.path.join(DESIGN, 'bom.csv')).read()
ok('bom.csv has C60 with 0402ZC225KAT2A', '0402ZC225KAT2A' in bomtxt)
ca = {m.group(1): float(m.group(4)) for m in re.finditer(r'^(\S+) courtyard ([\d.]+) x ([\d.]+) = ([\d.]+) mm2', open(os.path.join(HERE, 'final_courtyard.log')).read(), re.M)}
ok('0201 courtyard 0.667 and 0402 1.292 (log)', abs(ca['Chip_0201'] - 0.667) < 1e-9 and abs(ca['Chip_0402'] - 1.292) < 1e-9)
x7 = open(os.path.join(HERE, 'avx_x7r_cells.log')).read()
ok('AVX X7R cell: 2.2 uF 0402 10 V exists, code E', '2.2 uF -> size 0402, 10 V, thickness code E' in x7)
ok('AVX X7R: 1.0 uF in 0402 only at 6.3 V', '1.0 uF -> size 0402, 6.3 V' in x7 and '1.0 uF -> size 0402, 10 V' not in x7 and '1.0 uF -> size 0402, 25 V' not in x7)
c0 = open(os.path.join(HERE, 'avx_c0g_options.log')).read()
ok('AVX C0G: 0.1 uF only in 1206 (16, 25, 50 V, code X)', all(('0.1 -> size 1206, %s V, thickness code X' % v) in c0 for v in (16, 25, 50)) and '0.1 -> size 0805' not in c0)
ok('AVX C0G: 0402 stops at 1000 pF (no 1200 pF cell), 0603 stops at 4700 pF (no 5600 pF cell)', '1200 -> size 0402' not in c0 and '1000 -> size 0402' in c0 and '4700 -> size 0603' in c0 and '5600 -> size 0603' not in c0)
kn = open((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt")).read().replace('\n', ' ')
ok('Knowles sentence is in the saved Knowles text', re.search(r'Capacitors near the microphone should not contain\s+Class 2 dielectrics due to their piezoelectric effect', kn) is not None)
cs = subprocess.run(['pdftotext', '-f', '11', '-l', '11', os.path.join(DESIGN, 'datasheets', 'slim2_cs-sdnand-20230403.pdf'), '-'], capture_output=True, text=True).stdout
ok('storage sheet PDF p11 recommends 2.2uF on VCC', '2.2uF capacitance on VCC' in cs.replace('\n', ' '))
kp = subprocess.run(['pdftotext', '-f', '5', '-l', '5', os.path.join(DESIGN, 'datasheets', 'w1_knowles_spk0641ht4h-1_chipsmall.pdf'), '-'], capture_output=True, text=True).stdout
ok('Knowles sentence is on PDF page 5 of the saved copy', 'Class 2 dielectrics' in kp.replace('\n', ' '))
bom_b = open(os.path.join(HERE, 'check_bom_before.log')).read().strip().splitlines()
bom_a = open(os.path.join(HERE, 'final_check_bom_after.log')).read().strip().splitlines()
ok('check_bom.py before: failures 0 and after: failures 0', 'failures 0' in bom_b[-2] and 'failures 0' in bom_a[-2], bom_b[-2][-30:] + ' | ' + bom_a[-2][-30:])
log_exit = lambda n: open(os.path.join(HERE, n)).read().strip().splitlines()[-1]
ok('check_footprints with the band library absent fails (exit 1, 14 failures)', log_exit('final_check_footprints_band_absent.log') == 'exit 1' and 'RESULT FAIL 14' in open(os.path.join(HERE, 'final_check_footprints_band_absent.log')).read())
ok('check_band.py ends RESULT: PASS boards checked 14', 'RESULT: PASS boards checked 14' in open(os.path.join(HERE, 'final_check_band.log')).read())
ok('check_footprints good exit 0', log_exit('final_check_footprints_good.log') == 'exit 0')
ok('check_footprints renamed ball exit 1', log_exit('final_check_footprints_broken_ball.log') == 'exit 1')
ok('check_footprints missing pad exit 1', log_exit('final_check_footprints_broken_missing.log') == 'exit 1')
u1 = open(os.path.join(HERE, 'final_measure_u1.log')).read()
ok('U1: 61 names matched 61 pads and only one orientation fits', 'RESULT PASS: 61 names matched 61 pads' in u1 and "['A1 top left (used)']" in u1)
pl = [r for r in csv.DictReader(open(os.path.join(DESIGN, 'mech', 'thin', 'placement.csv'))) if r['reference'] == 'J1'][0]
ok('placement.csv J1 housing is 3.2 x 5.2 (size_x %s, size_y %s)' % (pl['size_x'], pl['size_y']), pl['size_x'] == '3.200' and pl['size_y'] == '5.200')
dl = open(os.path.join(HERE, 'doc-lines.txt')).read()
ok('Hirose catalogue line for FH35C-15S shows A 6.1 and C 4.2', re.search(r'FH35C-15S-0\.3SHW\(50\) CL580-2919-0-50 15 6\.1 3\.6 4\.2', dl) is not None)
ok('depth 4.2 (X) against 3.2 is 1.0 deeper', abs((4.2 - 3.2) - 1.0) < 1e-9)
nc = notes.split('### g. Not closed')[1].split('## Deferred items answered')[0]
n_items = len(re.findall(r'^\d+\. ', nc, re.M))
ok('Not closed list in the notes has 8 items (count %d)' % n_items, n_items == 8)
last_note = [l for l in notes.splitlines() if l.strip()][-1]
ok('last line of footprint-notes.md starts with RESULT:', last_note.startswith('RESULT:'), last_note[:80])
ok('the reply quotes the last line of the notes exactly', last_note in reply)
ok('final_check_netlist_full.log holds RESULT PASS netlist netlist.csv', 'RESULT PASS netlist netlist.csv' in open(os.path.join(HERE, 'final_check_netlist_full.log')).read())
ok('final_erc_report.txt holds the ERC line', '** ERC messages: 0  Errors 0  Warnings 0' in open(os.path.join(HERE, 'final_erc_report.txt')).read())
fa = open(os.path.join(HERE, 'fetch_attempts.log')).read()
ok('fetch_attempts.log: no row returned a PDF', 'PDF document' not in fa, '%d rows' % len(fa.strip().splitlines()))
hp = open(os.path.join(RING, 'sch-notes.md')).read()
ok('sch-notes.md has the W1 section', '## W1 (2026-11-13)' in hp)

# ---- 5. disagreements between statements of the reply and the notes
print('== 5. reply against notes')
for what, pat in (('footprints', r'(\d+) footprints'), ('parts', r'the (\d+) parts'), ('rows', r'(\d+) rows')):
    rv = sorted(set(re.findall(pat, reply)))
    nv = sorted(set(re.findall(pat, notes)))
    ok('%s: reply %s vs notes %s share a value and no reply value is missing from the notes' % (what, rv, nv), all(v in nv for v in rv))
rn = re.search(r'Not closed \((\d+)\)', reply)
ok('reply does not restate a different Not closed count (%s), notes list has %d' % (rn.group(1) if rn else 'none', n_items), rn is None or int(rn.group(1)) == n_items)
rr = re.search(r'(\d+) items under Not closed', notes)
ok('notes RESULT line says %s items under Not closed, list has %d' % (rr.group(1) if rr else '?', n_items), rr and int(rr.group(1)) == n_items)

print('claims checked: %d, failures: %d' % (checked, len(fails)))
for f in fails:
    print('FAILED:', f)
sys.exit(1 if fails else 0)
