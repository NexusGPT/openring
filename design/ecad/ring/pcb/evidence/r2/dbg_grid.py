# dbg_grid.py board net x y: loads finish_route.py's definitions, builds its grid and prints why a track or via is blocked at (x, y)
import sys, os
src = open((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/finish_route.py")).read().split('\nb = load(src)')[0]
board, net, x, y = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
sys.argv = ['finish_route.py', board, board]
g = {'__file__': (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/finish_route.py")}; exec(compile(src, 'finish_route.py', 'exec'), g)
b = g['load'](board); items = g['board_items'](b); grid = g['Grid'](items)
NX, NY = g['NX'], g['NY']; win = (0, NY, 0, NX)
tb, vb, halo = grid.blocked(net, win)
i, j = g['ix'](x), g['iy'](y)
for l in range(4):
    print('layer', l, 'track blocked', bool(tb[l][j, i]), 'via blocked', bool(vb[l][j, i]), 'lab', grid.lab[l, j, i], 'own id', grid.net_ids.get(net))
import numpy as np
for l in range(4):
    other = (grid.lab[l] >= 0) & (grid.lab[l] != grid.net_ids.get(net, -5))
    ys, xs = np.nonzero(other[j-10:j+11, i-10:i+11])
    near = sorted(set(int(grid.lab[l, j-10+a, i-10+c]) for a, c in zip(ys, xs)))
    inv = {v: k for k, v in grid.net_ids.items()}
    print('layer', l, 'other nets within 0.25 mm:', [inv.get(v, v) for v in near])
print('vias within 0.35:', [(round(vx, 3), round(vy, 3)) for vx, vy in grid.vias if ((vx - x) ** 2 + (vy - y) ** 2) ** 0.5 < 0.35])
