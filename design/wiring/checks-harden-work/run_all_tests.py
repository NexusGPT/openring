# Runs every test of the three hardened checks and the check_board option, then the existing joint-table tests; prints the total.
import re, subprocess, sys
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = ROOT + "/design/wiring/checks-harden-work"
PY = ROOT + "/design/.venv/bin/python"
tot_ok = tot = 0
for name, cmd in [("check_wiring", [PY, "-B", W + "/run_cw.py"]), ("check_joints", [PY, "-B", W + "/run_cj.py"]),
                  ("check_assembly", [PY, "-B", W + "/run_ca.py"]), ("check_board", [PY, "-B", W + "/run_board.py"]),
                  ("joint-table tests (existing)", [PY, "-B", ROOT + "/design/mfg/assembly/joint-table-work/tests/run_tests.py"])]:
    r = subprocess.run(["nice", "-n", "19"] + cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    open(W + "/logs/all-" + re.sub(r"\W+", "_", name) + ".log", "w").write(out)
    m = re.search(r"SECTION \S+ ok=(\d+) of (\d+)", out) or re.search(r"TESTS PASS (\d+) of (\d+)", out)
    a, b = (int(m.group(1)), int(m.group(2))) if m else (0, 1)
    print("SECTION %-30s %d of %d  (%s)" % (name, a, b, "ok" if a == b else "DIFFERS"), flush=True)
    tot_ok += a; tot += b
print("TESTS %s %d of %d as expected" % ("PASS" if tot_ok == tot else "FAIL", tot_ok, tot))
