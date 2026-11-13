# near.py board x y r: every pad, track and via within r mm of (x, y), model mm
import sys, math, pcbnew
from pcbnew import ToMM
b=pcbnew.LoadBoard(sys.argv[1]); x,y,r=map(float,sys.argv[2:5])
def m(v): return (ToMM(v.x)-100, ToMM(v.y)-100)
for f in b.GetFootprints():
    for p in f.Pads():
        q=m(p.GetPosition())
        if math.dist(q,(x,y))<r: print('pad %s.%s %s at (%.3f, %.3f) layers %s'%(f.GetReference(),p.GetNumber(),p.GetNetname(),q[0],q[1],'F' if p.IsOnLayer(pcbnew.F_Cu) else 'B'))
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_VIA_T:
        q=m(t.GetPosition())
        if math.dist(q,(x,y))<r: print('via %s at (%.3f, %.3f) %s-%s locked %s'%(t.GetNetname(),q[0],q[1],b.GetLayerName(t.TopLayer()),b.GetLayerName(t.BottomLayer()),t.IsLocked()))
    else:
        a,c=m(t.GetStart()),m(t.GetEnd())
        L=math.dist(a,c); best=min(math.dist(a,(x,y)),math.dist(c,(x,y)))
        for i in range(21):
            pt=(a[0]+(c[0]-a[0])*i/20,a[1]+(c[1]-a[1])*i/20); best=min(best,math.dist(pt,(x,y)))
        if best<r: print('track %s %s (%.3f, %.3f)-(%.3f, %.3f) w %.3f locked %s'%(t.GetNetname(),b.GetLayerName(t.GetLayer()),a[0],a[1],c[0],c[1],ToMM(t.GetWidth()),t.IsLocked()))
