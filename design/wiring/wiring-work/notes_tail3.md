## Step 11. Fourth pass: case lead and wire specifications (08:27 to 08:30)

- The lead added three rows to design/wiring/lead-decisions.md (case wires W1 to W4 and W7: colour; case cell BT1 leads; case thermistor TH1 leads); maker facts in design/case/lead-specs.md. build_wiring.py (copy before: wiring-work/build_wiring.before-pass4.py; patch wiring-work/patch_pass4.py, `patched 3`) finds those rows by pattern and cites the matched text as carrier proof: wires get their colour (W1 red, W2 white, W3 green, W4 black, W7 yellow) and "30 AWG stranded hook-up wire"; the cell leads get "DNK852338 own lead as delivered (no gauge stated by the maker; polarity measured before cutting)" with red (+) and black (-); TH1's leads get "bare, no polarity" and "Semitec 103AT-2 own lead as delivered (0.5 mm tin plated 42 alloy)", soldered either way round, joint 5 mm or more from the bead (lead-specs.md line 35).
- Ring board file time: 08:08:50 before and after the final runs (wiring-work/final6-run.time); the lead says another helper is rerouting it; the build read the file as it was.
- Final runs 08:28:47 to 08:29:16 (wiring-work/final6-run.time): build twice, exit 0, cmp exit 0. `python check_wiring.py` (wiring-work/check-final6.log) exit 0; last two lines, verbatim:
  `COMPLETE 43 of 66 conductors (65 percent)`
  `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 19, drawn, not routed 15, stated in text only 9, not drawn 0, complete 43 of 66 conductors (65 percent), problems 0`
- `python check_wiring.py --require-complete` (wiring-work/check-final6-require.log) exit 1, 23 FAIL[incomplete] lines (W028, W033 to W035, W039 to W057), last line verbatim:
  `RESULT FAIL lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 19, drawn, not routed 15, stated in text only 9, not drawn 0, complete 43 of 66 conductors (65 percent), problems 23 (checks failing: incomplete)`
- Broken copies: the first run (wiring-work/broken-final7.log) failed my own rule for one copy: the lead-length copy blanked a length on wire W063, which is now complete, so state-kind fired too. The copy now also sets that line `drawn, not routed` so only the length is wrong; rerun wiring-work/broken-final8.log: 7 copies, each only its check, last line `BROKEN COPIES PASS: 7 copies, each fails its named check with new FAIL lines and no other new failure`.
- Drawing (wiring-work/draw-final6.log): `csv lines: 67 = 66 conductors + 1 sensing gap`, `conductors drawn: 66 ; sensing gaps drawn apart: 1`. In wiring-work/pictures/final6-svg.png the C1, C2, C3 and C5 lines are now solid green; the rest as in Step 10.
- connections.md (copy before: wiring-work/connections.before-pass4.md; wiring-work/apply_connections3.py, `cells changed: 4`; 22 rows with 8 cells, wiring-work/connections-fieldcount3.log): cells C1, C2, C3, C5 and a third dated note (08:29).

## Files delivered

- design/wiring/product-wiring.csv (67 lines: 66 conductors and 1 sensing gap), system-joints.csv (9 typed rows), build_wiring.py, check_wiring.py, draw_wiring.py, product-wiring.svg, product-wiring.pdf, connections.md, this file; work files in design/wiring/wiring-work/.
- How to run: `python design/wiring/build_wiring.py`; `python design/wiring/check_wiring.py` (consistency) or with `--require-complete`; `design/.venv/bin/python design/wiring/draw_wiring.py`; `design/.venv/bin/python design/wiring/wiring-work/make_broken.py` (7 broken copies).

## questions_for_owner

none

## missing in the design files

| File | What a line needs | Conductors that wait |
|---|---|---|
| design/ecad/ring/pcb/ring.kicad_pcb | J1 pads and ANT1 pad 4 joined to their nets (round 3 routing; J1 already on the screen face) | W039, W040 to W053 |
| design/ecad/ring/netlist.csv and parts.csv (or a cell maker drawing on file) | PRT1 as a part with its output tabs P+, P-, NTC and RT1 on it | W028, W033, W034, W035 |
| no file today (for example a system netlist of ring and case) | one file holding both ends of each ring pad to case pin contact; the spring pin stroke is also unconfirmed (design/case/case-architecture.md line 123) | W054 to W057 |

R16 (W058) needs nothing: it is a sensing gap with no conductor, counted apart. The case leads and wires (W059 to W067) wait for nothing since the lead's rows of 08:21 and 08:28.

RESULT: done, 67 lines (66 conductors, 1 sensing gap) built from the files; check_wiring.py passes for consistency and with --require-complete fails honestly at COMPLETE 43 of 66 conductors (65 percent), each of the 23 incomplete lines listed with what it waits for.
