import json, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work"))
from runlib import *
man = json.load(open(W + "/copies/cj/manifest.json"))
RV = ROOT + "/design/wiring/review4-work/fakes-cj/"
# the reviewer's own fake files (made from the table as it stood in review 4); each must still exit 1; the honest copy is run for its result only
for nm, f in [("rev_checkempty", "checkempty"), ("rev_checkok_file", "checkok"), ("rev_heatok_file", "heatok"), ("rev_dropped", "dropped"), ("rev_empty", "empty"),
              ("rev_flood", "flood"), ("rev_gap", "gap"), ("rev_stepbad", "stepbad"), ("rev_brokenpaste", "brokenpaste"), ("rev_nofile", "nofile")]:
    tag = {"rev_checkok_file": "R6 weak-check", "rev_heatok_file": "R7 weak-heat"}.get(nm)
    man.append({"name": nm, "csv": RV + f + ".csv", "want_exit": 1, "want_tag": tag, "want_id": None})
CHK = ROOT + "/design/mfg/assembly/check_joints.py"
n_ok, n = run_cases("check_joints", lambda c: [PY, "-B", CHK, "--joints", c["csv"]], man, W + "/logs/cj")
print("SECTION check_joints ok=%d of %d" % (n_ok, n))
