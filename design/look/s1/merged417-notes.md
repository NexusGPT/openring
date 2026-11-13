# merged417: the exterior with the block 0.970 taller above the board (owner card 2026-11-13, "4.17 mm, stock screen with connector")

Written step by step while working. Evidence folder: design/look/s1/out/work-417/ (below: work-417/). Clock from `date`.

## Steps
- 06:54 started (work-417/ first `date` in the shell). Read exterior.py in full, measure_32f.py, merged32h-report.md, merged32g-report.md, direction.md, screen-cable-study.md (whole file), envelope_slim.py, the three owner pictures in look/feedback/, model-v9-notes.md section a.
- 06:56 base runs started (work-417/base.sh): merged32h US 9 rebuilt with the unchanged exterior.py into work-417/before/h-us9/ (log work-417/before/build-h-us9.log), and measure_32f.py on the delivered out/ring-merged32h-us9.step with the merged32h flags (log work-417/before/measure-32h-us9-base.log).
- Open point sent to the lead (SendMessage, about 06:55): merged32h's real top is 3.85 at the centre line (exterior.py C dict TOP_Z, architecture.md line 490), not 3.20; "3.20" is the old nominal stack (architecture.md line 426) the cable study used. +0.970 on glass, seat and top gives 4.820 at the centre line, so check (1) "4.170" and check (2) "+0.970" cannot both hold with the crown kept.
- 07:00 exterior.py changed (diff: work-417/exterior-diff-417.log against work-417/before/exterior-before.py): new variant merged417, H_LIKE (merged417 takes every merged32h branch), LIFT417 0.970 on TOP_Z and GLASS_Z, the plan box 0.970 taller, the top-edge pick 0.970 higher, an STL export for merged417 only.
- 07:03 measure_417.py written from measure_32f.py (new checks (1), (2), (3) with --ref, --lift, --height; rule round the opening 0.50; the two light-place checks near the top moved up by --lift).
- 07:04 chain1.sh started in the background (pid 76461): waits for base.sh (pid 7785), then build_417.sh (rebuilds and compares, then merged417 US 7 to 13), then the control run of measure_417.py on merged32h US 9 against itself. Expectations: work-417/expect-chain1.txt. Machine load average 107 at 07:04 (`uptime`), so the measure runs are slow.
- 07:05 lead's ruling: reading A (top 4.820 centre, 3.920 long edges, glass split 3.72); check (1) = merged32h's measured top + 0.970 within 0.005, and 4.170 printed as the study's flat-stack figure. Plus one owner option at US 9 only: the lowest crown the glass allows with the seat at 3.72.
- 07:06 measure_417.py check (1) changed to the ruling. exterior.py: option variant merged417flat (flat top through the height merged417 has over the screen panel's long edge, Y 6.4; no STL), work-417/edit-flat.log; build added to build_417.sh before it started.
- 07:07 chain2.sh started (waits for chain1.done): the pictures (render_417.py), then measure_417.py on merged417 US 7 to 13, done file work-417/chain2.done.

## Run 1 (07:07 to 08:26): every size RESULT FAIL, and what was found
All run-1 files are kept in work-417/run1/ (outputs, logs, pictures).
- Rebuilds with the run-1 exterior.py: merged32h US 9, US 7, default, merged32g US 7, merged32f, merged32e: glb cmp, step cmp without FILE_NAME and json diff all exit 0 (work-417/run1/build-417-all.log). merged417 US 7 to 12 and the flat option built; US 13 exit 1, "junction fillet failed down to 2.5" (run1/build-417-us13.log), so run1/measure-417-us13.log ends in FileNotFoundError, not in a RESULT line.
- Control run (merged32h US 9 against itself, run1/measure-417-control-32h-us9.log): RESULT PASS, and its -Y wall line reads "0 of 285 points are not metal". The microphones have no wall slot since merged32f (underside holes), so the -Y wall finding of merged417 is not the slots.
- Cause 1, a real defect of the shape: the 4.0 junction blend, made by OCC on the taller block, came out on the wrong side and took metal out of both long walls round X 0. Section at X 0 of US 9 (work-417/diag-section-417-us9-x0.log): the band's own circle runs on inside the wall to (Y -6.868, Z 1.251) and a blend face rises from there to the wall at Z 2.859; merged32h at the same place (diag-section-32h-us9-x0.log) has its blend outside the wall, from the band at (-9.478, -0.870) to (-7.364, 2.308). Skin at X 0, Z 1.3: merged417 run 1 at Y -6.87, merged32h at -7.74 (diag-junc-417-us9.log, diag-junc-32h-us9.log). The same 12 junction edges in both. Tried, all dented: radius 3.0, 3.5 and 4.0 (4.5, 5.0, 6.0 fail) (diag-radii-417-us9.log); the long junction edges alone (diag-subsets-417-us9.log); the crown cut after the blend (diag-junc-417-us9-order2.log).
- Cause 2, a fault of the new check (3): one Z grid from 0.45 up for every zone, so "high" compared Z 3.70 (0.02 under the 3.72 seat) with Z 2.70 (0.05 under the 2.75 seat), which are unlike places. Run 1 US 9: +X end high 0.4840 at Z 3.70 against 0.5029 at Z 2.70; +Y wall high 0.6747 against 0.6971; -X end high 0.4904 against 0.5090; -Y wall high 0.7451 against 0.7652; corners high 0.1228 against 0.1414 (run1/measure-417-us9.log). The low and mid "thinner" lines on both long walls (0.4134 at X 0, Z 1.30 and 0.4439 at X 0, Z 1.50, against 0.6617 and 0.9250) are cause 1: same Z in both files.

## Changes for run 2 (08:45 to 08:53)
- exterior.py, merged417 path only (work-417/edit-union.log): the body is merged32h's own block, band and 4.0 blend, made exactly as merged32h at merged32h's heights, united with the tall block (same plan, corners and bottom roll; crown and top rolls 0.970 higher). merged32h's block lies inside the tall block, so the union keeps merged32h's blend and adds the taller wall above it. The blend meets the taller wall in a crease of about 11 degrees at X 0 (from 7.395 at Z 2.143 to 7.375 at Z 2.241, diag-section-417-us9-x0-union.log); it is rounded with the largest of 2.0, 1.5, 1.0 that gives a valid solid and adds metal (2.0 ends tangent on the wall at Z 2.50 at US 9: diag-crease-417-us9.log). Trial at US 13 into a scratch folder: exit 0, junction 4.0 reached, crease rounding 1.0 (2.0 and 1.5 failed) (work-417/try-union.log).
- measure_417.py check (3): low and mid from the floor up, high from the seat down (seat - 0.02 - 0.05 k), so each zone compares the same place in both files. No limit was changed.
- 08:53 chain3.sh started (pid 94657, done file work-417/chain3.done): rebuild comparisons, merged417 US 7 to 13 and the flat option, the control run, the pictures, then measure_417.py US 7 to 13.

## Run 2 (08:53 to 10:12): only US 10 passes. All run-2 files are in work-417/run2/.
Rebuild comparisons with the run-2 exterior.py (merged32h US 9, US 7, default; merged32g US 7; merged32f; merged32e): every glb cmp, step cmp without FILE_NAME and json diff exit 0 (run2/build-417-all.log).

| Size | Built (run2/build-417-usN.log) | Crease rounding tried 2.0, 1.5, 1.0: reached | Measure (run2/measure-417-usN.log, last line) |
|---|---|---|---|
| US 7 | no, exit 1 | none (2.0, 1.5, 1.0 failed) | FileNotFoundError: out/ring-merged417-us7.step |
| US 8 | no, exit 1 | none (no candidate accepted; no "failed" line, so each was rejected as invalid or as removing metal) | FileNotFoundError: out/ring-merged417-us8.step |
| US 9 | yes | 2.0, metal added 0.8940 mm3 | Traceback, OCP Standard_Failure in hits() (IntCurvesFace) |
| US 10 | yes | 2.0, metal added 0.0542 mm3 | RESULT PASS |
| US 11 | no, exit 1 | none (1.5 failed; 2.0 and 1.0 rejected) | FileNotFoundError: out/ring-merged417-us11.step |
| US 12 | yes | 1.0 (2.0 failed), metal added 0.3240 mm3 | Traceback, OCP Standard_Failure in hits() |
| US 13 | yes | 1.0 (2.0, 1.5 failed), metal added 0.1416 mm3 | ValueError: max() iterable argument is empty (hits() returned no point on X 0, Y 6.8) |

Causes and fixes (10:13 to 10:16):
- build_417.sh exited 0 although three sizes failed: it echoed each exit code but never acted on it. Fixed: each failed size (and a size with no STEP file) is named in a "failed:" line and the script exits 1 (work-417/edit-build-sh-2.log).
- The crease rounding builds on some sizes only, and at US 10 the 2.0 rounding added only 0.0542 mm3 where US 9 added 0.8940 (not checked further). At US 7 every radius fails, on all 6 crease edges and on the 2 long edges alone: 2.0, 1.0, 0.5, 0.3 (work-417/diag-crease2-us7.log; before rounding the skin there is never inside the wall: least |Y| 7.3750). Change: the rounding is dropped for every size, so all sizes carry the same unrounded crease where merged32h's blend meets the taller wall (about 11 degrees at X 0, US 9; work-417/edit-nocrease.log). This is a look point, listed below. No limit was changed.
- measure_417.py: OCC's line intersector failed on these files (Standard_Failure at US 9 and 12, no point at all at US 13). Replaced by plane sections turned into polylines (chord error under 1e-5) and crossed with the line in the plane. The same method measures both the file and the reference.
- 10:16 run 3 started: work-417/chain4.sh (pid 98158), done file work-417/chain4.done; expectations in work-417/expect-chain1.txt (run 3 block).
- 10:17 lead's ruling: the unrounded crease is accepted for run 3 only (to prove walls and joystick checks at all sizes); it is NOT the look. After run 3: try one other blend construction on US 9 (then US 7 and US 13).
- 10:20 prepared, not yet run (one heavy job at a time; run 3 is running): work-417/make_sweep.py writes work-417/exterior_sweep.py, a copy of exterior.py with one experimental path (merged417, env BLEND417=sweep): the long-side blend is built directly as the 2D radius-4.0 blend between the band (R1) and the TALL wall, tangent to both (centre Y = 7.375 + 4.0, Z from the band radius), extruded along X over the band width, its end faces rounded 0.4 (or 0.3, 0.2); OCC rounds only the other junction edges. exterior.py is not changed until the experiment passes (work-417/make-sweep.log).

## Run 3 (10:16 to 11:14): the ENGINEERING shape, all 7 sizes RESULT PASS
This is the engineering shape, not the look. It carries an unrounded fold line on both long sides where merged32h's band blend meets the taller wall (about 11 degrees at X 0, Z 2.24 at US 9, from the section in work-417/diag-section-417-us9-x0-union.log: Y 7.395 at Z 2.143 to 7.375 at Z 2.241). The lead accepted it for run 3 only, to prove the walls and the joystick checks; it is not accepted as the look (owner: "merge INTO ring").

- Builds: work-417/build-417-all.log ends `failed: none`; merged417 US 7 to 13 and merged417flat US 9 exit 0.
- The accepted variant is untouched: with the final exterior.py, merged32h US 9, US 7 and default, merged32g US 7, merged32f and merged32e rebuild to the same GLB bytes (cmp exit 0), the same STEP without its FILE_NAME line (cmp exit 0) and the same json (diff exit 0) as the delivered out/ files (build-417-all.log). merged32h US 9 before and after the change: json diff exit 0 and GLB cmp exit 0 between work-417/before/h-us9/ and work-417/after/h-us9/; body volume 2569.7004 mm3 and whole bounding box X -14.650..14.650, Y -13.076..12.073, Z -21.945..3.850 both before (work-417/before/build-h-us9.log) and in the after json (identical file).
- Control: measure_417.py on merged32h US 9 against itself ends `RESULT PASS` (work-417/measure-417-control-32h-us9.log).
- Table (work-417/table-417-run3.log, made by table_417.py from the logs; every measure-417-usN.log ends with `RESULT PASS` followed by its closing `date` line):

| Size | Built | Crease | Centre deg | Opening X x band | Metal +X/-X / bottom | Frame clearance +X,-X,block,bottom | Top Z (ref + 0.970) | Seat rise | Thinnest wall this / ref | Wall classes not thinner | Result line |
|---|---|---|---|---|---|---|---|---|---|---|---|
| US 7 | yes | unrounded | -84.000 | 5.597 x 5.600 | 1.067/1.067 / 1.094 | 0.098, 0.098, 0.101, 0.099 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |
| US 8 | yes | unrounded | -81.000 | 5.597 x 5.600 | 1.067/1.067 / 1.094 | 0.098, 0.098, 0.101, 0.099 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |
| US 9 | yes | unrounded | -78.000 | 5.597 x 5.600 | 1.067/1.067 / 1.097 | 0.098, 0.098, 0.099, 0.100 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |
| US 10 | yes | unrounded | -78.000 | 5.597 x 5.597 | 1.067/1.067 / 1.219 | 0.098, 0.098, 0.097, 0.100 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |
| US 11 | yes | unrounded | -78.000 | 5.597 x 5.600 | 1.067/1.067 / 1.344 | 0.098, 0.098, 0.100, 0.100 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |
| US 12 | yes | unrounded | -78.000 | 5.597 x 5.600 | 1.067/1.067 / 1.467 | 0.098, 0.098, 0.100, 0.100 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |
| US 13 | yes | unrounded | -78.000 | 5.597 x 5.600 | 1.067/1.067 / 1.592 | 0.098, 0.098, 0.100, 0.100 | 4.8200 (4.8200) PASS | 0.9700 PASS | 0.0508 / 0.0508 | 15 | RESULT PASS |

  "Wall classes not thinner" counts the lines "not thinner" in check (3): 5 sides x 3 zones = 15 of 15 per size; "THINNER" appears 0 times in each of the 7 logs.
- Already there (not caused by merged417): the thinnest wall, 0.0508 mm, is at the cavity envelope's plan corner (X 13.696, Y 6.421, Z 0.45), where the 0.1 corner of thin.py's panel pocket meets the outer corner (R 2.5) inside the bottom roll (1.2). merged32h has the same 0.0508 at the same point (control log). Who must act: the inside model's owner (design/mech/thin/), if a pocket corner of 0.1 there is not intended.
- Cap profile, ridges, microphones, -Y wall (0 of 285 points open), no light, specks: as merged32h in every log.
- Load into the inside model: the files hold the solids body, glass, joystick, mic_1, mic_2, screen (measure logs, "solids in the file"), the labels thin.py load_exterior() reads (by["body"], by["glass"], design/mech/thin/thin.py lines 284 to 286), so THIN_EXTERIOR=out/ring-merged417-usN.step loads them the same way. thin.py itself was not run (not my file).

## Dimensions against merged32h
Changed (source: exterior.py lines 608 to 611 and 642 to 654, measured in each measure-417-usN.log):
- Top at the centre line: 3.850 to 4.820 (+0.970), measured check (1). Reason: J1 between board and panel (screen-cable-study.md 4.3 item 1).
- Glass seat (glass bottom, body top): 2.750 to 3.720 (+0.970), measured check (2); the cover glass is unchanged, 1.1000 thick at X 0, Y 0 in both (measure-417-us9.log).
- Long edge of the face: 2.95 (architecture.md line 490) to 3.921 (printed by the build, build-417-us9.log: "3.921 at the long edges").
- Body volume at US 9: 2569.7004 to 2983.5850 mm3 (measure logs, "solid body").
- The band blend to the wall: merged32h's own blend, then an unrounded fold line onto the taller wall (engineering shape); see the swept blend below for the look.
Kept, unchanged (exterior.py line 587 C dict and lines 602, 603, 625): plan 29.3 x 14.75, plan corner 2.5, bottom roll 1.2, long-edge roll 1.0, end roll 1.2, crown arc 30.7 (rise 0.9), band 8.0 wide, wall 2.6, shoulders 3.6, band edge 0.4, bore gap 0.4, junction blend 4.0, joystick per size (G32_JOY_DEG), opening 5.6, frame 5.4, cap 4.4 (0.5 more proud), ridges 0.7 / 1.3 / 1.9, microphone holes and seats, no record button, pads inside, no light.
Why these radii (the brief: make 4.17 read slim): I kept every radius. Each of the rolls sits within the 0.925 of metal between the outer plan (Y 7.375, X 14.65) and thin.py's pocket (Y 6.45, X 13.725): a larger long-edge roll or bottom roll thins the wall at the seat or at the floor, which check (3) forbids; the crown is the owner's "more incurved". The one lever left is the crown height itself: that is the flat-glass option for the owner below. The study's plan size holds: section 4.3 changes no plan dimension (item 1 is height only; item 4 is an inside pocket).

## Pictures (render_417.py, no browser; each opened with Read; sizes 146 to 255 kB)
- a-us9-three-quarter.png: merged417 US 9 from the fingertip end on the joystick side: dark crowned glass over a taller dark block, the band sweeping into the block, the round ridged joystick on the band's side.
- b-us9-side.png: merged32h left, merged417 right, same scale: the block band is visibly thicker on the right (glass top 3.850 against 4.820 in the caption); the band and joystick are the same.
- c-us9-end.png: same pair along the finger: the taller block sits on the same band; the crown and the long-edge rolls look the same; the fold line is not readable at this scale.
- d-us9-top.png: merged417 from above: the rounded rectangle of glass with the band ends and the joystick cap showing past the long sides.
- b-us7-side.png and b-us13-side.png: the same side pair at US 7 and US 13: the same taller block on the smaller and the larger band.
- option-us9-side-417-vs-flat.png and option-us9-end-417-vs-flat.png: merged417 (crowned, glass top 4.820) beside merged417flat (flat, glass top 4.145); the flat one reads lower and boxier, the crowned one rounder.
- Renderer limit: triangle edges of the tessellation show as faint lines and streaks; they are not shape.

## The swept blend for the look (BLEND417=sweep), US 9: RESULT FAIL, not carried on
- Build (work-417/sweep-build-us9.log, exterior_sweep.py from make_sweep.py, into work-417/sweep-us9/): exit 0. The blend was built as planned: radius 4.0, centre Y 11.3750 Z 2.8586, tangent to the tall wall at Z 2.8586 and to the band at Y 8.7099 Z -0.1243; its end rounding failed at 0.4, 0.3 and 0.2, so its two end faces stay flat in the band side planes. OCC rounded the other 6 junction edges (4 at the underside corners, 2 under the block).
- End view beside the creased shape (work-417/sweep-us9-end-creased-vs-sweep.png, opened with Read): the right one's blend climbs higher up the block side and meets it without the visible bend of the left one; otherwise the two look alike at this scale.
- Same checks (work-417/measure-sweep-us9.log): checks (1) and (2) PASS, joystick opening, metal round it (1.067 / 1.097), frame clearances, -Y wall (0 of 285) as the engineering shape; but check (3) fails on both long walls, low and mid zones: 0.4134 at X 0, Z 1.30 against 0.6617, and 0.4439 at X 0, Z 1.50 against 0.9250. Last line: `RESULT FAIL wall +Y wall low thinner than the reference; wall +Y wall mid thinner than the reference; wall -Y wall low thinner than the reference; wall -Y wall mid thinner than the reference`. These are run 1's numbers exactly (run1/measure-417-us9.log).
- Cause (my reading, from these numbers; not proven): run 1's dented face is a 4.0 blend face tangent to the wall at Z 2.859 (diag-section-417-us9-x0.log), the same height as this build's wall contact. So OCC still rounded the long-side edges although only the 6 underside edges were given to it: OCC extends a rounding along every edge that joins tangentially, and the underside edges join the long edges. Any OCC rounding of the junction made on the tall block will therefore dent the wall. A swept blend only works if the OCC rounding of the other edges is made where it does not reach the long side (on merged32h's block, as in run 3), and the swept blend is then joined to that body.
- Per the lead's rule (US 7 and US 13 only if US 9 passes), US 7 and US 13 were not run (work-417/sweep-chain.log: "US 9 not RESULT PASS: US 7 and US 13 not run").
- Against the delivered engineering file of US 9 (work-417/compare-sweep-us9.log): glass, joystick, mic_1, mic_2 and screen are equal (the same volume and bounding box, symmetric difference 0.000000 mm3). The body boolean comparison failed ("Boolean operation unable to clean"; its symmetric difference 5963.0132 mm3 is about the two volumes added together, a failed operation, not a result), so the body is NOT shown byte-equal or boolean-equal. Measured equal between the two files: glass seat 3.7200, top 4.8200, opening 5.597 x 5.600 at -78.000, metal round it, the high-zone walls, the ends and corners (same figures in both logs). Measured different: the long walls round X 0 below Z 1.6 (above), and the body volume, 2979.5059 against 2983.5850 mm3.
- Next step for a follow-up helper: take run 3's body (merged32h's block, band and blend joined to the tall block) and join the swept blend solid to it, on both long sides, then measure the remaining fold where the two blends cross, and check (3) at US 9, then US 7 and US 13. exterior_sweep.py and make_sweep.py are the starting point; exterior.py is not changed by the experiment.

## Open items for the lead
1. The look: the delivered merged417 files carry the fold line (engineering shape). The swept blend did not pass; see the next step above.
2. Already there in merged32h: 0.0508 mm of metal at the pocket's plan corner low in the bottom roll (inside model's owner).
3. The 4.170 figure: printed in every log as "NOT met by 0.6500"; the real crown top is 4.820 (lead's ruling, reading A).

## Totals
- Files written: out/ring-merged417-usN.step, .stl, .glb and out/measures-merged417-usN.json for N = 7 to 13, and out/ring-merged417flat-us9.step, .glb and json: 117,022,367 bytes (`ls -la`, 11:20). work-417/: 379,828 kB (`du -sk`, work-417/du-work.log, 11:30), of which run1/ 151,576 kB and run2/ 147,076 kB (kept as evidence; the lead may delete them). No file over 50 MB (`find -size +50M` found none).
- exterior.py: diff against the copy as found is work-417/exterior-diff-417.log; sha1 of the final exterior.py and measure_417.py in work-417/shasum-final.log.
- One stray file of mine outside the work folder (s1/__pycache__/measure_417.cpython-312.pyc from a syntax check) was moved into work-417/ (pycache-after-move.log).

## questions_for_owner
1. Crown height. merged417 keeps the crowned glass: top 4.820 mm at the centre line, 3.921 at the long edges (the cable study's "4.17" is the flat-stack figure; the crown adds the rest). Option: a flat glass face at 4.1455 mm, the lowest the glass allows with the seat at 3.72 if it keeps the 0.42 mm it has over the screen panel's long edge (cover-glass.md line 29); then the glass is 0.4255 thick everywhere, against 1.10 at the centre today, and the face is no longer "more incurved". Pictures: design/look/s1/out/work-417/option-us9-side-417-vs-flat.png and option-us9-end-417-vs-flat.png (crowned left, flat right). Built at US 9 only (work-417/build-417flat-us9.log). Which do you want: the crowned 4.82, or the flat 4.15?

RESULT: done, merged417 (top 4.820, glass seat 3.720, both +0.970 over merged32h) is built for US 7 to 13 and every size ends RESULT PASS as the engineering shape with an unrounded fold line where the band blend meets the taller wall; the look (no fold) is not reached: the swept blend failed check (3) at US 9.
