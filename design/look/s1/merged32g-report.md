# merged32g: joystick angle per ring size, with the thick zone moved with it (architecture 17.25, lead's ruling)

Evidence folder: design/look/s1/out/work-32g/. Logs are there unless the path says out/. Round 1 (thick zone not moved, blocked) is kept in work-32g/round1/. The round-1 build logs build-32g*.log were overwritten by round 2, my slip.

## Result
- All seven sizes pass. Every metal figure round the opening is at least 0.567 mm (rule 0.40) at 0.1, 0.2 and 0.3 mm under the surface.
- US 9 to US 13 are identical to merged32f.
- US 7 bottom side: merged32f had 0.847 mm (out/measure-32f-us7.log line 34). merged32g has 1.094 mm (out/measure-32g-us7.log line 35).

## What changed in design/look/s1/exterior.py
Full diff: work-32g/exterior-diff-32g.log. Line list: work-32g/lines-32g.log.

- **Line 28:** new variant `merged32g`.
- **Line 600:** `F_LIKE` makes merged32g take every merged32f branch (lines 753, 805, 819, 844).
- **Line 611:** `G32_JOY_DEG` gives 84.0 on US 7, 81.0 on US 8, and 78.0 on US 9 to 13.
- **Lines 612 to 627:** on US 7 and US 8 the thick zone is re-centred on the joystick. US 9 to 13 keep 63 to 93 with an ease of 12.
- **Lines 861 onward:** the measures json records the joystick angle, the thick zone and the outer radius.

## Width kept in mm along the surface, not in degrees
I compared both on US 7 and US 8 with the same quick metal probe (work-32g/zone-try2-*.log). Metal toward the bottom, 0.1 mm under the surface:

| | US 9 reference | US 7 | US 8 |
|---|---|---|---|
| Widths in mm | 1.089 | 1.089 | 1.089 |
| Widths in degrees | 1.089 | 0.839 | 0.964 |

- The degree reading differs from US 9 by 0.250 and 0.125, both over 0.05. So I kept the width in mm, by your rule.
- The mm widths are the US 9 ones: the flat part is 30 degrees at radius 13.075, with a 12 degree ease. They are scaled by 13.075 divided by this size's outer radius.

## For inside-v5: thick zone and outer radius per size
In each out/measures-merged32g-usN.json: keys `joystick_deg`, `thick_zone_flat_deg`, `thick_zone_with_ease_deg` and `outer_radius_at_joystick_x0`. Summary in work-32g/zone-per-size-32g.log. Angles are negative toward the joystick side.

| Size | Bore | Joystick | Flat zone | With ease | Outer radius at the joystick, X 0 (json) | Outer radius beside the opening, X 3.5 (measure line 12) |
|---|---|---|---|---|---|---|
| US 7 | 17.3196 | -84.0 | -68.003 to -99.997 | -55.205 to -112.795 | 12.2598 | 12.259 |
| US 8 | 18.1324 | -81.0 | -65.516 to -96.484 | -53.129 to -108.871 | 12.6662 | 12.665 |
| US 9 | 18.9452 | -78.0 | -63 to -93 | -51 to -105 | 13.0726 | 13.072 |
| US 10 | 19.758 | -78.0 | -63 to -93 | -51 to -105 | 13.479 | 13.478 |
| US 11 | 20.5708 | -78.0 | -63 to -93 | -51 to -105 | 13.8854 | 13.884 |
| US 12 | 21.3836 | -78.0 | -63 to -93 | -51 to -105 | 14.2918 | 14.291 |
| US 13 | 22.1964 | -78.0 | -63 to -93 | -51 to -105 | 14.6982 | 14.697 |

## Measure (measure_32f.py --angle; out/measure-32g-usN.log, each last line `RESULT PASS`)

