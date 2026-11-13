# Soft cube case: the six open points (version C5d, 2026-11-11)

The soft cube on disk was labelled C5c (C5b with detail). This round is C5d. All paths below are under `design/`. Outer size unchanged: 45.4 x 45.9 x 41.4 mm (`case/out/case_size.txt`).

## The six bar points

| # | Point | Result | Evidence |
|---|---|---|---|
| 1 | Room for the round, higher joystick at US 7 to 13 | The model and the check now use the real exterior file of every size, `look/s1/out/ring-merged32h-us7.step` to `-us13.step` (frame dia 5.4, cap dia 4.4, cap top 1.48 mm above the frame, at -84 / -81 / -78 degrees). The dish grew from radius 17.10 to 17.64 mm at the floor. New test 13 prints the clearance per size: US 7 1.310, US 8 1.310, US 9 1.310, US 10 1.310, US 11 1.310, US 12 1.074, US 13 0.514 mm (nearest part: liner; limit 0.3). | `case/look/c5d_check_final.log` lines 11, 23, 35, 47, 59, 71, 83 |
| 2 | Pads read from `mech/thin/placement.csv` | `case.py` and `case_check.py` read the rows `pad_<net>` (row X -1.000, disc 1.60 x 0.07, arc pitch 2.4000, face radius 9.4761 about Z -9.8740 by a circle fit); no pad value is typed in the case files. The check reads the file again and matches every pin to the pad of its own net. Test copy with the four pads at the band's middle (X 0.000): 28 failures (all four pins at all seven sizes, lateral offset 1.000 mm), exit 1. | pass: `case/look/c5d_check_final.log`; fail: `case/look/c5d_check_pads_at_band_middle.log`; test copy `case/look/c5d_placement_pads_at_band_middle.csv` |
| 3 | Pin holder as a designed part | `pin_holder`: own solid (check test 14: 1 solid, valid, 156.3 mm3), Celanese Vectra E130i black (LCP, 30 percent glass fibre), envelope X 3.83 to 9.00, Y -5.50 to 5.50, Z 19.71 to 27.03 mm; four bores dia 1.60 with 0.2 x 45 degree lead-in; front follows the band's inner face 0.35 mm along X (true distance 0.270 to 0.339 mm by size, test 14); lip 0.80 mm on the lug top; fixed by two heat stakes moulded on the post (pegs dia 1.0, heads dia 1.70 x 0.35 in dia 1.80 x 0.40 counterbores at x 7.95, y +-3.60). Assembly order and full dimensions: `case/case-architecture.md` section 7 "Pin holder". Parts list MECH16, MECH17 (MECH5 updated). Maker files: `case/out/parts/pin_holder.step`, `case/out/case_pin_holder.stl`, node `pin_holder` in `case/out/case_assembly_US9.step` and `.glb`. | `case/case-bom.csv` items 96, 97; check test 14 lines |
| 4 | The two rest bars in the dish | Kept, with the reason written: they are the band's seat (the pins push the band onto these two flanks, which is what lets one post serve US 7 to 13). Tidied: they end 1.0 mm below the band's top (7.0 mm high, they ran to the rim before), top edges rounded 0.8 mm, flank-face edges 0.25 mm. Band to both flanks 0.0105 to 0.0111 mm model gap at every size. | `case/case-architecture.md` section 7 "Band rests"; check lines "flank -Y / +Y" |
| 5 | `case_check.py` ends with PASS | `case_check: PASS, 3447 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]` (45 min run) | `case/look/c5d_check_final.log` |
| 6 | Pictures written by a script, no browser | `case/look/render.py` (numpy and Pillow software renderer) | `case/look/case-closed.png`, `case/look/case-open.png` (US 9 ring seated), `case/look/case-post-closeup.png` and `case/look/case-post-closeup-ring.png` (cutaway at x = -4.0 mm, lid left out, so the pin face shows), `case/look/case-open-empty.png`; log `case/look/c5d_render_final.log` |

## Findings

- Pad order: `placement.csv` puts VBUS at +Y (away from the joystick). C4 to C5c had VBUS at -Y by assumption A1. The pins now follow the file: P1 VBUS y +3.521, P2 D- +1.197, P3 D+ -1.197, P4 GND -3.521 (case frame). The electrical side (PCB2 wiring W1 to W4) must follow this order.
- With the real per-size files the block pocket's flare slab is 0.37 mm wider (half width 10.42 mm), and the roll play is 0.25 to 0.75 degrees (largest pad row shift 0.135 mm, limit 0.50).
- Holder gap: 0.35 mm measured along X is 0.270 mm true distance at US 7 near the holder's edges, because the band face is curved there. Limit 0.2 holds.

