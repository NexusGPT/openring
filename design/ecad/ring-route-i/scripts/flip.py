# flip.py in out REF[@x,y[,rot]] ... : put each part on F.Cu (under face). Without x,y: same place, rotation chosen so that pad 1 lands
# where it was (falls back to the nearest). Prints old and new pad centres. Saves without refill.
import sys, math, pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1])
def pads(m): return {p.GetNumber(): (ToMM(p.GetPosition().x) - O, ToMM(p.GetPosition().y) - O) for p in m.Pads()}
for arg in sys.argv[3:]:
    ref, _, spec = arg.partition("@")
    m = b.FindFootprintByReference(ref); old = pads(m); want = old; pos = m.GetPosition()
    if m.GetLayer() != pcbnew.F_Cu: m.Flip(pos, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if spec:
        v = [float(s) for s in spec.split(",")]; m.SetPosition(VECTOR2I(FromMM(v[0] + O), FromMM(v[1] + O)))
        rots = [v[2]] if len(v) == 3 else [0, 90, 180, 270]
        if len(v) == 4: want = {"1": (v[2], v[3])}
    else:
        m.SetPosition(pos); rots = [0, 90, 180, 270]
    best = None
    for r in rots:
        m.SetOrientationDegrees(r); n = pads(m); d = sum(math.hypot(n[k][0] - want[k][0], n[k][1] - want[k][1]) for k in n if k in want)
        if best is None or d < best[0] - 1e-6: best = (d, r)
    m.SetOrientationDegrees(best[1]); n = pads(m)
    print("%s -> %s (%.3f,%.3f) rot %.0f; pads %s" % (ref, b.GetLayerName(m.GetLayer()), ToMM(m.GetPosition().x) - O, ToMM(m.GetPosition().y) - O, best[1],
          "; ".join("%s %s (%.3f,%.3f) was (%.3f,%.3f)" % (k, p.GetNetname(), n[k][0], n[k][1], old[k][0], old[k][1]) for k, p in ((q.GetNumber(), q) for q in m.Pads()))))
b.Save(sys.argv[2]); print("saved", sys.argv[2])
