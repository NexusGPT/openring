"""Dump every pad of the board copies in boards/ to pads/<board>-pads.csv.
Run with design/ecad/ring/pcb/run_kipy.sh (KiCad's own Python). Reads only the copies."""
import csv, glob, os, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pads")
os.makedirs(OUT, exist_ok=True)
for path in sorted(glob.glob(os.path.join(HERE, "boards", "*.kicad_pcb"))):
    name = os.path.basename(path)[:-len(".kicad_pcb")]
    b = pcbnew.LoadBoard(path)
    rows = []
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        for p in fp.Pads():
            ls = p.GetLayerSet()
            layers = [b.GetLayerName(l) for l in ls.Seq()]
            pos = p.GetPosition()
            sz = p.GetSize()
            rows.append(dict(board=name, ref=ref, pad=p.GetNumber(), net=p.GetNetname(),
                             x_mm="%.4f" % pcbnew.ToMM(pos.x), y_mm="%.4f" % pcbnew.ToMM(pos.y),
                             w_mm="%.4f" % pcbnew.ToMM(sz.x), h_mm="%.4f" % pcbnew.ToMM(sz.y),
                             attr={0: "PTH", 1: "SMD", 2: "CONN", 3: "NPTH"}.get(p.GetAttribute(), str(p.GetAttribute())),
                             fp_side="B" if fp.IsFlipped() else "F",
                             fp_name=str(fp.GetFPID().GetLibItemName()),
                             layers=" ".join(layers)))
    with open(os.path.join(OUT, name + "-pads.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(name, "pads", len(rows))
