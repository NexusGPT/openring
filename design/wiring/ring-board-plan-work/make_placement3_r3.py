# Round 3 placement: regulator capacitors at their pins. Keeps the round 2 core parts, searches a place for the
# U4 + L10 block, then places "must" parts within 1.5 mm and "should" parts within 3.0 mm of the pin they serve
# (pad-to-pin distance), then every other part as in round 2. Writes placement-r3.csv (+ -boxes.json).
import sys, csv, math, json
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
import rules
from rules import *
NET={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))):
    NET[(r['reference'],r['pin_number'])]=r['net']
r2={r['reference']:r for r in csv.DictReader(open('placement-plan-r2.csv'))}
FP={k:v['footprint'] for k,v in r2.items()}
KEEP=['U1','U2','U3','U5','U6','J1','ANT1','J_BAND_A','J_BAND_B','L2','C3','L3','C12','C13','L4','C89','LT1','X1','X2','U9','U11','C83','C84',
      'L71','L72','C74','C35','C36','C85','C71','C86','C87','R71','R72','C14','C1','C2','C10']
REL={}; PADREL={}
def rel(fp,rot):
    if (fp,rot) not in REL:
        cy,pads=place(fp,0,0,rot); REL[(fp,rot)]=cy; PADREL[(fp,rot)]={n:(x,y) for n,x,y,_ in pads}
    return REL[(fp,rot)]
def cyat(ref,x,y,rot):
    if ref in ('J1','U5','U6','J_BAND_A','J_BAND_B'): return override_cy(ref,None,x,y,rot)
    r=rel(FP[ref],rot); return (r[0]+x,r[1]+y,r[2]+x,r[3]+y)
def padat(ref,x,y,rot,n):
    rel(FP[ref],rot); px,py=PADREL[(FP[ref],rot)][n]; return (x+px,y+py)
# constrained parts: (served ref, pin), limit, priority order
CONS=[('L1',[('U1','A5')],1.5),('C6',[('U1','A6')],1.5),('L10',[('U4','B1'),('U4','C1')],4.0),
      ('C23',[('U4','A4'),('U4','B4')],1.5),('C21',[('U4','A1')],1.5),('C24',[('U4','D1')],1.5),('C27',[('U4','C4')],1.5),
      ('C78',[('L71','2')],3.0),('C79',[('L72','2')],3.0),
      ('C22',[('U4','A2')],3.0),('C26',[('U4','D2')],3.0),('C25',[('U4','D3')],3.0),('C28',[('U4','D4')],3.0),('C29',[('U4','D4')],3.0),
      ('C75',[('U2','C1')],3.0),('C88',[('U2','C1')],3.0),('C72',[('U2','B1')],3.0),('C11',[('U1','H9')],3.0),
      ('C4',[('U1','A4')],3.0),('C5',[('U1','A4')],3.0),('FB1',[('U1','A6')],3.0),('C7',[('U1','A8')],3.0)]
CONSD={c:(p,l) for c,p,l in CONS}
def ok(ref,cy,placed):
    if not inside(cy,ref): return False
    for z in KEEPOUTS:
        if ref not in z['allow'] and overlap(cy,z['r']): return False
    for b in RESERVED+AVOID.get(ref,[]):
        if overlap(cy,b): return False
    for o,v in placed.items():
        if o not in BSIDE and overlap(cy,v[3]): return False
    return True
def served_dist(ref,x,y,rot,pins,placed):
    worst=0
    for sref,pin in pins:
        sx,sy,srot=placed[sref][:3]; P=padat(sref,sx,sy,srot,pin); net=NET.get((sref,pin))
        rel(FP[ref],rot)
        ds=[math.dist((x+px,y+py),P) for n,(px,py) in PADREL[(FP[ref],rot)].items() if NET.get((ref,n))==net]
        if not ds: return 99
        worst=max(worst,min(ds))
    return worst
GRID=[(i*0.1,j*0.1) for i in range(-40,41) for j in range(-40,41)]
GRID.sort(key=lambda t:t[0]**2+t[1]**2)
def place_cons(ref,placed):
    pins,lim=CONSD[ref]
    sx,sy=[0,0]
    pts=[padat(s,*placed[s][:3],p) for s,p in pins]
    cx=sum(p[0] for p in pts)/len(pts); cy0=sum(p[1] for p in pts)/len(pts)
    best=None
    for dx,dy in GRID:
        if dx*dx+dy*dy>(lim+1.6)**2: break
        x=round(cx+dx,3); y=round(cy0+dy,3)
        for rot in (0,90,180,270):
            c=cyat(ref,x,y,rot)
            if not ok(ref,c,placed): continue
            d=served_dist(ref,x,y,rot,pins,placed)
            if d<=lim and (best is None or d<best[4]-1e-9):
                best=(x,y,rot,c,d)
        if best and math.hypot(dx,dy)>0.6: break
    return best
STAGEA=[c for c in CONS if c[0] in ('L1','C6')]
STAGEB=[c for c in CONS if any(p[0]=='U4' for p in c[1]) and (c[2]<=1.5 or c[0]=='L10')]
STAGEC=[c for c in CONS if c not in STAGEA and c not in STAGEB and c[0] not in ('C26','C25','C28','C29','C22')]
base={}
for r in KEEP:
    v=r2[r]; x,y,rot=float(v['x_mm']),float(v['y_mm']),int(v['rotation_deg'])
    base[r]=(x,y,rot,cyat(r,x,y,rot),v['zone'])
