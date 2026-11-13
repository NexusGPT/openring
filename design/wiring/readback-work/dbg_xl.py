import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S
b, c, rows = L.load('ring')
rs = [S.RHO / 0.018] * 4
g = L.net_group(c, 'XL1'); gm = [b.group_map(k) for k in range(4)]
def ok(k, x, y):
    i, j = b.ij(x, y); l = b.labs[k][i, j]
    return bool(l) and int(gm[k][l]) == g
G = S.DGraph(b, ok, rs)
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
for ref, pin in (('U1', 'B6'), ('X2', '1')):
    for k, Ly in enumerate(b.layers):
        for f in Ly.flashes:
            if f[3] == ref and f[4] == pin:
                kk = G.key(k, f[0], f[1]); print(ref, pin, 'layer', k, (f[0], f[1]), 'in graph', kk in G.adj, 'comp', seen.get(kk))
                print('   holes near:', [(d['span'], hx, hy) for d in b.drills if d['plated'] and d['span'] for (hx, hy, dia) in d['holes'] if abs(hx - f[0]) < 0.1 and abs(hy - f[1]) < 0.1])
                print('   nearest nodes per layer:', [(kx, G.nearest(f[0], f[1], [kx])) for kx in range(4)])
for n, cid in seen.items():
    if cid == seen[G.key(0, 103.997, -99.348)]: print('comp of B6:', n)
d0 = [d for d in G.draws if d[0] == 1][:3]
print('first L2 draws', d0)
print('L2 draws near B6', [d[1:5] for d in G.draws if d[0] == 1 and abs(d[1] - 103.997) < 0.3 and abs(d[2] + 99.348) < 0.3])
print('L2 draws near (103.997,-98.922):', [d[1:5] for d in G.draws if d[0] == 1 and (abs(d[1] - 103.997) < 0.1 and abs(d[2] + 98.922) < 0.1 or abs(d[3] - 103.997) < 0.1 and abs(d[4] + 98.922) < 0.1)])
print('L2 flashes near:', [(f[0], f[1], f[3], f[4], f[6]) for f in b.layers[1].flashes if abs(f[0] - 103.997) < 0.4 and abs(f[1] + 98.922) < 0.4])
print('L1 draws near:', [d[:5] for d in b.layers[0].draws if abs(d[0] - 103.997) < 0.4 and abs(d[1] + 98.922) < 0.4])
