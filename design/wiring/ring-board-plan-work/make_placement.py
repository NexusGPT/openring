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
        if overlap(cy,KEEPOUTS[0]['r']): return False
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
order.sort(key=lambda r:ANCHOR[r][3])   # priority
for ref in order:
    ax,ay,zone,_=ANCHOR[ref]
    best=None
    for ring in range(0,240):
        cands=[]
        for i in range(-ring,ring+1):
            for j in (-ring,ring):
                cands+=[(i,j),(j,i)]
        for i,j in sorted(set(cands),key=lambda t:(t[0]**2+t[1]**2)):
            x=round(ax+i*0.05,3); y=round(ay+j*0.05,3)
            for rot in (0,90):
                cy,_=place(FP[ref],x,y,rot); cy=override_cy(ref,cy,x,y,rot)
                if ok(ref,cy):
                    best=(x,y,rot,cy); break
            if best: break
        if best: break
    if not best:
        print('NO PLACE',ref); unplaced.append(ref); continue
    placed[ref]=(best[0],best[1],best[2],best[3],zone)
    print(ref,'placed',best[:3],'from anchor',(ax,ay),'distance %.2f'%math.dist(best[:2],(ax,ay)))
with open('placement-plan.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['reference','footprint','side','x_mm','y_mm','rotation_deg','zone','kicad_x','kicad_y'])
    for ref in refs:
        if ref not in placed: continue
        x,y,r,c,z=placed[ref]; w.writerow([ref,FP[ref],'B' if ref in BSIDE else 'F','%.3f'%x,'%.3f'%y,r,z,'%.3f'%(x+100),'%.3f'%(y+100)])
print('RESULT written',len(refs),'parts')

import json
json.dump({r:[v[0],v[1],v[2],list(v[3]),v[4]] for r,v in placed.items()},open('placement-boxes.json','w'))
print('UNPLACED',unplaced)
