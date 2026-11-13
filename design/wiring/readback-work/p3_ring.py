import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S
OUT = os.path.dirname(os.path.abspath(__file__)) + '/results/p3_ring.json'
def log(s):
    print(s); sys.stdout.flush()
t0 = time.time()
b, c, rows = L.load('ring')
rs = [S.RHO / 0.018] * 4      # fab/stackup.txt: 0.018 mm finished copper on L1 to L4
log('P3 ring: rho %.3e ohm mm, copper 0.018 mm, sheet resistance %.3f mohm/sq, hole step 1 mohm (brief), raster %.0f um' % (S.RHO, rs[0] * 1e3, b.res * 1e3))
res = {}
o, m, g = L.path_R(b, c, 'VBAT', [('J_BAND_B', '1')], [[('U2', 'D1'), ('U2', 'D2')], [('U11', '4')], [('U4', 'A1')]], rs, log, 'ring VBAT band land->chip/regulator', [0.235])
res['VBAT'] = o
o, m, g = L.path_R(b, c, 'VMOT', [('U11', '1')], [[('J_BAND_A', '7')]], rs, log, 'ring VMOT regulator->motor land', [0.175, 0.080]); res['VMOT'] = o
o, m, g = L.path_R(b, c, 'VBUS', [('J_BAND_B', '4')], [[('U2', 'B1'), ('U2', 'B2')], [('U9', '4')], [('R1', '1')]], rs, log, 'ring VBUS band land->power chip', [0.015, 0.100]); res['VBUS'] = o
for net, src, cur in (('VDD_1V8', ('U2', 'B6'), [0.2]), ('VDD_SD', ('U2', 'A5'), [0.1, 0.025])):
    loads = [p for p in L.net_pads(rows, net) if p != src]
    o, m, g = L.path_R(b, c, net, [src], [[p] for p in loads], rs, log, 'ring %s source->each load' % net, cur)
    res[net] = o
    ok = [r for r in o if 'R_mesh_mohm' in r]
    far = max(ok, key=lambda r: r['R_mesh_mohm'])
    log('P3 ring %s FARTHEST LOAD %s R=%.2f mohm; drops: %s' % (net, far['sink'], far['R_mesh_mohm'], far['drops_mV']))
json.dump(res, open(OUT, 'w'), indent=1)
log('P3_RING_DONE seconds %.1f' % (time.time() - t0))
