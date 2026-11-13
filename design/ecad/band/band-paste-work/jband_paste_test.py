#!/usr/bin/env python3
"""Places J_BAND_A_BOARD and J_BAND_B_BOARD from a library on a scratch board (as the ring board does: X -2.250, Y -+4.325),
saves it, and lists pads and F.Paste shapes. usage: run_kipy.sh jband_paste_test.py <library.pretty> <out.kicad_pcb>"""
import sys
import pcbnew
from pcbnew import FromMM, VECTOR2I, ToMM

lib, out = sys.argv[1], sys.argv[2]
b = pcbnew.BOARD()
for name, y in (("J_BAND_A_BOARD", -4.325), ("J_BAND_B_BOARD", 4.325)):
    fp = pcbnew.FootprintLoad(lib, name)
    fp.SetReference(name[:8])
    fp.SetPosition(VECTOR2I(FromMM(100 - 2.25), FromMM(100 + y)))
    b.Add(fp)
    pads = [p for p in fp.Pads()]
    paste = [g for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.F_Paste]
    print(f"{name}: pads {len(pads)} numbers {sorted(p.GetNumber() for p in pads)}, F.Paste shapes {len(paste)}, "
          f"pads with F.Paste layer {sum(1 for p in pads if p.IsOnLayer(pcbnew.F_Paste))}")
    for p in sorted(pads, key=lambda p: p.GetNumber()):
        c = p.GetPosition()
        hit = [g for g in paste if abs(ToMM((g.GetStart().x + g.GetEnd().x) // 2 - c.x)) < 0.001 and abs(ToMM((g.GetStart().y + g.GetEnd().y) // 2 - c.y)) < 0.001]
        sz = [(round(abs(ToMM(g.GetEnd().x - g.GetStart().x)), 4), round(abs(ToMM(g.GetEnd().y - g.GetStart().y)), 4), g.IsSolidFill() if hasattr(g, "IsSolidFill") else g.GetFillMode()) for g in hit]
        print(f"  land {p.GetNumber()} centred openings {sz}")
pcbnew.SaveBoard(out, b)
print("saved", out)
