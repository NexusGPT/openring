#!/usr/bin/env python3
"""usage: diag2.py <deck> <workdir>: same deck, wave also holds i(vocv), i(v.xu11.vs), i(v.xu2.vsb), v(n_MOTOR) and
v(n_MOT_EN); prints a time table from 31.9 to 34.2 ms (cell V, cell mA, U11 out mA, chip battery mA, VMOT, EN)."""
import os, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/circuit"))
import bench
deck, work = sys.argv[1], sys.argv[2]
T0, T1, STEP = (float(x) for x in (sys.argv[3:6] if len(sys.argv) > 5 else (0.0319, 0.0342, 0.0001)))
txt = open(deck).read()
i = txt.index('wrdata @WAVE@ ')
j = txt.index('\n', i)
line = 'wrdata @WAVE@ v(n_VBAT) i(vocv) i(v.xu11.vs) i(v.xu2.vsb) v(n_VMOT) v(n_MOT_EN)'
d2 = os.path.join(work, 'diag2_' + os.path.basename(deck))
os.makedirs(work, exist_ok=True)
open(d2, 'w').write(txt[:i] + line + txt[j:])
res, err = bench.run_deck(d2, {'ocv': 3.45, 'rcell': (3.45 - 3.0) / 0.230}, tag='d2', workdir=work, keep_wave=True)
print('errors', err[:2], 'vbat_min', res.get('motor.vbat_min'))
wave = os.path.join(work, os.path.splitext(os.path.basename(d2))[0] + '__d2.wave.txt')
rows = []
for l in open(wave):
    try:
        c = [float(x) for x in l.split()]
    except ValueError:
        continue
    rows.append((c[0], c[1], c[3], c[5], c[7], c[9], c[11]))
last = -1
print('t_ms cell_V cell_mA u11_out_mA chip_bat_mA vmot_V en_V')
for r in rows:
    if T0 <= r[0] <= T1 and r[0] - last >= STEP:
        print('%.4f %.5f %.1f %.1f %.1f %.4f %.3f' % (1000 * r[0], r[1], -1000 * r[2], 1000 * r[3], 1000 * r[4], r[5], r[6]))
        last = r[0]
