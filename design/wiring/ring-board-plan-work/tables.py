import csv
B={r['ball']:(float(r['x_mm']),float(r['y_mm'])) for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/w1-evidence/u1-measured-pads.csv")))}
N={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))):
    N[(r['reference'],r['pin_number'])]=(r['net'] or '(no connect)',r['pin_name'])
NE={r['ball']:r for r in csv.DictReader(open('nordic-escape.csv'))}
ring1=set('A4 A5 A6 A7 A8 A9 A10 H1 H2 H4 H5 H6 H7 H8 H9 H10 B2 B10 C1 D10 E1 E10 F1 F10 G1 G10'.split())
ring2=set('B4 B5 B6 B7 B8 B9 G2 G4 G5 G6 G7 G8 G9 E2 F2 D9 E9 F9'.split())
ring3=set('A1 A2 D5 D6 D7 D8 F4 F5 F6 F7 F8 E4 E7'.split())
drop=set('E5 E6 E8'.split())
def side(b):
    r=b[0]; c=int(b[1:])
    if b=='B2' or b=='C1' or c==1: return 'west (-X)'
    if r=='A': return 'north (-Y)'
    if r=='H': return 'south (+Y)'
    if c==10: return 'east (+X)'
    return '?'
def l2dir(b):
    if b[0]=='B': return 'north (-Y), straight through the row A site'
    if b[0]=='G': return 'south (+Y), straight through the row H site'
    if b in('E2','F2'): return 'west (-X), along its row through the column 1 site'
    return 'east (+X), along its row through the column 10 site'
def l3dir(b):
    if b[0]=='D': return 'north (-Y), straight through the row B and row A sites'
    if b[0]=='F': return 'south (+Y), straight through the row G and row H sites'
    if b=='E4': return 'north (-Y) through the empty site of column 3 in row C/D (no ball there), between D3 and D5, then through the B4 and A4 sites'
    if b=='A1': return 'south (+Y) along the column 1 line X 2.698 inside the body (column 1 sites have no via on L3), out through the H1 site, to X1 (d.4)'
    if b=='A2': return 'south (+Y) along the column 2 line X 3.024 inside the body (B2, D3, E2, F2, G2 have no via on L3), out through the H2 site, to X1 (d.4)'
    if b=='E7': return 'east (+X), along row E through the empty E8 site, then the E9 and E10 sites'
rows=[]
order=sorted(B,key=lambda b:(b[0],int(b[1:])))
cnt={'L1':0,'L2':0,'L3':0,'L4':0,'none':0}
for b in order:
    x,y=B[b]; net,name=N[('U1',b)]
    gnd = net=='GND'
    if b in ring1:
        if gnd: how=f'L1, 0.15 mm track {side(b)} to a GND stack L1-L4 placed 0.35 mm outside the body edge'; lay='L1'
        else: how=f'L1 direct, track leaves {side(b)}'+(' (crosses the RF line on L3: stack L1-L3 at X 2.30)' if b in ('F1','G1') else ''); lay='L1'
        via='none'
    elif b=='D3':
        how='microvia L1-L2 in the pad into the L2 ground copper, joined west along its row under the C1 site (L2 is solid ground there: the RF reference, d.1)'; lay='L2'; via='microvia L1-L2 in pad'
    elif b in ring2:
        how='L2, '+l2dir(b)+(' (crosses the RF line on L3: via L2-L3 at X 2.00)' if b in ('E2','F2') else ''); lay='L2'; via='microvia L1-L2 in pad'
    elif b in ring3:
        how='L3, '+l3dir(b); lay='L3'; via='2 stacked microvias L1-L2, L2-L3 in pad'
    else:
        how='not connected: land only, no via, no track (its test pad is removed, see h)'; lay='none'; via='none'
    cnt[lay]+=1
    ne=NE[b]; nord=(ne['exit'] or 'no exit')+' '+(ne['vias'].replace('@pad',' in pad') or 'no via')
    rows.append(f'| {b} | {name} | {net} | {4+x:.3f}, {y:+.3f} | {lay} | {via} | {how} | {nord} |')
