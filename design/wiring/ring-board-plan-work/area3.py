import sys,csv,math
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
from rules import override_cy, KEEPOUTS, overlap
rows=list(csv.DictReader(open('placement-plan.csv')))
F=0;B=0;lib=0;byfp={}
cys={}
for r in rows:
    x,y,rot=float(r['x_mm']),float(r['y_mm']),int(r['rotation_deg'])
    cy0,_=place(r['footprint'],x,y,rot); cy=override_cy(r['reference'],cy0,x,y,rot)
    a=(cy[2]-cy[0])*(cy[3]-cy[1]); a0=(cy0[2]-cy0[0])*(cy0[3]-cy0[1])
    if r['side']=='F': F+=a; lib+=a0; cys[r['reference']]=cy
    else: B+=a
    k=r['footprint'].split(':')[1]; byfp[k]=byfp.get(k,0)+a
board=27.2*12.6-4*(0.8**2-math.pi*0.8**2/4)
ant=sum((k['r'][2]-k['r'][0])*(k['r'][3]-k['r'][1]) for k in KEEPOUTS if k['name']=='antenna')
antpart=0
for ref in ('ANT1','LT1'):
    c=cys[ref]
    for k in KEEPOUTS:
        if k['name']!='antenna': continue
        r=k['r']; w=max(0,min(c[2],r[2])-max(c[0],r[0])); h=max(0,min(c[3],r[3])-max(c[1],r[1])); antpart+=w*h
print('board %.1f mm2'%board)
print('F-side courtyards (library bbox incl. stroke, J1/J_BAND/U5/U6 as overrides) %.1f; same with the library courtyards unchanged %.1f'%(F,lib))
print('antenna keep-out on the board %.2f, of it under ANT1 and LT1 %.2f, rest %.2f'%(ant,antpart,ant-antpart))
print('B-side test pads %.1f'%B)
tot=F+ant-antpart
print('RESULT F-side %.1f of %.1f = %.1f percent'%(tot,board,100*tot/board))
print('by footprint',{k:round(v,2) for k,v in sorted(byfp.items(),key=lambda t:-t[1])})
