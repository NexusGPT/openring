#!/usr/bin/env python3
"""H5: correct the design/bom.csv:N citations of assembly.md, and verify all of them.

Usage: fix_bom_cites.py --apply   (rewrite assembly.md in place, line count unchanged)
       fix_bom_cites.py --verify  (read assembly.md as it stands and check every citation)

The mapping below is keyed by (assembly line, old bom line) and gives the new bom line.
It comes from review4-work/bom-cites-judged.csv (which part each sentence names) and
from design/bom.csv as it stands (which line holds that part).
EXPECT gives, for each (assembly line, new bom line), the designators or item words the
sentence names (a 'row word|text word' pair when the bom row and the sentence use different words); --verify passes a citation only when the cited bom line holds one of them
in its reference or item field AND the assembly line names it.
"""
import csv, re, sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
ASM = ROOT + '/design/mfg/assembly/assembly.md'
BOM = ROOT + '/design/bom.csv'

MAP = {
    (54, 57): 60, (57, 45): 47, (57, 46): 49, (58, 67): 70, (58, 69): 72,
    (59, 59): 62, (60, 58): 61, (61, 51): 54, (63, 82): 85, (64, 81): 84,
    (65, 55): 58, (69, 48): 51, (70, 74): 77, (71, 78): 81, (72, 79): 82,
    (74, 80): 83, (75, 54): 57,
    (96, 11): 12, (96, 9): 10, (96, 85): 88, (96, 86): 87, (96, 67): 70,
    (96, 69): 72, (96, 18): 19,
    (124, 77): 64, (145, 44): 47, (159, 48): 50, (162, 48): 51, (163, 74): 77,
    (193, 82): 85, (193, 81): 84, (251, 55): 58, (275, 54): 57, (331, 55): 58,
    (332, 54): 57, (334, 76): 81, (334, 77): 82, (340, 55): 58, (348, 54): 57,
    (349, 55): 58, (402, 55): 58, (373, 53): 56, (374, 57): 60, (381, 81): 84, (381, 82): 85,
}
# what each sentence names, by (assembly line, cited bom line after the fix)
EXPECT = {
    (54, 60): ['FOAM1'], (57, 47): ['U11'], (57, 49): ['C84'], (58, 70): ['C85'],
    (58, 72): ['C88'], (59, 62): ['GSK2'], (60, 61): ['MEM1'], (61, 54): ['HSG1'],
    (63, 85): ['FRM1'], (64, 84): ['CAP1'], (65, 58): ['DAM1'], (69, 51): ['PRT1'],
    (70, 77): ['RT1'], (71, 81): ['FLEX1'], (72, 82): ['FLEX2'], (73, 64): ['CP1'],
    (74, 83): ['LNR1'], (75, 57): ['SEAL1'],
    (96, 12): ['J1'], (96, 10): ['U5'], (96, 88): ['C89'], (96, 87): ['LT1'],
    (96, 70): ['C85'], (96, 72): ['C88'], (96, 6): ['R73'], (96, 74): ['C90'],
    (96, 19): ['C13'],
    (124, 64): ['charging pads'], (145, 47): ['U11'], (150, 64): ['CP1'],
    (159, 50): ['BT1'], (162, 51): ['protection'], (163, 77): ['thermistor'],
    (193, 85): ['FRM1'], (193, 84): ['CAP1'], (251, 58): ['dam'], (275, 57): ['seal'],
    (331, 58): ['dam'], (332, 57): ['seal'], (334, 81): ['FLEX1'], (334, 82): ['FLEX2'],
    (340, 58): ['dam'], (348, 57): ['SEAL1'], (349, 58): ['DAM1'], (373, 56): ['ADH1'],
    (374, 60): ['FOAM1'], (381, 84): ['CAP1'], (381, 85): ['FRM1'], (384, 64): ['charging pads'],
    (402, 58): ["DAM1|switch head"],
}
CITE = re.compile(r'design/bom\.csv:(\d+)')


def bom_rows():
    lines = open(BOM, encoding='utf-8').read().split('\n')
    rows = {}
    for i, l in enumerate(lines, 1):
        if not l.strip():
            continue
        r = next(csv.reader([l]))
        rows[i] = (r[0], r[1])
    return rows


def apply():
    text = open(ASM, encoding='utf-8').read()
    lines = text.split('\n')
    n_before = len(lines)
    changed = 0
    for i, l in enumerate(lines, 1):
        def sub(m):
            nonlocal changed
            old = int(m.group(1))
            new = MAP.get((i, old))
            if new is None:
                return m.group(0)
            changed += 1
            print(f'CHANGE assembly.md:{i} bom.csv:{old} -> bom.csv:{new}')
            return f'design/bom.csv:{new}'
        lines[i - 1] = CITE.sub(sub, l)
    assert len(lines) == n_before
    open(ASM, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f'RESULT applied {changed} of {len(MAP)} mapped citations; lines {n_before}')


def verify():
    rows = bom_rows()
    lines = open(ASM, encoding='utf-8').read().split('\n')
    total = bad = 0
    for i, l in enumerate(lines, 1):
        for m in CITE.finditer(l):
            total += 1
            n = int(m.group(1))
            exp = EXPECT.get((i, n))
            row = rows.get(n)
            if exp is None or row is None:
                bad += 1
                print(f'FAIL assembly.md:{i} bom.csv:{n} no expectation or no row: row={row}')
                continue
            item, ref = row
            refs = set(x.strip() for x in ref.split(','))
            pairs = [(e.split('|')[0], e.split('|')[-1]) for e in exp]
            ok_row = any((r in refs) or (r.lower() in item.lower()) or (r.lower() in ref.lower()) for r, t in pairs)
            ok_text = any(t.lower() in l.lower() for r, t in pairs)
            status = 'OK  ' if ok_row and ok_text else 'FAIL'
            if status == 'FAIL':
                bad += 1
            print(f'{status} assembly.md:{i} bom.csv:{n} names {exp} | bom row: item "{item[:50]}" ref "{ref}" | row holds it {ok_row} | sentence names it {ok_text}')
    print(f'RESULT bom citations {total} problems {bad}')
    return bad


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply()
    sys.exit(1 if verify() else 0)
