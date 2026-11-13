#!/usr/bin/env python3
"""Dump every item of the 14 band boards to a text file per board, in classes, sorted.
usage: run_kipy.sh dump_boards.py <board folder> <out folder> [names ...]
Classes: PAD (copper, net, position, size, shape, layers incl. paste), TRACK, VIA, EDGE, DRAW (other graphics), TEXT, FPTEXT."""
import os, sys
import pcbnew
from pcbnew import ToMM

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
names = sys.argv[3:] or [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]


def r(v):
    return f"{ToMM(v):.4f}"


for n in names:
    b = pcbnew.LoadBoard(os.path.join(src, n + ".kicad_pcb"))
    rows = []
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        rows.append(f"FP {ref} {fp.GetFPID().GetLibItemName()} at {r(fp.GetPosition().x)} {r(fp.GetPosition().y)} rot {fp.GetOrientationDegrees():.1f} side {b.GetLayerName(fp.GetLayer())}")
        for p in fp.Pads():
            ls = ",".join(sorted(b.GetLayerName(l) for l in p.GetLayerSet().Seq()))
            cu = ",".join(sorted(b.GetLayerName(l) for l in p.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)))
            rows.append(f"PAD {ref}.{p.GetNumber()} net {p.GetNetname()} at {r(p.GetPosition().x)} {r(p.GetPosition().y)} size {r(p.GetSize(pcbnew.F_Cu).x)} {r(p.GetSize(pcbnew.F_Cu).y)} shape {p.GetShape()} cu {cu} attr {p.GetAttribute()}")
            rows.append(f"PADLAYERS {ref}.{p.GetNumber()} at {r(p.GetPosition().x)} {r(p.GetPosition().y)} layers {ls}")
        for g in fp.GraphicalItems():
            if isinstance(g, pcbnew.PCB_TEXT):
                rows.append(f"FPTEXT {ref} {b.GetLayerName(g.GetLayer())} {g.GetText()!r}")
            else:
                rows.append(f"FPDRAW {ref} {b.GetLayerName(g.GetLayer())} {g.GetShape()} {r(g.GetStart().x)} {r(g.GetStart().y)} {r(g.GetEnd().x)} {r(g.GetEnd().y)}")
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            rows.append(f"VIA net {t.GetNetname()} at {r(t.GetPosition().x)} {r(t.GetPosition().y)} d {r(t.GetWidth(pcbnew.F_Cu))} drill {r(t.GetDrill())}")
        else:
            rows.append(f"TRACK {b.GetLayerName(t.GetLayer())} net {t.GetNetname()} {r(t.GetStart().x)} {r(t.GetStart().y)} {r(t.GetEnd().x)} {r(t.GetEnd().y)} w {r(t.GetWidth())}")
    for d in b.GetDrawings():
        ly = b.GetLayerName(d.GetLayer())
        if isinstance(d, pcbnew.PCB_TEXT):
            rows.append(f"TEXT {ly} at {r(d.GetPosition().x)} {r(d.GetPosition().y)} h {r(d.GetTextHeight())} {d.GetText()!r}")
        elif d.GetClass().startswith("PCB_DIM"):
            rows.append(f"DIM {ly} {r(d.GetStart().x)} {r(d.GetStart().y)} {r(d.GetEnd().x)} {r(d.GetEnd().y)}")
        else:
            kind = "EDGE" if ly == "Edge.Cuts" else "DRAW"
            rows.append(f"{kind} {ly} shape {d.GetShape()} {r(d.GetStart().x)} {r(d.GetStart().y)} {r(d.GetEnd().x)} {r(d.GetEnd().y)} w {r(d.GetWidth())}")
    rows.append(f"NETS {sorted(str(k) for k in b.GetNetsByName().keys())}")
    with open(os.path.join(out, n + ".dump"), "w") as f:
        f.write("\n".join(sorted(rows)) + "\n")
    print(n, len(rows))
print("dumped", len(names))
