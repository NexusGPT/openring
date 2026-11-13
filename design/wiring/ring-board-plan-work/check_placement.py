# Checks placement-plan.csv (ring-board-plan.md round 2). Usage: run_kipy.sh check_placement.py <csv>
# Fails on: two courtyards overlapping (same face), a courtyard outside the outline (antenna and microphones
# may pass by their stated tolerance; pads never), a pad closer than 0.10 mm to the outline, a part in a keep-out
# it is not allowed in, a pad of another part within 0.20 mm of the RF line or the USB pair copper.
import sys, csv, math
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
from rules import KEEPOUTS, EDGE_EXC, override_cy, overlap, inside, _in_outline, BODY_PAIRS
rows=list(csv.DictReader(open(sys.argv[1])))
P={}
for r in rows:
    x,y,rot=float(r['x_mm']),float(r['y_mm']),int(r['rotation_deg'])
    cy,pads=place(r['footprint'],x,y,rot); cy=override_cy(r['reference'],cy,x,y,rot)
    P[r['reference']]=(r['side'],cy,pads)
fails=[]
refs=list(P)
for i,a in enumerate(refs):
    for b in refs[i+1:]:
        if P[a][0]==P[b][0] and overlap(P[a][1],P[b][1]):
            if (a,b) in BODY_PAIRS:
                print(f'note: {a} and {b} courtyards overlap; bodies stated {BODY_PAIRS[(a,b)]} mm apart (mic-path.md C13), not counted')
            else: fails.append(f'courtyard overlap {a} {b}')
for a,(side,cy,pads) in P.items():
    if not inside(cy,a): fails.append(f'courtyard outside outline {a}')
    for n,px,py,bb in pads:
        if not all(_in_outline(x,y,-0.10) for x in (bb[0],bb[2]) for y in (bb[1],bb[3])): fails.append(f'pad {a}.{n} closer than 0.10 to the edge')
    for k in KEEPOUTS:
        if a in k['allow']: continue
        if side=='B' and k['name']!='antenna': continue
        if overlap(cy,k['r']): fails.append(f'{a} in keep-out {k["name"]}')
def seg_box(p,q,bb):
    # least distance from segment pq to rectangle bb (0 if they touch)
    def ps(pt,a,b):
        dx,dy=b[0]-a[0],b[1]-a[1];L=dx*dx+dy*dy;t=0 if L==0 else max(0,min(1,((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/L));return math.dist(pt,(a[0]+t*dx,a[1]+t*dy))
    cx=min(max(p[0],bb[0]),bb[2]); cy=min(max(p[1],bb[1]),bb[3])
    best=9
    for t in [i/50 for i in range(51)]:
        pt=(p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t)
        dx=max(bb[0]-pt[0],0,pt[0]-bb[2]); dy=max(bb[1]-pt[1],0,pt[1]-bb[3]); best=min(best,math.hypot(dx,dy))
    return best
LINES={ 'RF':(0.12,[[(1.985,-0.39),(2.698,-0.393)],[(1.415,-0.39),(0.765,-0.39)],[(0.195,-0.39),(0.0,-0.39),(0.0,3.30),(-6.50,3.30),(-6.70,3.50),(-6.70,5.70),(-6.90,5.90),(-7.465,5.90)],[(-8.035,5.90),(-9.30,5.90)]],
              {'L2','L3','C3','C12','L4','C13','C89','ANT1','U1'}),
        'USB':(0.10,[[(3.997,1.36),(3.997,1.60),(4.40,1.80),(4.40,4.30)],[(4.323,1.36),(4.323,1.55),(4.575,1.80),(4.575,4.30)],
                     [(1.60,5.95),(-2.505,5.95)],[(1.60,6.125),(-3.015,6.125)]],{'U1','U9','J_BAND_B'})}
for name,(w,polys,exempt) in LINES.items():
    for poly in polys:
        for p,q in zip(poly,poly[1:]):
            for a,(side,cy,pads) in P.items():
                if a in exempt or side=='B': continue
                for n,px,py,bb in pads:
                    g=seg_box(p,q,bb)-w/2
                    if g<0.20-1e-6: fails.append(f'{name} line {p}-{q} {g:.3f} mm from pad {a}.{n}')
print('parts',len(P),'F',sum(1 for v in P.values() if v[0]=='F'),'B',sum(1 for v in P.values() if v[0]=='B'))
for f in fails: print('FAIL',f)
print('RESULT','PASS' if not fails else 'FAIL %d'%len(fails))
