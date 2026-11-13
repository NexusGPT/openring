"""Dump what the hot-bar study needs from copies of the board files (run with KiCad's Python via run_kipy.sh).
usage: run_kipy.sh dump_boards.py <out_dir> <board.kicad_pcb> [...]
ring board: every footprint (ref, side, centre, rotation, body box from F/B.Fab or courtyard or pads), every J_BAND pad with its layers.
band board: outline box, stiffener shapes (User.1), the 15 foot lands, vias, the Dwgs.User text.
"""
import sys, os, pcbnew

out_dir = sys.argv[1]
MM = 1e6


def mm(v):
    return v / MM


def bbox_of_layer(fp, layer_names):
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetLayerName() in layer_names:
            b = it.GetBoundingBox()
            xs += [mm(b.GetLeft()), mm(b.GetRight())]
            ys += [mm(b.GetTop()), mm(b.GetBottom())]
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys)


for path in sys.argv[2:]:
    name = os.path.basename(path).replace(".kicad_pcb", "")
    b = pcbnew.LoadBoard(path)
    lines = [f"file {path}"]
    if name == "ring":
        lines.append("ref,side,x,y,rot,box_src,x0,x1,y0,y1")
        for fp in b.GetFootprints():
            side = "F" if fp.GetLayer() == pcbnew.F_Cu else "B"
            p = fp.GetPosition()
            box, src = None, ""
            for src_try, lay in (("fab", ("F.Fab", "B.Fab")), ("courtyard", ("F.Courtyard", "B.Courtyard"))):
                box = bbox_of_layer(fp, lay)
                if box:
                    src = src_try
                    break
            if not box:
                xs, ys = [], []
                for pad in fp.Pads():
                    bb = pad.GetBoundingBox()
                    xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
                    ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
                box = (min(xs), max(xs), min(ys), max(ys)) if xs else (0, 0, 0, 0)
                src = "pads"
            lines.append(f"{fp.GetReference()},{side},{mm(p.x):.4f},{mm(p.y):.4f},{fp.GetOrientationDegrees():.1f},{src},"
                         f"{box[0]:.4f},{box[1]:.4f},{box[2]:.4f},{box[3]:.4f}")
        lines.append("pads of J_BAND_A, J_BAND_B: ref,pad,net,x,y,sx,sy,layers")
        for fp in b.GetFootprints():
            if fp.GetReference() in ("J_BAND_A", "J_BAND_B"):
                for pad in fp.Pads():
                    c = pad.GetPosition()
                    s = pad.GetSize()
                    lays = [b.GetLayerName(l) for l in pad.GetLayerSet().Seq()]
                    lines.append(f"{fp.GetReference()},{pad.GetNumber()},{pad.GetNetname()},{mm(c.x):.4f},{mm(c.y):.4f},"
                                 f"{mm(s.x):.3f},{mm(s.y):.3f},{'|'.join(lays)}")
        lines.append("board outline (Edge.Cuts) box:")
        xs, ys = [], []
        for d in b.GetDrawings():
            if d.GetLayerName() == "Edge.Cuts":
                bb = d.GetBoundingBox()
                xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
                ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
        lines.append(f"edge x {min(xs):.4f} {max(xs):.4f} y {min(ys):.4f} {max(ys):.4f}")
    else:
        xs, ys = [], []
        per = 0.0
        for d in b.GetDrawings():
            ln = d.GetLayerName()
            bb = d.GetBoundingBox()
            if ln == "Edge.Cuts":
                xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
                ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
                s, e = d.GetStart(), d.GetEnd()
                lines.append(f"edge {d.GetShapeStr()} {mm(s.x):.4f},{mm(s.y):.4f} -> {mm(e.x):.4f},{mm(e.y):.4f} w {mm(d.GetWidth()):.3f}")
                try:
                    per += mm(d.GetLength())
                except Exception:
                    pass
            elif ln in ("User.1", "Dwgs.User"):
                if d.GetClass() in ("PCB_TEXT", "PTEXT"):
                    lines.append(f"{ln} text at ({mm(d.GetPosition().x):.3f},{mm(d.GetPosition().y):.3f}): {d.GetText()!r}")
                else:
                    lines.append(f"{ln} shape {d.GetShapeStr() if hasattr(d, 'GetShapeStr') else d.GetClass()} box x {mm(bb.GetLeft()):.4f} {mm(bb.GetRight()):.4f} y {mm(bb.GetTop()):.4f} {mm(bb.GetBottom()):.4f}")
        lines.append(f"edge box x {min(xs):.4f} {max(xs):.4f} y {min(ys):.4f} {max(ys):.4f} outline_perimeter {per:.4f}")
        # width of the outline at given x positions (scan the Edge.Cuts segments)
        for fp in b.GetFootprints():
            for pad in fp.Pads():
                c = pad.GetPosition()
                s = pad.GetSize()
                lays = [b.GetLayerName(l) for l in pad.GetLayerSet().Seq()]
                lines.append(f"pad {fp.GetReference()},{fp.GetFPID().GetLibItemName()},{pad.GetNumber()},{pad.GetNetname()},{mm(c.x):.4f},{mm(c.y):.4f},{mm(s.x):.3f},{mm(s.y):.3f},{'|'.join(lays)}")
        for t in b.GetTracks():
            if t.GetClass() == "PCB_VIA":
                c = t.GetPosition()
                lines.append(f"via {mm(c.x):.4f},{mm(c.y):.4f},{t.GetNetname()}")
    with open(os.path.join(out_dir, name + "-dump.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(name, len(lines), "lines")
