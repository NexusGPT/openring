"""Audit of design/mfg/assembly/process.md: every citation is searched again at the page or line it names; every WORK/
file it names exists; every quoted check line is found in its log. Writes logs/audit.log; last line AUDIT ..."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cites_lib import *
W = os.path.dirname(os.path.abspath(__file__))
txt = open(ROOT + '/design/mfg/assembly/process.md', encoding='utf-8').read()
out, n, ok = [], 0, 0
for m in re.finditer(r'\(([A-Z]+\d*) (p\.\d+): "([^"]+)"\)', txt):
    n += 1
    path = D + KEYS[m.group(1)]
    good = m.group(2) in find(path, m.group(3))
    ok += good
    out.append('%s %s %s | %s' % ('FOUND' if good else 'NOTFOUND', m.group(1), m.group(2), m.group(3)))
for m in re.finditer(r'\(([A-Z]+\d*) (:\d+): "([^"]+)"\)', txt):
    n += 1
    good = m.group(2) in find(D + KEYS[m.group(1)], m.group(3)); ok += good
    out.append('%s %s %s | %s' % ('FOUND' if good else 'NOTFOUND', m.group(1), m.group(2), m.group(3)))
for m in re.finditer(r'\(`(design/[^`:]+):(\d+)`: "([^"]+)"\)', txt):
    n += 1
    lines = open(ROOT + '/' + m.group(1), encoding='utf-8', newline='').read().split('\n')
    i = int(m.group(2))
    good = i <= len(lines) and norm(m.group(3)) in norm(lines[i - 1]); ok += good
    out.append('%s %s:%s | %s' % ('FOUND' if good else 'NOTFOUND', m.group(1), m.group(2), m.group(3)))
for m in re.finditer(r'\(([A-Z]+\d*) p\.(\d+), drawing image, seen in WORK/([^)]+)\)', txt):
    n += 1
    pages = len(units(D + KEYS[m.group(1)]))
    good = os.path.isfile(os.path.join(W, m.group(3))) and int(m.group(2)) <= pages; ok += good
    out.append('%s IMAGE %s p.%s %s (pdf pages %d)' % ('FOUND' if good else 'NOTFOUND', m.group(1), m.group(2), m.group(3), pages))
nf = 0
for p in sorted(set(re.findall(r'`WORK/([^`]+)`', txt))):
    for q in re.split(r'`, `', p):
        q = q.rstrip('/')
        e = os.path.exists(os.path.join(W, q))
        nf += 1; ok_f = e
        out.append('%s WORKFILE %s' % ('FOUND' if e else 'NOTFOUND', q))
        n += 1; ok += e
for key, rel in KEYS.items():
    if '(' + key + ' ' in txt or '| ' + key + ' |' in txt:
        e = os.path.isfile(D + rel); n += 1; ok += e
        out.append('%s SOURCEFILE %s %s' % ('FOUND' if e else 'NOTFOUND', key, rel))
checks = [('logs/check-before.log', 'RESULT FAIL 365'), ('logs/check-final.log', 'RESULT FAIL 160'), ('logs/check-after1.log', 'RESULT FAIL 160'),
          ('logs/tests.log', 'TESTS PASS 13 of 13 as expected'), ('logs/list-gaps-final.log', 'GAPS 67 of 99 rows'),
          ('logs/make_gaps.log', 'gap lines 67 complete 32 unplaced 0 []'), ('logs/fill.log', 'FILL changed fields 517 rows 99'),
          ('logs/stencil_calc.log', '302 openings'), ('logs/stencil_calc.log', '45 openings'), ('logs/stencil_calc.log', '265 openings'),
          ('logs/calc.log', 'AR 0.667'), ('logs/calc.log', 'between 0.070 and 0.112 mm'), ('logs/calc.log', '66.4 %'), ('logs/calc.log', 'AR 0.591'),
          ('logs/reason-counts.log', 'hotbar-joint.md 15'), ('logs/reason-counts.log', 'passes 32')]
for f, q in checks:
    e = q in open(os.path.join(W, f)).read(); n += 1; ok += e
    out.append('%s LOGQUOTE %s | %s' % ('FOUND' if e else 'NOTFOUND', f, q))
bad = [l for l in out if l.startswith('NOTFOUND')]
open(W + '/logs/audit.log', 'w').write('\n'.join(out) + '\nAUDIT cited sources found %d of %d, not found %d\n' % (ok, n, len(bad)))
print('\n'.join(bad)); print('AUDIT cited sources found %d of %d, not found %d' % (ok, n, len(bad)))
