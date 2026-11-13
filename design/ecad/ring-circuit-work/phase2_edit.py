#!/usr/bin/env python3
"""Phase 2 edits of the circuit changes C1 (R73, 330 kohm VBUS to GND), C2 (C84 4.7 uF) and C3 (C90, second 10 uF on VDD_3V0),
the two C88 text fixes, and the check rows the lead granted in check_netlist.py (A7-2, A6-3, C1-R73, C3-VDD_3V0).

usage: phase2_edit.py <design_folder>   (the real design/ folder, or a copy holding the same files)

Each replacement must match exactly once in its file, or the script stops before writing anything. Each file is written
whole to a temporary name in its own folder and moved over the old one (os.replace), so a reader never sees half a file.
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
CK = os.path.join(D, 'ecad', 'ring', 'check_netlist.py')

DECIDE = 'design/wiring/lead-decisions.md'

# ------------------------------------------------------------------ make_netlist.py
MK_EDITS = [
    # text fix (lead, 2026-11-13): C88's own sheet says 10 Vdc; Nordic Table 37 names 16 V
    ("# A7 D3: third 10 uF on VSYS/PVDD as Nordic C2, C3, C4 (Table 37, page 157; X5R 16 V)\n",
     "# A7 D3: third 10 uF on VSYS/PVDD as Nordic C2, C3, C4 (Table 37, page 157, which names X5R 16 V); the part fitted,\n"
     "# GRT188R61A106KE13D, is X5R 10 V (datasheets/w1c_murata_grt188r61a106ke13.pdf; pmic-caps-facts.md G3)\n"),
    # C3: C90 beside C79 on VDD_3V0
    ("two('C79', 'C', '10uF', '', 'ring:C_0402', P, 'VDD_3V0', 'GND')\n",
     "two('C79', 'C', '10uF', '', 'ring:C_0402', P, 'VDD_3V0', 'GND')\n"
     "# C90 second 10 uF on VDD_3V0 beside C79 (lead change C3, 2026-11-13; pmic-caps-facts.md G5 and D7): nPM1304 Table 18\n"
     "# page 45 asks an effective output capacitance of 4 uF or more (datasheets/npm1304_datasheet_v1_0.txt lines 3172 to 3174);\n"
     "# C79 alone is about 4 uF at 3.0 V (Murata DC bias graph, w1d_murata_grm155r60j106me15.pdf p2), two give about 8 uF\n"
     "two('C90', 'C', '10uF', 'GRM155R60J106ME15D', 'ring:C_0402', P, 'VDD_3V0', 'GND')\n"),
    ("    ('C79', 'U2 VOUT2 10 uF (nPM1300 DK C48; confirm for the nPM1304, S18)'), ",
     "    ('C79', 'U2 VOUT2 10 uF (nPM1300 DK C48; confirm for the nPM1304, S18)'),\n"
     "    ('C90', 'U2 VOUT2 (VDD_3V0) second 10 uF beside C79: nPM1304 Table 18 page 45 asks 4 uF or more effective, C79 alone gives about 4 uF at 3.0 V (lead change C3, 2026-11-13)'),\n    "),
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
OLD_C79ROW = 'Schematic addition: U2 VSYS 10 uF (DK C40),"C74,C75,C78,C79",4,U2 VSYS 10 uF (DK C40); value from'
NEW_C79ROW = ('Schematic addition: U2 VSYS 10 uF (DK C40),"C74,C75,C78,C79,C90",5,U2 VSYS 10 uF (DK C40); C90 is a second 10 uF on '
              'VDD_3V0 beside C79 (lead change C3 of 2026-11-13: nPM1304 Table 18 page 45 asks 4 uF or more effective; C79 alone gives '
              'about 4 uF at 3.0 V); value from')
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
          'C83 stays 10 uF GRM155R60J106ME15; C84 is 4.7 uF Murata GRM155R61A475MEAAD, same 0402 footprint and nets.\n'
          '- C90 added (2026-11-13, circuit change C3, pmic-caps-facts.md G5 and D7): a second 10 uF 0402 Murata GRM155R60J106ME15D on VDD_3V0 '
          'beside C79, in the 10 uF row of C74, C75, C78, C79 (quantity 5): nPM1304 Table 18 page 45 asks 4 uF or more effective.\n')

SN_ADD = ('\n2026-11-13 (circuit changes C1 and C2: discharge resistor R73, C84 4.7 uF): lead decisions of 2026-11-13 (`design/wiring/lead-decisions.md` rows "sim finding 1", "sim finding 4 (item 41)", '
          '"sim finding 4, correction"), applied in `make_netlist.py`: R73 (330 kohm, 0201, sheet power) joins VBUS (pin 1) to GND '
          '(pin 2), so that the pads on the finger fall under 0.1 V within 10 s after the ring leaves the case; its code Yageo '
          'RC0201FR-07330KL follows the coding of the series RC0201FR-07 (`design/parts/order-codes.md` section 1) and is not confirmed '
          'at a distributor. C84 changes from 10 uF (GRM155R60J106ME15) to 4.7 uF (Murata GRM155R61A475MEAAD), same 0402 footprint and '
          'nets; C83 stays 10 uF. Where a line above says C84 is 10 uF (the motor drive paragraph, table row 12) or that with no '
          'case no voltage is on the pad (pads statement 1), this paragraph wins: R73 is what takes the voltage off the pad. The board (`pcb/`) is not changed here: until the board carries R73, a board check against this '
          'netlist reports R73 as missing. C3: C90 (10 uF, Murata GRM155R60J106ME15D, 0402, sheet power) joins C79 on VDD_3V0 '
          '(pin 1) and GND (pin 2): the nPM1304 datasheet asks an effective output capacitance of 4 uF or more (Table 18, page 45; '
          '`datasheets/npm1304_datasheet_v1_0.txt` lines 3172 to 3174) and C79 alone gives about 4 uF at 3.0 V (`pmic-caps-facts.md` G5, D7). '
          'VDD_MIC and VDD_SD are the power chip\'s two load switches (LSOUT1, LSOUT2) used in load switch mode (`make_netlist.py`, '
          'comment of C86 and C87), with soft start left enabled (datasheet text line 4678: "Soft start is enabled by default"). '
          'C88 is X5R 10 V (its sheet `datasheets/w1c_murata_grt188r61a106ke13.pdf`); Nordic Table 37 names 16 V (row 6 of the A7 table is corrected). '
          'Evidence and the bench rows before and after: `circuit-two-notes.md`.\n')
SN_ROW6_OLD = '| 6 | D3 | C88, third 10 uF X5R 16 V on VSYS/PVDD (Table 37) |'
SN_ROW6_NEW = ('| 6 | D3 | C88, third 10 uF on VSYS/PVDD (Table 37 names X5R 16 V; the part fitted, GRT188R61A106KE13D, is X5R 10 V: '
               '`datasheets/w1c_murata_grt188r61a106ke13.pdf`, `pmic-caps-facts.md` G3) |')

# ------------------------------------------------------------------ check_netlist.py (granted by the lead, 2026-11-13)
CK_EDITS = [
    ("bad2 += ['%s value %r' % (c, parts.get(c, {}).get('value')) for c in ('C83', 'C84') if parts.get(c, {}).get('value') != '10uF']\n",
     "# expected value changed by the lead's decision \"sim finding 4, correction\" (wiring/lead-decisions.md, 2026-11-13): C84 4.7 uF, C83 stays 10 uF\n"
     "bad2 += ['%s value %r' % (c, parts.get(c, {}).get('value')) for c, v in (('C83', '10uF'), ('C84', '4.7uF')) if parts.get(c, {}).get('value') != v]\n"),
    ("C83 VBAT, C84 VMOT 10uF; Q1, D1, MOTOR_DRV, MOTOR_G absent'",
     "C83 VBAT 10uF, C84 VMOT 4.7uF; Q1, D1, MOTOR_DRV, MOTOR_G absent'"),
    ("o3 = o3 and {r['reference'] for r in nets['VBUS']} == {'CP1', 'U2', 'U9', 'R1', 'C71', 'C72', tail_of('VBUS')}\n",
     "# R73 added by the lead's decision \"sim finding 1\" (wiring/lead-decisions.md, 2026-11-13): the discharge resistor VBUS to GND\n"
     "o3 = o3 and {r['reference'] for r in nets['VBUS']} == {'CP1', 'U2', 'U9', 'R1', 'C71', 'C72', 'R73', tail_of('VBUS')}\n"),
    ("# A6-7 (d, review F07) storage bus: no line joins the 1.8 V chip ball and the 3.0 V storage pad directly\n",
     "# C1-R73: decision \"sim finding 1\" (wiring/lead-decisions.md, 2026-11-13): R73 330 kohm, pad 1 on VBUS, pad 2 on GND\n"
     "r73 = parts.get('R73', {})\n"
     "a5('C1-R73', r73.get('value') == '330k' and (netof('R73', '1'), netof('R73', '2')) == ('VBUS', 'GND'),\n"
     "   'R73 330k, pad 1 VBUS, pad 2 GND (discharge resistor)', 'R73 wrong or absent: %r on %s %s' % (r73.get('value'), netof('R73', '1'), netof('R73', '2')))\n"
     "# C3-VDD_3V0: lead change C3 (2026-11-13; pmic-caps-facts.md G5, D7; nPM1304 Table 18 page 45): VDD_3V0 holds C79 and C90, 10uF each\n"
     "c3bad = ['%s %r on %s %s' % (c, parts.get(c, {}).get('value'), netof(c, '1'), netof(c, '2')) for c in ('C79', 'C90')\n"
     "         if parts.get(c, {}).get('value') != '10uF' or (netof(c, '1'), netof(c, '2')) != ('VDD_3V0', 'GND')]\n"
     "a5('C3-VDD_3V0', not c3bad, 'VDD_3V0 holds C79 and C90, 10uF each', 'VDD_3V0 capacitors wrong: %s' % c3bad)\n\n"
     "# A6-7 (d, review F07) storage bus: no line joins the 1.8 V chip ball and the 3.0 V storage pad directly\n"),
]


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
    b = once(b, OLD_C79ROW, NEW_C79ROW, 'bom.csv 10 uF row with C79')
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
    sn = once(sn, SN_ROW6_OLD, SN_ROW6_NEW, 'sch-notes.md row 6')
    out[SN] = sn + ('' if sn.endswith('\n') else '\n') + SN_ADD

    ck = open(CK).read()
    for old, new in CK_EDITS:
        ck = once(ck, old, new, 'check_netlist.py')
    out[CK] = ck

    for p, txt in out.items():
        tmp = os.path.join(os.path.dirname(p), '.' + os.path.basename(p) + '.c2tmp')
        with open(tmp, 'w') as f:
            f.write(txt)
        os.replace(tmp, p)
        print('written', p)
    print('edits applied: make_netlist.py %d, bom.csv 3 (split C83,C84; add R73; C90 in the 10 uF row), bom-notes.md 3 lines, sch-notes.md 1 paragraph and row 6, check_netlist.py %d' % (len(MK_EDITS), len(CK_EDITS)))


if __name__ == '__main__':
    main()
