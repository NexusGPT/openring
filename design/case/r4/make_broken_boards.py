"""Broken copies of the main board for check tests 15 to 17 (run with KiCad's Python; the real board files are only read).
usage: run_kipy.sh make_broken_boards.py <case_main.kicad_pcb> <out_dir>
Writes <out_dir>/board_long/case_main.kicad_pcb: the board 1 mm longer at its socket end (the two outline corners at KiCad y = min y move 1 mm to -y,
       i.e. 1 mm toward case +y);
       <out_dir>/part_tall/case_main.kicad_pcb: the socket J1 1 mm taller (its 3D model scaled in z by (h + 1) / h, h = 3.31 mm, USB4105 drawing p.1)."""
import os
import sys

import pcbnew

src, out = sys.argv[1], sys.argv[2]
FromMM, ToMM = pcbnew.FromMM, pcbnew.ToMM
SRC_DIR = os.path.dirname(os.path.abspath(src))


def fix_paths(board):
    """the copy lives in another folder: ${KIPRJMOD} model paths point back to the original board's folder (only in the copy)"""
    n = 0
    for fp in board.GetFootprints():
        for m in fp.Models():
            if "${KIPRJMOD}" in m.m_Filename:
                m.m_Filename = m.m_Filename.replace("${KIPRJMOD}", SRC_DIR)
                n += 1
    return n

# board 1 mm longer
b = pcbnew.LoadBoard(src)
ys = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        ys += [d.GetStart().y, d.GetEnd().y]
ymin = min(ys)
moved = 0
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        if s.y == ymin:
            d.SetStart(pcbnew.VECTOR2I(s.x, s.y - FromMM(1.0)))
            moved += 1
        if e.y == ymin:
            d.SetEnd(pcbnew.VECTOR2I(e.x, e.y - FromMM(1.0)))
            moved += 1
print("board_long: model paths made absolute:", fix_paths(b))
os.makedirs(os.path.join(out, "board_long"), exist_ok=True)
p1 = os.path.join(out, "board_long", "case_main.kicad_pcb")
pcbnew.SaveBoard(p1, b)
print("board_long: outline end points at KiCad y %.3f moved 1.0 mm to y %.3f: %d end points -> %s" % (ToMM(ymin), ToMM(ymin) - 1.0, moved, p1))

# J1 1 mm taller
b = pcbnew.LoadBoard(src)
f = [x for x in b.GetFootprints() if x.GetReference() == "J1"][0]
h = 3.31
for m in f.Models():
    m.m_Scale.z = (h + 1.0) / h
print("part_tall: model paths made absolute:", fix_paths(b))
os.makedirs(os.path.join(out, "part_tall"), exist_ok=True)
p2 = os.path.join(out, "part_tall", "case_main.kicad_pcb")
pcbnew.SaveBoard(p2, b)
print("part_tall: J1 model scale z %.4f (height %.2f -> %.2f mm) -> %s" % ((h + 1.0) / h, h, h + 1.0, p2))
