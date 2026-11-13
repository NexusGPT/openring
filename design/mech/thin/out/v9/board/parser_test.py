#!/usr/bin/env python3
"""The check's own footprint reader (check_thin.py section 14, _fp_read and _turn, copied by text from out/v9/dev/check_thin.py) against fp_read.py's board_rows.json."""
import json, math, re, sys
from pathlib import Path
src = open((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin/out/v9/dev/check_thin.py")).read()
a = src.index("PLAN_CSV = Path("); b = src.index("def check_board_plan(")
ns = {"Path": Path, "math": math}
exec(src[a:b], ns)
rows = json.load(open("board_rows.json"))
bad = 0
for ref, r in rows.items():
    fp = ns["_fp_read"](r["footprint"])
    same_fab = all(abs(u - v) < 1e-9 for u, v in zip(fp["fab"], r["fab_local"]))
    same_pads = len(fp["pads"]) == len(r["pads"])
    print(f"{ref}: fab {fp['fab']} same as fp_read {same_fab}; pads {len(fp['pads'])} (fp_read {len(r['pads'])}); descr height {fp['height']}")
    bad += (not same_fab) + (not same_pads)
print(f"differences: {bad}")
