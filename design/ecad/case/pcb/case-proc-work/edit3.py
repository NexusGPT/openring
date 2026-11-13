F = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/board-notes.md")
t = open(F, encoding="utf-8").read().rstrip("\n").split("\n")
assert t[-1].startswith("RESULT:")
res = t.pop()
while t[-1] == "":
    t.pop()
sec = """
## Round 4 (process sheet changes C4, C5, C6, C15, C16)

Written 2026-11-13 from 13:47 (clock from the `date` command). PM = design/mfg/assembly/process.md. Work folder: design/ecad/case/pcb/case-proc-work/ (every log). No pad, hole, track, zone or outline of either board changed (proof in case-proc-notes.md).

### Fabrication notes for both case boards (PCB1 case_main, PCB2 case_pins)

These notes go to the board maker and the stencil maker with the Gerber files of fab/case_main/ and fab/case_pins/ (export_fab.sh).

1. Panel (change C4; PM P7 and its first lines): no new copper on either board. Each board is delivered in a panel with rails of 5 mm (PM P7, first bullet: \"The board maker's assembly rule: 5 mm tooling edges\"), and three fiducials of 1 mm, centred 3.85 mm from the panel edges, on the rails, not in a line (PM P7: \"1 mm fiducials centered at 3.85 mm from the panel edges\"; three is a [CHOICE], PM \"for the lead to confirm\"). PCB1 panel: three on the top face (F). PCB2 panel: three on the top face (F), the face with the pins (PM P7, bullet \"Case main board panel: three on the top face (F). Case pin board panel: three on F.\"). The bottom face of PCB1 has no paste, so it gets no fiducial for paste. PCB2 is three separate pieces in one file (Round 3, m2): all three pieces stay in the same panel.
2. Fiducial mask opening: not in any saved document (PM P7, last bullet); the board maker takes it from the fiducial footprint it uses. Open, for the lead.
3. Stencils (PM P2 table, rows \"Case main board, top (F)\", \"Case main board, bottom (B)\" and \"Case pin board (PCB2)\"): both stencils stainless steel, laser cut, 0.10 mm. PCB1: F paste file with 265 openings, no bottom stencil. PCB2: F paste file with 4 openings, one ring over each spring pin pad, outer 1.70 mm, inner 1.10 mm (added by case-proc-work/add_pin_paste.py; the ring shape is a [CHOICE] of this round: PM gives no opening size). The rings are drawn as stroked circles of 0.30 mm width in case_pins-F_Paste.gbr (two half arcs each, 8 arcs in all), not as flashed pads; the stencil maker reads them as four ring openings.
4. Copper weight: 35 um on outer layers (1 oz) and 17.5 um on inner layers, for the boards that have inner layers (PCB1 only) (`design/wiring/lead-decisions.md` row \"board read-back test: the lead's rulings on its four open points\", ruling 4: \"ordered with 35 um outer copper (1 oz) and 17.5 um inner copper where a board has inner layers; this is written into the case board notes at the next change of those files\").
5. Reflow after paste: the assembly follows the case procedure, steps 1 and 4 (one reflow of the main board with the profile of PM P3; one reflow of the pin board with the same profile).
"""
t += sec.split("\n")
t += ["", res]
open(F, "w", encoding="utf-8").write("\n".join(t) + "\n")
print("ok")
