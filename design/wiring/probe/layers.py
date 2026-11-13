import sys, pcbnew, collections
b = pcbnew.LoadBoard(sys.argv[1])
c = collections.Counter(); v = collections.Counter()
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        v[f"{b.GetLayerName(t.TopLayer())}-{b.GetLayerName(t.BottomLayer())}"] += 1
    else:
        c[b.GetLayerName(t.GetLayer())] += 1
print("segments by layer:", dict(c), "total", sum(c.values()))
print("vias by span:", dict(v), "total", sum(v.values()))
