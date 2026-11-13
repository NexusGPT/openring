"""pilot: on every board of the main run, the scorer must show a planted open and a planted short (in-memory edits of the parsed Gerber)"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_p1 as P, rb_lib as R
boards = ['ring', 'case_main', 'case_pins'] + ['flex%d-us%d' % (f, u) for f in (1, 2) for u in range(7, 14)]
for bd in boards:
    sp = P.spec(bd); lp = R.find_board_files(sp['gerber'], sp['prefix']); rows = R.read_netlist(sp['nl']) + sp['extra']
    def mk():
        return R.Board(bd, lp, sp['drills'], res=sp['res'])
    b = mk(); b.connectivity(); c0 = R.compare(b, rows, sp['scope'])
    # planted open
    cands = sorted([(math.hypot(d[2] - d[0], d[3] - d[1]), k, i) for k, L in enumerate(b.layers) for i, d in enumerate(L.draws) if d[5] not in ('GND', 'N/C', None, '')], reverse=True)
    got_open = None
    for ln, k, i in cands[:60]:
        b = mk(); net = b.layers[k].draws[i][5]; del b.layers[k].draws[i]; b.masks = [b.raster(L) for L in b.layers]; b.connectivity()
        c = R.compare(b, rows, sp['scope'])
        if c['opens'] > c0['opens']:
            got_open = (net, ln, k + 1, c['opens']); break
    # planted short: nearest end points of draws of two different non-GND nets on one layer
    b = mk(); best = None
    for k, L in enumerate(b.layers):
        ds = [d for d in L.draws if d[5] not in ('GND', 'N/C', None, '')]
        for a in range(len(ds)):
            for c_ in range(a + 1, len(ds)):
                if ds[a][5] == ds[c_][5]:
                    continue
                for pa in ((ds[a][0], ds[a][1]), (ds[a][2], ds[a][3])):
                    for pb in ((ds[c_][0], ds[c_][1]), (ds[c_][2], ds[c_][3])):
                        dd = math.hypot(pa[0] - pb[0], pa[1] - pb[1])
                        if best is None or dd < best[0]:
                            best = (dd, k, pa, pb, ds[a][5], ds[c_][5])
    got_short = None
    if best:
        dd, k, pa, pb, n1, n2 = best
        b.layers[k].draws.append((pa[0], pa[1], pb[0], pb[1], 0.1, n1)); b.masks = [b.raster(L) for L in b.layers]; b.connectivity()
        c = R.compare(b, rows, sp['scope'])
        got_short = (n1, n2, round(dd, 3), k + 1, c['shorts'])
    print('PILOTALL %-10s base shorts=%d opens=%d | planted open: %s | planted short: %s | both shown: %s' % (bd, c0['shorts'], c0['opens'], got_open, got_short, bool(got_open and got_short and got_short[4] > c0['shorts'])))
