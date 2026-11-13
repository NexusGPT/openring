#!/usr/bin/env python3
"""Phase 2 edits of the circuit changes C1 (R73, 330 kohm VBUS to GND) and C2 (C84 4.7 uF).

usage: phase2_edit.py <design_folder>   (the real design/ folder, or a copy holding the same files)

Each replacement must match exactly once in its file, or the script stops before writing anything.
Files edited: ecad/ring/make_netlist.py (the source of netlist.csv, parts.csv, additions.csv), bom.csv,
bom-notes.md, ecad/ring/sch-notes.md. After it: run make_netlist.py, then run_all.sh (gen_sch.py writes the
schematic from netlist.csv and parts.csv; R73 has sheet 'power', so the power sheet shows it).
"""
import csv
import io
import os
import sys

D = os.path.abspath(sys.argv[1])
MK = os.path.join(D, 'ecad', 'ring', 'make_netlist.py')
BOM = os.path.join(D, 'bom.csv')
BN = os.path.join(D, 'bom-notes.md')
SN = os.path.join(D, 'ecad', 'ring', 'sch-notes.md')

DECIDE = 'design/wiring/lead-decisions.md'

# ------------------------------------------------------------------ make_netlist.py
MK_EDITS = [
    # C2: C84 10 uF -> 4.7 uF, same 0402 footprint, same nets
    ("two('C84', 'C', '10uF', 'GRM155R60J106ME15', 'ring:C_0402', K, 'VMOT', 'GND')\n",
     "# C84 4.7 uF in place of 10 uF (lead-decisions.md rows \"sim finding 4 (item 41)\" and \"sim finding 4, correction\", 2026-11-13):\n"
     "# Murata GRM155R61A475MEAAD, same 0402 footprint and nets; C83 stays 10 uF\n"
     "two('C84', 'C', '4.7uF', 'GRM155R61A475MEAAD', 'ring:C_0402', K, 'VMOT', 'GND')\n"),
    # C1: R73 after R72 on the power sheet
    ("two('R72', 'R', '150k', '', 'ring:R_0201', P, 'VSET2', 'GND')\n",
     "two('R72', 'R', '150k', '', 'ring:R_0201', P, 'VSET2', 'GND')\n"
     "# R73 discharge resistor VBUS to GND, 330 kohm 0201 (lead-decisions.md row \"sim finding 1\", 2026-11-13): without it the\n"
     "# circuit bench holds up to 4.5 V on the VBUS pad 10 s after the ring leaves the case. Yageo RC0201FR-07330KL follows the\n"
     "# coding of the series RC0201FR-07 (parts/order-codes.md section 1) and is NOT confirmed at a distributor.\n"
     "two('R73', 'R', '330k', 'RC0201FR-07330KL', 'ring:R_0201', P, 'VBUS', 'GND')\n"),
    # additions: C84 text, R73 added
    ("('C84', 'U11 output and motor 10 uF (Jinlong 9-4 asks 2 uF or more)'),\n",
     "('C84', 'U11 output and motor 4.7 uF GRM155R61A475MEAAD, was 10 uF (lead-decisions.md sim finding 4 and its correction; Jinlong 9-4 asks 2 uF or more)'),\n"
     "    ('R73', 'discharge resistor VBUS to GND 330 kohm: the pads fall under 0.1 V within 10 s after the ring leaves the case (lead-decisions.md sim finding 1); code RC0201FR-07330KL by the series coding, not confirmed at a distributor'),\n"),
]

# ------------------------------------------------------------------ bom.csv
OLD_C8384 = ('Capacitor 10 uF 0402 6.3 V,"C83,C84",2,U11 input and output; C84 is also the 2 uF or more across the motor that '
             'Jinlong asks,Murata,GRM155R60J106ME15,0402,1.0 x 0.5,10 uF,"X5R, 6.3 V",DS,design/datasheets/p3_sgm38046.pdf p4 '
             'Table 1 ; design/ecad/motor-drive/motor-drive.md 2.2,,\n')
ROW_C83 = ['Capacitor 10 uF 0402 6.3 V', 'C83', '1', 'U11 input (C84 at the output is a separate line since the change of 2026-11-13)',
           'Murata', 'GRM155R60J106ME15', '0402', '1.0 x 0.5', '10 uF', 'X5R, 6.3 V', 'DS',
           'design/datasheets/p3_sgm38046.pdf p4 Table 1 ; design/ecad/motor-drive/motor-drive.md 2.2', '', '']
ROW_C84 = ['Capacitor 4.7 uF 0402 10 V', 'C84', '1',
           'U11 output; also the 2 uF or more across the motor that Jinlong asks; 4.7 uF in place of 10 uF (lead-decisions.md rows '
           '"sim finding 4 (item 41)" and "sim finding 4, correction")',
           'Murata', 'GRM155R61A475MEAAD', '0402', '1.0 x 0.5', '4.7 uF',
           'X5R, 10 V, +-20 %; T 0.5 +-0.15 mm (0.65 max); DC bias graph p2: about 3.9 uF at 2 V, 2.6 uF at 4 V (as read in design/ecad/ring/pcb/u4-capacitors.md)',
           'DS', 'design/datasheets/w1d_murata_grm155r61a475meaa.pdf p1 p2 ; design/ecad/ring/pcb/u4-capacitors.md ; design/wiring/lead-decisions.md',
           '', '']
