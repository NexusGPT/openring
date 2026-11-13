#!/usr/bin/env python3
"""Stepped enable of the motor regulator U11: builds the ring1 deck of the bench (make_decks.deck_motor) from a
ring folder (netlist.csv, parts.csv), changes only the MOTOR pin waveform and, for motor model M2, the start window
of the motor load, runs every case through the bench's own runner (bench.run_deck) and writes the results.
Pass line and conditions: pass-line.md in this folder (written before the first run).

usage: stepped.py <ring_folder> <out_folder> [<bench_folder>]
"""
import csv
import os
import re
import sys

RING = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
BENCH = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/circuit")
sys.path.insert(0, BENCH)
import bench  # noqa: E402
import circuit_lib as cl  # noqa: E402
import make_decks as md  # noqa: E402

V20, I_SPEC = 3.45, 0.230          # run_tests.py
RSPEC = (V20 - 3.0) / I_SPEC       # 1.9565 ohm, pass-lines.md R1.1
T0 = md.TMOT                        # 0.03 s
RUN = md.SRC['motor_run_s'][0]      # 0.08 s
TSTART = md.SRC['motor_start_s'][0]  # 0.01 s (ESTIMATE)
R_START = md.SRC['motor_v'][0] / md.SRC['motor_start_a'][0]
R_RUN = md.SRC['motor_v'][0] / md.SRC['motor_run_a'][0]
VH = 1.8
LIMIT = 3.0


def pattern(name):
    """list of (t_on, t_off) on windows; the last one ends at T0 + RUN."""
    if name == 'E1':
        return [(T0, T0 + RUN)]
    w = {'E3': 0.002, 'E3s': 0.0003}[name]
    wins = [(T0 + 2 * k * w, T0 + (2 * k + 1) * w) for k in range(3)]
    wins.append((T0 + 6 * w, T0 + RUN))
    return wins


def pwl(wins):
    pts = ['0 0']
    for a, b in wins:
        pts += ['%.7g 0' % a, '%.7g %g' % (a + 1e-6, VH), '%.7g %g' % (b, VH), '%.7g 0' % (b + 1e-6)]
    return 'PWL(' + ' '.join(pts) + ')'


def build(c84, pat, motor):
    d = cl.Design(RING, {'C84': c84})
    dk = md.deck_motor(d)
    txt = dk.text()
    wins = pattern(pat)
    lines = txt.split('\n')
    iv = [i for i, l in enumerate(lines) if l.startswith('Vmotor ')]
    ib = [i for i, l in enumerate(lines) if l.startswith('Bm ')]
    if len(iv) != 1 or len(ib) != 1:
        raise SystemExit('deck: Vmotor lines %d, Bm lines %d' % (len(iv), len(ib)))
    f = lines[iv[0]].split()
    lines[iv[0]] = '%s %s %s %s ; U1 pin MOTOR, enable pattern %s (stepped.py, pass-line.md)' % (f[0], f[1], f[2], pwl(wins), pat)
    t_last = wins[-1][0]
    t_end_start = (T0 if motor == 'M1' else t_last) + TSTART
    m = re.match(r'^(Bm \S+ 0 I = v\(\S+\) / \(\(time < )([0-9.eE+-]+)(\) \? \S+ : \S+\))$', lines[ib[0]])
    if not m:
        raise SystemExit('Bm line not in the expected form: %s' % lines[ib[0]])
    lines[ib[0]] = m.group(1) + '%.7g' % t_end_start + m.group(3) + ' ; motor model %s: start %g ohm until %.7g s, then %g ohm' % (motor, R_START, t_end_start, R_RUN)
    return '\n'.join(lines), wins


def main():
    os.makedirs(os.path.join(OUT, 'decks'), exist_ok=True)
    work = os.path.join(OUT, 'run')
    cases = []
    for c84, kind in (('4.7uF', 'pass line'), ('10uF', 'pass line'), ('3.25uF', 'info: 4.7 uF part at 3 V DC bias'), ('4.0uF', 'info: 10 uF part at 3 V DC bias')):
        for motor in ('M1', 'M2'):
            for pat in ('E1', 'E3', 'E3s'):
                if pat == 'E1' and motor == 'M2':
                    continue  # M2 equals M1 for one step
                cases.append((c84, kind, motor, pat))
    rows = []
    for c84, kind, motor, pat in cases:
        txt, wins = build(c84, pat, motor)
        name = 'stepped_C84_%s_%s_%s' % (c84.replace('.', 'p'), motor, pat)
        p = os.path.join(OUT, 'decks', name + '.cir')
        open(p, 'w').write(txt)
        res, err = bench.run_deck(p, {'ocv': V20, 'rcell': RSPEC}, tag='rspec', workdir=work)
        v = res.get('motor.vbat_min')
        status = 'ERROR ' + err[0][:120] if err else ('no value' if not isinstance(v, float) else ('PASS' if v >= LIMIT else 'FAIL'))
        rows.append(dict(c84=c84, kind=kind, motor=motor, pattern=pat, vbat_min=v, vmot_min=res.get('motor.vmot_min'),
                         icell_pk_mA=(-1000 * res['motor.icell_pk']) if isinstance(res.get('motor.icell_pk'), float) else None,
                         ildo_max_mA=(1000 * res['motor.ildo_max']) if isinstance(res.get('motor.ildo_max'), float) else None,
                         status=status, deck=p))
        print('%-7s %-2s %-4s vbat_min %s  %s' % (c84, motor, pat, v, status))
    with open(os.path.join(OUT, 'stepped_results.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    # comparison: stepped minus one step, same C84 and motor model (E1 of M1 serves both models)
    lines = ['C84,kind,motor,pattern,vbat_min_V,minus_one_step_mV,verdict']
    for r in rows:
        e1 = [x for x in rows if x['c84'] == r['c84'] and x['pattern'] == 'E1'][0]
        if isinstance(r['vbat_min'], float) and isinstance(e1['vbat_min'], float):
            dmv = 1000 * (r['vbat_min'] - e1['vbat_min'])
            verdict = 'reference' if r['pattern'] == 'E1' else ('stepped lowers the dip' if dmv > 0.05 else ('stepped makes it worse' if dmv < -0.05 else 'no change (within 0.05 mV)'))
            lines.append('%s,%s,%s,%s,%.5f,%.2f,%s' % (r['c84'], r['kind'], r['motor'], r['pattern'], r['vbat_min'], dmv, verdict))
        else:
            lines.append('%s,%s,%s,%s,,,no value' % (r['c84'], r['kind'], r['motor'], r['pattern']))
    open(os.path.join(OUT, 'stepped_compare.csv'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    npass = sum(1 for r in rows if r['status'] == 'PASS')
    print('runs %d, pass %d, other %d' % (len(rows), npass, len(rows) - npass))


if __name__ == '__main__':
    main()
