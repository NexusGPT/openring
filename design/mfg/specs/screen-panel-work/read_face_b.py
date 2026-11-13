"""Read only: the screen-face (B) parts of ring.kicad_pcb, their pads and nets, and tracks touching their pads.
Run: run_kipy.sh read_face_b.py <board> > logs/read_face_b.log 2>&1"""
import sys
import pcbnew
B = pcbnew.LoadBoard(sys.argv[1])
nets = {}
for fp in B.GetFootprints():
    if not fp.IsFlipped() or fp.GetReference().startswith("TP"):
        continue
    ref = fp.GetReference()
    pads = [(p.GetNumber(), p.GetNetname()) for p in fp.Pads()]
    print(f"{ref} {fp.GetFPIDAsString()} pads: {' '.join(f'{n}={net or None}' for n, net in pads)}")
    for n, net in pads:
        if net and ref != "J1":
            nets.setdefault(net, set()).add(ref)
print(f"nets of the eight 0201 parts: {len(nets)}: " + "; ".join(f"{k} ({', '.join(sorted(v))})" for k, v in sorted(nets.items())))
tp = [fp.GetReference() for fp in B.GetFootprints() if fp.IsFlipped() and fp.GetReference().startswith("TP")]
print(f"flat test pads on the screen face: {len(tp)}")
print("RESULT read_face_b done")
