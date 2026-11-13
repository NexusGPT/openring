"""Lists every new or changed cell of design/bom.csv (against evidence/a7/before/bom.csv, matched by reference) and
any of them that holds an absolute path of this machine."""
import csv
B = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/evidence/a7/before/bom.csv")
A = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/bom.csv")
old = {r['reference']: r for r in csv.DictReader(open(B))}
new = list(csv.DictReader(open(A)))
changed = bad = 0
for r in new:
    o = old.get(r['reference'])
    for k, v in r.items():
        if o is None or o.get(k) != v:
            changed += 1
            if '/Users/' in v or v.startswith('/'):
                bad += 1
                print('ABSOLUTE', r['reference'], k, v[:100])
print('deleted lines', sorted(set(old) - {r['reference'] for r in new}))
print('new or changed cells', changed, 'with an absolute path', bad)
