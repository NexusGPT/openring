# jobs_from_drc.py drc.json [skipnet,...] : hand.py jobs (NET sx sy layer tx ty) for every unconnected pair except GND / skipped
import json, sys, re
d = json.load(open(sys.argv[1])); skip = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
LN = {"F.Cu": "F", "In1.Cu": "In1", "In2.Cu": "In2", "B.Cu": "B"}
out = []
for u in d["unconnected_items"]:
    a, b = u["items"][0], u["items"][1]
    m = re.search(r"\[([^\]]+)\]", a["description"]); n = m.group(1) if m else None
    if not n or n == "GND" or n in skip: continue
    la = LN[re.search(r"on ([A-Za-z0-9.]+)", a["description"]).group(1)]
    out += [n, "%.3f" % (a["pos"]["x"] - 100), "%.3f" % (a["pos"]["y"] - 100), la, "%.3f" % (b["pos"]["x"] - 100), "%.3f" % (b["pos"]["y"] - 100)]
print(" ".join(out))
