# Dump every pad of a board (ref, pad, net, layers, position in mm, footprint side and angle)
# and the copper items count; also list, for each pad, the set of pads KiCad's connectivity
# says are joined to it by copper (cluster id). Usage: run_kipy.sh dump_pads.py <board> <out.csv>
import sys, csv
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
b.BuildConnectivity()
conn = b.GetConnectivity()
def c_items(it):
    try:
        return list(conn.GetConnectedItems(it))
    except Exception:
        return []
rows = []
pads = list(b.GetPads())
# cluster: union of pads that KiCad reports as connected through copper
idx = {}
for i, p in enumerate(pads):
    idx[p.m_Uuid.AsString()] = i
parent = list(range(len(pads)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
api = 'GetConnectedItems BFS'
# BFS over KiCad's connected items (pads, tracks, vias, zones) from each pad
keyof = lambda it: it.m_Uuid.AsString()
seen_cluster = {}
cid = 0
for i, p in enumerate(pads):
    k = keyof(p)
    if k in seen_cluster:
        continue
    stack = [p]; seen = {k}
    while stack:
        it = stack.pop()
        for o in c_items(it):
            ko = keyof(o)
            if ko not in seen:
                seen.add(ko); stack.append(o)
    for ko in seen:
        seen_cluster[ko] = cid
    cid += 1
def find(i):
    return seen_cluster[keyof(pads[i])]
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ref', 'pad', 'net', 'layers', 'x_mm', 'y_mm', 'fp_side', 'fp_angle', 'fp_name', 'cluster', 'pad_w', 'pad_h'])
    for i, p in enumerate(pads):
        fp = p.GetParentFootprint()
        ls = p.GetLayerSet()
        layers = [b.GetLayerName(l) for l in ls.CuStack()]
        pos = p.GetPosition()
        sz = p.GetSize(pcbnew.F_Cu) if hasattr(p, 'GetSize') else None
        try:
            sw, sh = pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y)
        except Exception:
            sw, sh = '', ''
        w.writerow([fp.GetReference(), p.GetNumber(), p.GetNetname(), '|'.join(layers),
                    round(pcbnew.ToMM(pos.x), 4), round(pcbnew.ToMM(pos.y), 4),
                    'B' if fp.IsFlipped() else 'F', round(fp.GetOrientationDegrees(), 2),
                    fp.GetFPIDAsString(), find(i), sw, sh])
nt = sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK')
nv = sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_VIA')
print('board', sys.argv[1], 'pads', len(pads), 'footprints', len(b.GetFootprints()), 'tracks', nt, 'vias', nv, 'zones', b.GetAreaCount(), 'api', api)
