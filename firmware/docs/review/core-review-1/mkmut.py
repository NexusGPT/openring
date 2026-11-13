import glob,os
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware/docs/review/core-review-1")
rows=[]
for f in ["mut-results.tsv","mut-results2.tsv","mut-results3.tsv"]:
    for l in open(os.path.join(R,f),encoding="utf-8"):
        p=l.rstrip("\n").split("\t")
        if len(p)==5: rows.append(p)
print("| # | mutation | file:line changed | failing tests (first 3 of N) | caught | log |")
print("|---|---|---|---|---|---|")
for n,c,nf,names,desc in rows:
    d=os.path.join(R,"mut",n,"change.diff")
    ln=open(d).readline().strip() if os.path.exists(d) else "?"
    nm=",".join(x.split(".")[-1] for x in names.split(",")[:3] if x)
    print(f"| {n} | {desc} | diff `{ln}` | {nf}: {nm} | {c} | mut/{n}/host-run.log |")
tot=len(rows)
ap=[r for r in rows if r[1] not in("NOT-APPLIED","COMPILE-ERROR")]
print()
print("rows in tsv",tot,"applied and compiled",len(ap),"caught yes",sum(1 for r in ap if r[1]=="yes"),"survived NO",sum(1 for r in ap if r[1]=="NO"))
print("not applied/compile error:",[r[0]+":"+r[1] for r in rows if r[1] in("NOT-APPLIED","COMPILE-ERROR")])
print("survivors:",[r[0] for r in ap if r[1]=="NO"])
