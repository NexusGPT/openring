import csv
N={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))):
    if r['reference']=='U2': N[r['pin_number']]=(r['net'] or '(no connect)',r['pin_name'])
P={
'A1':('none','none','not connected: land only'),'A2':('none','none','not connected: land only'),'A3':('none','none','not connected: land only'),
'A4':('L1','none','L1 east (+X) to C86'),'A5':('L1','none','L1 east (+X) to C87'),
'A6':('L1','none','L1 east (+X), 0.15 mm, into the L1 ground copper; its stacks to L4 sit at least 1.0 mm east of the body, off the B6 line of L2 (g.5)'),
'A7':('L1','none','L1 east (+X), 0.2 mm, to its own GND stack L1-L4 at (10.00, 1.26) (PVSS1, NPM-DS schematic note)'),
'B1':('L1','none','L1 north (-Y), 0.25 mm; joined to B2 by a 0.15 mm copper bridge on L1; then on L3 (0.60) to tail B pad 4'),
'B2':('L1','none','joined to B1 on L1 (same net)'),
'B3':('none','none','not connected: land only'),
'B4':('L2','microvia L1-L2 in pad','L2 east (+X) through the A4 site'),
'B5':('L2','microvia L1-L2 in pad','L2 east (+X) through the A5 site'),
'B6':('L2','microvia L1-L2 in pad','L2 east (+X) through the A6 site'),
'B7':('L1','none','L1 south (+Y) to Y 1.65, east along Y 1.65 to X 10.20, south to the west pad of L71 (11.00, 3.45); 0.15 mm, no via'),
'C1':('L1','none','L1 north (-Y), 0.15 mm, to C75, C76, C77; joined to C2 on L1'),
'C2':('L1','none','joined to C1 on L1 (same net)'),
'C3':('L2','microvia L1-L2 in pad','L2 north (-Y) through the C2 and C1 sites, to C73'),
'C4':('none','none','not connected: land only'),'C5':('none','none','not connected: land only'),
'C6':('L2','microvia L1-L2 in pad','L2 south (+Y) through the C7 site'),
'C7':('L1','none','L1 south (+Y), 0.15 mm, to C74 at (8.50, 2.15), between the two switching tracks'),
'D1':('L1','none','L1 north (-Y), 0.15 mm; joined to D2 on L1; then on L3 (0.30) to tail B pad 1 and C85'),
'D2':('L1','none','joined to D1 on L1 (same net)'),
'D3':('L2','microvia L1-L2 in pad','L2 west (-X) through the E3 site'),
'D4':('L2','microvia L1-L2 in pad','L2 west (-X) through the E4 site'),
'D5':('none','none','not connected: land only'),
'D6':('L2','microvia L1-L2 in pad','L2 west (-X) through the E6 site'),
'D7':('L1','none','L1 south-west to (7.60, 1.72), south along X 7.60 to the west pad of L72 (8.50, 3.45); 0.15 mm, no via'),
'E1':('L1','none','L1 north (-Y) to R72'),'E2':('L1','none','L1 west (-X) to R71'),'E3':('L1','none','L1 west (-X), toward U1 E7'),
'E4':('L1','none','L1 west (-X)'),'E5':('L1','none','L1 west (-X), toward U1 B8'),'E6':('none','none','not connected: land only'),
'E7':('L1','none','L1 west (-X), 0.2 mm, to its own GND stack L1-L4 at (7.00, 1.26) (PVSS2, NPM-DS schematic note), shared with the ground pad of C88 at (7.00, 1.95)'),
}
rows=[]
for b in sorted(P,key=lambda b:(b[0],int(b[1:]))):
    x=(int(b[1])-4)*0.419; y=('ABCDE'.index(b[0])-2)*0.44
    X,Y=8.5-y, 0.0+x   # rotation 90: (x,y) -> (-y, x)
    net,name=N[b]; lay,via,how=P[b]
    rows.append(f'| {b} | {name} | {net} | {X:.3f}, {Y:+.3f} | {lay} | {via} | {how} |')
open('u2_table.md','w').write('\n'.join(rows)+'\n')
print(rows[6]); print(rows[13]); print(rows[34])
