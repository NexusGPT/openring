#!/usr/bin/env python3
"""usage: compare_rows.py <before rows.csv> <after rows.csv>: prints every row with its status and value on both sides,
and the list of rows that went PASS to FAIL and FAIL to PASS."""
import csv, sys
a = {r['id']: r for r in csv.DictReader(open(sys.argv[1]))}
b = {r['id']: r for r in csv.DictReader(open(sys.argv[2]))}
p2f, f2p = [], []
for k in sorted(set(a) | set(b), key=lambda x: (x[0], [int(t) for t in x[1:].split('.')])):
    ra, rb = a.get(k, {}), b.get(k, {})
    print('%-6s %-34s before %-4s %-12s after %-4s %-12s' % (k, (ra or rb).get('qty', ''), ra.get('ok', '-'), ra.get('value', '-'), rb.get('ok', '-'), rb.get('value', '-')))
    if ra.get('ok') == 'PASS' and rb.get('ok') != 'PASS': p2f.append(k)
    if ra.get('ok') != 'PASS' and rb.get('ok') == 'PASS': f2p.append(k)
print('rows before %d, after %d' % (len(a), len(b)))
print('PASS to FAIL: %s' % (', '.join(p2f) or 'none'))
print('FAIL to PASS: %s' % (', '.join(f2p) or 'none'))
