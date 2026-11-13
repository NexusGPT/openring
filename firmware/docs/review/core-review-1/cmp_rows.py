import re,sys
B=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
doc=open(B+"design/firmware.md",encoding="utf-8").read().split("\n")
spec=[]
for i in range(132,193):
    l=doc[i]
    c=[x.strip() for x in l.strip().strip("|").split(" | ")]
    spec.append((i+1,c[0].strip("`"),c[1],c[2].strip("`"),c[3]))
inc=open(B+"firmware/modules/ring_core/src/state_table.inc").read().split("\n")
rows=[]
for l in inc:
    m=re.match(r'RC_ROW\((\d+), (\d+), (\w+), (\w+), (\w+), (\w+), "(.*)"\)$',l)
    if m: rows.append(m.groups())
print("spec rows",len(spec),"code rows",len(rows))
bad=0
for s,r in zip(spec,rows):
    n,line,fr,ev,g,to,txt=r
    txt=txt.replace('\\"','"')
    ok = int(line)==s[0] and fr==s[1] and to==s[3] and txt==s[2]
    print(("OK  " if ok else "DIFF"),n,s[0],s[1],"|",s[2][:50],"|",s[3],"||",fr,ev,g,to)
    bad+= (not ok)
print("diffs",bad)
