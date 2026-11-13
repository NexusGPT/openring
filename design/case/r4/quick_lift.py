"""Debug run (not the proof): case_check's test 17 on one build folder (CASE_OUT) for the sizes given. usage: CASE_OUT=<folder> python quick_lift.py 7 [13 ...]"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402
import case_check as K  # noqa: E402
from build123d import import_step  # noqa: E402

prm = json.load(open(os.path.join(C.OUT, "case_params.json")))
prm["sizes"] = [int(a) for a in sys.argv[1:]]
parts = {n: import_step(os.path.join(C.OUT, "parts", f"{n}.step")) for n in prm["parts"]}
rings = {n: C.Ring(n) for n in prm["sizes"]}
t0 = time.time()
K.test17_lift(parts, prm, rings)
print("quick_lift: sizes %s, %.0f s, failures %d" % (prm["sizes"], time.time() - t0, K.fails))
