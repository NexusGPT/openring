import json, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work"))
from runlib import *
man = json.load(open(W + "/copies/cw/manifest.json"))
# The live list was rebuilt by the lead on 2026-11-13 with the fixed generator (no carriage return left), so it must pass now.
# The copy with the carriage returns stays as the case rev_honest_copy below.
man.append({"name": "LIVE_list_as_it_stands", "csv": ROOT + "/design/wiring/product-wiring.csv", "want_exit": 0, "want_tag": None, "want_id": None})
RV = ROOT + "/design/wiring/review4-work/fakes-cw/"
for nm, f, tag, i in [("rev_honest_copy(has the CRs)", "honest", "field-newline", "W054"), ("rev_wrongnet", "wrongnet", "states-net", "W001"),
        ("rev_wrongtail", "wrongtail", "states-tail", "W001"), ("rev_wrongface_W040", "wrongface", "states-face", "W040"),
        ("rev_wrongface_W029", "wrongface", "states-face", "W029"), ("rev_colourswap", "colourswap", "states-colour", "W023"),
        ("rev_cutwrong", "cutwrong", "states-cut", "W023"), ("rev_empty", "empty", None, None), ("rev_flood", "flood", None, None),
        ("rev_oneline", "oneline", None, None), ("rev_nomark", "nomark", None, None), ("rev_nocut", "nocut", None, None),
        ("rev_swapB", "swapB", None, None), ("rev_springswap", "springswap", None, None), ("rev_wireswap", "wireswap", None, None),
        ("rev_prooffake", "prooffake", None, None), ("rev_dropped", "dropped", None, None)]:
    man.append({"name": nm, "csv": RV + f + ".csv", "want_exit": 1, "want_tag": tag, "want_id": i})
CHK = ROOT + "/design/wiring/check_wiring.py"
n_ok, n = run_cases("check_wiring", lambda c: [PY, CHK, "--require-complete", "--csv", c["csv"]], man, W + "/logs/cw")
print("SECTION check_wiring ok=%d of %d" % (n_ok, n))
