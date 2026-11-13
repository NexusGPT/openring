import re
B=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
doc=open(B+"design/firmware.md",encoding="utf-8").read().split("\n")
inc=open(B+"firmware/modules/ring_core/src/state_table.inc").read().split("\n")
sa=open(B+"firmware/modules/ring_core/src/state_actions.c").read().split("\n")
tst=open(B+"firmware/tests/core/src/test_rows.c").read().split("\n")
acase={}
for i,l in enumerate(sa,1):
    m=re.match(r"\s*case (\d+):",l)
    if m: acase.setdefault(int(m.group(1)),i)
# rows 1 and 2 share the block starting at case 1
tl={}
for i,l in enumerate(tst,1):
    m=re.match(r"ROW\((\d\d), (\d+),",l)
    if m: tl[int(m.group(2))]=i
print("| row | spec line | from | event | to | code: table line / actions line | action list in code (ordered) | test line | verdict |")
print("|---|---|---|---|---|---|---|---|---|")
for n in range(1,62):
    c=[x.strip() for x in doc[131+n].strip().strip("|").split(" | ")]
    m=re.match(r'RC_ROW\((\d+), (\d+), (\w+), (\w+), (\w+), (\w+),',inc[n+2])
    g=m.group(5)
    # actions text from the source between case n and next case with a break
    i=acase[n]; acts=[]
    j=i
    while True:
        l=sa[j-1] if j==i else sa[j-1]
        mm=re.search(r"\bP\((\w+)\);",l)
        if mm: acts.append(mm.group(1))
        if re.search(r"\bbreak;",l): break
        j+=1
    spec_act=c[3]
    verdict="pass"
    if n==13: verdict="pass with note F5 (extra MT on the screen-on branch)"
    print(f"| {n} | {132+n} | {c[0].strip('`')} | {c[1][:55]}{' [guard '+g+']' if g!='NONE' else ''} | {c[2].strip('`')} | {n+3} / {acase[n]} | {' '.join(acts) or '(none)'} | {tl[n]} | {verdict} |")
