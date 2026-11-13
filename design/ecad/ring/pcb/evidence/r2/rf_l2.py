# rf_l2.py board [mm]: L2 (In1.Cu) copper of other nets within `mm` (default 0.50) of the antenna line's L1 tracks, outside the
# chip exit area RF_CHIP_EXIT (plan d.1: L2 solid ground under the line and 0.50 mm each side, no L2 track under it)
import sys, math, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(sys.argv[1]); lim = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
RF = {"ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED"}
EXIT = (1.90, -0.75, 2.80, -0.05)
def m(v): return (ToMM(v.x) - 100, ToMM(v.y) - 100)
def pseg(p, a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2)); return math.dist(p, (a[0] + t * dx, a[1] + t * dy))
rf = [(m(t.GetStart()), m(t.GetEnd()), ToMM(t.GetWidth()) / 2) for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == pcbnew.F_Cu and t.GetNetname() in RF]
bad = []
for t in b.GetTracks():
    if t.GetNetname() in ('GND',) or t.GetNetname() in RF: continue
    if t.Type() == pcbnew.PCB_VIA_T:
        if not t.IsOnLayer(pcbnew.In1_Cu): continue
        pts = [m(t.GetPosition())]; hw = ToMM(t.GetWidth(pcbnew.In1_Cu)) / 2
    elif t.GetLayer() == pcbnew.In1_Cu:
        a, c = m(t.GetStart()), m(t.GetEnd()); n = max(2, int(math.dist(a, c) / 0.02)); pts = [(a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n) for i in range(n + 1)]; hw = ToMM(t.GetWidth()) / 2
    else: continue
    for p in pts:
        if EXIT[0] <= p[0] <= EXIT[2] and EXIT[1] <= p[1] <= EXIT[3]: continue
        d = min(pseg(p, a, c) - w for a, c, w in rf) - hw
        if d < lim:
            bad.append((t.GetNetname(), 'via' if t.Type() == pcbnew.PCB_VIA_T else 'track', round(p[0], 2), round(p[1], 2), round(d, 3))); break
for x in bad: print('L2 under the antenna line:', x)
print('RESULT', 'PASS' if not bad else 'FAIL %d' % len(bad), 'L2 items of other nets within %.2f mm of the antenna line edge' % lim)
