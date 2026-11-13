#!/usr/bin/env python3
"""Rewrites the Files paragraph and the Open points of design/mfg/specs/band-flex-tails.md from the export rows (out/v8/rows_flex_us9.json etc.): boxes and solid counts are read from the rows."""
import json
from pathlib import Path
V = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin/out/v8"))
p = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mfg/specs/band-flex-tails.md"))
rows = {}
for us in range(7, 14):
    for r in json.load(open(V / f"rows_flex_us{us}.json")):
        rows[(r["part"], us)] = r
def box(part, us=9):
    r = rows[(part, us)]
    return f"{r['bbox_x_mm']} x {r['bbox_y_mm']} x {r['bbox_z_mm']}", r["solids"]
bt, nt = box("flex-tail-thumb"); ba, na = box("flex-tail-away")
st, ns = box("flex-tail-thumb-footstiffener"); sa, nsa = box("flex-tail-away-footstiffener")
s = p.read_text()
i = s.index("## Files"); j = s.index("## Open points")
files = (f"## Files\nDrawing: design/mfg/drawings/flex-tail-thumb.svg and .pdf (FLEX1), design/mfg/drawings/flex-tail-away.svg and .pdf (FLEX2); both are the v7 drawings until they are redrawn from the files below. "
 f"The flat patterns are design/ecad/band/flex1-us7.kicad_pcb to flex2-us13.kicad_pcb with their Gerber, drill and PDF drawings in design/ecad/band/fab/. "
 f"STEP only for the 3D shape, one per ring size, exported from the inside model v8 (out/v8/export_ribbons.py, the v7 exporter's emit()): design/mfg/parts/flex-tail-thumb/flex-tail-thumb-us7.step to flex-tail-thumb-us13.step and design/mfg/parts/flex-tail-away/flex-tail-away-us7.step to flex-tail-away-us13.step (no STL exists for the tails). "
 f"Each file is the bent ribbon as drawn, 0.11 thick outside the liner and 0.15 in it, no copper and no layer stack: {nt} solids for FLEX1 (vertical neck, fold, foot, trunk, flat head, bend) and {na} for FLEX2 (vertical neck, fold, foot, trunk, pad strip). "
 f"The polyimide foot stiffener of each tail is its own file in the same folder: flex-tail-thumb-footstiffener-us7.step to -us13.step and flex-tail-away-footstiffener-us7.step to -us13.step ({ns} solid, 0.10 thick). "
 f"At US 9 the box of the thumb file is {bt} and that of the away file {ba}; the stiffener boxes are {st} and {sa}. They give the shape and the length of the path; the flat pattern is the board file of design/ecad/band.\n\n")
openp = ("## Open points\n"
 "0. S16 (architecture 17.9 and 17.10), route of both tails in the band: closed for the route and the shape at every ring size by design/ecad/band/band-notes.md (14 boards, check_band.py) and the inside model v8 fit check (design/mech/thin/band-fit-notes.md). A liner cast with the ribbon inside is not proven by any maker (B8, S19; band-liner.md open point 10).\n"
 "1. Line count per tail: closed by design/ecad/band/band-interface.md section 2 (8 lands on FLEX1, 7 on FLEX2) and band-notes.md section c (connectivity computed from the netlist for every board; the motor's supply comes from the regulator U11 on the board, the tail carries the motor's two lines).\n"
 "2. Stack-up, copper weight, coverlay, stiffener, pad finish, tolerances: closed by design/ecad/band/band-notes.md section \"Stack and rules\" (polyimide 25 um, copper 12 um, coverlay, finished 0.11, stiffener 0.10, ENIG, outline +-0.10).\n"
 "3. Soldering method: closed by design/ecad/band/band-interface.md sections 5 to 7 (hot bar for the foot, hand soldering for the motor leads and the protection circuit tabs; assembly order steps 7, 9, 16 and the cast at step 21 in design/mfg/assembly/assembly.md). The hot bar and iron values are starting values that no unit has measured (band-notes.md \"Not closed\" 2).\n"
 "4. Outline drawing, widths, lengths per size, bend radii, slot size: closed by design/ecad/band (outlines and flat lengths band-notes.md section b; fold radius band-interface.md section 3) and the model's floor slot 2.1 x 0.6 (thin-notes.md \"Model v8\").\n"
 "5. Pad pitch and position at the floor slot on the main board: closed by design/ecad/band/band-interface.md section 2 (lands at X -3.015 to -1.485, |Y| 3.875 and 4.775 on each side, keep-out X -3.5 to -1.0, |Y| 3.4 to 5.6).\n"
 "6. Still unmeasured (design/ecad/band/band-notes.md \"Not closed\" 1, 2, 3, 5, 6): the cell supplier's build of the protection circuit tabs (S12), the hot bar and iron settings, the motor lead exit pitch read from a small drawing, via-in-pad acceptance by the flex maker, the Gerber layer names for the coverlay and the stiffener.\n\n")
k = s.index("## Source lines")
p.write_text(s[:i] + files + openp + s[k:])
print("specs updated", nt, na, ns, nsa)
