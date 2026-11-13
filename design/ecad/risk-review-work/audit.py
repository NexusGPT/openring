# Final audit: every `path` line N "text" citation in the review and the reply is opened and the text looked for on line N;
# also: the quote check is run again, decision lines counted, verdict counts recomputed from the table.
import re,os,sys,subprocess
ROOT=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
files=[ROOT+'design/ecad/risk-review.md']+sys.argv[1:]
short={'netlist.csv':'design/ecad/ring/netlist.csv','parts.csv':'design/ecad/ring/parts.csv',
 'case/netlist.csv':'design/ecad/case/netlist.csv','case/parts.csv':'design/ecad/case/parts.csv','case/sch-notes.md':'design/ecad/case/sch-notes.md'}
pat=re.compile(r'`([^`]+)` lines? (\d+)(?: \([^)]*\))? "([^"]+)"')
n=bad=unres=0
for f in files:
    t=open(f,encoding='utf-8').read()
    for m in pat.finditer(t):
        p,ln,txt=m.group(1),int(m.group(2)),m.group(3)
        p=short.get(p,p)
        fp=ROOT+p
        if not os.path.exists(fp):
            unres+=1; print('UNRESOLVED',p,ln,txt); continue
        L=open(fp,encoding='utf-8').read().split('\n')
        n+=1
        ok= ln<=len(L) and txt in L[ln-1]
        if not ok:
            bad+=1; hits=[i+1 for i,l in enumerate(L) if txt in l]
            print('MISMATCH',p,ln,repr(txt),'found on lines',hits)
        else: print('OK',p,ln,txt[:70])
print(f'citations checked {n}, mismatched {bad}, unresolved {unres}')
r=open(ROOT+'design/ecad/risk-review.md',encoding='utf-8').read()
rows=re.findall(r'^\| (ring|case) (\d+) [^|]*\| ([A-Z ’\']+?) \|',r,re.M)
from collections import Counter
print('table rows',len(rows),dict(Counter(v for _,_,v in rows)))
for nm in ['design/ecad/ring/sch-notes.md','design/ecad/case/sch-notes.md']:
    print(nm,'decision lines',sum(1 for l in open(ROOT+nm) if l.startswith('Decision 2026-11-13:')))
q=subprocess.run([sys.executable,'-I',ROOT+'design/ecad/risk-review-work/verify_quotes.py'],capture_output=True,text=True).stdout.strip().splitlines()[-1]
print('quote check again:',q)
print('proposals',len(re.findall(r'^\| P\d ',r,re.M)),'measurements',len(re.findall(r'^\| M\d ',r,re.M)))
print('last line:',r.rstrip('\n').split('\n')[-1][:60])
