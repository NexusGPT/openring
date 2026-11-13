import os,re,glob
D=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/firmware/docs/review/core-review-2/mut")
out=[]; caught=0; total=0; missed=[]; invalid=[]
out.append('| # | Mutation | Host tests failed (of 181) | Caught by host tests | My probes that failed (A/B/C/D) | Log |')
out.append('|---|---|---|---|---|---|')
for w in sorted(glob.glob(D+'/m[0-9][0-9]*_*')):
    name=os.path.basename(w)
    hl=open(w+'/host-run.log').read().split('\n')
    if not os.path.exists(w+'/mutation.diff'):
        out.append('| - | %s | pattern did not apply, the copy ran unmutated (invalid, replaced by m05b) | invalid | - | mut/%s/host-run.log |'%(name,name)); invalid.append(name); continue
    if 'compile failed' in '\n'.join(hl):
        out.append('| - | %s | build error (mutation does not compile, not counted) | invalid | - | mut/%s/host-run.log |'%(name,name)); invalid.append(name); continue
    fails=[l[5:] for l in hl if l.startswith('FAIL ')]
    res=[l for l in hl if l.startswith('RESULT')]
    pr=''
    for pn,k in (('pA_standby_entry','A'),('pB_hold','B'),('pC_scen','C'),('pD_fuzz','D')):
        t=open(w+'/'+pn+'.log').read().strip().split('\n')[-1] if os.path.exists(w+'/'+pn+'.log') else 'missing'
        pr+=(k if t!='exit 0' else '-')
    gen=any('generator' in f for f in fails)
    c = len(fails)>0
    total+=1; caught+=c
    if not c: missed.append(name)
    short=', '.join(f.split(' ')[0].split('.')[-1] for f in fails[:3])+(' ...' if len(fails)>3 else '')
    out.append('| %d | %s | %d: %s | %s | %s | %s |'%(total,name,len(fails),short,'yes' if c else '**NO**',pr,'mut/%s/host-run.log'%name))
open(D+'/mutation-table.md','w').write('\n'.join(out)+'\n')
print('invalid',invalid,'mutations',total,'caught by host tests',caught,'missed',missed)
