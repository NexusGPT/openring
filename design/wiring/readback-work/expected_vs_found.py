"""Rule 3 (expectation versus result). The expectations below are the design documents' OWN stated values (file and line in logs/limit_quotes.log);
this file was written after the runs, so it is NOT a blind pre-run expectation; the blind expectations I wrote before running are in
board-readback.md section 0.1 M9 (Route A will not see the cut or join; Route B will) and the pilot logs. The script lists every case where the found figure differs."""
import json, os, math
Wd = os.path.dirname(os.path.abspath(__file__)); R = Wd + '/results/'
q = json.load(open(R + 'p4p5.json')); b = json.load(open(R + 'p3_band.json')); p1 = json.load(open(R + 'p1_ring.json'))
rows = []
def chk(name, expected, found, tol_rel=None, ok_if=None, src=''):
    ok = ok_if(found) if ok_if else abs(found - expected) <= tol_rel * abs(expected)
    rows.append((name, expected, found, ok, src))
chk('antenna Z0 ohm (plan d.1 line 295: 49.3)', 49.3, q['P4_1']['Z0'], 0.01, src='p4p5.json P4_1.Z0')
chk('USB Zdiff at the plan gap 0.075 (plan d.2 line 301: 91.5)', 91.5, 2 * q['P4_4']['Z0'] * (1 - 0.48 * math.exp(-0.96 * 0.075 / 0.065)), 0.01, src='formula check')
chk('USB Zdiff at the drawn modal gap (plan intends 90 +-10%)', 90.0, q['P4_4']['Zdiff_mode'], 0.10, src='p4p5.json P4_4')
chk('antenna L1 clearance mm (plan d.1: 0.200)', 0.200, q['P4_2']['min_clear_mm'], ok_if=lambda x: x >= 0.200, src='p4p5.json P4_2')
chk('antenna L2 GND under line (plan d.1: solid, 100 percent)', 100.0, q['P4_3']['cov_pct'], ok_if=lambda x: x >= 100.0, src='p4p5.json P4_3')
chk('antenna line length mm (plan R2.0: 16.4)', 16.4, q['P4_len']['sum'], 0.02, src='p4p5.json P4_len')
chk('USB mismatch mm (plan d.2: <= 0.10)', 0.10, q['P4_5']['mismatch'], ok_if=lambda x: x <= 0.10, src='p4p5.json P4_5')
for n, lim in (('XL1', 9.0), ('XL2', 9.0), ('XC1', 6.0), ('XC2', 6.0)):
    p = q['P5'][n]; L = p['path'] if p['path'] is not None else p['total']
    chk('%s length mm (plan d.4: <= %.1f)' % (n, lim), lim, L, ok_if=lambda x, lim=lim: x <= lim, src='p4p5.json P5.%s' % n)
    chk('%s other-net gap mm (plan d.4: >= 0.20)' % n, 0.20, min(v[0] for v in p['clear'].values()), ok_if=lambda x: x >= 0.20, src='p4p5.json P5.%s.clear' % n)
for nm, key, cur, st in (('band US13 VMOT mV (band-interface.md line 132: 8.7)', 'vmot', '175mA', 8.7), ('band US13 motor GND land 6 mV (line 132: 12.9)', 'gnd6', '175mA', 12.9), ('band US13 cell VBAT mV (line 133: 11.0)', 'vbat', '227.5mA', 11.0), ('band US13 cell GND land 2 mV (line 133: 12.5)', 'cell_gnd2', '227.5mA', 12.5)):
    chk(nm, st, b['us13'][key][0]['drops_mV'][cur], 0.10, src='p3_band.json us13.%s' % key)
chk('ring shorts+opens (board notes: routed, 0 unconnected)', 0, p1['shorts'] + p1['opens'], ok_if=lambda x: x == 0, src='p1_ring.json')
n = 0
for (name, e, f, ok, s) in rows:
    n += 1
    print('EXPECT %-3s | %s | expected %s | found %.4f | %s | %s' % ('OK' if ok else 'DIFF', name, e, f, 'matches' if ok else 'DIFFERS', s))
print('EXPECT cases %d, differing %d' % (n, sum(1 for r in rows if not r[3])))
