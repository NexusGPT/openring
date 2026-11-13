#!/usr/bin/env python3
"""Shows that the changed and new rows of check_netlist.py can fail. usage: fail_proof.py <patched design copy>
Three copies, each one change, check_netlist.py of the copy run on it. Expected (written before the run):
  fp_c84_10uF : C84 value back to 10uF in parts.csv  -> FAIL A7-2
  fp_no_r73   : R73 rows removed from netlist.csv and parts.csv -> FAIL A6-3 and FAIL C1-R73
  fp_no_c90   : C90 rows removed from netlist.csv and parts.csv -> FAIL C3-VDD_3V0
Logs: logs/failproof_<name>.log; summary logs/failproof_summary.txt."""
import csv, os, shutil, subprocess, sys
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring-circuit-work")
PY = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/.venv/bin/python")
SRC = os.path.abspath(sys.argv[1])
EXPECT = {'fp_c84_10uF': ['A7-2'], 'fp_no_r73': ['A6-3', 'C1-R73'], 'fp_no_c90': ['C3-VDD_3V0']}

def rw(path, keep, change=None):
    rows = list(csv.DictReader(open(path)))
    head = list(rows[0].keys())
    rows = [change(r) if change else r for r in rows if keep(r)]
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, head); w.writeheader(); w.writerows(rows)

out = []
for name, tags in EXPECT.items():
    dst = os.path.join(W, name)
    if os.path.exists(dst):
        raise SystemExit('%s exists already' % dst)
    shutil.copytree(SRC, os.path.join(dst, 'design'), symlinks=True)
    ring = os.path.join(dst, 'design', 'ecad', 'ring')
    if name == 'fp_c84_10uF':
        rw(os.path.join(ring, 'parts.csv'), lambda r: True, lambda r: dict(r, value='10uF') if r['reference'] == 'C84' else r)
    else:
        ref = 'R73' if name == 'fp_no_r73' else 'C90'
        rw(os.path.join(ring, 'parts.csv'), lambda r: r['reference'] != ref)
        rw(os.path.join(ring, 'netlist.csv'), lambda r: r['reference'] != ref)
    log = os.path.join(W, 'logs', 'failproof_%s.log' % name)
    with open(log, 'w') as f:
        rc = subprocess.call([PY, '-B', os.path.join(ring, 'check_netlist.py')], cwd=ring, stdout=f, stderr=subprocess.STDOUT)
    text = open(log).read()
    got = [t for t in tags if ('FAIL %s ' % t) in text]
    last = text.strip().split('\n')[-1]
    out.append('%s exit %d; expected FAIL %s; found %s; last line: %s' % (name, rc, ','.join(tags), ','.join(got) or 'none', last))
    print(out[-1])
open(os.path.join(W, 'logs', 'failproof_summary.txt'), 'w').write('\n'.join(out) + '\n')
