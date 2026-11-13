"""The KiCad-Python edits of 3D model entries in make_broken_boards.py did not reach the saved copies (Models() hands out copies): this edits the two
broken copies' text instead. ${KIPRJMOD}/models/ -> the original board folder's models/; in part_tall, J1's model scale z -> (3.31 + 1) / 3.31.
Prints what it changed. usage: fix_broken_text.py <r4/broken folder> <original board folder>"""
import os
import re
import sys

B, SRC = sys.argv[1], sys.argv[2]
for sub in ("board_long", "part_tall"):
    p = os.path.join(B, sub, "case_main.kicad_pcb")
    s = open(p).read()
    n = s.count("${KIPRJMOD}/models/")
    s = s.replace("${KIPRJMOD}/models/", os.path.join(SRC, "models") + "/")
    print(f"{sub}: {n} model paths made absolute")
    if sub == "part_tall":
        i = s.index("USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step")
        m = re.compile(r"\(scale\s*\(xyz 1 1 1\)").search(s, i)
        assert m and m.start() - i < 400, "J1 scale block not found"
        f = (3.31 + 1.0) / 3.31
        s = s[:m.start()] + "(scale\n\t\t\t\t(xyz 1 1 %.6f)" % f + s[m.end():]
        print(f"part_tall: J1 model scale z set to {f:.6f}")
    open(p, "w").write(s)
