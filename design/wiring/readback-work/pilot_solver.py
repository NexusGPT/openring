"""pilot: validates the resistance mesh, the impedance formulas and the draw graph on synthetic and known cases."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rb_lib as R, rb_res as S
W = os.path.dirname(os.path.abspath(__file__))
os.makedirs(W + '/synthetic', exist_ok=True)
def gbr(draws, flashes, path, ap=(0.15,)):
    L = ['%FSLAX46Y46*%', '%MOMM*%', '%LPD*%', '%ADD10C,0.150000*%', '%ADD11R,0.600000X0.600000*%', '%ADD12C,0.100000*%']
    L.append('G01*')
    for (x1, y1, x2, y2, w) in draws:
        a = 10 if abs(w - 0.15) < 1e-9 else 12
        L.append('D%d*' % a); L.append('X%dY%dD02*' % (round(x1 * 1e6), round(y1 * 1e6))); L.append('X%dY%dD01*' % (round(x2 * 1e6), round(y2 * 1e6)))
    for (x, y, ref, pin) in flashes:
        L.append('D11*'); L.append('%%TO.P,%s,%s*%%' % (ref, pin)); L.append('X%dY%dD03*' % (round(x * 1e6), round(y * 1e6))); L.append('%TD*%')
    L.append('M02*')
    open(path, 'w').write('\n'.join(L) + '\n')
# case 1: straight 5 mm track 0.15 wide between two 0.6 pads; analytic R = Rs * (L_between pads / w) with pads equipotential
rho, t = S.RHO, 0.018
rs = rho / t
gbr([(10.0, 10.0, 15.0, 10.0, 0.15)], [(10.0, 10.0, 'A', '1'), (15.0, 10.0, 'B', '1')], W + '/synthetic/s1.gbr')
gbr([(10.0, 10.0, 13.5355339, 13.5355339, 0.15)], [(10.0, 10.0, 'A', '1'), (13.5355339, 13.5355339, 'B', '1')], W + '/synthetic/s2.gbr')
open(W + '/synthetic/empty.drl', 'w').write('M48\n; #@! TF.FileFunction,Plated,1,1,PTH\nMETRIC\n%\nM30\n')
for name, Ltrack, pad_cut in (('s1', 5.0, 0.6), ('s2', 5.0, 0.6 * math.sqrt(2))):
    b = R.Board(name, [('F_Cu', W + '/synthetic/%s.gbr' % name)], [], res=0.005)
    b.connectivity()
    g = b.pads()[0]['group']
    mesh = S.build_mesh(b, g, [rs])
    src = S.pad_nodes(b, mesh, [('A', '1')]); snk = S.pad_nodes(b, mesh, [('B', '1')])
    r, nfree = S.resistance(mesh, src, snk)
    # track between the pad edges: pads 0.6 wide: centre distance 5.0, copper between pad edges 4.4 mm plus pad effects; compare the track-only analytic
    analytic = rs * (Ltrack - pad_cut) / 0.15
    print('PILOT mesh %s: R=%.5f ohm, analytic rho L/(w t) over the %.4f mm between the pad edges = %.5f ohm, ratio %.4f, nodes %d' % (name, r, Ltrack - pad_cut, analytic, r / analytic, mesh['N']))
# case 2: known-fail check for the solver: the same track cut in the middle must give an open (infinite or no path)
gbr([(10.0, 10.0, 12.4, 10.0, 0.15), (12.6, 10.0, 15.0, 10.0, 0.15)], [(10.0, 10.0, 'A', '1'), (15.0, 10.0, 'B', '1')], W + '/synthetic/s3.gbr')
b = R.Board('s3', [('F_Cu', W + '/synthetic/s3.gbr')], [], res=0.005); b.connectivity()
pads = b.pads(); print('PILOT cut track: pad groups differ =', pads[0]['group'] != pads[1]['group'])
# impedance formulas against the plan's own published values (ring-board-plan.md section d)
z, ee = S.z_microstrip_hj(0.120, 0.065, 0.018, 4.1)
print('PILOT Z0 microstrip 0.120/0.065/0.018 er 4.1 = %.2f ohm eeff %.3f   (plan d.1: 49.3 ohm, eeff 3.14)' % (z, ee))
z0, _ = S.z_microstrip_hj(0.100, 0.065, 0.018, 4.1)
print('PILOT USB 0.100 gap 0.075: Z0 %.2f ohm, Zdiff %.2f ohm   (plan d.2: 54.4 and 91.5)' % (z0, S.zdiff_ipc2141(z0, 0.075, 0.065)))
z, _ = S.z_microstrip_hj(0.117, 0.065, 0.018, 4.1); print('PILOT 0.117 mm -> %.2f ohm  (plan d.1: calculation gives 0.117 mm for 50.0 ohm)' % z)
