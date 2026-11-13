# dump_area.py board x0 y0 x1 y1: courtyard box and pads (net) of every footprint touching the window (model mm)
import sys, pcbnew
from pcbnew import ToMM
b=pcbnew.LoadBoard(sys.argv[1]); x0,y0,x1,y1=map(float,sys.argv[2:6])
for f in sorted(b.GetFootprints(), key=lambda f:f.GetReference()):
    if f.IsFlipped(): continue
    c=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    bx=(ToMM(c.GetLeft())-100,ToMM(c.GetTop())-100,ToMM(c.GetRight())-100,ToMM(c.GetBottom())-100)
    if bx[2]<x0 or bx[0]>x1 or bx[3]<y0 or bx[1]>y1: continue
    pads=' '.join('%s:%s@(%.2f,%.2f)'%(p.GetNumber(),p.GetNetname(),ToMM(p.GetPosition().x)-100,ToMM(p.GetPosition().y)-100) for p in f.Pads()) if f.GetReference() not in ('U1','U2','U3','J1') else ''
    print('%-6s cy X %.2f..%.2f Y %.2f..%.2f rot %.0f %s'%(f.GetReference(),bx[0],bx[2],bx[1],bx[3],f.GetOrientationDegrees(),pads))
