
---

# Round 4: regulator capacitors with the two new moves

Written 2026-11-13 from 02:04 to 02:45 (Mac clock). Inputs: the lead's round 4 ruling (moves 1 and 2); `design/ecad/ring/pcb/u4-capacitors.md` (last line: "RESULT: done, 4 of the 5 capacitors (C21, C25, C26, C27) can be 0402 with a smaller effective value, and C24 stays 0603 because 6.3 V is only 1.29 times its 4.9 V"). Scripts and logs in `design/wiring/ring-board-plan-work/`: `make_placement3.py`, `capdist.py`, `check_placement.py`, logs `r4a.log` to `r4m.log`, `r4-final.log`, `capdist-r4*.log`, `check_placement_r4*.log`.

**Result: a table passes both checks and is now `placement-plan.csv`** (the round 2 table is kept as `placement-plan-r2.csv`; the lead was told by one message at 02:42).

## R4.1 What the SGM38046 sheet says about a capacitor at the panel end (move 2)

Nothing. The sheet's layout text (`p3_sgm38046.pdf` page 15, "Layout and Component Selection") asks to "place the components as close as possible to the device" and to connect "the input and output bypass capacitors ... to the PCB ground plane"; Figure 1 (page 4) draws C5 (OVDD) and C8, C9 at the device. The word "panel" appears only in the product description (pages 1 and 14) and the thermal note (page 15); no sentence names a capacitor at the load end. So, as the lead ruled: one capacitor of each output rail at U4's ball; a second one (C29 on ELVSS) may sit at either end. ELVDD has only one capacitor (C25: `netlist.csv`, net ELVDD = C25, DISP1.2, J1.2, U4.D3), so C25 is at U4. In the passing table C29 is also at U4 (2.97 mm from D4); J1's ELVSS pin (pin 1) lies under J1's housing on the hand-end row, more than 3.0 mm from any free place.

## R4.2 Runs

| Run | Moves | Result (`capdist`) |
|---|---|---|
| r4a | move 2 only, five capacitors 0603 | FAIL 6: C26 has no place on the board; C25 13.2, C29 7.4, C75 3.9, C88 4.1, C11 3.1 mm |
| r4c to r4g | move 2 + C21, C25, C26, C27 in 0402 (the parts helper's subset) | r4g: PASS on the list of round 3 |
| r4h to r4m | the same, adding U1's VDD 10 uF C4 as a must (it is the input of U1's own DC/DC; same rule as C74) and C7 as a should | best before the last change: 1 overrun (C22 3.71) |
| **r4 (final)** | same; U1's DC/DC parts C4, L1, C6 placed by hand along U1's row A; U4's should capacitors placed in the order C26, C22, C25, C28, C29; U4 at (3.25, -3.80) rotation 180 (found by the grid search, 1,008 places) | **PASS** |

Every change kept within the ruling: four U4 capacitors in 0402; X2 shifted 1.00 mm toward +Y inside its zone (to (6.00, 4.25)) to open a place for C11 at U1's VBUS ball; C86 and C87 (load-switch outputs, no switching current) moved to free U2's east face for the VSYS capacitors; bias and series resistors moved. Not moved: U1, U2, U3, U5, U6, J1, ANT1, the band lands, the keep-outs, L71, L72, the RF parts. 48 of the 104 rows changed from round 2.

## R4.3 Checks

- Distance check `capdist.py placement-plan.csv` (`capdist-r4.log`) ends `RESULT PASS`. Values (mm, pad centre to pin centre): musts C21 0.90, C23 0.92, C24 1.30, C27 1.05 (U4); C74 0.89 (U2); L1 1.01, C6 0.90 (to L1's DECD pad, the inductor end of U1's DC/DC loop), C4 1.02 (U1); shoulds C22 2.81, C26 2.84, C25 2.59, C28 2.74, C29 2.97 (U4); C78 1.61, C79 1.66 (buck outputs at L71, L72 pad 2); C75 1.80, C88 2.06 (VSYS, nearest of U2's balls C1, C2, C7), C71 1.33, C72 2.20, C85 0.87 (U2); C11 1.52, C7 2.96 (U1). Mays: C80 4.82, C73 4.20.
- Placement check `check_placement.py placement-plan.csv` (`check_placement_r4.log`) ends `RESULT PASS` (104 parts, 85 parts face, 19 screen face; the U5-U3 courtyard note as in round 2).
- Broken copy (C21 moved 3.0 mm, C79 pushed past the edge): placement check `RESULT FAIL 5` (`check_placement_r4_broken.log`), distance check `RESULT FAIL 2` (`capdist-r4-broken.log`).
- Inductor L10 (SW1, SW2): 3.1 mm from the SW balls, as in round 3 (its 2.5 x 2.0 body keeps its pads at least about 1.6 mm away); ferrite FB1 (DECD to DECA of U1, not a capacitor): 3.2 mm from A6.

## R4.4 The new table

Command: `U4=3.25,-3.8,180 SUB=C21,C25,C26,C27 TAG=r4 run_kipy.sh make_placement3.py`, then the file is copied to `placement-plan.csv`. Rows (model mm; KiCad = model + (100, 100); face F = L1, B = L4):

@@TABLE@@

## R4.5 Changes other files need (added to h.1 and R2.6)

| File | Value now | Value needed | Reason |
|---|---|---|---|
| `design/ecad/ring/parts.csv`, `design/bom.csv`, `make_netlist.py` | C21, C26, C27 0603 4.7 uF (GRM188R61C475KAAJD); C25 0603 10 uF (GRM188R61C106KAALD) | C21, C26, C27 0402, Murata GRM155R61A475MEAAD (4.7 uF 10 V X5R); C25 0402, Murata GRM155R60J106ME15D (10 uF 6.3 V X5R); footprint Chip_0402 | `u4-capacitors.md` section 3 (effective capacitance at the rail voltage: about 2.4, 3.05, 2.55 and 2.7 uF) |
| `design/mech/thin/placement.csv` | U4 (4.000, -3.500); L10 (6.500, -3.500); X2 (5.500, 3.000) (and the round 2 values of R2.6) | U4 (3.250, -3.800), rotation 180; L10 (6.500, -4.200), 2.0 x 2.5; X2 (6.000, 4.250) | R4.2 |
| `design/wiring/ring-board-plan.md` h.2 | | add: SGM38046 output ripple with the four 0402 capacitors (effective 2.4 to 3.05 uF) at full white screen; U1 DC/DC ripple on DECD | `u4-capacitors.md` notes: the sheet gives no minimum capacitance |

RESULT: done, a placement with every must capacitor within 1.5 mm and every should within 3.0 mm of its pin passes both checks on the 4-layer board's one face (C21, C25, C26, C27 in 0402, U4 at (3.25, -3.80) rotated 180, X2 moved to (6.00, 4.25), 48 rows changed) and is now placement-plan.csv.
