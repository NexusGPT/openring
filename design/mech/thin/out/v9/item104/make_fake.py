#!/usr/bin/env python3
"""Broken copy for the item 104 read-back: the v9 thin-inside.step with ONE solid left out (one solder ball of main_chip__metal); writes fake_missing_ball.step here."""
import sys
from build123d import import_step, export_step, Compound, Solid
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
st = import_step(sys.argv[1])
kids = []
dropped = None
def walk(node):
    global dropped
    lab = getattr(node, "label", "")
    if "__" in lab:
        sols = [Solid(BRepBuilderAPI_Copy(x.wrapped).Shape()) for x in node.solids()]
        if lab == "main_chip__metal" and dropped is None:
            dropped = len(sols)
            sols = sols[1:]
        c = Compound(children=sols) if len(sols) != 1 else sols[0]
        c.label = lab
        kids.append(c)
        return
    for c in getattr(node, "children", []) or []:
        walk(c)
walk(st)
export_step(Compound(children=kids, label="thin_ring_inside"), sys.argv[2])
print(f"labels {len(kids)}; main_chip__metal had {dropped} solids, written with {dropped - 1}; file {sys.argv[2]}")
