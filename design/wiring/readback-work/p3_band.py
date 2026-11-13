"""P3 band: motor lines (flex1) and cell lines (flex2) per size"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S
OUT = os.path.dirname(os.path.abspath(__file__)) + '/results/p3_band.json'
def log(s):
    print(s); sys.stdout.flush()
res = {}
rs = [S.RHO / 0.012] * 2      # band-interface.md line 132 and the board file stackup block: 0.012 mm copper
log('P3 band: rho %.3e ohm mm, copper 0.012 mm, sheet resistance %.3f mohm/sq, hole step 1 mohm, raster 5 um' % (S.RHO, rs[0] * 1e3))
for us in (7, 9, 13, 8, 10, 11, 12):
    b, c, rows = L.load('flex1-us%d' % us)
    r1 = L.path_R(b, c, 'VMOT', [('J_BAND_A', '7')], [[('M1', '1')]], rs, log, 'band flex1-us%d VMOT land7->motor' % us, [0.175, 0.080])[0]
    r2 = L.path_R(b, c, 'GND', [('J_BAND_A', '6'), ('J_BAND_A', '8')], [[('M1', '2')]], rs, log, 'band flex1-us%d GND lands6+8->motor' % us, [0.175, 0.080])[0]
    r3 = L.path_R(b, c, 'GND', [('J_BAND_A', '6')], [[('M1', '2')]], rs, log, 'band flex1-us%d GND land6 only->motor' % us, [0.175, 0.080])[0]
    b, c, rows = L.load('flex2-us%d' % us)
    r4 = L.path_R(b, c, 'VBAT', [('J_BAND_B', '1')], [[('PRT1', '1')]], rs, log, 'band flex2-us%d VBAT land1->PRT1' % us, [0.2275])[0]
    r5 = L.path_R(b, c, 'GND', [('J_BAND_B', '2'), ('J_BAND_B', '7')], [[('PRT1', '2')]], rs, log, 'band flex2-us%d GND lands2+7->PRT1' % us, [0.2275])[0]
    r6 = L.path_R(b, c, 'GND', [('J_BAND_B', '2')], [[('PRT1', '2')]], rs, log, 'band flex2-us%d GND land2 only->PRT1' % us, [0.2275])[0]
    res['us%d' % us] = dict(vmot=r1, gnd_both=r2, gnd6=r3, vbat=r4, cell_gnd_both=r5, cell_gnd2=r6)
json.dump(res, open(OUT, 'w'), indent=1, default=float)
log('P3_BAND_DONE')
