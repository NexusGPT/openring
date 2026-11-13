#!/usr/bin/env python3
"""Item 104, side A: build the model in memory (thin.py of the folder given as arg 1, with the env of the caller) and write, per part and class,
the solid count and volume (tight integration) of the part's own sub-solid list, to the json file arg 2. Writes nothing else."""
import json, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import thin  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402


def pvol(s):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s.wrapped, g, 1e-7)
    return g.Mass()


m = thin.build()
out = {}
for p in m["parts"]:
    for cls, lst in p.subs.items():
        sols = [x for s in lst for x in s.solids()]
        out[f"{p.name}__{cls}"] = dict(solids=len(sols), volume=sum(pvol(x) for x in sols))
json.dump(dict(thin=thin.__file__, exterior=thin.EXT_FILE, bore=thin.P["bore_d"], parts=len(m["parts"]), labels=out), open(sys.argv[2], "w"), indent=1)
print(f"model in memory: {thin.__file__}, {len(m['parts'])} parts, {len(out)} part classes, {sum(v['solids'] for v in out.values())} solids; wrote {sys.argv[2]}")
