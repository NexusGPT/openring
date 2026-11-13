#!/usr/bin/env python3
"""Freezes the electrical designators of design/case/case-bom.csv into bom_refs_snapshot.csv."""
import csv, re, os, time
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/")
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
src = 'case-bom.csv mtime %s' % time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(D + 'case/case-bom.csv')))
rows = []
for r in csv.DictReader(open(D + 'case/case-bom.csv')):
    for x in expand(r['reference']):
        if not MECH.match(x):
            rows.append((x, src))
with open(D + 'ecad/case/bom_refs_snapshot.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['reference', 'source']); w.writerows(rows)
print(len(rows), src)
