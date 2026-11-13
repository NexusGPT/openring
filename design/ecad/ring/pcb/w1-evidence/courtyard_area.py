import sys, os, pcbnew
lib = sys.argv[1]
for name in ('Chip_0201', 'Chip_0402', 'Chip_0603', 'L_Murata_1269AS-H_2.5x2.0'):
    fp = pcbnew.FootprintLoad(lib, name)
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
    print('%s courtyard %.3f x %.3f = %.3f mm2' % (name, w, h, w * h))
