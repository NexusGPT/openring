import pymupdf,re,sys
f=sys.argv[1]; pats=sys.argv[2:]
d=pymupdf.open((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/")+f)
for i,p in enumerate(d):
    t=p.get_text().replace('\n',' | ')
    for pt in pats:
        for m in list(re.finditer(pt,t))[:2]:
            print(f,'p',i+1,pt,'>>',t[max(0,m.start()-150):m.start()+350]); print()
