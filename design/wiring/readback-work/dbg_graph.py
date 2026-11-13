import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S
b, c, rows = L.load('ring')
rs = [S.RHO / 0.018] * 4
g = L.net_group(c, 'VMOT')
gm = [b.group_map(k) for k in range(4)]
def ok(k, x, y):
    i, j = b.ij(x, y); l = b.labs[k][i, j]
    return bool(l) and int(gm[k][l]) == g
G = S.DGraph(b, ok, rs)
print('nodes', len(G.adj), 'draws', len(G.draws), 'total len', G.total_len)
for ref, pin in (('U11', '1'), ('J_BAND_A', '7')):
    for k, Ly in enumerate(b.layers):
        for f in Ly.flashes:
            if f[3] == ref and f[4] == pin:
                kk = G.key(k, f[0], f[1]); print(ref, pin, 'layer', k, 'flash', f[0], f[1], 'key in graph', kk in G.adj)
                print('  nearest', G.nearest(f[0], f[1], [k]))
print('draw layers', sorted(set(d[0] for d in G.draws)))
print('holes in net', sum(1 for n in G.adj))
# components
seen = {}; comps = []
for n in G.adj:
    if n in seen: continue
    st = [n]; seen[n] = len(comps); cnt = 0
    while st:
        u = st.pop(); cnt += 1
        for (v, ln, r) in G.adj[u]:
            if v not in seen: seen[v] = len(comps); st.append(v)
    comps.append(cnt)
print('components', comps)
a = G.key(0, 99.57, -103.875); z = G.key(0, 97.495001, -95.225)
print('src comp', seen[a], 'sink comp', seen[z])
byl = {}
for n in G.adj: byl[n[0]] = byl.get(n[0], 0) + 1
print('nodes by layer', byl)
import collections
print('draws per layer', collections.Counter(d[0] for d in G.draws))
# holes in net
hs = [(hx, hy, d['span']) for d in b.drills if d['plated'] and d['span'] for (hx, hy, dia) in d['holes'] if G.nearest(hx, hy, None) and G.nearest(hx, hy, None)[0] < 0.03]
print('holes near graph nodes', len(hs), hs[:5])
print('--- sink comp nodes')
for n, cid in seen.items():
    if cid == seen[z]: print(n)
for d in b.drills:
    if d['plated'] and d['span']:
        for (hx, hy, dia) in d['holes']:
            if abs(hx - 97.495) < 0.8 and abs(hy + 95.225) < 0.8: print('hole', d['span'], hx, hy, dia)
print([ (d[0], d[1:5]) for d in G.draws if abs(d[1] - 97.495) < 0.8 and abs(d[2] + 95.225) < 1.0][:6])
print('--- L2/L3 nodes near the hole (99.15,-95.675)')
for k in (1, 2, 3):
    print(k, G.nearest(99.15, -95.675, [k]))
print('L3 flashes near:', [(f[0], f[1], f[3], f[4], len(f[2])) for f in b.layers[2].flashes if abs(f[0]-99.15)<0.2 and abs(f[1]+95.675)<0.2])
print('L1 flashes near:', [(f[0], f[1], f[3], f[4]) for f in b.layers[0].flashes if abs(f[0]-99.15)<0.2 and abs(f[1]+95.675)<0.2])
print('L2 draws near:', [d[1:5] for d in G.draws if d[0]==1 and abs(d[1]-99.15)<0.5 and abs(d[2]+95.675)<0.5][:4])
print('L3 draws near:', [d[1:5] for d in G.draws if d[0]==2 and abs(d[1]-99.15)<0.5 and abs(d[2]+95.675)<0.5][:4])
