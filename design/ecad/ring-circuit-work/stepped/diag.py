#!/usr/bin/env python3
"""usage: diag.py <deck> <workdir>: runs the deck at ocv 3.45 V, rcell R_SPEC, keeps the wave, prints the time of the
lowest cell voltage in 30.5 to 110 ms, and the cell and VMOT voltage at each enable edge window (wave columns: vbat vsys v18 v30 vmot vsd)."""
import os, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/circuit"))
import bench
deck, work = sys.argv[1], sys.argv[2]
res, err = bench.run_deck(deck, {'ocv': 3.45, 'rcell': (3.45 - 3.0) / 0.230}, tag='diag', workdir=work, keep_wave=True)
print('errors', err[:2], 'vbat_min', res.get('motor.vbat_min'))
wave = os.path.join(work, os.path.splitext(os.path.basename(deck))[0] + '__diag.wave.txt')
rows = []
for l in open(wave):
    c = l.split()
    try:
        rows.append([float(x) for x in c])
    except ValueError:
        continue
pts = [(r[0], r[1], r[9]) for r in rows if 0.0305 <= r[0] <= 0.11]
tmin = min(pts, key=lambda p: p[1])
print('lowest cell %.5f V at t = %.6f s (VMOT %.4f V)' % (tmin[1], tmin[0], tmin[2]))
for t0, t1 in ((0.0305, 0.032), (0.032, 0.034), (0.034, 0.036), (0.036, 0.038), (0.038, 0.040), (0.040, 0.042), (0.042, 0.052), (0.052, 0.11)):
    s = [p for p in pts if t0 <= p[0] < t1]
    if s:
        m = min(s, key=lambda p: p[1])
        print('window %.4f to %.4f s: lowest cell %.5f V at %.6f s, VMOT max %.4f V' % (t0, t1, m[1], m[0], max(p[2] for p in s)))
