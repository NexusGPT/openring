import re, os, glob
FW = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware")
reply = open(FW + "/tests/core/evidence/r2-final-reply.md").read()
ev = ["tests/core/host/host-tests.log", "tests/core/evidence/r2-zephyr-run-1.log", "tests/core/evidence/r2-count-rows.log",
      "tests/core/evidence/r2-fwcheck-final.log", "tests/core/evidence/r2-fwcheck-1.log", "tests/core/evidence/r2-firmware-md.diff",
      "docs/core-notes.md", "build-logs/20261111-113611-core-tests-r2.log", "tests/core/testcase.yaml"] + \
     [os.path.relpath(p, FW) for p in glob.glob(FW + "/tests/core/broken/broken-*.log")]
T = {p: open(os.path.join(FW, p)).read() for p in ev}
bad = 0; n = 0
def chk(s, f):
    global bad, n
    n += 1; ok = s in T[f]; bad += not ok
    print(("OK  " if ok else "BAD ") + f"'{s}' in {f}")
for s, f in [
 ("suites=10 tests=176 pass=176 fail=0", "tests/core/host/host-tests.log"), ("RESULT PASS tests=176", "tests/core/host/host-tests.log"),
 ("exit 0", "tests/core/host/host-tests.log"),
 ("2 of 2 executed test configurations passed", "tests/core/evidence/r2-zephyr-run-1.log"),
 ("352 of 352 executed test cases passed", "tests/core/evidence/r2-zephyr-run-1.log"),
 ("with no warnings", "tests/core/evidence/r2-zephyr-run-1.log"), ("remote exit code: 0", "tests/core/evidence/r2-zephyr-run-1.log"),
 ("-p native_sim -p nrf54lm20bsim/nrf54lm20a/cpuapp", "tests/core/evidence/r2-zephyr-run-1.log"),
 (": 65 (the document states 65)", "tests/core/evidence/r2-count-rows.log"), ("row tests in tests/core/src/test_rows.c: 65", "tests/core/evidence/r2-count-rows.log"),
 ("action cases in src/state_actions.c: 65, each with the document line of its row: yes", "tests/core/evidence/r2-count-rows.log"),
 ("COUNT MATCH", "tests/core/evidence/r2-count-rows.log"),
 ("FAIL header does not say Version F6", "tests/core/evidence/r2-fwcheck-final.log"), ("1 failures", "tests/core/evidence/r2-fwcheck-final.log"),
 ("0 failures", "tests/core/evidence/r2-fwcheck-1.log"),
 ("Version F7 part 1 (2026-11-11): rulings R1 to R8", "tests/core/evidence/r2-firmware-md.diff"),
 ("fail=28", "tests/core/broken/broken-long900.log"), ("fail=13", "tests/core/broken/broken-row12to.log"),
 ("FAIL generator.fresh_run_matches_committed_table", "tests/core/broken/broken-row12to.log"),
 ("fail=2", "tests/core/broken/broken-gap60.log"), ("fail=3", "tests/core/broken/broken-row27act.log"),
 ("fail=1", "tests/core/broken/broken-m15.log"), ("fail=1", "tests/core/broken/broken-m25.log"),
 ("fail=1", "tests/core/broken/broken-m29.log"), ("fail=1", "tests/core/broken/broken-m33.log"),
 ("fail=12", "tests/core/broken/broken-m09.log"), ("fail=0", "tests/core/broken/broken-m21.log"), ("fail=0", "tests/core/broken/broken-m23.log"),
 ("nrf54lm20bsim/nrf54lm20a/cpuapp", "tests/core/testcase.yaml"), ("## Round 2", "docs/core-notes.md"),
]:
    chk(s, f)
for m in ["long900", "row12to", "gap60", "row27act", "m15", "m25", "m29", "m33", "m09"]:
    chk("RESULT FAIL", f"tests/core/broken/broken-{m}.log")
n += 1; seg = "Segmentation" in T["tests/core/broken/broken-m09.log"]; bad += seg; print(("BAD " if seg else "OK  ") + "no crash in m09")
diff = T["tests/core/evidence/r2-firmware-md.diff"]
hunks = re.findall(r"^(\d+)(?:,\d+)?[acd]", diff, re.M)
n += 1; ok = all(int(h) == 3 or 91 <= int(h) <= 283 for h in hunks); bad += not ok
print(("OK  " if ok else "BAD ") + f"diff hunks at lines {hunks} are line 3 or in sections 1 and 2 (lines 91 to 283)")
for p in re.findall(r"`([a-z][\w./-]*/[\w./*-]+)`", reply):
    n += 1; c = glob.glob(os.path.join(FW, p)) + glob.glob(os.path.join(FW, "tests/core", p))
    bad += not c; print(("OK  " if c else "BAD ") + "path " + p)
nl = T["docs/core-notes.md"].strip().splitlines()[-1]
n += 1; ok = nl.startswith("RESULT: done"); bad += not ok; print(("OK  " if ok else "BAD ") + "notes last line RESULT")
n += 1; ok = len(reply) < 3500; bad += not ok; print(("OK  " if ok else "BAD ") + f"reply {len(reply)} chars")
print(f"claims checked={n} bad={bad}")
