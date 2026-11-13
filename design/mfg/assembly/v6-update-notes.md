# assembly.md brought to the inside model v6 (2026-11-11, from 05:38)

Sources read: `design/architecture.md` 17.22 to 17.26 (lines 697 to 792); `design/mech/thin/thin-notes.md` "Model v5" (lines 99 to 200) and "Model v6, continued" (lines 240 to 294); `design/firmware.md` F6 (ship and factory lines 787 to 886); `design/cell-sweep-notes.md`; `design/bom.csv`; `design/mech/thin/placement.csv`.

## Before and after

- Before (05:38, design tree as found): `check_assembly.py` ended `RESULT FAIL A1, A2`, exit 1. Missing from every step: U11, C83, C84, C85, C86, C87, C88, SEAL1, DAM1 (the parts list); motor_regulator, motor_cap_in, motor_cap_out, glass_seal, joystick_dam (the placement rows).
- After: `check.log` in this folder ends `RESULT PASS`, exit 0: 48 placement rows and 139 parts list references named in a step, steps 1 to 28 continuous, five fields per step, 225 distinct citations open, no dash, last line `RESULT:`.
- `check_assembly.py` is not changed: no new rule was needed.

## What changed in assembly.md

1. New parts in steps: U11, C83, C84 (step 2, with the model's places and the note that the board layout confirms them, architecture line 757); C85 to C88 (step 2); SEAL1 (step 23); DAM1 (step 20). They are also in the parts table of section 1.
2. Joystick, model v6 (steps 6, 10, 13, 14, 20, 21), in this order and with what each waits for:
   - step 6: the flat head 6.4 x 6.4 x 0.15 on its 6.4 x 6.4 x 0.075 stiffener; the flex maker bonds the stiffener first.
   - step 10: the body has the 7.0 mm pocket open from the bore up to the roof of the size, and the channel uncut over the joystick.
   - step 13 (retitled "Fit the joystick frame from outside, then the nub from the bore"): the frame goes in from outside first; its adhesive, if any, cures; then the nub with its 6.9 mm flange goes in straight from the bore through the 7.0 mm pocket and stops under the roof, 0.05 mm below it. The nub must be in before the harness, because the switch head lies under the flange.
   - step 14: the flat head goes under the flange.
   - step 20 (retitled "Dam the joystick pocket (DAM1)"): DAM1 is dispensed round the head. It waits for steps 13, 14 and 19.
   - step 21: the liner fills under the stiffener and a 0.1 mm strip on each side of the pocket, up to the dam.
3. Motor (17.22): step 2 no longer lists the motor switch and the motor diode, and R61 and R62 now serve U11's enable pin. Step 7 says the motor's lines carry VMOT. Step 25 no longer warns of a reset through the power chip. It now tests the cell's protection at a motor start on the cell alone, because the cell's own limit is unknown (architecture line 707).
4. Per ring size: a new table "What changes by ring size at assembly" in section 0 gives, for each size, the joystick angle, motor angle, protection circuit start, slot bottom Z, pocket roof radius, cell ends and cell length (architecture lines 779 to 789, thin-notes lines 275 to 281). It names the steps the table touches: 6, 7, 8, 9, 10, 13, 14, 19, 20, 21 and 26. The block's contents are the same at every size (thin-notes line 245).
5. Conflicts (section 3): a status column was added.
   - Closed: K-A4 (seat and SEAL1, model v5), K-A7 (SHIP_SAMPLE and the VBUS wait, firmware F6), K-A10 (body spec now X -2.2).
   - Changed: K-A1 (the boot loader lock is applied in firmware F6), K-A3 (DAM1 exists; material open; edge only, K15), K-A6 (fold volume reserved; bend radius open, K21).
   - Still open: K-A2, K-A5, K-A8, K-A9.
   - Never a conflict: K-A11.
   - New: K-A12, where the sources contradict each other. DAM1 is drawn standing on the liner (placement.csv line 40, bom.csv line 60), but it must be made before the liner is cast (band-liner.md line 50, step 20).
6. Steps 23 and 27 follow the closed conflicts: SEAL1 in the lowered seat; SHIP_ENTER or SHIP_SAMPLE, the firmware waiting for VBUS removal.
7. Water and dust (section 4): the glass-to-body row moves from "cannot" to "needs a test" (SEAL1 named, tape not chosen). The joystick row names DAM1. The verdict stands: no rating can be claimed today.
8. Sections 5 and 6 were brought up to date. Of the first issue's changes to other files, all are made except two: requirements.md line 26, and a parts list row for the floor slot sealant. New rows: the "on the liner" wording (K-A12); architecture line 713, whose remarks on steps 2 and 25 are now answered; S26 to add K-A12.
9. Citations: placement.csv and bom.csv gained rows, and the architecture gained lines. 60 stale citations were moved by matching their old cited text (the script and its log are kept beside the repo). 10 more were moved by hand: architecture 580 to 582, bom 58 to 62, bom 59 to 63, placement 17, 18, 21, 22, 25 and 32 to 24, 25, 28, 30, 34 and 42, and body.md 87 to 90. The firmware citations, already remapped by the cell sweep, were not touched.

## Step numbers

No step was added, removed or moved: steps 1 to 28 keep their numbers. Only the titles of step 13 and step 20 changed. design/firmware.md and design/mfg/specs need no change for step numbers.

## Open, said plainly

- The motor's free space to the body is under the lead's 0.05 mm rule at US 9 to US 13 (architecture line 791), and a fix is in work. If placement.csv changes for that fix, the motor angles in the per-size table may change. The check would still pass, because no part is added; the citations to placement.csv rows would move only if rows are added.
- The motor angle and the pocket roof per size come from the model v6 tables, not from a body file: the body STEP per size does not exist yet (body.md line 5).

RESULT: done, assembly.md follows model v6 and architecture 17.22 to 17.26 (U11, C83 to C88, SEAL1, DAM1 in steps; the joystick order of v6; a per-size table; conflict statuses, with one new conflict K-A12), step numbers unchanged, check_assembly.py ends RESULT PASS.
