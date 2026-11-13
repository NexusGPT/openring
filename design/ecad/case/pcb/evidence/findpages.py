import pymupdf, sys, re
D=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/")
f=sys.argv[1]; pats=sys.argv[2:]
d=pymupdf.open(D+f)
for i,pg in enumerate(d):
    t=pg.get_text()
    hits=[p for p in pats if re.search(p,t,re.I)]
    if hits: print(f,'page',i+1,hits)
