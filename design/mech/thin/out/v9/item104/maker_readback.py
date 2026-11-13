#!/usr/bin/env python3
"""Item 104 for the regenerated maker files: a fresh process reads every STEP file listed in out/v9/export/rows_usN.json and compares its solid count
and volume (tight integration) with the model's own figures that the exporter recorded from the model in memory (model_solids, model_volume).
Prints one line per file and 'RESULT PASS files=<n>' or 'RESULT FAIL ...'; exit 0 / 1. Volume rule 0.01 mm3."""
import glob, json, os, sys
from build123d import import_step
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
DESIGN = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design")
OUTD = os.path.join(DESIGN, "mech/thin/out/v9/export")


def pvol(s):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s.wrapped, g, 1e-7)
    return g.Mass()


n = bad = 0
for f in sorted(glob.glob(os.path.join(OUTD, "rows_us*.json"))):
    for r in json.load(open(f)):
        if r.get("format") != "STEP" or "model_solids" not in r:
            continue
        n += 1
        st = import_step(os.path.join(DESIGN, r["path"]))
        sols = st.solids()
        v = sum(pvol(x) for x in sols)
        ok = len(sols) == r["model_solids"] and abs(v - r["model_volume"]) <= 0.01
        bad += not ok
        print(f"{r['path']}: model {r['model_solids']} solids {r['model_volume']:.4f} mm3; file {len(sols)} solids {v:.4f} mm3; difference {v - r['model_volume']:+.4f}{'' if ok else '  DIFFERS'}", flush=True)
print(f"files compared {n}, differing {bad}")
print(f"RESULT {'FAIL' if bad or n == 0 else 'PASS'} files={n}")
sys.exit(1 if bad or n == 0 else 0)
