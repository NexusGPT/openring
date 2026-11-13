# merged32h: round, textured, more proud joystick (owner 2026-11-11)

Evidence folder: design/look/s1/out/work-32h/. Logs are there unless the path says out/. Clock: started 12:03:37, finished after 13:12 (`date` in the logs).

## Result
- All seven sizes end `RESULT PASS`.
- The thinnest metal round the round opening is 1.067 mm on the X sides at every size (rule 0.50). So the 5.4 / 5.2 fallback was not needed.
- The thumb texture is real geometry: three ridges measured at 0.700, 1.300 and 1.900 mm, each 0.250 wide, on every size.

## What changed in design/look/s1/exterior.py
Full diff: work-32h/exterior-diff-32h.log. Line list: work-32h/lines-32h.log.

- **Line 29:** new variant `merged32h`.
- **Line 600:** `H32` holds the values: opening 5.6, frame 5.4, cap 4.4, cap 0.5 more proud, edge 0.3, dish 0.25, ridges at 0.7, 1.3 and 1.9, each 0.25 wide and 0.08 high.
- **Lines 603 to 615:** merged32h takes every merged32g branch: the same angle per size and the same moved thick zone.
- **Lines 802 to 828:** the round frame, the cap and its texture.
  - Frame: a disc 5.4 across, at the same height as before (0.3 under to 0.5 over the surface).
  - Cap: a cylinder 4.4 across. Its rim is 0.900 + 0.5 = 1.400 above the frame (build log: "cap rim 1.400 above the frame (was 0.900)"). The top edge is rounded 0.3.
  - Dish: spherical, 0.25 deep, with its rim where the rounded edge starts (radius 1.9).
  - Each ridge is the cap's own top surface raised 0.08 inside a ring 0.25 wide. So it follows the dish, and the outer ridge rides onto the start of the rounded edge with no overhang.
- **Lines 842 to 846:** the round opening, 5.6 across, on the radial line at the joystick angle, through the wall.
- **Line 896:** the json records the angle, the thick zone and the radius, as for merged32g.

**Edge chamfer:** today's opening (merged32g) has none. It is a straight cut with sharp edges, so the round opening has none either.

## Per size (out/measure-32h-usN.log, run with `--angle` and `--round 5.6`; summary in work-32h/summary-32h.log)

| Size | Centre | Opening X x band | Metal +X / -X | Toward the block | Toward the bottom | Frame clearance (+X, -X, block, bottom) | Cap above the frame / above the body (highest, +X line) | Ridges (centre / width) | Result |
|---|---|---|---|---|---|---|---|---|---|
| US 7 | -84.000 | 5.597 x 5.600 | 1.067 / 1.067 | 4.003 (cap) | 1.094 | 0.098, 0.098, 0.101, 0.099 | 1.480 / 1.982 | 0.700, 1.300, 1.900 / 0.250 | PASS |
| US 8 | -81.000 | 5.597 x 5.600 | 1.067 / 1.067 | 4.003 (cap) | 1.094 | 0.098, 0.098, 0.101, 0.099 | 1.480 / 1.981 | 0.700, 1.300, 1.900 / 0.250 | PASS |
| US 9 | -78.000 | 5.597 x 5.600 | 1.067 / 1.067 | 4.003 (cap) | 1.097 | 0.098, 0.098, 0.099, 0.100 | 1.480 / 1.981 | 0.700, 1.300, 1.900 / 0.250 | PASS |
| US 10 | -78.000 | 5.597 x 5.597 | 1.067 / 1.067 | 4.003 (cap) | 1.219 | 0.098, 0.098, 0.097, 0.100 | 1.480 / 1.982 | 0.700, 1.300, 1.900 / 0.250 | PASS |
| US 11 | -78.000 | 5.597 x 5.600 | 1.067 / 1.067 | 4.003 (cap) | 1.344 | 0.098, 0.098, 0.100, 0.100 | 1.480 / 1.982 | 0.700, 1.300, 1.900 / 0.250 | PASS |
| US 12 | -78.000 | 5.597 x 5.600 | 1.067 / 1.067 | 4.003 (cap) | 1.467 | 0.098, 0.098, 0.100, 0.100 | 1.480 / 1.982 | 0.700, 1.300, 1.900 / 0.250 | PASS |
| US 13 | -78.000 | 5.597 x 5.600 | 1.067 / 1.067 | 4.003 (cap) | 1.592 | 0.098, 0.098, 0.100, 0.100 | 1.480 / 1.982 | 0.700, 1.300, 1.900 / 0.250 | PASS |

