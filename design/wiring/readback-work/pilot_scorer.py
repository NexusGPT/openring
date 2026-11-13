"""pilot: does the scorer pass a known-pass case and fail a known-fail case? In-memory edits of the parsed ring Gerber (not P2)."""
import sys, os, copy, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rb_lib as R
F = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/fab")
lp = R.find_board_files(F + '/gerber', 'ring'); dr = sorted(glob.glob(F + '/drill/*.drl'))
rows = R.read_netlist((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))

def score(b, label):
    b.connectivity(); c = R.compare(b, rows)
    print('PILOT %-34s nets=%d pads=%d shorts=%d opens=%d missing=%d open_nets=%s short_groups=%s' % (label, c['nets'], c['pads'], c['shorts'], c['opens'], c['missing'], c['open_nets'], c['short_groups']))
    return c

b = R.Board('ring', lp, dr, res=0.005)
c0 = score(b, 'known-pass (unedited)')
# known-fail 1: remove one draw of LCD_SCK (selected by its X2 label only to choose the draw)
cands = [(k, i, d) for k, L in enumerate(b.layers) for i, d in enumerate(L.draws) if d[5] == 'LCD_SCK']
cands.sort(key=lambda t: -math.hypot(t[2][2] - t[2][0], t[2][3] - t[2][1]))
done = False
for k, i, d in cands:
    b = R.Board('ring', lp, dr, res=0.005)
    del b.layers[k].draws[i]
    b.masks = [b.raster(L) for L in b.layers]
    c = score(b, 'known-fail cut LCD_SCK draw L%d #%d len %.3f' % (k + 1, i, math.hypot(d[2] - d[0], d[3] - d[1])))
    if c['opens'] >= 1:
        done = True; break
print('PILOT cut detected:', done)
# known-fail 2: join LCD_SCK and LCD_MOSI with a draw between the nearest draw end points on one layer
best = None
for k, L in enumerate(b.layers):
    A = [d for d in L.draws if d[5] == 'LCD_SCK']; B = [d for d in L.draws if d[5] == 'LCD_MOSI']
    for a in A:
        for bb in B:
            for pa in ((a[0], a[1]), (a[2], a[3])):
                for pb in ((bb[0], bb[1]), (bb[2], bb[3])):
                    dd = math.hypot(pa[0] - pb[0], pa[1] - pb[1])
                    if best is None or dd < best[0]:
                        best = (dd, k, pa, pb)
print('PILOT nearest SCK/MOSI draw ends: %.3f mm on L%d' % (best[0], best[1] + 1))
b = R.Board('ring', lp, dr, res=0.005)
b.layers[best[1]].draws.append((best[2][0], best[2][1], best[3][0], best[3][1], 0.1, 'LCD_SCK'))
b.masks = [b.raster(L) for L in b.layers]
c = score(b, 'known-fail join LCD_SCK-LCD_MOSI')
# known-fail 3: GND to VBAT via a draw between two pads on L1 (power short)
