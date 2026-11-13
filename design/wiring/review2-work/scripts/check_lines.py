# B1/B2: each csv line's board ends against the KiCad pad dumps (all 7 sizes for band boards); once-only; cut fields; coverage of interface pads
import csv,sys,re,collections,glob,os
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
W=R+'design/wiring/review2-work/'
csvpath=sys.argv[1] if len(sys.argv)>1 else R+'design/wiring/product-wiring.csv'
def load(n):
    d={}
    for r in csv.DictReader(open(W+'pads/%s.csv'%n)): d.setdefault((r['ref'],r['pad']),[]).append(r)
    return d
P={'ring':load('ring'),'case_main':load('case_main'),'case_pins':load('case_pins')}
for f in (1,2):
    for s in range(7,14): P['flex%d-us%d'%(f,s)]=load('flex%d-us%d'%(f,s))
def boards(name):
    n=name.lower()
    if n.startswith('ring main board'): return ['ring']
    if n.startswith('flex1'): return ['flex1-us%d'%s for s in range(7,14)]
    if n.startswith('flex2'): return ['flex2-us%d'%s for s in range(7,14)]
    if 'pin board' in n: return ['case_pins']
    if 'case main board' in n: return ['case_main']
    return None
rows=list(csv.DictReader(open(csvpath)))
fails=[];checked=0;inst=0;used=collections.Counter()
pairs=collections.Counter()
for r in rows:
    ends=[]
    for e in 'AB':
        b=boards(r['end_%s_board'%e]); ref=r['end_%s_ref'%e]; pin=r['end_%s_pin'%e].split(' ')[0]; sig=r['signal_%s'%e]
        if b is None or ref.startswith('copper') or ref=='band metal': ends.append(None); continue
        ends.append((ref,pin))
        for bn in b:
            got=P[bn].get((ref,pin))
            inst+=1
            if not got: fails.append('%s end %s %s:%s:%s not on board'%(r['id'],e,bn,ref,pin)); continue
            nets={g['net'] for g in got}
            if nets!={sig}: fails.append('%s end %s %s %s:%s net %s != %s'%(r['id'],e,bn,ref,pin,nets,sig))
            face=r['end_%s_face'%e]
            lay=got[0]['pad_layers']
            if face.startswith('F.Cu') and 'F.Cu' not in lay.split('|'): fails.append('%s end %s face %s but pad %s'%(r['id'],e,face,lay))
            if face.startswith('B.Cu') and 'B.Cu' not in lay.split('|'): fails.append('%s end %s face %s but pad %s'%(r['id'],e,face,lay))
            used[(bn,ref,pin)]+=1
    if r['signal_A'] and r['signal_B'] and r['pairing_rule'].startswith('same net') and r['signal_A']!=r['signal_B']: fails.append('%s same net but %s/%s'%(r['id'],r['signal_A'],r['signal_B']))
    key=tuple(sorted(['%s|%s|%s'%(r['end_%s_board'%e],r['end_%s_ref'%e],r['end_%s_pin'%e]) for e in 'AB']))
    m=re.search(r'hot bar \(main board land to (FLEX[12]) tail land (\d+)\)',r['join_A'])
    if m and r['end_A_ref'].startswith('J_BAND'):
        k=r['end_A_pin'].split(' ')[0]
        if m.group(2)!=k: fails.append('%s tail land %s != board land %s'%(r['id'],m.group(2),k))
        for s_ in range(7,14):
            bn='%s-us%d'%(m.group(1).lower(),s_); g=P[bn].get((r['end_A_ref'],k))
            if not g or g[0]['net']!=r['signal_A']: fails.append('%s tail %s land %s net %s'%(r['id'],bn,k,g and g[0]['net']))
            used[(bn,r['end_A_ref'],k)]+=1
    pairs[key]+=1
    if r['carrier_kind'] in ('lead','wire','tab','part cable'):
        cuts=[r['cut_mm_us%d'%s] for s in range(7,14)]
        if not (all(cuts) or 'not size dependent' in r['cut_note']): fails.append('%s %s: no cut per size and no not-size-dependent'%(r['id'],r['carrier_kind']))
        if not r['carrier_marking']: fails.append('%s no marking'%r['id'])
    checked+=1
dups=[k for k,v in pairs.items() if v>1]
print('lines read',checked,'board pad instances checked',inst)
print('duplicate end pairs',dups)
# coverage: interface pads (connectors, off-board part lands, wire pads, spring pins)
iface=[('ring','J_BAND_A'),('ring','J_BAND_B'),('ring','J1'),('ring','ANT1'),('case_pins','P'),('case_pins','WP'),('case_pins','E1'),('case_main','W'),('case_main','TH1')]
for f in (1,2):
    for s in range(7,14): iface.append(('flex%d-us%d'%(f,s),''))
unc=[]
for bn,pre in iface:
    for (ref,pin),g in P[bn].items():
        if pre and not re.match(re.escape(pre)+(r'\d*$' if pre in('P','WP','W') else '$'),ref): continue
        if ref=='J1' and pin in('MP','3'): continue
        if (bn,ref,pin) not in used: unc.append((bn,ref,pin,g[0]['net']))
print('interface pads not on any line',len(unc))
for u in unc: print('  ',u)
for f in fails: print('FAIL',f)
print('RESULT lines=%d fails=%d uncovered=%d dups=%d'%(checked,len(fails),len(unc),len(dups)))
