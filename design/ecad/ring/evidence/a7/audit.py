"""Final audit of evidence/a7/final_reply.md: pulls every number, backticked path and quoted phrase out of the reply by
itself and prints the first saved evidence line that holds it; lists the ones with no match."""
import re, os, glob
E = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/evidence")
R = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring")
reply = open(os.path.join(E, 'a7', 'final_reply.md')).read()
files = (glob.glob(os.path.join(E, 'a7', '*.log')) + glob.glob(os.path.join(E, 'a7', 'broken', '*')) +
         glob.glob(os.path.join(E, '*a7_final*')) + [os.path.join(R, 'sch-notes.md'), os.path.join(R, 'npm1304-balls.csv'),
         os.path.join(R, 'make_netlist.py'), os.path.join(R, 'check_netlist.py'), (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/bom.csv")])
lines = []
for f in files:
    if os.path.isfile(f) and not f.endswith('.csv') or f.endswith('bom.csv') or f.endswith('balls.csv') or f.endswith('broken.csv'):
        try:
            for i, l in enumerate(open(f, errors='replace').read().split('\n'), 1):
                lines.append((os.path.relpath(f, R), i, l))
        except IsADirectoryError:
            pass
claims = set(re.findall(r'\b\d+(?:\.\d+)?\b', reply))
claims |= set(re.findall(r'`([^`]+)`', reply))
claims |= set(re.findall(r'"([^"]+)"', reply))
claims |= set(re.findall(r'\b(?:A[567]-\d+|[A-Z]+\d+[A-Z0-9-]*)\b', reply))
nomatch = []
for c in sorted(claims):
    key = c.split('/')[-1] if '/' in c else c
    hit = next(((f, i, l) for f, i, l in lines if key in l or (key.endswith('/') and key[:-1] in l)), None)
    if hit is None and os.path.exists(os.path.join(R, c)) or os.path.exists(os.path.join(E, c)) or os.path.exists(os.path.join(R, '..', '..', '..', c)):
        hit = hit or ('(path exists)', 0, c)
    if hit:
        print('MATCH %-40s %s:%d %s' % (c[:40], hit[0], hit[1], hit[2].strip()[:110]))
    else:
        nomatch.append(c); print('NO MATCH', c)
print('claims checked', len(claims), 'no match', len(nomatch), nomatch)
