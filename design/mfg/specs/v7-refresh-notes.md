# Specs refresh to design version 7 (2026-11-11)

Basis: architecture 17.29 (round joystick, gloss black finish) and 17.30 (no recording light); exterior report `design/look/s1/merged32h-report.md`; parts list `design/bom.csv` at v7 (read, not edited); the lead's fixed choices for CAP1, FRM1, the glass print and the board hole. No git command was run.

## Files changed
- `design/mfg/specs/joystick-nub.md`: rewritten. Title "joystick cap CAP1 and frame FRM1"; material, process, finish, tolerances, inspection and per-size rows for the round cap and the round frame; open points 1 to 5 of v6 answered as fixed rows.
- `design/mfg/specs/cover-glass.md`: print window row removed (history line says removed in v7); print continuous with no opening; ADH1 over the whole face; inspection and open point 4 updated.
- `design/mfg/specs/main-board.md`: light guide hole row and LED1 row replaced by "holes through the board: 0"; open point 10 closed; note that the v6.2 STEP still has the hole.
- `design/mfg/specs/body.md`: material fixed to Ti-6Al-4V (17.29); joystick opening round 5.60; frame FRM1 row; flange held by the roof round the 5.60 opening; metal round the opening per size from merged32h (1.067 on X; 1.094 to 1.592 toward the bottom); inspection, open points 3 and 9.
- `design/mfg/specs/band-liner.md`, `band-flex-tails.md`: "nub" became "cap CAP1"; "light end" became "hand end".
- `design/mfg/part-map.csv`: joystick-nub maps to CAP1 (round), joystick-frame maps to FRM1; light-guide and light-plug rows removed.
- `design/mfg/parts-notes.md`, `design/mfg/mfg-notes.md`: v7 banner; the v6.2 files for the light parts, the rectangular joystick and the board hole are marked removed in v7 and not to be made.
- Not changed: `cell.md`, `record-cap.md` (no v7 content), `tools/check_docs.py` (no rule needs a removed part).

## Checks
- `check_docs.py`: last line `RESULT PASS` (checked 7 specs, 153 table rows, 252 values, 6 current-value rows, 0 problems). Log: `design/mfg/specs/v7-check-docs.log`.
- grep of the owned files for the removed terms: log `design/mfg/specs/v7-refresh-grep.log`. Every hit outside the check scripts' own rule lists says "removed in v7", or is the kept file or folder name joystick-nub. Left: `check_assembly.py` lines 17, 19, 83, 132, 133 (the term list of the new rule); `tools/check_docs.py` line 11 docstring "joystick nub" (no rule needs a removed part, so it is not mine to edit).

## Choices this page had to make (the lead confirms)
- ISO 2768-1 gives no general tolerance under 0.5 mm. joystick-nub.md sets: ridge height 0.08 +-0.02; ridge width, dish depth, edge radius, flange thickness +-0.05; frame top 0.50 +-0.05. Tagged [PROPOSED].
- Fit stack found: the flange 6.90 under ISO 2768-m (+-0.2) can be 7.10. The pocket is 7.0 under ISO 2768-f (+-0.1). A flange at the top of its tolerance does not pass. The spec inspects each flange against the 6.95 go gauge of assembly step 10. Proposal: put ISO 2768-f or 6.90 -0.10/0 on the flange. Your call.
- 7.345 (sphere radius) and 1.480 (highest point) sit in the "where measured" cell. Reason: check_docs accepts value-cell numbers only when they are in architecture.md or a STEP box. Their sources are the brief and merged32h-report.
- DP420 cure: 24 h at 22 C. Read from 3M's data sheet for DP420 Black (revision June 2024, page 3: 4,500 psi on aluminium after 24 h at 22 C; 60 min at 49 or 60 C also listed). Room temperature is chosen because the membranes and gaskets are already in the body. Copy read: https://aircraftspruce.ca/catalog/pdf/3M-Scotch-Weld-Epoxy-Adhesive-DP420-Black%20TDS.pdf.

## Not proven
- No v7 inside model is measured yet. The total length of CAP1 and the opening's wall length between frame and roof have no accepted figure; joystick-nub.md open point 8 says the inside model v7 gives them.
- The maker files and drawings in `design/mfg/parts/` and `design/mfg/drawings/` are still v6.2. `draw.py` lines 40 to 52 still list the light parts and the rectangular frame (not mine).
- The bond of DP420 Black on the gloss black coating, the cap's feel and the coating's wear are bench items (B9).
- The stiffener material and the dam material stay open (S26). They are outside the v7 fixed set.