OLD_R72 = None  # found below by its first field and reference (the R72 line is matched whole)
ROW_R73 = ['VBUS discharge resistor', 'R73', '1',
           'from VBUS to GND on the ring: empties the VBUS capacitors after the ring leaves the case, so the pads on the finger fall '
           'under 0.1 V within 10 s (lead-decisions.md row "sim finding 1"); draws about 15 uA from the case while charging, nothing from the cell',
           'Yageo', 'RC0201FR-07330KL', '0201', '', '330 kohm 1 %',
           'order code written by the coding of the series RC0201FR-07 (RC_L), NOT confirmed at a distributor; 1 % from the series',
           'LIST', 'design/parts/order-codes.md section 1 ; design/wiring/lead-decisions.md row sim finding 1 ; design/sim/circuit/sim-notes.md finding 1', '',
           'confirm at a distributor that RC0201FR-07330KL exists (code by the series coding only), its stock and price']

BN_ADD = ('- R73 added (2026-11-13, circuit change C1, lead-decisions.md row "sim finding 1"): 330 kohm 0201 from VBUS to GND, Yageo '
          'RC0201FR-07330KL; the code follows the coding of the series RC0201FR-07 (parts/order-codes.md section 1) and is not confirmed at a distributor.\n'
          '- C83 and C84 are two lines (2026-11-13, circuit change C2, lead-decisions.md rows "sim finding 4 (item 41)" and "sim finding 4, correction"): '
          'C83 stays 10 uF GRM155R60J106ME15; C84 is 4.7 uF Murata GRM155R61A475MEAAD, same 0402 footprint and nets.\n')

SN_ADD = ('\n2026-11-13 (circuit changes C1 and C2: discharge resistor R73, C84 4.7 uF): lead decisions of 2026-11-13 (`design/wiring/lead-decisions.md` rows "sim finding 1", "sim finding 4 (item 41)", '
          '"sim finding 4, correction"), applied in `make_netlist.py`: R73 (330 kohm, 0201, sheet power) joins VBUS (pin 1) to GND '
          '(pin 2), so that the pads on the finger fall under 0.1 V within 10 s after the ring leaves the case; its code Yageo '
          'RC0201FR-07330KL follows the coding of the series RC0201FR-07 (`design/parts/order-codes.md` section 1) and is not confirmed '
          'at a distributor. C84 changes from 10 uF (GRM155R60J106ME15) to 4.7 uF (Murata GRM155R61A475MEAAD), same 0402 footprint and '
          'nets; C83 stays 10 uF. Where a line above says C84 is 10 uF (the motor drive paragraph, table row 12) or that with no '
          'case no voltage is on the pad (pads statement 1), this paragraph wins: R73 is what takes the voltage off the pad. The board (`pcb/`) is not changed here: until the board carries R73, a board check against this '
          'netlist reports R73 as missing. Evidence and the bench rows before and after: `circuit-two-notes.md`.\n')


def once(text, old, new, name):
    n = text.count(old)
    if n != 1:
        raise SystemExit('%s: expected 1 match, found %d for %r' % (name, n, old[:80]))
    return text.replace(old, new)


def csv_line(row):
    s = io.StringIO()
    csv.writer(s, lineterminator='\n').writerow(row)
    return s.getvalue()


def main():
    out = {}
    t = open(MK).read()
    for old, new in MK_EDITS:
        t = once(t, old, new, 'make_netlist.py')
    out[MK] = t

    b = open(BOM).read()
    b = once(b, OLD_C8384, csv_line(ROW_C83) + csv_line(ROW_C84), 'bom.csv C83,C84')
    lines = b.splitlines(keepends=True)
    r72 = [i for i, l in enumerate(lines) if next(csv.reader([l]))[1:2] == ['R72']]
    if len(r72) != 1:
        raise SystemExit('bom.csv: expected 1 R72 line, found %d' % len(r72))
    if any(next(csv.reader([l]))[1:2] == ['R73'] for l in lines):
        raise SystemExit('bom.csv: R73 already present')
    lines.insert(r72[0] + 1, csv_line(ROW_R73))
    b = ''.join(lines)
    rows = list(csv.reader(io.StringIO(b)))
    bad = [i + 1 for i, r in enumerate(rows) if len(r) != 14]
    if bad:
        raise SystemExit('bom.csv: rows without 14 fields: %s' % bad)
    out[BOM] = b

    bn = open(BN).read()
    if 'R73' in bn:
        raise SystemExit('bom-notes.md already names R73')
    out[BN] = bn + ('' if bn.endswith('\n') else '\n') + BN_ADD

    sn = open(SN).read()
    if '(circuit changes C1 and C2' in sn:
        raise SystemExit('sch-notes.md already has the C1 and C2 section')
    out[SN] = sn + ('' if sn.endswith('\n') else '\n') + SN_ADD

    for p, txt in out.items():
        open(p, 'w').write(txt)
        print('written', p)
    print('edits applied: make_netlist.py %d, bom.csv 2 (split C83,C84; add R73), bom-notes.md 2 lines, sch-notes.md 1 section' % len(MK_EDITS))


if __name__ == '__main__':
    main()
