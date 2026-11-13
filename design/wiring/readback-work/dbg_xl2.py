import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S
b, c, rows = L.load('ring')
for k, Ly in enumerate(b.layers):
    for f in Ly.flashes:
        if abs(f[0] - 105.275) < 0.9 and abs(f[1] + 104.0) < 1.0:
            xs = [p[0] for pg in f[2] for p in (pg[1:3] and [(pg[1], pg[2])] if pg and pg[0] == 'c' else pg)]
            ys = [p[1] for pg in f[2] for p in (pg[1:3] and [(pg[1], pg[2])] if pg and pg[0] == 'c' else pg)]
            print('L%d flash center (%.3f,%.3f) ref %s pin %s bbox x %.3f..%.3f y %.3f..%.3f kind %s' % (k + 1, f[0], f[1], f[3], f[4], min(xs), max(xs), min(ys), max(ys), f[6]))
g = L.net_group(c, 'XL1')
gm = [b.group_map(kk) for kk in range(4)]
for k, Ly in enumerate(b.layers):
    for d in Ly.draws:
        i, j = b.ij((d[0] + d[2]) / 2, (d[1] + d[3]) / 2); l = b.labs[k][i, j]
        if l and int(gm[k][l]) == g and (abs(d[2] - 104.9) < 0.3 and abs(d[3] + 103.55) < 0.3 or abs(d[0] - 104.9) < 0.3 and abs(d[1] + 103.55) < 0.3):
            print('XL1 draw L%d' % (k + 1), d[:5])
for d in b.drills:
    if d['plated'] and d['span']:
        for (hx, hy, dia) in d['holes']:
            if abs(hx - 104.9) < 0.4 and abs(hy + 103.55) < 0.4: print('hole', d['span'], hx, hy, dia)