open('u1_table.md','w').write('\n'.join(rows)+'\n')
print(cnt)
# U2
U2=[]
col=lambda b:int(b[1]); rowi=lambda b:'ABCDE'.index(b[0])
plan={
'A1':('none','none','not connected: land only'),'A2':('none','none','not connected: land only'),'A3':('none','none','not connected: land only'),
'A4':('L1','none','L1 north (-Y) to C86'),'A5':('L1','none','L1 north (-Y) to C87'),
'A6':('L1','none','L1 north (-Y), 0.15 mm, to its own GND stack L1-L4 0.35 mm outside the body'),
'A7':('L1','none','L1 east (+X), 0.2 mm, to its own GND stack L1-L4 (PVSS1 net tie, Nordic Figure 59 note); return of C74'),
'B1':('L1','none','L1 west (-X), 0.25 mm; joined to B2 by a 0.15 mm copper bridge on L1'),
'B2':('L1','none','joined to B1 on L1 (same net)'),
'B3':('none','none','not connected: land only'),
'B4':('L2','microvia L1-L2 in pad','L2 north (-Y) through the A4 site'),
'B5':('L2','microvia L1-L2 in pad','L2 north (-Y) through the A5 site'),
'B6':('L2','microvia L1-L2 in pad','L2 north (-Y) through the A6 site'),
'B7':('L1','none','L1 east (+X), 0.15 mm, then south outside the SW2 track to L71 at its new place X 11.0 (see f)'),
'C1':('L1','none','L1 west (-X), 0.15 mm; joined to C2 on L1'),
'C2':('L1','none','joined to C1 on L1 (same net)'),
'C3':('L2','microvia L1-L2 in pad','L2 west (-X) through the C2 and C1 sites, to C73'),
'C4':('none','none','not connected: land only'),'C5':('none','none','not connected: land only'),
'C6':('L2','microvia L1-L2 in pad','L2 east (+X) through the C7 site'),
'C7':('L1','none','L1 east (+X), 0.15 mm, to C74, C75, C88'),
'D1':('L1','none','L1 west (-X), 0.15 mm; joined to D2 on L1'),
'D2':('L1','none','joined to D1 on L1 (same net)'),
'D3':('L2','microvia L1-L2 in pad','L2 south (+Y) through the E3 site'),
'D4':('L2','microvia L1-L2 in pad','L2 south (+Y) through the E4 site'),
'D5':('none','none','not connected: land only'),
'D6':('L2','microvia L1-L2 in pad','L2 south (+Y) through the E6 site'),
'D7':('L1','none','L1 east (+X), 0.15 mm, then south to L72 at its new place X 8.5 (see f)'),
'E1':('L1','none','L1 south (+Y) to R72'),'E2':('L1','none','L1 south (+Y) to R71'),'E3':('L1','none','L1 south (+Y)'),
'E4':('L1','none','L1 south (+Y)'),'E5':('L1','none','L1 south (+Y)'),'E6':('none','none','not connected: land only'),
'E7':('L1','none','L1 east (+X), 0.2 mm, to its own GND stack L1-L4 (PVSS2 net tie); return of C75 and C88'),
}
r2=[]; c2={}
for b in sorted(plan,key=lambda b:(b[0],int(b[1:]))):
    x=(col(b)-4)*0.419; y=(rowi(b)-2)*0.44
    net,name=N[('U2',b)]; lay,via,how=plan[b]; c2[lay]=c2.get(lay,0)+1
    r2.append(f'| {b} | {name} | {net} | {8.5+x:.3f}, {y:+.3f} | {lay} | {via} | {how} |')
open('u2_table.md','w').write('\n'.join(r2)+'\n'); print(c2)
