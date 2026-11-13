import csv
W=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/")
for name,p in (("live csv",W+"product-wiring.csv"),("rebuilt copy",W+"checks-harden-work/copies/rebuilt-fixed.csv")):
    b=open(p,'rb').read()
    print(name,"bytes",len(b),"CR",b.count(b"\r"),"LF",b.count(b"\n"))
a=list(csv.DictReader(open(W+"product-wiring.csv",newline="")));c=list(csv.DictReader(open(W+"checks-harden-work/copies/rebuilt-fixed.csv",newline="")))
d=[(x['id'],k) for x,y in zip(a,c) for k in x if x[k]!=y[k]]
print("rows",len(a),len(c),"differing fields",len(d),sorted(set(d)))