## Files changed

- `case/case.py`: real ring files per size; pads, pitch, disc and row offset read from placement.csv (`read_placement`); pin positions and nets from it; pocket over all seven files; well hull from the seven real joysticks; band rests lowered and rounded; new part `pin_holder`; staking pegs on the post; STL of the holder; new keys in `case_params.json` (`pin_holder`, `rests`, `pin_nets`, `placement`, `ring_files`, `joy_deg`).
- `case/case_check.py`: real ring files; pads from placement.csv (env `CASE_PLACEMENT` for another copy); pin-to-pad by net; tests 13 and 14; holder in the wrong-placement and post tests.
- `case/look/render.py`: material for the holder, cutaway close-up views `post-closeup`, `post-closeup-ring`, `CASE_OUT` for the parameters.
- `case/case-architecture.md`: new section "Changes from C5c to C5d"; section 6 pin order; section 7 ring source, "Pin holder", "Band rests", files and pictures.
- `case/case-notes.md`: new section "C5d" at the top.
- `case/case-bom.csv`: MECH5 updated, MECH16 (pin holder) and MECH17 (heat stakes) added (written by `case/look/c5d_bom.py`).
- Rebuilt outputs: `case/out/parts/*.step` (36 parts), `case/out/case_assembly_US9.step`, `.glb`, `case/out/case_*.stl`, `case/out/case_params.json`, `case/out/case_size.txt`, `case/look/meshes.npz`, the five pictures above.
- New: `case/look/c5d_bom.py`, `case/look/c5d_placement_pads_at_band_middle.csv`, logs `case/look/c5d_build1.log`, `c5d_check1.log` (trial build in `case/look/c5d_try/`, PASS 3447 pairs), `c5d_build_final.log`, `c5d_check_final.log`, `c5d_check_pads_at_band_middle.log`, `c5d_render_try1.log` to `try4.log`, `c5d_render_final.log`.
- Kept copies of the C5c state: `case/look/case_c5c_before_c5d.py`, `case_check_c5c_before_c5d.py`, `case-bom_c5c_before_c5d.csv`, `case_params_c5c_before_c5d.json`, `meshes_c5c.npz`, `case-closed-c5c.png`, `case-open-c5c.png`, `case-open-empty-c5c.png`.
- Nothing outside `design/case/` was written; `mech/thin/placement.csv` and the ring files were only read.

## Checks, last lines

- Build: `case.py done` (`case/look/c5d_build_final.log`).
- Fit check, delivered model: `case_check: PASS, 3447 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]` (`case/look/c5d_check_final.log`).
- Fit check, pads moved to the band's middle (test copy): `case_check: FAIL, 3447 pairs checked, 28 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]`, exit 1 (`case/look/c5d_check_pads_at_band_middle.log`).

## Not proven

- The Harwin P70-6000045R pin is still proposed, not confirmed (conflict K1: stroke not in the files read); the contact window 2.15 to 2.65 mm is an assumption.
- Holder: the moulder has not confirmed the 0.79 mm walls between bores (0.794 mm, the bores dia 1.60 at 2.39 mm centres) in LCP, the stake strength is not tested, and the touch electrode E1 now reads through a 1.97 mm LCP wall (bench B3). The five wires below the holder are not modelled.
- The ring is checked in its seated pose, turned (roll), and against the swinging lid; the straight lift out is not simulated as a motion. REPLACED 2026-11-13 (lead-decisions.md row 'case item 95'): the straight lift out IS checked, as test 17 of case_check.py: the ring is lifted straight up in 136 steps of 0.25 mm at every size (r4/final_check.log lines 157 to 160; smallest free space 0.172 mm at US 7).
- The other pictures (side, underside, in-hand, compare) are the C5c renders; the outside did not change.
- If the inside model's placement.csv changes, the case must be rebuilt (`case.py`), then checked; the check fails until then.

RESULT: done, all six points hold: real merged32h rings with joystick clearance printed per size (smallest 0.514 mm at US 13), pads read from placement.csv with a failing test copy, a designed LCP pin holder in the parts list and maker files, rests kept and tidied with a reason, case_check PASS 3447 pairs, and five script-rendered pictures in case/look/.
