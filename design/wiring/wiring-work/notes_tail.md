## Step 7. Lead's ruling and the ring board's round 3 (08:10 to 08:17)

- Ruling of the lead (message received after the first report): a new state `specified and landed` for a carrier that is a lead, wire, tab, spring pin or a part's own cable (every end pad or pin drawn with its net, no open connection at that pad, carrier fully specified: colour or marking, gauge or model, cut length per size or "not size dependent", which end is soldered first where the files say). A line is complete only in `drawn and routed` (copper) or `specified and landed`. The screen cable gets one line per contact that carries a signal.
- build_wiring.py (copy before the change: wiring-work/build_wiring.before-ruling.py; patch wiring-work/patch_ruling.py, log `patched 10`): new columns carrier_marking, carrier_gauge_or_model, solder_first, spec_missing; function spec_state; the WIRING_STRICT switch is gone. The screen lines cite the maker drawing's contact numbers (screen-cable-study.md line 48, sch-notes.md line 309) and the cable's thickness and pitch (lines 46, 49); DISP1 pin 3 and J1 pin 3 (MTP, no net) have no line.
- check_wiring.py (copy: wiring-work/check_wiring.before-ruling.py; patch wiring-work/patch_check.py, `patched 7`): new checks `incomplete` (a line not complete) and `state-kind` (`drawn and routed` on a non-copper carrier, or `specified and landed` on copper or without its specification); the terminal set leaves out pins with no net and prints them; the counts line prints the share complete.
- The build script parsed after the 07:58 disk-full failure of one edit: it ran at 07:58 onward many times, and `py_compile` of the three scripts gave exit 0 at the start of this step (wiring-work/compile-0816.log, empty).
- Two builds on the same ring board file (time 08:08:50) differed (wiring-work/diff-fields-run8-run9.log): KiCad's list of unconnected items named different pads of the large nets in the two runs. The per-pad state is now taken from KiCad's copper connectivity (a pad is open when its copper cluster holds at most half of the pads of its net); after that two builds are byte-equal (wiring-work/cmp-run10-run11.log and cmp-run12-run13.log, empty, cmp exit 0).
- The ring board was rewritten at 08:08:50 for round 3: J1 now stands on B.Cu (the screen face) and the board is unrouted (rules check at 08:11:39: 133 violations, 237 unconnected items, wiring-work/drc json of that build). So the 14 screen lines and ANT1 pad 4 come out `drawn, not routed`, and the J_BAND lands show "open on main board" in the column main_board_land (that column is information; the band lines' carrier is the band circuit, which is routed).
- connections.md second pass (copy before: wiring-work/connections.before-ruling.md; script wiring-work/apply_connections2.py, `cells changed: 8 of 8`; diff wiring-work/connections2.diff; 22 rows with 8 cells, wiring-work/connections-fieldcount2.log): cells R5, R11, R12, R13, C1, C2, C3, C5 and a second dated note (08:12).

## Step 8. Final runs (08:16:29 to 08:16:53, wiring-work/final3-run.time)

- Disk before: 25 GB free (wiring-work/final3-run.time first line).
- Build twice, exit 0 each, cmp exit 0. Check exit 1 (wiring-work/check-final3.log): 89 terminals with a net required, 89 in exactly one line; no-connect pins not required: 2 (DISP1.3, J1.3). Last line, verbatim:
  `RESULT FAIL lines 67, drawn and routed 24, specified and landed 10, drawn, not routed 24, stated in text only 9, not drawn 0, complete 34 of 67 (51 percent), problems 33 (checks failing: incomplete)`
- The 33 lines that fail `incomplete`, with what is missing:
  - W028 (R8), W033, W034, W035 (R10): stated in text only; PRT1 and its board copper are drawn in no file.
  - W039 (R12, ANT1 pad 4 GND): main board copper not joined (round 3 routing).
  - W040 to W053 (R13, 14 screen contacts): J1 pads not joined on the main board (round 3 routing); cable specification complete.
  - W054 to W057 (R15): pairing ring pad to case pin stated in text only.
  - W058 (R16): no conductor by design; stated in text only.
  - W059, W060 (C1, C2, case cell leads): gauge of the cell lead in no file.
  - W061, W062 (C3, TH1 leads): marking and gauge of the thermistor leads in no file.
  - W063 to W067 (C5, case wires): colour or marking of the wire in no file (30 AWG and cut lengths are given).
- Broken copies (wiring-work/broken-final4.log): the good csv fails only `incomplete` (33 lines); each of 6 copies exits 1 and adds new FAIL lines of its own check only: terminal-twice (2), terminal-missing (1), ends-disagree (1), lead-length (1, on wire W063; a first try on the motor lead also tripped state-kind, which is correct but not "only its check", wiring-work/broken-final3.log), proof-text (1), state-kind (1). Last line `BROKEN COPIES PASS: 6 copies, each fails its named check with new FAIL lines and no other new failure`.
- Drawing (wiring-work/draw-final3.log): `csv lines: 67`, `conductors drawn: 67`. Seen in wiring-work/pictures/final3-svg.png: the legend now has five styles; green solid lines for the 8 switch "inside the part" lines and the 2 motor leads; blue dashed for R13 (14 lines), ANT1 pad 4, C1, C2, C3 and C5; orange dash-dot for R8, R10, R15, R16; black for the band circuit and antenna copper; no red line.

## Files delivered

- design/wiring/product-wiring.csv (67 lines plus header), system-joints.csv (9 typed rows), build_wiring.py, check_wiring.py, draw_wiring.py, product-wiring.svg, product-wiring.pdf, connections.md (Part 1 "Drawn?" cells and notes), this file; work files in design/wiring/wiring-work/.
- How to run: `python design/wiring/build_wiring.py`, then `python design/wiring/check_wiring.py` (both re-run themselves under KiCad's Python), then `design/.venv/bin/python design/wiring/draw_wiring.py`; `design/.venv/bin/python design/wiring/wiring-work/make_broken.py` makes and checks the 6 broken copies.

## questions_for_owner

none

## missing in the design files

| File | What a line needs | Conductors that wait |
|---|---|---|
| design/ecad/ring/pcb/ring.kicad_pcb | J1 pads and ANT1 pad 4 joined to their nets (round 3 routing; J1 already on the screen face) | W039, W040 to W053 |
| design/ecad/ring/netlist.csv and parts.csv (or a cell maker drawing on file) | PRT1 as a part with its output tabs P+, P-, NTC and RT1 on it | W028, W033, W034, W035 |
| no file today (for example a system netlist of ring and case) | one file holding both ends of each ring pad to case pin contact; the spring pin stroke is also unconfirmed (design/case/case-architecture.md line 123) | W054 to W057 |
| none needed | R16 has no conductor by design | W058 |
| design/ecad/case/pcb/board-notes.md (or case-bom.csv) | gauge of the case cell's flying leads | W059, W060 |
| same | marking (or "either way round") and gauge of TH1's leads | W061, W062 |
| same | colour or marking of the 30 AWG wires W1 to W4 and W7 (case-bom.csv line 27 says only "D+ D- twisted") | W063 to W067 |

RESULT: done, the 67-line wiring list is built from the files and check_wiring.py ends RESULT FAIL honestly with 34 of 67 lines complete and 33 incomplete lines listed with what each waits for, 0 not drawn.
