# B3: every pad's net on the board equals the netlist row (ref,pin); lists pads with a net and no row, rows with no pad
import csv,sys,collections
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
W=R+'design/wiring/review2-work/'
def nl(p):
    d={}
    for r in csv.DictReader(open(p)): d[(r['reference'],r['pin_number'])]=r['net']
    return d
def pads(n):
    d={}
    for r in csv.DictReader(open(W+'pads/%s.csv'%n)): d.setdefault((r['ref'],r['pad']),set()).add(r['net'])
    return d
ring=nl(R+'design/ecad/ring/netlist.csv'); case=nl(R+'design/ecad/case/netlist.csv')
tot_bad=0
jobs=[('ring',ring),('case_main',case),('case_pins',case)]+[('flex%d-us%d'%(f,s),ring) for f in (1,2) for s in range(7,14)]
if len(sys.argv)>2: jobs=[(sys.argv[1],nl(sys.argv[2]))]
for bn,n in jobs:
    p=pads(bn); match=0; bad=[]; norow=[]
    for k,nets in p.items():
        if k[1] in ('','MP') or k[1].startswith('MP'): 
            if nets-{''}: norow.append((k,nets))
            continue
        if k not in n:
            if nets-{''}: norow.append((k,nets))
            continue
        exp=n[k]
        if exp.lower() in ('no_connect','nc','') or exp.startswith('unconnected'):
            if nets-{''}: bad.append((k,nets,exp))
            else: match+=1
            continue
        if nets=={exp}: match+=1
        else: bad.append((k,nets,exp))
    refs={k[0] for k in p}
    missing=[k for k in n if k[0] in refs and k not in p] if bn in('ring','case_main','case_pins') else []
    tot_bad+=len(bad)
    print(bn,'pads',len(p),'match',match,'wrong',len(bad),'net-but-no-row',len(norow),'rows-of-placed-refs-with-no-pad',len(missing))
    for b in bad: print('   WRONG',b)
    for b in norow: print('   NOROW',b)
    for b in missing[:20]: print('   NOPAD',b,n[b])
print('RESULT parity wrong=%d'%tot_bad)
