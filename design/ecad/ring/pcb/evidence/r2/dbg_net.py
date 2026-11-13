# dbg_net.py board net: runs finish_route.py's A* for the smallest open group of one net and prints its start cells and result
import sys
src = open((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/finish_route.py")).read().split('\nb = load(src)')[0]
board, net = sys.argv[1], sys.argv[2]
sys.argv = ['finish_route.py', board, board]
g = {'__file__': (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/finish_route.py")}; exec(compile(src, 'finish_route.py', 'exec'), g)
b = g['load'](board); items = g['board_items'](b); grid = g['Grid'](items)
comps = g['components'](items, net); comps.sort(key=len)
print('groups', [len(c) for c in comps], [tuple(round(v, 2) for v in g['bbox_of'](c)) for c in comps])
g0 = comps[0]; rest = [it for c in comps[1:] for it in c]
pts = []
for it in g0 + rest:
    (aj0, aj1, ai0, ai1), m = g['raster'](it); pts += [(aj0, ai0), (aj1, ai1)]
mg = int(3.0 / g['G']); NY, NX = g['NY'], g['NX']
win = (max(0, min(p[0] for p in pts) - mg), min(NY, max(p[0] for p in pts) + mg), max(0, min(p[1] for p in pts) - mg), min(NX, max(p[1] for p in pts) + mg))
tb, vb, halo = grid.blocked(net, win)
S = g['ends_or_all'](g0, win); print('free ends', g['free_ends'](g0)); print('start cells', len(S), 'blocked', sum(1 for (l, y, x) in S if tb[l][y, x]))
T = set()
for c in comps[1:]: T |= g['ends_or_all'](c, win)
print('goal cells', len(T), 'blocked', sum(1 for (l, y, x) in T if tb[l][y, x]))
path, n = g['astar'](S, T, tb, vb, halo); print('path', path is not None, 'expanded', n)
