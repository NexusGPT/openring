#!/usr/bin/env python3
"""import_route.py board.kicad_pcb route.ses out.kicad_pcb -- plan step g.8: imports the router's session into the board
with the scripted copper and refills every zone. Prints counts. Run with ./run_kipy.sh."""
import sys
import pcbnew
from pcbnew import FromMM, ToMM

src, ses, out = sys.argv[1:4]
b = pcbnew.LoadBoard(src)
n0 = len(b.GetTracks())
ok = pcbnew.ImportSpecctraSES(b, ses)
print("import ok:", ok, "items before", n0, "after", len(b.GetTracks()))

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
pcbnew.SaveBoard(out, b)
tr = list(b.GetTracks())
vias = [t for t in tr if t.Type() == pcbnew.PCB_VIA_T]
span = {}
for v in vias:
    k = b.GetLayerName(v.TopLayer()) + "-" + b.GetLayerName(v.BottomLayer())
    span[k] = span.get(k, 0) + 1
lay = {}
for t in tr:
    if t.Type() != pcbnew.PCB_VIA_T:
        k = b.GetLayerName(t.GetLayer()); lay[k] = lay.get(k, 0) + 1
print("track segments", len(tr) - len(vias), dict(sorted(lay.items())), "vias", len(vias), dict(sorted(span.items())), "zones", len(list(b.Zones())))
