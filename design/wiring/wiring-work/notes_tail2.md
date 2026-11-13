## Step 9. Third pass (lead's four changes, 08:19 to 08:27)

1. States: one rule only. `drawn and routed` for copper; `specified and landed` for leads, wires, tabs, spring pins and a part's own cable (every end in a board file or netlist with its net, the pad joined to its net, the specification cited: marking, gauge or pin model, cut length per size or "not size dependent"). No WIRING_STRICT switch exists in build_wiring.py (removed in Step 7). The open state of a pad is KiCad's copper connectivity (Step 7), which the check now reads too.
2. Completeness: check_wiring.py prints `COMPLETE <n> of <total> conductors (<percent>)` before the RESULT line. Without a flag the check is about consistency (incomplete lines counted, not failed); `--require-complete` adds FAIL[incomplete] per line with the new csv column waits_for (system-joints.csv got the same column for its 8 conductor rows). New check `complete-open`: a line marked complete whose board pad is not joined fails. New broken copy complete_but_open (screen contact W040 marked `specified and landed` while J1 pad 1 is open).
3. R16 (W058, carrier_kind none) stays in the csv and is counted apart: the check prints "sensing gaps, no conductor ...: 1 (W058 R16)" and the percent is of the 66 conductors; the drawing puts it in its own panel "SENSING GAP, NO CONDUCTOR" with a grey dotted line and prints the two counts apart.
4. Copper lengths against band-interface.md section 6, at US 13 (traces: wiring-work/len_cause.log, len_cause2.log to len_cause4.log, script wiring-work/probe/len_cause.py):
   - How band_calc.py measures (design/ecad/band/band_calc.py, read, not changed): it reads no track. VMOT = m1 - U_NEAR (motor land 1 position along the tail minus the near land row, U_NEAR 1.375); motor GND = (m1 + 1.0 - U_FAR) + 1.5 (motor land 2 minus the far row U_FAR 0.475, plus a fixed 1.5 commented "with the strap"); VBAT = PRT1 land 1 position minus U_FAR; cell GND = VBAT + 0.9. These are straight distances along the tail axis between land centres, with two fixed allowances.
   - My first measure (in the csv until Step 8) let the path jump at no cost wherever two copper shapes overlap without their centre lines meeting (a jog between two 0.20 tracks, a via whose copper covers a track end), so it was too short. Fixed in build_wiring.py: such a step now counts its centre-to-centre distance. The csv now holds the centre-line length of the routed copper from land centre to land centre.
   - VMOT: board copper 6.931 (F.Cu 0.475 from land 7, a 0.106 step, then 6.350 along the B.Cu line to the motor land 1 centre). band_calc 6.90 = the straight distance between the two land centres (6.900); the copper is 0.031 longer because the line steps 0.205 across (Y 80.005 to 79.800).
   - Motor GND: board copper 8.980 (F.Cu stub 0.450 from land 6 to its via, 0.125, a 0.615 diagonal, 7.790 along the B.Cu lane to the via in motor land 2). band_calc 10.30 = straight distance 8.80 plus its fixed 1.5 for a path through the strap to land 8; the board's motor ground does not pass land 8 (path printed in len_cause4.log), so 10.30 is 1.32 too long.
   - VBAT: board copper 6.799 (0.450 + 0.275 + a 0.198 jog + 5.876). band_calc 6.74 = straight distance 6.741; the copper is 0.058 longer because of the 0.14 mm jog in Y.
   - Cell GND: board copper 8.037 (0.450 + 0.275 + 0.460 diagonal + 0.235 + 5.956 + 0.662 diagonal to PRT1 land 2). band_calc 7.64 = its VBAT figure plus a fixed 0.9; the straight distance between the land centres is 7.601 and the lane runs 0.33 mm off the land row with two diagonals, so the copper is 0.40 longer than 7.64.
   - So for all four the csv's number describes the copper in the board file; band_calc's numbers are axis distances with allowances. Its voltage drops therefore use 10.30 (too long, safe side) for the motor ground and 7.64 (0.40 short) for the cell ground. Nothing in design/ecad/band was changed.

## Step 10. Final runs of the third pass (08:26:05 to 08:26:40, wiring-work/final5-run.time)

- Disk: 24 GB free (first line of final5-run.time). Ring board file time 08:08:50 (unchanged since round 3 began).
- Build twice, exit 0, cmp exit 0 (wiring-work/cmp-run16-run17.log empty).
- `python check_wiring.py` (wiring-work/check-final5.log), exit 0. Its last two lines, verbatim:
  `COMPLETE 34 of 66 conductors (52 percent)`
  `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 10, drawn, not routed 24, stated in text only 9, not drawn 0, complete 34 of 66 conductors (52 percent), problems 0`
- `python check_wiring.py --require-complete` (wiring-work/check-final5-require.log), exit 1, 32 FAIL[incomplete] lines, each with what it waits for; last line verbatim:
  `RESULT FAIL lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 10, drawn, not routed 24, stated in text only 9, not drawn 0, complete 34 of 66 conductors (52 percent), problems 32 (checks failing: incomplete)`
- Broken copies (wiring-work/broken-final6.log): the good csv passes; 7 copies each exit 1 with new FAIL lines of their own check only (terminal-twice, terminal-missing, ends-disagree, lead-length, proof-text, state-kind, complete-open); last line `BROKEN COPIES PASS: 7 copies, each fails its named check with new FAIL lines and no other new failure`.
- Drawing (wiring-work/draw-final5.log): `csv lines: 67 = 66 conductors + 1 sensing gap`, `conductors drawn: 66 ; sensing gaps drawn apart: 1`. Seen in wiring-work/pictures/final5-svg.png: as in Step 8, plus the R16 line moved to its own grey dotted panel at the foot of the right column; the band copper labels show the new lengths (for example W021 7.786-8.980 mm, W022 5.737-6.931 mm).

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
| design/ecad/case/pcb/board-notes.md (or case-bom.csv) | gauge of the case cell's flying leads | W059, W060 |
| same | marking (or "either way round") and gauge of TH1's leads | W061, W062 |
| same | colour or marking of the 30 AWG wires W1 to W4 and W7 (case-bom.csv line 27 says only "D+ D- twisted") | W063 to W067 |

R16 (W058) needs nothing: it is a sensing gap with no conductor, counted apart.

RESULT: done, 67 lines (66 conductors, 1 sensing gap) built from the files; check_wiring.py passes for consistency and with --require-complete fails honestly at COMPLETE 34 of 66 conductors (52 percent), each of the 32 incomplete lines listed with what it waits for.
