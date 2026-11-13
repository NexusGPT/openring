#!/usr/bin/env python3
"""make_broken_fp.py : writes two broken copies of OpenRing.pretty into w1-evidence/ for check_footprints.py to reject:
broken_ball.pretty (U1 ball A1 renamed A1X) and broken_missing.pretty (U2 pad E7 deleted).  Plain python."""
import os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.join(HERE, 'w1-evidence')
SRC = os.path.join(HERE, 'OpenRing.pretty')
for name in ('broken_ball.pretty', 'broken_missing.pretty'):
    d = os.path.join(E, name)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(SRC, d)
p = os.path.join(E, 'broken_ball.pretty', 'WLCSP-61_nRF54LM20A-CAAA.kicad_mod')
t = open(p).read(); assert t.count('(pad "A1"') == 1
open(p, 'w').write(t.replace('(pad "A1"', '(pad "A1X"'))
p = os.path.join(E, 'broken_missing.pretty', 'WLCSP-35_nPM1304-CAAA.kicad_mod')
t = open(p).read()
t2 = re.sub(r'\t\(pad "E7" smd circle\n(?:\t\t.*\n)*?\t\)\n', '', t)
assert t2 != t
open(p, 'w').write(t2)
print('wrote broken_ball.pretty and broken_missing.pretty')