base['X2']=(6.0,3.75,90,cyat('X2',6.0,3.75,90),'Z3')   # round 3: X2 shifted 0.40 toward +Y inside its zone
for ref,pins,lim in STAGEA:
    b=place_cons(ref,base)
    if not b: print('STAGE A no place within',lim,'for',ref); continue
    base[ref]=(b[0],b[1],b[2],b[3],'R3'); print('A',ref,b[:3],'dist %.2f'%b[4])
import itertools
MUSTB=[c for c in STAGEB if c[0]!='L10']
LB=[c for c in STAGEB if c[0]=='L10'][0]
def run(u4x,u4y,u4rot):
    placed=dict(base)
    c=cyat('U4',u4x,u4y,u4rot)
    if not ok('U4',c,placed): return None,'U4'
    placed['U4']=(u4x,u4y,u4rot,c,'Z12')
    last='?'
    ORD=[c for n in ('C21','C24','C23','C27') for c in MUSTB if c[0]==n]
    for perm in [ORD]:
        pl=dict(placed); good=True
        for ref,pins,lim in perm:
            b=place_cons(ref,pl)
            if not b: good=False; last=ref; break
            pl[ref]=(b[0],b[1],b[2],b[3],'Z12')
        if not good: continue
        b=place_cons('L10',pl)
        if not b: last='L10'; continue
        pl['L10']=(b[0],b[1],b[2],b[3],'Z12'); tot=b[4]
        for ref in ('C26','C25','C28','C29','C22'):
            pins,lim=CONSD[ref]; bb=place_cons(ref,pl)
            if not bb: last=ref; good=False; break
            pl[ref]=(bb[0],bb[1],bb[2],bb[3],'Z12'); tot+=bb[4]
        if not good: continue
        pl['_L10d']=tot
        return pl,None
    return None,last
best=None; tried=0; fails={}
for rot in (0,90,180,270):
    for X in [x*0.25 for x in range(4,30)]:
        for Y in [y*0.1 for y in range(-55,-30)]:
            tried+=1
            pl,why=run(X,Y,rot)
            if pl is None: fails[why]=fails.get(why,0)+1; continue
            score=pl.pop('_L10d')
            if best is None or score<best[0]: best=(score,(X,Y,rot),pl)
print('tried',tried,'feasible' if best else 'none','fail stats',sorted(fails.items(),key=lambda t:-t[1])[:8])
if not best: sys.exit(1)
print('U4 at',best[1],'score %.2f'%best[0])
pl=best[2]
ORDC=['C88','C75','C72','C78','C79','C11','C7','C5','FB1','C4']
STAGEC.sort(key=lambda c:ORDC.index(c[0]))
for ref,pins,lim in STAGEC:
    b=place_cons(ref,pl)
    if not b:
        CONSD[ref]=(pins,9.0); b=place_cons(ref,pl); CONSD[ref]=(pins,lim)
        print('STAGE C over limit',lim,'for',ref,'nearest found %.2f'%(b[4] if b else -1))
    if not b: print('NO PLACE',ref); continue
    pl[ref]=(b[0],b[1],b[2],b[3],'R3'); print('C',ref,b[:3],'dist %.2f'%b[4])
# stage D: every other board part as in round 2 (nearest free place to its anchor)
parts=[r for r in r2 if r not in pl]
AREA={r:(lambda c:(c[2]-c[0])*(c[3]-c[1]))(cyat(r,0,0,0)) for r in parts if r not in BSIDE}
for r in [r for r in parts if r in BSIDE]:
    v=r2[r]; x,y,rot=float(v['x_mm']),float(v['y_mm']),int(v['rotation_deg']); pl[r]=(x,y,rot,cyat(r,x,y,rot),v['zone'])
rest=[r for r in parts if r not in BSIDE]
rest.sort(key=lambda r:(ANCHOR[r][3] if r in ANCHOR else 9,-AREA[r]))
FAR=[(i*0.1,j*0.1) for i in range(-140,141) for j in range(-70,71)]
FAR.sort(key=lambda t:t[0]**2+t[1]**2)
for r in rest:
    ax,ay=(ANCHOR[r][0],ANCHOR[r][1]) if r in ANCHOR else (float(r2[r]['x_mm']),float(r2[r]['y_mm']))
    best=None
    for dx,dy in FAR:
        x=round(ax+dx,3); y=round(ay+dy,3)
        if not (X0<x<X1E and Y0<y<Y1E): continue
        for rot in (0,90):
            c=cyat(r,x,y,rot)
            if ok(r,c,pl): best=(x,y,rot,c); break
        if best: break
    if not best: print('NO PLACE',r); continue
    pl[r]=(best[0],best[1],best[2],best[3],r2[r]['zone']); print('D',r,best[:3],'from anchor (%.2f, %.2f) distance %.2f'%(ax,ay,math.dist(best[:2],(ax,ay))))
with open('placement-r3.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['reference','footprint','side','x_mm','y_mm','rotation_deg','zone','kicad_x','kicad_y'])
    for r in r2:
        if r not in pl: continue
        x,y,rot,c,z=pl[r]; w.writerow([r,FP[r],'B' if r in BSIDE else 'F','%.3f'%x,'%.3f'%y,rot,z,'%.3f'%(x+100),'%.3f'%(y+100)])
json.dump({r:[v[0],v[1],v[2],list(v[3]),v[4]] for r,v in pl.items()},open('placement-r3-boxes.json','w'))
print('RESULT written',sum(1 for r in r2 if r in pl),'of',len(r2))
for r in [c[0] for c in STAGEB]: print('B',r,best[2][r][:3])
json.dump({r:[v[0],v[1],v[2],list(v[3]),v[4]] for r,v in best[2].items()},open('r3-core.json','w'))
