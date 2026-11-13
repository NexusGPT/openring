# Inside model v7: handover

Work 2026-11-11, 21:32 to 22:55 (clock from `date`). Project at commit b37b157 plus the working tree as found. No git command was run. Detail: `design/mech/thin/thin-notes.md` section "Model v7"; architecture section 17.31.

## What changed
- **Recording light removed** from the model, parts list, wiring, behaviour rules, maker files and assembly order: LED1, R41, Q2, light guide LG1, light plug LP1, the 0.50 mm board hole, the foam notch, the print window. The recording sign is the screen (firmware 3.2, test SIGN-1, factory test T-SIGN).
- **Lit screen over the whole face:** same panel (17.30); clear adhesive ADH1 has the panel's full outline (checked); glass print black with no opening.
- **Round joystick** (exterior merged32h), one fixed choice per item:
  - opening round 5.60 mm at -84.0 (US 7), -81.0 (US 8), -78.0 deg (US 9 to 13);
  - frame FRM1 (new reference): Ti-6Al-4V ring, CNC turned, polished, gloss black coating with the body, outer 5.40, bore 4.80, 1.30 long (0.80 under the surface to 0.50 over), bonded with 3M Scotch-Weld DP420 Black, 24 h at 22 C;
  - cap CAP1: Covestro Makrolon 2407 colour 901510, injection moulded, SPI A-2, top face VDI 3400 Ref 21; shank 4.40; rim plane 1.400 over the frame top; edge 0.30; dish 0.25 (sphere r 7.345); ridges at 0.70, 1.30, 1.90 (0.25 wide, 0.08 high); flange 6.90 (+0/-0.10) x 6.40 x 0.40; length flange underside to rim 4.517, to the outer ridge 4.597;
  - five Alps SKTAAAE010 under it; long press 1.0 s on SW2 records. No record button.
- **Pads** unchanged at X -1.0 (test a -1.0000 at every size).
- **Fault fixed:** the model's surface probe started at r 14.5, under the US 13 surface (14.695): v6 to v6.3 put the US 13 joystick 0.195 mm too low. v7 places it on the surface.
- **Fault fixed:** the maker-file exporter lost solids of shared parts (build123d compound re-parenting): the first v7 cap file held only its flange. It now copies each solid and stops on any solid-count or volume difference.

## Files changed
Lead (this lane):
- design/mech/thin/thin.py, check_thin.py, placement.csv, layers.json, out/thin-inside.glb, out/thin-inside.step, out/triangles.txt, thin-notes.md, v7-handover.md; out/v7/ (logs, broken copies, probes, table_v7.py, table_v7.md); out/v7-export/export_size.py (v6.3 copy export_size_v63.py) and its export logs.
- design/architecture.md: header line, section 2 (joystick row; light rows removed; removal line), 3 (VDD_3V0 row), 4 (light row), 9 (light bullet struck), new 17.31.
- design/mfg/parts/: export_parts.py (copy export_parts_v63.py), index.csv, every maker file regenerated; new joystick-cap/; joystick-nub/, light-guide/, light-plug/ moved to parts/old_v63/ with index_v62.csv and the old notes.
- design/mfg/drawings/: every sheet redrawn (65); joystick-cap.svg/.pdf new; joystick-nub, light-guide, light-plug sheets moved to drawings/old_v63/.
- design/mfg/tools/draw.py (copy draw_v63.py); design/mfg/parts-notes.md; mfg-notes.md; part-map.csv (joystick-cap row); specs/joystick-nub.md (flange tolerance, files, open point 8); assembly/assembly.md (placement.csv citations renumbered, rows 6 and 7).
Helper lanes (their notes list each file):
- Wiring and parts list: design/bom.csv, bom-notes.md, ecad/ring/ make_netlist.py, gen_sch.py, check_netlist.py, bom_refs_snapshot.csv, sch-notes.md and the regenerated netlist.csv, parts.csv, symbols.csv, additions.csv, open-pins.csv, *.kicad_sch, ring.kicad_sym, ring-kicad.xml, ring-schematic.pdf, erc-report.*; notes ecad/ring/v7-wiring-notes.md.
- Behaviour rules: design/firmware.md (40 blocks), firmware-check.py (check 21); notes design/firmware-v7-evidence/v7-firmware-notes.md.
- Maker specs and assembly: mfg/specs/joystick-nub.md, cover-glass.md, main-board.md, body.md, band-liner.md, band-flex-tails.md; mfg/assembly/assembly.md, check_assembly.py (rule H1); notes mfg/specs/v7-refresh-notes.md, mfg/assembly/v7-update-notes.md.

