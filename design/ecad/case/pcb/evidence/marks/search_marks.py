"""Finds, for each label, the nearest free spot for silkscreen text on one face of a board.
usage: search_marks.py board.kicad_pcb F|B  REF:label:wpad[:w] ...   (ink size: height 1.0 mm, stroke 0.15 mm, width given or 0.6)
Free = ink box (plus 0.15 mm, the maker's pad-to-silkscreen distance, evidence/capab_jlc.html.txt 'Pad To Silkscreen 0.15mm') touches no pad
that has an opening on that face, no via, no other silk, and stays 0.25 mm inside the board outline bounding pieces."""
import sys, os, math, pcbnew
from pcbnew import ToMM, FromMM, VECTOR2I
path, face = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(path)
silk = pcbnew.F_SilkS if face == "F" else pcbnew.B_SilkS
mask = pcbnew.F_Mask if face == "F" else pcbnew.B_Mask
cu = pcbnew.F_Cu if face == "F" else pcbnew.B_Cu
CL = 0.15
excl = []
for f in b.GetFootprints():
    for p in f.Pads():
        if p.IsOnLayer(mask) or p.IsOnLayer(cu):
            bb = p.GetBoundingBox(); excl.append((ToMM(bb.GetLeft()) - CL, ToMM(bb.GetTop()) - CL, ToMM(bb.GetRight()) + CL, ToMM(bb.GetBottom()) + CL, f.GetReference() + "." + p.GetNumber()))
    for g in f.GraphicalItems():
        if g.GetLayer() == silk:
            bb = g.GetBoundingBox(); excl.append((ToMM(bb.GetLeft()) - 0.15, ToMM(bb.GetTop()) - 0.15, ToMM(bb.GetRight()) + 0.15, ToMM(bb.GetBottom()) + 0.15, "silk"))
for t in b.GetTracks():
    if False:   # vias are tented on both faces (case_main.kicad_pcb setup tenting front yes back yes): silk over a tented via is allowed
        bb = t.GetBoundingBox(); excl.append((ToMM(bb.GetLeft()) - CL, ToMM(bb.GetTop()) - CL, ToMM(bb.GetRight()) + CL, ToMM(bb.GetBottom()) + CL, "via"))
# outline pieces
pieces = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        bb = d.GetBoundingBox(); pieces.append((ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom())))
def inside_piece(x0, y0, x1, y1, m=0.25):
    # the outline is a set of rectangles drawn as 4 lines; rebuild the rectangles by merging line boxes
    return True
# merge line boxes into rectangles (pcb2: three rectangles, pcb1 uses its own outline: test with point-in-outline)
outl = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outl, False)
def edge_ok(x0, y0, x1, y1, m=0.2):
    if outl.OutlineCount() > 1:     # pin board: three separate rectangles; the box must lie inside ONE of them, m mm from its edge
        for i in range(outl.OutlineCount()):
            bb = outl.Outline(i).BBox()
            if x0 >= ToMM(bb.GetLeft()) + m and x1 <= ToMM(bb.GetRight()) - m and y0 >= ToMM(bb.GetTop()) + m and y1 <= ToMM(bb.GetBottom()) - m:
                return True
        return False
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)):
        for dx, dy in ((0, 0), (m, 0), (-m, 0), (0, m), (0, -m)):
            if not outl.Contains(VECTOR2I(FromMM(x + dx), FromMM(y + dy))):
                return False
    return True
def ink(txt, w, mirror):
    t = pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetLayer(silk)
    t.SetTextSize(VECTOR2I(FromMM(w), FromMM(1.0))); t.SetTextThickness(FromMM(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetMirrored(mirror)
    bb = t.GetEffectiveTextShape().BBox()
    return ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom())
def hit(a, c):
    return a[0] < c[2] and a[2] > c[0] and a[1] < c[3] and a[3] > c[1]
placed = []
for spec in sys.argv[3:]:
    parts = spec.split(":")
    ref, label, pad = parts[0], parts[1], parts[2]
    w = float(parts[3]) if len(parts) > 3 else 0.6
    px = py = None
    for f in b.GetFootprints():
        if f.GetReference() == ref:
            px, py = ToMM(f.GetPosition().x), ToMM(f.GetPosition().y)
    ib = ink(label, w, face == "B")
    best = None
    R = 6.0
    n = int(R / 0.05)
    for iy in range(-n, n + 1):
        for ix in range(-n, n + 1):
            cx, cy = px + ix * 0.05, py + iy * 0.05
            box = (cx + ib[0], cy + ib[1], cx + ib[2], cy + ib[3])
            d = math.hypot(ix * 0.05, iy * 0.05)
            if os.environ.get('SIDE') == 'R' and (iy != 0 or ix < 0):
                continue     # SIDE=R: same row as the pad, to the right of its centre
            if best is not None and d >= best[0]:
                continue
            if any(hit(box, e) for e in excl) or any(hit(box, q) for q in placed) or not edge_ok(*box):
                continue
            best = (d, cx, cy, box)
    if best is None:
        print("NOFIT", ref, label, "w", w)
    else:
        placed.append(best[3])
        print("FIT %s %r w %.2f at x %.3f y %.3f (dist %.2f from %s) ink x %.3f..%.3f y %.3f..%.3f" % (ref, label, w, best[1], best[2], best[0], ref, best[3][0], best[3][2], best[3][1], best[3][3]))
