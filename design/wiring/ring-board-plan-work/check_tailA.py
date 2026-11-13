# Checks the round 3 exits of the tail A lands against the J_BAND_A_BOARD footprint and netlist.csv:
# pad number, net, position; then the least copper gap between each exit (track + stack) and every other land.
import sys, csv, math
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
NET={(r['reference'],r['pin_number']):r['net'] for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv")))}
cy,pads=place('OpenRingBand:J_BAND_A_BOARD',-2.25,-4.325,0)
L={n:(x,y,b) for n,x,y,b in pads}
EXP={'1':('JOY_UP',-1.485,-3.875),'4':('JOY_RIGHT',-1.485,-4.775),'6':('GND',-1.995,-3.875),'8':('GND',-1.995,-4.775),
     '2':('JOY_DOWN',-3.015,-3.875),'3':('JOY_LEFT',-2.505,-3.875),'5':('BTN_REC',-3.015,-4.775),'7':('VMOT',-2.505,-4.775)}
bad=0
for n,(net,x,y) in EXP.items():
    px,py,b=L[n]; nn=NET.get(('J_BAND_A',n))
    okp=abs(px-x)<1e-3 and abs(py-y)<1e-3 and nn==net
    bad+=not okp; print(f'land {n}: footprint ({px:.3f}, {py:.3f}) net {nn}  expected {net} ({x}, {y})  {"ok" if okp else "MISMATCH"}')
# exits: land -> (track polyline, width, stack position)
EX={'2':([(-3.015,-3.875),(-3.75,-3.875)],0.10,(-3.75,-3.875)),
    '3':([(-2.505,-3.875),(-2.505,-3.25)],0.10,(-2.505,-3.25)),
    '6':([(-1.995,-3.875),(-1.995,-3.25)],0.20,(-1.995,-3.25)),
    '1':([(-1.485,-3.875),(-0.85,-3.875)],0.10,(-0.85,-3.875)),
    '5':([(-3.015,-4.775),(-3.75,-4.775)],0.10,(-3.75,-4.775)),
    '7':([(-2.505,-4.775),(-2.505,-4.325),(-0.85,-4.325)],0.15,(-0.85,-4.325)),
    '4':([(-1.485,-4.775),(-0.85,-4.775)],0.10,(-0.85,-4.775)),
    '8':([(-1.995,-4.775),(-1.995,-5.75)],0.20,(-1.995,-5.75))}
def segbox(p,q,b):
    best=9
    for t in [i/100 for i in range(101)]:
        x=p[0]+(q[0]-p[0])*t; y=p[1]+(q[1]-p[1])*t
        dx=max(b[0]-x,0,x-b[2]); dy=max(b[1]-y,0,y-b[3]); best=min(best,math.hypot(dx,dy))
    return best
least=9
for n,(poly,w,st) in EX.items():
    net=NET[('J_BAND_A',n)]
    for m,(px,py,b) in L.items():
        if NET[('J_BAND_A',m)]==net: continue
        for p,q in zip(poly,poly[1:]):
            g=segbox(p,q,b)-w/2; least=min(least,g)
            if g<0.075-1e-6: bad+=1; print('gap',n,'to land',m,round(g,3))
        sx,sy=st; g=max(b[0]-sx,0,sx-b[2]); h=max(b[1]-sy,0,sy-b[3]); g=math.hypot(g,h)-0.10; least=min(least,g)
        if g<0.075-1e-6: bad+=1; print('stack',n,'to land',m,round(g,3))
    for m,(poly2,w2,st2) in EX.items():
        if m<=n or NET[('J_BAND_A',m)]==net: continue
        g=math.dist(st,st2)-0.20
        if g<0.075: bad+=1; print('stacks',n,m,round(g,3))
    ko=(-3.50,-5.60,-1.00,-3.40)
    if ko[0]<st[0]<ko[2] and ko[1]<st[1]<ko[3]: bad+=1; print('stack in keep-out',n)
print('least copper gap %.3f mm'%least)
print('RESULT','PASS' if bad==0 else 'FAIL %d'%bad)
