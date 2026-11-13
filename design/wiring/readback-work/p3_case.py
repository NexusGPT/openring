"""P3 case: VRING U5 OUT -> W1 (case_main) and P1 -> WP1 (case_pins) at 0.400 A; BAT U2 13+14 -> W5 and GND U2 25 -> W6 at 0.350 A.
Copper: outer 35 um, inner 17.5 um (case/pcb/power_width.py line 3: 1 oz outer, 0.5 oz inner; board files hold no stackup block: deviation D2)"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S, rb_lib as R, run_p1 as P
OUT = os.path.dirname(os.path.abspath(__file__)) + '/results/p3_case.json'
def log(s):
    print(s); sys.stdout.flush()
res = {}
b, c, rows = L.load('case_main')
rs = [S.RHO / 0.035, S.RHO / 0.0175, S.RHO / 0.0175, S.RHO / 0.035]
log('P3 case_main: rho %.3e, copper outer 0.035 / inner 0.0175 mm, sheet %.3f / %.3f mohm/sq, raster %.0f um' % (S.RHO, rs[0] * 1e3, rs[1] * 1e3, b.res * 1e3))
res['vring_main'] = L.path_R(b, c, 'VRING', [('U5', '6')], [[('W1', '1')], [('P1', '1')]] if False else [[('W1', '1')]], rs, log, 'case_main VRING U5 OUT -> W1', [0.400])[0]
res['bat'] = L.path_R(b, c, 'BAT', [('U2', '13'), ('U2', '14')], [[('W5', '1')]], rs, log, 'case_main BAT U2 13+14 -> W5', [0.350])[0]
b2, c2, rows2 = L.load('case_pins')
rs2 = [S.RHO / 0.035] * 2
res['vring_pins'] = L.path_R(b2, c2, 'VRING', [('WP1', '1')], [[('P1', '1')]], rs2, log, 'case_pins VRING WP1 -> P1', [0.400])[0]
# GND: coarse raster (memory): 50 um
sp = P.spec('case_main'); lp = R.find_board_files(sp['gerber'], sp['prefix'])
t = time.time()
bg = R.Board('case_main', lp, sp['drills'], res=0.05); bg.connectivity()
cg = R.compare(bg, R.read_netlist(sp['nl']), sp['scope'])
log('P3 case_main GND at 50 um raster: shorts %d opens %d (coarse raster check)' % (cg['shorts'], cg['opens']))
res['gnd_50um'] = L.path_R(bg, cg, 'GND', [('U2', '25')], [[('W6', '1')]], rs, log, 'case_main GND U2 25 -> W6 (50 um raster)', [0.350])[0]
res['vring_main_50um'] = L.path_R(bg, cg, 'VRING', [('U5', '6')], [[('W1', '1')]], rs, log, 'case_main VRING U5 OUT -> W1 (50 um raster, resolution check)', [0.400])[0]
json.dump(res, open(OUT, 'w'), indent=1, default=float)
log('P3_CASE_DONE seconds %.1f' % (time.time() - t))
