import re, os, glob, sys
FW = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware")
reply = open(os.path.join(FW, "tests/core/evidence/final-reply.md")).read()
print("reply chars:", len(reply))
ev_files = [os.path.join(FW, p) for p in [
    "tests/core/host/host-tests.log", "tests/core/evidence/zephyr-run-1.log", "tests/core/evidence/zephyr-run-2.log",
    "tests/core/evidence/count-rows.log", "tests/core/broken/broken-long900.log", "tests/core/broken/broken-row12to.log",
    "tests/core/broken/broken-gap60.log", "tests/core/broken/broken-row27act.log", "tests/core/evidence/includes.log",
    "docs/core-notes.md", "modules/ring_core/src/state_table.inc", "tests/core/testcase.yaml",
    "build-logs/20261111-105051-core-tests.log", "tests/core/src/th.h", "tests/core/.gitignore"]]
texts = {p: open(p).read() for p in ev_files}
checked = 0; bad = 0
# 1. paths in backticks
for m in re.findall(r"`([^`]+)`", reply):
    if "/" in m and not m.startswith("RESULT") and " " not in m:
        cands = glob.glob(os.path.join(FW, m)) + glob.glob(os.path.join(FW, "tests/core", m)) + glob.glob(os.path.join(FW, "modules/ring_core", m))
        checked += 1
        print(("OK  " if cands else "BAD ") + "path " + m)
        bad += not cands
# 2. quoted strings and key claims
claims = [
 ("RESULT PASS tests=153", "tests/core/host/host-tests.log"),
 ("153 of 153 executed test cases passed", "tests/core/evidence/zephyr-run-2.log"),
 ("with no warnings", "tests/core/evidence/zephyr-run-2.log"),
 ("remote exit code: 0", "tests/core/evidence/zephyr-run-2.log"),
 ("remote exit code: 2", "tests/core/evidence/zephyr-run-1.log"),
 ("unrecognized platform - nrf54lm20bsim/nrf54lm20/cpuapp", "tests/core/evidence/zephyr-run-1.log"),
 ("rows in section 1.2", "tests/core/evidence/count-rows.log"),
 (": 61 (the document states 61)", "tests/core/evidence/count-rows.log"),
 ("row tests in tests/core/src/test_rows.c: 61", "tests/core/evidence/count-rows.log"),
 ("COUNT MATCH", "tests/core/evidence/count-rows.log"),
 ("fail=21", "tests/core/broken/broken-long900.log"),
 ("RESULT FAIL", "tests/core/broken/broken-long900.log"),
 ("FAIL generator.fresh_run_matches_committed_table", "tests/core/broken/broken-row12to.log"),
 ("fail=10", "tests/core/broken/broken-row12to.log"),
 ("fail=2", "tests/core/broken/broken-gap60.log"),
 ("fail=4", "tests/core/broken/broken-row27act.log"),
 ("0xe23322c4", "modules/ring_core/src/state_table.inc"),
 ("#define RC_TABLE_ROWS 61", "modules/ring_core/src/state_table.inc"),
 ("exit 0", "tests/core/host/host-tests.log"),
 ("| U23 |", "docs/core-notes.md"),
 ("| U8 | 168, 169 |", "docs/core-notes.md"),
 ("| U6 | 136, 137, 200 |", "docs/core-notes.md"),
 ("| U7 |", "docs/core-notes.md"),
 ("| U9 | 185 |", "docs/core-notes.md"),
 ("SPEC_LONG_MS", "tests/core/src/th.h"),
 ("host/build/", "tests/core/.gitignore"),
 ("broken/copy-*/ring_core/", "tests/core/.gitignore"),
]
for s, f in claims:
    checked += 1
    p = os.path.join(FW, f)
    ok = s in texts[p]
    line = next((i + 1 for i, l in enumerate(texts[p].splitlines()) if s in l), None)
    print(("OK  " if ok else "BAD ") + f"'{s}' in {f} line {line}")
    bad += not ok
# 3. platform not in testcase.yaml
checked += 1
ok = "nrf54lm20bsim" not in texts[os.path.join(FW, "tests/core/testcase.yaml")]
print(("OK  " if ok else "BAD ") + "bsim board absent from testcase.yaml"); bad += not ok
# 4. includes only stdint, stdbool, string (system headers)
sys_inc = set(re.findall(r"#include <([^>]+)>", texts[os.path.join(FW, "tests/core/evidence/includes.log")]))
checked += 1
ok = sys_inc <= {"stdint.h", "stdbool.h", "string.h"}
print(("OK  " if ok else "BAD ") + f"system includes {sorted(sys_inc)}"); bad += not ok
# 5. every number in the reply found in some evidence text
for n in sorted(set(re.findall(r"\b\d+\b", reply))):
    checked += 1
    hit = [os.path.relpath(p, FW) for p, t in texts.items() if re.search(r"(?<!\d)" + n + r"(?!\d)", t)]
    print(("OK  " if hit else "BAD ") + f"number {n}: {hit[:2]}")
    bad += not hit
# 6. disagreement: host count vs zephyr count vs notes RESULT line
notes = texts[os.path.join(FW, "docs/core-notes.md")]
last = notes.strip().splitlines()[-1]
checked += 1
ok = last.startswith("RESULT: done") and "153" in last
print(("OK  " if ok else "BAD ") + "notes last line: " + last)
bad += not ok
checked += 1
ok = len(reply) < 3500
print(("OK  " if ok else "BAD ") + f"reply under 3500 chars ({len(reply)})"); bad += not ok
print(f"claims checked={checked} bad={bad}")
