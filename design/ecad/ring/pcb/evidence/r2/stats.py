# stats.py board: counts of footprints, tracks per layer (unlocked / locked), vias per span
import sys, pcbnew, collections
b = pcbnew.LoadBoard(sys.argv[1]); seg = collections.Counter(); via = collections.Counter(); lk = 0
for t in b.GetTracks():
    lk += t.IsLocked()
    if t.Type() == pcbnew.PCB_VIA_T: via[b.GetLayerName(t.TopLayer()) + '-' + b.GetLayerName(t.BottomLayer())] += 1
    else: seg[b.GetLayerName(t.GetLayer())] += 1
print('footprints', len(b.GetFootprints()), 'segments', dict(seg), 'vias', dict(via), 'locked', lk)
