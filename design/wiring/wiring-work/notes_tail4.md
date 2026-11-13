## Step 12. Fifth pass: cell pack and pad-to-pin rules (08:31 to 08:35)

- Lead's ruling 08:31: BT1 + PRT1 + RT1 is one purchased part. build_wiring.py (copy before: wiring-work/build_wiring.before-pass5.py; patch wiring-work/patch_pass5.py) now builds the R10 tab lines (BT1 pin 1, BT1 pin 2, RT1 pin 1 to FLEX2 lands PRT1 1, 2, 3) and the R8 line (RT1 pin 2, `inside the part`) from band-interface.md section 5 (lines 110 to 117 cited by pattern), and the four R15 pad-to-pin lines from the netlists, the board files, case-architecture.md (pin model, soldering) and design/case/pin-travel.md line 16 (maker working-height range). These 8 rows left system-joints.csv (copy before: wiring-work/system-joints.before-pass5.csv; wiring-work/sj-trim.log `kept 1 of 9`): only R16 stays typed by hand.
- R15 rule: complete only when design/wiring/ring-case-contact.csv pairs the pad with the pin at all 7 sizes and every in_range is yes, both ends drawn with their nets, the maker range cited. The file did not exist at the final build (`ls` in wiring-work/final7-run.time), so the 4 lines are `stated in text only` with that reason. The column names of that file are not known to me; my reader accepts pad / ring_pad, pin / case_pin, us / size / ring_size and in_range; any other naming leaves the lines incomplete with "columns not understood", never complete. Tested on two made-up fixtures (wiring-work/contact-test/, values invented for the test only, output to its own folder): all 7 sizes yes gives `specified and landed` for all 4; one `no` for P2 at US 11 leaves W055 `drawn, not routed` with "in_range not yes for P2 at lines 19". product-wiring.csv was unchanged by the tests (wiring-work/cmp-after-contact-test.log empty, cmp 0). build_wiring.py takes WIRING_CONTACT and WIRING_OUT only for such tests.
- Final runs 08:33:08 to 08:33:49 (wiring-work/final7-run.time): ring board file time 08:08:50 before and after; disk 22 GB free; build twice, cmp exit 0; check exit 0, last two lines verbatim:
  `COMPLETE 47 of 66 conductors (71 percent)`
  `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 23, drawn, not routed 15, stated in text only 5, not drawn 0, complete 47 of 66 conductors (71 percent), problems 0`
- `--require-complete` (wiring-work/check-final7-require.log) exit 1, 19 incomplete lines: W039 to W053 (ring board round 3: ANT1 pad 4 and J1 pads not joined) and W054 to W057 (contact file missing). Last line verbatim:
  `RESULT FAIL lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 23, drawn, not routed 15, stated in text only 5, not drawn 0, complete 47 of 66 conductors (71 percent), problems 19 (checks failing: incomplete)`
- Broken copies (wiring-work/broken-final9.log): `BROKEN COPIES PASS: 7 copies, each fails its named check with new FAIL lines and no other new failure`. Drawing (wiring-work/draw-final7.log): 66 conductors and 1 sensing gap drawn; pictures wiring-work/pictures/final7-svg.png and final7-pdf-1.png.
- connections.md: cells R8, R10, R15 and a fourth dated note (08:35); 22 rows with 8 cells (wiring-work/connections-fieldcount4.log).

## Files delivered

- design/wiring/product-wiring.csv (67 lines: 66 conductors and 1 sensing gap), system-joints.csv (1 typed row, R16), build_wiring.py, check_wiring.py, draw_wiring.py, product-wiring.svg, product-wiring.pdf, connections.md, this file; work files in design/wiring/wiring-work/. Commands: top of this file.

## questions_for_owner

none

## missing in the design files

| File | What a line needs | Conductors that wait |
|---|---|---|
| design/ecad/ring/pcb/ring.kicad_pcb | J1 pads and ANT1 pad 4 joined to their nets (round 3 routing; J1 already on the screen face) | W039, W040 to W053 |
| design/wiring/ring-case-contact.csv (being written by the case helper) | each pad paired with its pin at all 7 sizes, every in_range yes | W054 to W057 |

R16 (W058) needs nothing: a sensing gap with no conductor, counted apart.

RESULT: done, 67 lines (66 conductors, 1 sensing gap) built from the files; check_wiring.py passes for consistency and with --require-complete fails honestly at COMPLETE 47 of 66 conductors (71 percent), the 19 incomplete lines waiting only for the ring board's round 3 and design/wiring/ring-case-contact.csv.
