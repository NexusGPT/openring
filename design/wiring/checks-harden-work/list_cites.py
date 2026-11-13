import re,sys
doc=open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md"),encoding="utf-8").read().split("\n")
CITE=re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|csv|txt|py)):(\d+)`")
n=0
for i,l in enumerate(doc,1):
    for m in CITE.finditer(l):
        if "bom.csv" in m.group(1):
            n+=1
            a=max(l.rfind(". ",0,m.start()),0); print(i,m.group(0),"||",l[a:m.end()+30][:230])
print(n)
