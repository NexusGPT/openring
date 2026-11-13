import re,subprocess
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
D=R+'/firmware/docs/review/core-review-2'
doc=open(R+'/design/firmware.md').read().split('\n')
acts=open(R+'/firmware/modules/ring_core/src/state_actions.c').read().split('\n')
caseline={}
for i,l in enumerate(acts,1):
    m=re.match(r'\tcase (\d+):',l)
    if m: caseline[int(m.group(1))]=i
dump=[l.rstrip('\n').split('|') for l in open(D+'/rows/rows-dump.txt')]
byrow={}
for p in dump: byrow.setdefault(int(p[0]),[]).append(p)
rows=[]
for n in range(1,67):
    c=[x.strip().replace('`','') for x in doc[131+n].strip().strip('|').split('|')]
    p=byrow[n][0]
    g=p[3]
    rows.append('| %d | %d | %s | %s%s | %s | %s | inc:%d, actions:%d | pass |'%(n,132+n,c[0],c[1][:70],'' if g=='NONE' else ' [guard %s]'%g,c[2],p[7] if n not in (16,57) else ' / '.join(x[7] for x in byrow[n]),n+3,caseline[n]))
mt=open(D+'/mut/mutation-table.md').read()
chk=open(D+'/rows/check_rows.log').read().strip()
exact=open(D+'/rows/exact_event_text.log').read().strip()
rep=open(D+'/report_body.md').read()
rep=rep.replace('@@ROWS@@','\n'.join(rows)).replace('@@MUT@@',mt).replace('@@CHK@@',chk).replace('@@EXACT@@',exact)
open(D+'/core-review-2.md','w').write(rep)
print('written',len(rep))
