#!/usr/bin/env python3
"""H2, H3, N4: rewrite fields of six rows of design/mfg/assembly/joints.csv (and one field of J-W021-B).

Every other row and field is written back byte for byte: the script first proves that a plain
read and write of the table gives the same bytes, and prints every field it changes.
Run: design/.venv/bin/python -I edit_joints.py [--dry]
"""
import csv, io, sys

P = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/assembly/joints.csv")
raw = open(P, newline='', encoding='utf-8').read()
term = '\r\n' if '\r\n' in raw else '\n'


def dump(rows, fields):
    b = io.StringIO()
    w = csv.DictWriter(b, fieldnames=fields, lineterminator=term)
    w.writeheader()
    w.writerows(rows)
    return b.getvalue()


rows = list(csv.DictReader(io.StringIO(raw, newline='')))
fields = list(rows[0].keys())
same = dump(rows, fields) == raw or dump(rows, fields) == raw + ('' if raw.endswith(term) else term)
print('roundtrip identical:', dump(rows, fields) == raw, '| line terminator', repr(term))
if dump(rows, fields) != raw:
    sys.exit('roundtrip differs: not writing')

LD = 'design/wiring/lead-decisions.md:89'
EYE_HIDDEN = ("Eye: before the press, the land's own smooth solder dome and no bridge to its neighbours (step 14 How 2, "
              "at 10 times); after the press the land lies wholly under the foot, and both of its 0.125 mm ends lie under "
              "ribbon copper at all 7 sizes, so this land itself cannot be seen; the look of step 14 How 7 judges the foot as "
              "a whole: flat, no lifted corner, not moved, no solder ball beside it")
EYE_ONE_END = ("Eye: before the press, the land's own smooth solder dome and no bridge to its neighbours (step 14 How 2, "
               "at 10 times); after the press the land lies wholly under the foot; one of its 0.125 mm ends lies under no "
               "ribbon copper and could show through the foot only if the coverlay and the 0.10 mm stiffener let light "
               "through, which no file states (not proven); the look of step 14 How 7 judges the foot as a whole: flat, no "
               "lifted corner, not moved, no solder ball beside it")
PAIR_A = ("one of the ground pair A6 and A8 that FLEX1's own copper joins; by the lead's decision a redundant pair, proven "
          "as a pair by the electrical test of step 14, no X-ray asked (%s). Meter, board without power: SW1 terminal 4 to "
          "C28 pad 2 beeps; this proves that at least one of A6 and A8 is joined, not this land alone. " % LD)
PAIR_B = ("one of the ground pair B2 and B7 that FLEX2's own copper joins; by the lead's decision a redundant pair, proven "
          "as a pair by the electrical test of step 14, no X-ray asked (%s). " % LD)
CHECK = {
    'J-W011-A': 'land A8, ' + PAIR_A + EYE_HIDDEN + ' (hotbar-joint.md section 4)',
    'J-W021-A': 'land A6, ' + PAIR_A + EYE_ONE_END + ' (hotbar-joint.md section 4)',
    'J-W026-A': ('land B2, ' + PAIR_B + 'Meter, board on the cell: C83 pad 1 to C83 pad 2 reads the cell voltage recorded at '
                 'step 9 within 0.05 V (starting value), and disc CP4 to C83 pad 2 beeps; these prove land B1 and that at '
                 'least one of B2 and B7 is joined, not B2 alone. ' + EYE_ONE_END + ' (hotbar-joint.md section 4)'),
    'J-W032-A': ('land B7, ' + PAIR_B + 'Meter: disc CP4 to C83 pad 2 beeps; then USB through CP1 to CP4 enumerates; with the '
                 'cell voltage at C83 these prove that at least one of B2 and B7 is joined, not B7 alone. ' + EYE_ONE_END +
                 ' (hotbar-joint.md section 4)'),
}
TH_CHECK = ("case step 10 (a), board unpowered, ohmmeter, black probe on test pad TP16 (GND), red probe on point T, the pad of "
            "RT2 that does not beep to TP16 (net TS): before TH1 is fitted the steady reading R0 is 29.8 to 30.4 kohm (RT2 "
            "alone, if the unpowered charger draws nothing; any steady R0 from 4.5 to 30.4 kohm is accepted); after the two "
            "joints the steady reading R1 is 6.4 to 10.1 kohm when R0 was 29.8 to 30.4 kohm (about 7.5 kohm at 25 C), and "
            "R0 x R1 / (R0 - R1), the thermistor alone, is 8.2 to 15.1 kohm at 15 to 30 C; the meter's path runs through "
            "TH1.1, the bead and TH1.2, so the reading proves both joints; R1 equal to R0 means a joint is open, near 0 ohm "
            "a short. By eye at 10 times: the two bare leads touch nothing else over their whole length. Last, with the cell "
            "in place: continuity from each lead to the cell's can: open (design/wiring/lead-decisions.md:71)")
TH_SRC_OLD = 'check: design/wiring/lead-decisions.md:71 | check_possible_at_this_step: design/wiring/lead-decisions.md:71'
TH_SRC_NEW = ('check: design/ecad/case/pcb/board-notes.md:324; design/wiring/lead-decisions.md:71; '
              'design/mfg/assembly/guide-fix4-work/th1_values.py | check_possible_at_this_step: design/ecad/case/pcb/board-notes.md:324')
CK_SRC_OLD = 'check: design/mfg/assembly/assembly.md:205; design/mfg/assembly/hotbar-joint.md:147 |'
CK_SRC_NEW = ('check: design/mfg/assembly/assembly.md:205; design/mfg/assembly/hotbar-joint.md:147; '
              'design/mfg/assembly/hotbar-joint.md:184; ' + LD + ' |')
changed = 0


def setf(r, k, v):
    global changed
    if r[k] != v:
        print('%s | %s | %s\n    -> %s' % (r['joint_id'], k, r[k], v))
        r[k] = v
        changed += 1


for r in rows:
    j = r['joint_id']
    if j in CHECK:
        setf(r, 'check', CHECK[j])
        assert r['source'].count(CK_SRC_OLD) == 1, j
        setf(r, 'source', r['source'].replace(CK_SRC_OLD, CK_SRC_NEW))
    if j in ('J-W061-B', 'J-W062-B'):
        setf(r, 'check', TH_CHECK)
        assert r['source'].count(TH_SRC_OLD) == 1, j
        setf(r, 'source', r['source'].replace(TH_SRC_OLD, TH_SRC_NEW))
    if j == 'J-W021-B':
        old = 'blue lead to land 2 (-, GND), the land farther from the slot'
        assert r['orientation'].count(old) == 1
        setf(r, 'orientation', r['orientation'].replace(old, 'minus lead (black or blue: the maker gives "Black or Blue", '
                                                       'band-interface.md line 122) to land 2 (-, GND), the land farther from the slot'))
print('fields changed:', changed)
if '--dry' not in sys.argv:
    open(P, 'w', newline='', encoding='utf-8').write(dump(rows, fields))
    print('RESULT written', P)
else:
    print('RESULT dry run, nothing written')
