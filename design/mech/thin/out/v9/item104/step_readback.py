#!/usr/bin/env python3
"""Item 104, side B (a fresh process): read a STEP file back (arg 1) and compare, per label <part>__<class>, its solid count and volume with the model
figures of side A (json, arg 2). Prints one line per label and 'RESULT PASS labels=<n>' or 'RESULT FAIL ...'; exit 0 / 1. Volume rule 0.01 mm3."""
import json, sys
from build123d import import_step
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp


def pvol(s):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s.wrapped, g, 1e-7)
    return g.Mass()


st = import_step(sys.argv[1])
want = json.load(open(sys.argv[2]))["labels"]
got = {}
def walk(node):
    lab = getattr(node, "label", "")
    if lab in want:
        sols = node.solids()
        got[lab] = dict(solids=len(sols), volume=sum(pvol(x) for x in sols))
        return
    for c in getattr(node, "children", []) or []:
        walk(c)
walk(st)
bad = 0
for lab, w in want.items():
    g = got.get(lab)
    if g is None:
        print(f"{lab}: model {w['solids']} solids {w['volume']:.4f} mm3; STEP: label not found  DIFFERS")
        bad += 1
        continue
    ok = g["solids"] == w["solids"] and abs(g["volume"] - w["volume"]) <= 0.01
    bad += not ok
    print(f"{lab}: model {w['solids']} solids {w['volume']:.4f} mm3; STEP {g['solids']} solids {g['volume']:.4f} mm3; difference {g['volume'] - w['volume']:+.4f}{'' if ok else '  DIFFERS'}")
extra = sorted(set(got) - set(want))
tot = len(st.solids())
print(f"STEP {sys.argv[1]}: {tot} solids in the file, {sum(w['solids'] for w in want.values())} in the model; labels compared {len(want)}, differing {bad}, labels not in the model {extra}")
print(f"RESULT {'FAIL' if bad or tot != sum(w['solids'] for w in want.values()) else 'PASS'} labels={len(want)}")
sys.exit(1 if bad else 0)
