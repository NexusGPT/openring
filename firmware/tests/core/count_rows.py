#!/usr/bin/env python3
"""Print the number of rows of design/firmware.md section 1.2 and the number of
row tests in tests/core/src/test_rows.c, and check that each row has exactly one test.
With --table, also print the markdown table "row, line, from, event, to, test".
Exit 0 when the counts are equal and every row has its test, 1 otherwise."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(FW, "modules", "ring_core", "tools"))
import gen_table  # noqa: E402

doc_path = os.path.normpath(os.path.join(FW, "..", "design", "firmware.md"))
with open(doc_path, encoding="utf-8") as fh:
    rows, stated = gen_table.parse_rows(fh.read())
with open(os.path.join(HERE, "src", "test_rows.c"), encoding="utf-8") as fh:
    src = fh.read()
tests = re.findall(r"^ROW\((\d\d), (\d+),", src, re.M)
names = [int(a) for a, b in tests]
nums = [int(b) for a, b in tests]

print(f"rows in section 1.2 of {doc_path}: {len(rows)} (the document states {stated})")
print(f"row tests in tests/core/src/test_rows.c: {len(tests)}")
ok = len(rows) == len(tests) and names == nums and sorted(names) == list(range(1, len(rows) + 1))
if "--table" in sys.argv:
    print()
    print("| Row | Line | From | Event | To | Test |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        t = f"rc_rows.test_row_{r['row']:02d}" if r["row"] in names else "MISSING"
        ev = r["event_text"].replace("|", "/")
        print(f"| {r['row']} | {r['doc_line']} | {r['from']} | {ev} | {r['to']} | {t} |")
    print()
acts = open(os.path.join(FW, "modules", "ring_core", "src", "state_actions.c"), encoding="utf-8").read()
cases = {int(n): int(l) for n, l in re.findall(r"case (\d+): +/\* line (\d+)", acts)}
bad_cases = [(r["row"], r["doc_line"], cases.get(r["row"])) for r in rows if cases.get(r["row"]) != r["doc_line"]]
print(f"action cases in src/state_actions.c: {len(cases)}, each with the document line of its row: {'yes' if not bad_cases else bad_cases}")
ok = ok and not bad_cases and len(cases) == len(rows)
print("COUNT MATCH" if ok else "COUNT MISMATCH")
sys.exit(0 if ok else 1)