| Size | Centre (line 14) | Opening (line 31) | +X / -X | Toward the block | Toward the bottom at 0.1 / 0.2 / 0.3 |
|---|---|---|---|---|---|
| US 7 | -84.000 | 6.597 x 5.600 | 0.567 / 0.567 | 4.003 (cap) | 1.094 / 1.317 / 1.489 |
| US 8 | -81.000 | 6.597 x 5.600 | 0.567 / 0.567 | 4.003 (cap) | 1.094 / 1.322 / 1.494 |
| US 9 | -78.000 | 6.597 x 5.600 | 0.567 / 0.567 | 4.003 (cap) | 1.097 (0.1) |
| US 10 | -78.000 | 6.597 x 5.597 | 0.567 / 0.567 | 4.003 (cap) | 1.219 (0.1) |
| US 11 | -78.000 | 6.597 x 5.600 | 0.567 / 0.567 | 4.003 (cap) | 1.344 (0.1) |
| US 12 | -78.000 | 6.597 x 5.600 | 0.567 / 0.567 | 4.003 (cap) | 1.467 (0.1) |
| US 13 | -78.000 | 6.597 x 5.600 | 0.567 / 0.567 | 4.003 (cap) | 1.592 (0.1) |

- The thinnest figure on every size is the X side at 0.1 mm deep, 0.567. It grows deeper: 0.649 at 0.2 and 0.689 at 0.3 on US 7 and US 8 (lines 36, 40).
- Frame clearance on US 7 and US 8: 0.099, 0.099, 0.101 and 0.099 (line 47).
- At every size the light window is at X -12.425, Y -2.950, 0.400 x 0.400 (line 48).
- Microphone seats 1.999 and holes 0.999, centred at X -11.770 and 11.770, Y -4.800. Seats 0.100 deep (lines 52 to 58).
- No slot on the -Y wall: 0 of 285 points are open (line 60).

**Script fix**
- A missing rim now counts as 0 metal and fails. The rule now applies at every measured depth, not only 0.1.
- Proof: the round-1 US 7 shape, rebuilt from the saved script (work-32g/exterior-before-zone-32g.py), now reads "metal 0.000 mm (NO RIM ...)" at 0.1, 0.2 and 0.3 and ends `RESULT FAIL` (work-32g/rimproof-measure-32g.log lines 34, 38, 42, 66).

## Comparison with merged32f (work-32g/compare-32g-us9.log to -us13.log, and -default.log)
- US 9, 10, 11, 12, 13 and the US 9 default file: every solid's largest volume difference is 0.000000 mm3 and its largest bounding-box difference 0.000000 mm (limits 0.001).
- The body boolean is 0.000000 both ways. Each log's last line is SAME.
- merged32f and merged32e still rebuild the same: same GLB bytes, same STEP once the FILE_NAME line is set aside, same json (work-32g/final-32g.log).
- 0 merged32f files in out/ changed during this task (work-32g/f-files-changed-32g.log).

## Pictures (render without a browser, work-32g/render_32g.py; both opened with Read)
- **out/merged32g-us7-before-after.png:** merged32f on the left, merged32g on the right, same camera and scale. The caption gives -78.22 and -84.14 degrees, 5.93 apart, 1.268 mm on the surface at radius 12.257 (work-32g/render-32g-us7.log).
  - On the right, both the frame and the dark strip where the thick zone ends sit lower. The gap between the opening and that strip looks the same as on the left.
- **out/merged32g-us8-before-after.png:** the caption gives -78.21 and -81.18 degrees, 2.97 apart, 0.656 mm at radius 12.664 (work-32g/render-32g-us8.log). The same lower shift, half the size.
- The caption angles come from the joystick solid's bounding box. They read about 0.2 degrees off the opening centres in the measure logs (-84.000 and -81.000), and the dashed lines do not sit on the drawn frame centres.

## Notes
- I edited measure_32f.py (`--angle`, the missing-rim fix, the rule at every depth). Its before copies are in work-32g/.
- Disk was at least 12 GB free before every heavy run (work-32g/df-*.log).
- Time: about 60 minutes asked; I worked from 03:34 to after 05:27, with two rounds.

RESULT: done, merged32g has the joystick and its thick zone at -84.0 (US 7) and -81.0 (US 8) with the zone width kept in mm, every size passes with at least 0.567 mm of metal (US 7 bottom 1.094 against 0.847 before), and US 9 to 13 are identical to merged32f.