**How the metal is measured**
- As for merged32g: 0.1, 0.2 and 0.3 mm under the surface, with the rule checked at every depth. The table shows the thinnest.
- The X sides are thinnest at 0.1: 1.067. At 0.2 and 0.3 they are 1.149 and 1.189 (work-32h/measure-32h-default-try2.log).
- For a round opening the four main directions are where the metal is thinnest (the band edges run along the band). The diagonals were not measured.

**How the cap is measured**
- Heights come from scanning the joystick solid along lines parallel to the radial at the centre angle, 0.01 mm apart, out to 2.8 mm from the axis.
- Frame top: 0.500 to 0.501 above the body on the X lines. Before, the frame was the same height and the nub stood 0.900 above it, so the rim is now 1.400 above the frame.
- The highest point is the outer ridge on the rim: 1.480 above the frame and about 1.98 above the body.
- Cap centre (dish bottom): 1.651 above the body, which is 1.150 above the frame (US 9, measure-32h-default-try2.log).
- Cap edge: 2.19 to 2.20 from the axis, so 4.4 across.
- On US 9 to 13 the lines along the band read 0.01 off: ridges at 0.71 and 0.69, frame top 0.488 and 0.514. The cap stands on the surface normal, which leans about 0.3 degrees from the radial line used for the scan at 78 degrees. On US 7 and US 8 the thick zone is flat under the cap and all four lines agree.
- Microphone holes and seats and the -Y wall are unchanged from merged32g and pass at every size (each log, lines "microphone opening", "-Y wall"). The light window is gone: since 2026-11-12 the files hold no "light" solid (architecture 17.30; design/look/s1/out/no_light/notes.md), and the measuring script measure_32f.py, which expects that solid, no longer applies to merged32h.

## Earlier variants rebuild to the same files (work-32h/all-32h.log)
- merged32e, merged32f, merged32g (US 9 default) and merged32g US 7 were rebuilt with the final exterior.py into scratch folders.
- Each gives the same GLB bytes (cmp exit 0), the same STEP once the FILE_NAME timestamp line is set aside (cmp exit 0), and the same measures json (diff exit 0).
- merged32g US 7 was included because it uses the moved thick zone.
- Not rebuilt: merged32c, d1, d2, merged32f per size, and merged32g US 8 to 13. Their code paths only gained "merged32h" in the variant tests.

## Picture (out/merged32h-us9-before-after.png; render without a browser, work-32h/render_32h.py; opened with Read)
- Top row, straight along the surface normal at US 9:
  - left, merged32g: the dark rounded-rectangle nub in its rectangular frame;
  - right, merged32h: a round frame with the round cap inside it, and a thin light ring of the opening round the frame.
- Bottom row, 40 degrees from the normal from the fingertip side: the merged32h cap shows its height and its three concentric ridges round the shallow dish clearly. The straight-on view shows the ridges only faintly.
- Faint radial streaks on the body round the round opening come from the body's tessellation, not the shape.

## Problems on the way
- **First build:** the outer ridge was clipped flat at the rim, so the measure found only two ridges and failed (work-32h/measure-32h-default-try1.log). Rebuilding the ridges as the raised cap surface fixed it (try2, `RESULT PASS`).
- **First frame-fit check:** it read the round frame as 0.012 wide along the band, because the vertex projection does not work on a cylinder. It now scans the solid (try2: 5.401 x 5.400).
- **Earlier draft of the ridges** (as a shell of the dish sphere): it would have overhung the rounded edge. I replaced it before the second build.

RESULT: done, merged32h is built for US 7 to 13 with a round 5.6 opening (at least 1.067 mm of metal, rule 0.50), a round 5.4 frame and a round 4.4 cap whose rim is 1.400 above the frame with three measured ridges at 0.7, 1.3 and 1.9 mm, every size ends RESULT PASS, and merged32e, f and g rebuild to the same files.
