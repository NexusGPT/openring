#!/usr/bin/env python3
"""Broken copies of netlist.csv, one per C2 change (and one ring A3 change); each must make
check_netlist.py exit 1. Delivered files are not touched."""
import csv, subprocess, os
PY = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/.venv/bin/python")
OUT = []
def run(unit, name, edit):
    R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/%s/") % unit
    B = R + 'evidence/broken_c2/'
    os.makedirs(B, exist_ok=True)
    rows = [dict(r) for r in csv.DictReader(open(R + 'netlist.csv'))]
    edit(rows)
    p = B + name + '.csv'
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(B + 'check_' + name + '.log', 'w') as lg:
        rc = subprocess.call([PY, R + 'check_netlist.py', p], stdout=lg, stderr=lg)
    fails = [l.strip() for l in open(B + 'check_' + name + '.log') if l.startswith('FAIL')]
    OUT.append('%s %s exit %d | %s' % (unit, name, rc, ' ; '.join(fails[:3])))
def setnet(ref, pin, net, typ=None):
    def f(rows):
        for r in rows:
            if r['reference'] == ref and r['pin_number'] == pin:
                r['net'] = net
                if typ: r['pin_type'] = typ
    return f
def multi(*fs):
    def f(rows):
        for g in fs: g(rows)
    return f
run('case', 'r27_to_3v3', setnet('R27', '2', '3V3'))
run('case', 'r28_dsel_open', multi(setnet('R28', '1', 'GND'), setnet('U2', '24', '', 'no_connect')))
run('case', 'r29_missing_pullup', setnet('R29', '2', 'SD_D2'))
run('case', 'r30_to_gnd', setnet('R30', '2', 'GND'))
run('case', 'usbc_dp_to_u2', multi(setnet('U2', '2', 'USB_C_DP', 'bidirectional'), setnet('J1', 'A6', 'USB_C_DP', 'passive')))
run('case', 'u5_en_fault_swapped', multi(setnet('U5', '3', 'VRING_FAULT_N'), setnet('U5', '4', 'VRING_EN')))
run('case', 'led_anode_to_gnd', setnet('LED1', '1', 'GND'))
run('case', 'divider_r4_to_3v3', setnet('R4', '2', '3V3'))
run('ring', 'p305_on_light', setnet('U1', 'G4', 'LED_K'))
open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/case/evidence/broken_c2_exits.txt"), 'w').write('\n'.join(OUT) + '\n')
print('\n'.join(OUT))
