import sys
P = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s = open(P, encoding="utf-8").read()
def rep(tag, old, new):
    global s
    n = s.count(old); print(tag, "matches", n)
    if n != 1: sys.exit(1)
    s = s.replace(old, new)
rep("row70", "| Cell temperature sensor | RT1 | 10 k thermistor; on the cell (17.3) or on the board (W13): the owner decides | `design/bom.csv:74` | 9 |",
 "| Cell temperature sensor | RT1 | 10 k thermistor, inside the bought cell pack with PRT1 and BT1 (one part with three output tabs); not a separate part to buy or solder (`design/ecad/band/band-interface.md:108`, `design/wiring/lead-decisions.md:9`) | `design/bom.csv:74`, `design/wiring/product-wiring.csv:34` to `design/wiring/product-wiring.csv:36` | 9 |")
rep("row73", "| gold discs 1.6 mm on the inside face, in the liner, order VBUS, D-, D+, GND |",
 "| gold-plated discs 1.6 mm across, 0.07 mm thick, soldered flat on the four FLEX2 pad lands with SAC305 paste (step 8), on the inside face, in the liner, order VBUS, D-, D+, GND (the parts list has no row for the disc yet) |")
rep("noball", " with no tilt and no solder ball under it (a lifted disc fails);", " with no tilt (a lifted edge fails);")
rep("outline8", " (`design/ecad/band/band-interface.md:141`). The four discs are on hand.", ". Four discs are at hand.")
rep("notes8", " The part is not in the parts list today (see the notes of this round).", " The disc has no row in the parts list yet.")
rep("row373", "| Ribbon outlines, lengths per size, the fold's bend radius (K-A6) | 6, 8, 14, 16, 17 | the mechanical designer, the flex maker and the layout engineer | S16, S14, S26 |",
 "| Ribbon lengths per size and the fold's bend radius (K-A6); the ribbon outlines are drawn (14 band boards, `design/ecad/band/band-interface.md:100`) | 6, 8, 14, 16, 17 | the mechanical designer, the flex maker and the layout engineer | S16, S14, S26 |")
open(P, "w", encoding="utf-8").write(s)