## Checks (last line, log)
| Bar | Check | Last line | Log |
|---|---|---|---|
| 1 | inside model, default US 9 | `RESULT PASS pairs=1080 parts=47` | design/mech/thin/out/v7/check_us9_default_v7.log |
| 1 | broken copy, LED1 put back | `RESULT FAIL pairs=0 parts=48` | out/v7/broken_led/check.log |
| 1 | broken copy, cap at old height | `RESULT FAIL pairs=0 parts=47` | out/v7/broken_height/check.log |
| 2 | fit check US 7, 8, 9 | `RESULT PASS pairs=1080 parts=47` each | out/v7/size_us7_v7.log, size_us8_v7.log, size_us9_v7.log |
| 2 | fit check US 10, 11, 12, 13 | `RESULT PASS pairs=1034 parts=46` each | out/v7/size_us10_v7.log to size_us13_v7.log |
| 2 | cap top against the exterior's, every size | -0.002 to -0.010 mm | out/v7/probe/probe_captop.log |
| 3 | parts list | `failures 0`, exit 0 | out/v7/final/check_bom.log |
| 3 | wiring (netlist, ERC) | `RESULT PASS netlist netlist.csv`; ERC 0 errors 0 warnings | design/ecad/ring/evidence/check_v7_lead_final.log, erc-report_v7_lead_final.txt |
| 3 | wiring broken copies | `RESULT FAIL 8`, `RESULT FAIL 1`, `RESULT FAIL 1` | design/ecad/ring/evidence/v7/broken/check_case1.log to check_case3.log |
| 3 | behaviour rules | `0 failures`, exit 0 | out/v7/final/firmware_check.log |
| 3 | behaviour rules broken copies | exit 1 each | design/firmware-v7-evidence/check-broken-led1.log, check-broken-record-button.log, check-broken-screen-dark.log |
| 3 | assembly order | `RESULT PASS` | out/v7/final/check_assembly.log |
| 3 | assembly broken copies | `RESULT FAIL H1` | design/mfg/assembly/v7-check-fail-proof.log |
| 3 | maker specs | `RESULT PASS` | out/v7/final/check_docs.log |
| 3 | maker files | `RESULT PASS files=88` | out/v7-export/check_parts_v7.log |
| 3 | drawings | `65 drawn, 0 failed`; cap `1 drawn, 0 failed` | design/mfg/tools/logs/draw_v7.log, draw_v7_cap.log |
| 3 | removed-part grep over the owned files | 24 of 153 hits lack a "removed in v7" marker; each is a kept file name (joystick-nub.md), the power chip's own pin LED1, a v5 history file, or a FRM1 or cap line | out/v7/final/grep_removed.log |
| 4 | one choice per item | the joystick, frame, glass print, board and adhesive rows carry fixed values | specs/joystick-nub.md, bom.csv rows CAP1 and FRM1 |

All out/ paths are under design/mech/thin/.

## Not proven
- The model's broken copies ran with the pair test skipped. The pair test's own fail proof is the v6 one.
- Cap feel, tilt clearance in motion, sealing of the round opening (B9), the DP420 bond on the coating, the power of the always-lit recording dot: bench only.
- Proposed but not tested: the tolerances under 0.5 mm in joystick-nub.md and the two clean-and-inspect steps 4 and 22 in assembly.md.
- Behaviour rules still count 4.1 mA while recording (architecture 17.26). Without the light the figure is 2.6 mA plus the dot, which has no number yet.
- Still naming a removed part, outside this lane's files:
  - design/ecad/ring/pcb/ (build_board.py, check_board.py, board-notes.md, placement-report.csv, ring.kicad_pcb, drc-report.txt): R41, LED1 and Q2, lines in ecad/ring/v7-wiring-notes.md.
  - (closed 2026-11-12: the exterior files were rebuilt without the separate "light" skin solid; design/look/s1/out/no_light/notes.md);
  - firmware/ code: one comment in tests/core/src/test_round2.c:243, and the state table lacks the new SIGN row.
- Older multi-solid maker files of v6.2 may have lost solids the same way; they are history and were not re-examined.
- Pictures of the inside were not re-rendered.

RESULT: done, inside model v7 (round joystick, no recording light) passes its check at US 7 to 13 and the default US 9 with both broken copies failing, and the parts list, wiring, behaviour rules, maker files and assembly order follow it with each check passing
