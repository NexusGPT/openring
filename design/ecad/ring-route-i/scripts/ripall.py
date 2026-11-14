# ripall.py in out R x y : remove UNLOCKED tracks and vias of every net except GND, RF, USB within R mm of (x, y)
import sys, math, pcbnew
from pcbnew import ToMM
O = 100.0; b = pcbnew.LoadBoard(sys.argv[1]); R, X, Y = map(float, sys.argv[3:6])
import os
KEEP = set(os.environ.get("KEEPNETS", "").split(",")) | {"GND", "RF_FEED", "ANT_TRIM", "ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "USB_DP", "USB_DN"}
def dseg(p, s, c):
    dx, dy = c[0]-s[0], c[1]-s[1]; L = dx*dx+dy*dy
    t = 0 if L == 0 else max(0, min(1, ((p[0]-s[0])*dx+(p[1]-s[1])*dy)/L))
    return math.hypot(p[0]-s[0]-t*dx, p[1]-s[1]-t*dy)
rm = []
for t in list(b.GetTracks()):
    if (t.IsLocked() and not os.environ.get("LOCKED")) or t.GetNetname() in KEEP: continue
    if t.Type() == pcbnew.PCB_VIA_T: d = math.hypot(ToMM(t.GetPosition().x)-O-X, ToMM(t.GetPosition().y)-O-Y)
    else: d = dseg((X, Y), (ToMM(t.GetStart().x)-O, ToMM(t.GetStart().y)-O), (ToMM(t.GetEnd().x)-O, ToMM(t.GetEnd().y)-O))
    if d <= R: rm.append(t)
nets = sorted(set(t.GetNetname() for t in rm)); print("locked among removed:", [(t.GetNetname(), "via" if t.Type() == pcbnew.PCB_VIA_T else b.GetLayerName(t.GetLayer()), round(ToMM(t.GetPosition().x)-O, 3), round(ToMM(t.GetPosition().y)-O, 3)) for t in rm if t.IsLocked()])
for t in rm: b.Remove(t)
print("removed", len(rm), "unlocked items of nets", nets)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2])
