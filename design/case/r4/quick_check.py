"""Debug run (not the proof): on a build folder (CASE_OUT), the pairs of test 1 that involve a part r4 added or changed, test 5, and case_check's
new tests 15 and 16 (and 17 when given 'lift'). usage: CASE_OUT=<folder> python quick_check.py [lift]"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402
import case_check as K  # noqa: E402
from build123d import import_step  # noqa: E402

OUT = C.OUT
prm = json.load(open(os.path.join(OUT, "case_params.json")))
K.OUT = OUT
parts = {n: import_step(os.path.join(OUT, "parts", f"{n}.step")) for n in prm["parts"]}
print("parts:", len(parts), sorted(parts))
print("main_board children:", [c.label for c in parts["main_board"].children][:80])
new = {"main_board", "foam_pad", "insulation_sheet", "board_retainer", "TH1_bead", "pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R",
       "pin_holder", "shell", "post", "liner"} | {k for k in parts if k.startswith("lead_")}
rings = {9: C.Ring(9)}
r9 = rings[9].parts_in_case(prm["zb"])
allp = dict(parts)
allp.update({f"ring_US9_{k}": v for k, v in r9.items() if k != "pads"})
bad = 0
for a, b in itertools.combinations(sorted(allp), 2):
    if a.startswith("ring_") and b.startswith("ring_"):
        continue
    if a not in new and b not in new:
        continue
    v = C.common(allp[a], allp[b])
    if not (v <= K.LIMIT):
        bad += 1
        print(f"INTERSECT {a} x {b}: {v:.4f} mm3")
print("intersections among pairs with a new or changed part:", bad)
walls = [parts["shell"], parts["base_plate"]]
kids = {c.label: c for c in parts["main_board"].children}
for k, s in (("cell", parts["cell_dnk852338"]), ("main_board", parts["main_board"]), ("J1", kids.get("J1")), ("LED1", kids.get("LED1"))):
    print(f"test5 {k}: distance to shell walls {min(s.distance_to(w) for w in walls):.3f}")
K.test15_boards(parts, prm)
K.test16_leads(parts, prm)
if len(sys.argv) > 1 and sys.argv[1] == "lift":
    rings = {n: C.Ring(n) for n in prm["sizes"]}
    K.test17_lift(parts, prm, rings)
print("quick_check failures counted by case_check functions:", K.fails)
