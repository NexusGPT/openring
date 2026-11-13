# Writes placement-plan.csv for the ring main board (round 2 of ring-board-plan.md).
# Fixed parts: coordinates of the plan. Other parts: deterministic placer: nearest free place to the anchor
# (the pin the part serves), on a 0.05 mm grid, rotations 0 then 90, courtyard bounding boxes (incl. stroke)
# must not overlap each other, the keep-outs, or the reserved copper bands; inside the outline.
import sys, csv, math
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
from rules import *
parts={r['reference']:r for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/parts.csv")))}
FP={k:v['footprint'] for k,v in parts.items()}
FP.update(FP_OVERRIDE)
refs=[r for r in parts if r not in OFF_BOARD and r not in REMOVED]+ADDED
unplaced=[]
placed={}   # ref -> (x,y,rot,cy,zone)
def ok(ref,cy):
    if not inside(cy,ref): return False
    if ref in BSIDE:
        if any(overlap(cy,k['r']) for k in KEEPOUTS if k['name']=='antenna'): return False
        return all(not overlap(cy,c) for o,(x,y,r,c,zn) in placed.items() if o in BSIDE)
    for z in KEEPOUTS:
        if ref not in z['allow'] and overlap(cy,z['r']): return False
    for b in RESERVED+AVOID.get(ref,[]):
        if overlap(cy,b): return False
    for o,(x,y,r,c,zn) in placed.items():
        if o not in BSIDE and overlap(cy,c): return False
    return True
for ref,(x,y,rot,zone) in FIXED.items():
    cy,_=place(FP[ref],x,y,rot); cy=override_cy(ref,cy,x,y,rot)
    placed[ref]=(x,y,rot,cy,zone)
miss=[r for r in refs if r not in placed and r not in ANCHOR]
if miss: sys.exit('no anchor for '+','.join(miss))
order=[r for r in refs if r not in placed]
AREA={}
for r in order:
    c,_=place(FP[r],0,0,0); AREA[r]=(c[2]-c[0])*(c[3]-c[1])
import os, random
SEED=int(os.environ.get('SEED','0'))
rnd=random.Random(SEED)
JIT={r:(rnd.random() if SEED else 0) for r in order}
order.sort(key=lambda r:(ANCHOR[r][3],-AREA[r]*(1+0.6*JIT[r]),r))   # priority, then larger parts first (SEED>0 shuffles inside a tier)
pts=[]
for i in range(-60,61):
    for j in range(-60,61):
        pts.append((i*0.05,j*0.05))
for i in range(-140,141):
    for j in range(-70,71):
        if abs(i)>30 or abs(j)>30: pts.append((i*0.1,j*0.1))
pts=sorted(set((round(a,2),round(b,2)) for a,b in pts),key=lambda t:(t[0]**2+t[1]**2,t))
REL={}
def rel(fp,rot):
    if (fp,rot) not in REL: REL[(fp,rot)]=place(fp,0,0,rot)[0]
    return REL[(fp,rot)]
for ref in order:
    ax,ay,zone,_=ANCHOR[ref]
    best=None
    for dx,dy in pts:
        x=round(ax+dx,3); y=round(ay+dy,3)
        if not (X0<x<X1E and Y0<y<Y1E): continue
        for rot in (0,90):
            r0=rel(FP[ref],rot); cy=(r0[0]+x,r0[1]+y,r0[2]+x,r0[3]+y)
            if ok(ref,cy):
                best=(x,y,rot,cy); break
        if best: break
    if not best:   # second pass: every 0.025 mm of the board
        cands=sorted(((i*0.025,j*0.025) for i in range(-544,545) for j in range(-252,253)),key=lambda t:(t[0]-ax)**2+(t[1]-ay)**2)
        for x,y in cands:
            for rot in (0,90):
                r0=rel(FP[ref],rot); cy=(r0[0]+x,r0[1]+y,r0[2]+x,r0[3]+y)
                if ok(ref,cy): best=(round(x,3),round(y,3),rot,cy); break
            if best: break
    if not best:
        print('NO PLACE',ref); unplaced.append(ref); continue
    placed[ref]=(best[0],best[1],best[2],best[3],zone)
    if ref=='U10':   # its two supply capacitors follow U10 to where it went
        for c,(dx,dy) in (('C81',(-1.5,0.0)),('C82',(1.5,0.0))):
            if c in ANCHOR: ANCHOR[c]=(best[0]+dx,best[1]+dy)+tuple(ANCHOR[c][2:])
    print(ref,'placed',best[:3],'from anchor',(ax,ay),'distance %.2f'%math.dist(best[:2],(ax,ay)))
OUT=os.environ.get('OUT','placement-plan.csv')
with open(OUT,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['reference','footprint','side','x_mm','y_mm','rotation_deg','zone','kicad_x','kicad_y'])
    for ref in refs:
        if ref not in placed: continue
        x,y,r,c,z=placed[ref]; w.writerow([ref,FP[ref],'B' if ref in BSIDE else 'F','%.3f'%x,'%.3f'%y,r,z,'%.3f'%(x+100),'%.3f'%(y+100)])
print('RESULT written',len(refs),'parts')

import json
json.dump({r:[v[0],v[1],v[2],list(v[3]),v[4]] for r,v in placed.items()},open(OUT.replace('.csv','-boxes.json'),'w'))
print('UNPLACED',unplaced)
