# Assembly order brought to design version 7 (2026-11-11)

Basis: architecture 17.29 and 17.30; `design/bom.csv` at v7 (read only); the lead's fixed choices for CAP1 and FRM1. No git command was run.

## Files changed
- `design/mfg/assembly/assembly.md`.
- `design/mfg/assembly/check_assembly.py`: new rule H1, and A1 no longer requires placement rows LED1, LG1, LP1.

## What changed in assembly.md
- Step numbers are unchanged (28 steps). `design/firmware.md` 9.3 cites steps 5, 18, 20, 21, 25 and 27, so those references still hold.
- Step 4 (fit the light guide) is now "Clean and inspect the under face before the jig" [PROPOSED].
- Step 22 (place the light plug) is now "Clean and inspect the glass seat and the screen face before the bond" [PROPOSED].
- Each of those two steps carries one history line that says "removed in v7".
- Step 13 bonds the frame FRM1 into the round 5.60 opening from outside. It uses 3M Scotch-Weld DP420 Black with a 0.10 mm radial gap. Cure is 24 h at 22 C with no heat, from 3M's data sheet for DP420 Black (revision June 2024, page 3). After the cure, step 13 fits the round cap CAP1 straight from the bore, flange first. The flange is 6.90 x 6.40 and passes the 7.0 x 6.8 pocket. The 4.40 shank passes the 4.80 bore.
- Step 1 checks that the board has no hole. Step 2 does not fit LED1, R41 or Q2 (removed in v7).
- Steps 5, 18 and 25 use T-SIGN in place of the light test, with firmware.md cited at 892, 904, 918 and 920. Step 15 uses the foam with no notch. Step 23 has no print window.
- Step 10 checks the round opening with a pin gauge. It also checks the metal round the opening from merged32h: 1.067 on the X sides, and 1.094 (US 7) to 1.592 (US 13) toward the bottom.
- Section 1: the LG1 and LP1 rows are gone. FRM1 and CAP1 have their own rows. The "Not used" line lists the parts removed in v7.
- Section 3: K-A11 is closed. Section 4: row 2 is the bonded frame seam plus the unsealed cap clearance; row 4 is the print with no opening. Section 5: the frame adhesive and the cap and frame material are fixed, and the LG1/LP1 row is gone. Section 6: rows 6 and 7 are new (placement.csv light rows, draw.py and the maker files: the lead).
- Citations were refreshed after the v7 bom.csv dropped 5 rows: 49 bom.csv citations mapped by part, 109 others moved to the line that now holds the same text (matched against the old check.log), and 4 more moved by hand. The check prints every cited line (v7-check.log).

## Checks
- `check_assembly.py` on the new assembly.md ends `RESULT PASS`: 28 steps, all 136 bom.csv references in a step, 46 placement rows, 213 citations open, H1 pass. Log: `design/mfg/assembly/v7-check.log`.
- Fail proof: two scratch copies, each with one sentence added to step 4 ("Light guide fitted on the board." / "Light plug placed on the screen ledge."). Each ends `RESULT FAIL H1`, exit 1. Log: `design/mfg/assembly/v7-check-fail-proof.log`. The copies are in the session scratchpad, `assembly-broken-light-guide.md` and `assembly-broken-light-plug.md`.

## Not proven
- Steps 4 and 22 are proposals. No file names the flux or the cleaner.
- The DP420 bond on the gloss black coating is not tested (bench B9). The frame's depth stop on the bonding fixture is a proposal.
- (Old statement of 2026-11-11, stale, checked 2026-11-13: "The inside model v7 is not built yet. Placement.csv still holds the v6.3 light rows and the rectangular joystick_cap row (section 6, row 6)." The inside model v7 was built and exported (`design/mfg/parts/export_parts_v7.py`), and `design/mfg/parts/index.csv` now reads `design/mech/thin/thin.py v9 built at US 9`: the model is v9, placement.csv has no light rows, and joystick_cap is the round cap CAP1.)
- The flange tolerance stack: under ISO 2768-m the flange can exceed the pocket. See `design/mfg/specs/v7-refresh-notes.md`.
