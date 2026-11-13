"""print what board_read.py found (outline, every footprint with side, place, model and courtyard). usage: inspect_boards.py <dir with main.json pins.json>"""
import json
import os
import sys

D = sys.argv[1]
for t in ("main", "pins"):
    d = json.load(open(os.path.join(D, "%s.json" % t)))
    print(t, "thickness", d["thickness"], "kicad", d["kicad"])
    for o in d["outlines"]:
        xs, ys = [p[0] for p in o], [p[1] for p in o]
        print(" outline", len(o), "points, x %.3f..%.3f y %.3f..%.3f" % (min(xs), max(xs), min(ys), max(ys)), [(round(x, 3), round(y, 3)) for x, y in o])
    nb = 0
    for f in d["footprints"]:
        nb += f["side"] == "B"
        print(" ", f["ref"], f["side"], round(f["x"], 3), round(f["y"], 3), f["rot"],
              [(m["file"].split("/")[-1], m["offset"], m["rot"], m["scale"], m["show"]) for m in f["models"]],
              f["courtyard"] and [round(v, 2) for v in f["courtyard"]], "pads", len(f["pads"]),
              "front" if all(p["front"] for p in f["pads"]) else ("back" if all(p["back"] and not p["front"] for p in f["pads"]) else "mixed/th"))
    print(t, "footprints on the back side:", nb)
