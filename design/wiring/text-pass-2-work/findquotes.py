import csv,re,os
R=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
out=[]
for f in ['state-a','state-b']:
    for x in csv.DictReader(open(R+f'design/wiring/deferred-work/{f}.csv')):
        files=[s.strip() for s in re.split(r'\s*[|;]\s*',x['file']) if s.strip()]
        lines=[s.strip() for s in re.split(r'\s*[|;]\s*',x['line'])]
        quotes=[s.strip() for s in x['quote'].split(' | ')]
        uf=[]
        for s in files:
            if s not in uf: uf.append(s)
        for q in quotes:
            hits=[]
            for fn in uf:
                p=R+fn
                if not os.path.exists(p): hits.append((fn,'MISSING FILE')); continue
                for i,l in enumerate(open(p,encoding='utf-8',errors='replace'),1):
                    if q in l: hits.append((fn,i))
            out.append((x['item'],x['state'][:12],q[:50],hits[:4]))
for o in out: print(o)
