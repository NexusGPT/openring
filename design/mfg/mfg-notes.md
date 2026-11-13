# Manufacturing notes: maker files and drawings (inside model v7)

State of 2026-11-11, 22:31. The files and drawings follow the inside model v7 (`design/mech/thin/thin.py`, `thin-notes.md` section "Model v7"; architecture 17.31) on the accepted exterior merged32h at every size. The specifications are in `design/mfg/specs/` (design version 7: `specs/v7-refresh-notes.md`) and the assembly order in `design/mfg/assembly/assembly.md`. Owner's words: "a manufacturer cannot do anything with just this", "There should be no ambiguity to build it 100%".

Old states, for reference only: `parts/old_v63/` (the v6 joystick nub, the light guide LG1 and light plug LP1, all removed in v7, and the v6.2 index), `drawings/old_v63/` (their sheets); `parts/old_merged32c/`, `drawings/old_merged32c/` (the older exterior). Do not make anything from them.

## Files (design/mfg/parts/, read parts-notes.md)
Per ring size US 7 to 13: body with every inside pocket cut and the round 5.6 joystick opening (STEP, STL), band liner (STEP, STL), cell pouch, both flex tails, the joystick stiffener, the joystick dam, the glass seal, the motor window seal (US 7, 8, 9), and a whole-ring assembly STEP. Once: cover glass (print with no opening), joystick cap CAP1 with its 6.9 flange (STEP, STL; one moulded part that the file writes as two touching solids, `parts-notes.md`), joystick frame FRM1 (STEP, STL), main board (no hole), microphone gaskets and membranes. 88 files in `parts/index.csv`; `check_parts.py` ends `RESULT PASS files=88` (`design/mech/thin/out/v7-export/check_parts_v7.log`).
What a 3D printer can do: print the body, liner, cap and frame STL as fit and look samples. A print is not the part: not the metal, the resin grade, the coating or any tolerance.

## Tools (design/mfg/tools/)
- `draw.py`: one A3 sheet (SVG and PDF) per STEP file in `parts/<part>/` (not the assemblies and not the old_ folders): front, top, right side in third-angle layout, overall dimension lines, title block with the v7 materials of CAP1 and FRM1. Last full run: `tools/logs/draw_v7.log`, `65 drawn, 0 failed`; the cap sheet again after its shank was restored: `tools/logs/draw_v7_cap.log`, `1 drawn, 0 failed`. The v6.3 version is kept as `draw_v63.py`.
- What draw.py cannot do: dimension an inside feature on the views. It draws the outline with hidden edges dashed and dimensions only the overall size; the pockets, slots, roof and the motor window are given in each body sheet's table (values from the model), the cap and frame dimensions in `specs/joystick-nub.md`.
- `draw_ring.py` (ring assembly sheet) still points at the old merged32c exterior; it was not run. The whole ring per size is in `parts/assembly/` as STEP.
- `check_docs.py`: last run `specs/v7-check-docs-lead.log`, `RESULT PASS`.

## Ring sizes
US 7 to 13, seven sizes (17.17). The body, liner, cell, flex tails, stiffener, dam and the motor window seal change with the size; the joystick sits at -84 (US 7), -81 (US 8) and -78 (US 9 to 13) (17.25); the block and everything in it, the glass, the cap CAP1, the frame FRM1, the board, gaskets and membranes do not.
