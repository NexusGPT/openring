# j1_rot.py: J1 footprint flipped to the screen face at (-4.933, -0.003) for each rotation: where the 0.8 mm row (contact 1
# side, the FPC entry) and the courtyard lie
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
lib = (__import__("pathlib").Path(__file__).resolve().parents[7].as_posix() + "/design/ecad/ring/pcb/OpenRing.pretty")
for rot in (0, 90, 180, 270):
    b = pcbnew.BOARD(); fp = pcbnew.FootprintLoad(lib, 'FPC_Hirose_FH35C-15S-0.3SHW'); b.Add(fp)
    x, y = -4.933, -0.003
    fp.SetPosition(VECTOR2I(FromMM(100 + x), FromMM(100 + y))); fp.SetOrientationDegrees(rot)
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM); fp.SetOrientationDegrees(rot)
    big = [p for p in fp.Pads() if p.GetNumber() not in ('MP',) and abs(ToMM(p.GetSize().y) - 0.8) < 0.01 or abs(ToMM(p.GetSize().x) - 0.8) < 0.01]
    xs = [ToMM(p.GetPosition().x) - 100 for p in big if p.GetNumber() != 'MP']
    p1 = [p for p in fp.Pads() if p.GetNumber() == '1'][0]
    cy = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
    allx = [ToMM(p.GetPosition().x) - 100 for p in fp.Pads()]
    print('rot %d: 0.8 mm row mean X %.3f, pin 1 at (%.3f, %.3f), pads X %.3f..%.3f, courtyard X %.3f..%.3f Y %.3f..%.3f, flipped %s' % (
        rot, sum(xs) / len(xs) if xs else 0, ToMM(p1.GetPosition().x) - 100, ToMM(p1.GetPosition().y) - 100, min(allx), max(allx),
        ToMM(cy.GetLeft()) - 100, ToMM(cy.GetRight()) - 100, ToMM(cy.GetTop()) - 100, ToMM(cy.GetBottom()) - 100, fp.IsFlipped()))
