# ring-route-d: SWIRE (U4 C3 to J1 pad 6), 2026-11-13 09:18 to 09:21

Board: `pcb/ring.kicad_pcb` from `git archive ca4d5f3c design/ecad/ring` (4651 `(segment` lines), base copy `steps/00-base.kicad_pcb`.
Scripts: route-c's `scripts/` copied to `scripts/` (paths changed to ring-route-d); new `scripts/verify.py`, `scripts/samecheck.py`, `scripts/probe_api.py`.
Rules check: `scripts/drc.sh`, run inside `pcb/` (project rules loaded).

## Base
`logs/drc-base.log`: `Found 7 violations` / `Found 18 unconnected items` (2 via_dangling, 5 track_dangling; SWIRE 1 item, list `logs/drc-base.list`).

## What walls U4 C3
`logs/near-c3.log` (0.6 mm round (3.000, -4.050)): F: the four neighbour balls at 0.5 mm (D3 ELVDD, C2 OLED_PWR_EN, C4 SGM_VON, B3 GND);
In1: SGM_AVDD track 0.35 mm south (unlocked); In2: SGM_AVIN tracks 0.37 mm north (unlocked). No room for a track between balls on F,
but a via in the ball's pad (F-In1, 0.20/0.10) keeps the rules' clearances; the run-9 router did not place one there.

## Try 1 (the only try)
`hand.py` with no rip-up: `SWIRE 3.0 -4.05 F -6.408 0.597`, `logs/01-try.log`: `SWIRE expanded 153503 found True`, board `steps/01-try.kicad_pcb` = `pcb/ring.kicad_pcb`.
Rules check `logs/drc-01.log`: `Found 7 violations` / `Found 17 unconnected items`.
- By net (`logs/nets-compare.log`): closed `['SWIRE']`; open after but not before `[]`; violations by type unchanged (2 via_dangling, 5 track_dangling).
- KiCad connectivity (`logs/verify-01.log`): cluster of J1.6 has 71 items, contains U4.C3 True, pads `['J1.6', 'U4.C3']`, nets `['SWIRE']` (base `logs/verify-base.log`: 1 item, False).
- `logs/samecheck.log`: 100 footprints identical (no part moved); 5058 non-SWIRE tracks+vias identical (nothing ripped, no locked escape changed); antenna nets 20 items and USB pair 24 items identical.
- `pcb/check_board.py` (`logs/check_board-final.log`): checks 1 to 6 pass, check 7 `7 violations ... 17 unconnected` (base build log `pcb/build-logs/5_check_board.log`: 18). It rewrote `pcb/ring-drc.json` (in this folder).

## Items added (all net SWIRE, tracks 0.100 mm, vias 0.20/0.10 mm, model mm = board mm - 100)
Full list (69 items: 62 segments F 2, In1 23, In2 28, B 9; 7 vias): `swire-items.txt` (from `logs/verify-01.log`). Vias:
- F-In1 (3.000, -4.050) in U4 C3's pad; In1-B (-0.333, -4.100); In2-B (-1.183, -3.175); In1-In2 (-1.983, -2.100);
  F-In1 (-3.108, -1.625); F-In2 (-3.608, -1.350); In2-B (-5.733, 0.150), then B to J1 pad 6 (-6.408, 0.597).
To apply to the main board: copy the 69 items of `swire-items.txt` (or the SWIRE tracks/vias of `steps/01-try.kicad_pcb`); valid only if the main board's copper near the path equals ca4d5f3c's.


## Round 2 (lead 09:21: the other 17 items, one net at a time; numbered boards in steps/, kept only if unconnected down and no net newly open)
Trap found: hand.py must load the board from pcb/ (02-sck loaded steps/...: zone refill without the project rules, GND 1 -> 5, `logs/drc-02-sck.log` 10 / 21, rejected); step.sh fixed.
- 02-sck SD_SCK from stub end (4.973,-1.365) F, no rip: `SD_SCK expanded 210 found False`; rejected (board restored).
- 03-xl2 XL2 from via (4.323,-0.652) In1, no rip: `XL2 expanded 256 found False`, `logs/drc-03-xl2.log` 7 / 17; rejected.
- 04-xl2 rip 0.5: `FAILED XL2`, 8 / 17; rejected. 05-xl2 from stub end (4.323,-1.078) In1, rip 0.5, ripped nets first: `FAILED XL2`, 11 / 17; rejected.
- 06-xl2 same, XL2 first: `logs/drc-06-xl2.log` `Found 10 violations` / `Found 16 unconnected items` (4 new locked-stub dangles); 07-fixd rejoined the 4 stub tips: `logs/drc-07-fixd.log` `Found 6 violations` / `Found 16 unconnected items`. XL2 CLOSED. Items: `xl2-items.txt` (removed 18, added 163, nets DECA, LCD_TE, MIC_B_DATA, PMIC_INT, PMIC_SDA, SD_CS, SD_MOSI, XL1, XL2; no locked item removed). XL2 closest other-net copper 0.081 mm (In1, XL1), `logs/07-xl2-gap.log`.
- 08-sck..19-sck SD_SCK (rip 0.5 / 0.8 round the A9 stub, orders varied): SD_SCK always found, but each time one rerouted neighbour stays open (PMIC_SDA, MIC_B_DATA, SD_CS, XL1, PMIC_INT in turn; `logs/drc-08-sck.log` .. `logs/drc-19-sck.log`); 12-cs, 13-cs, 20-mbd, 21-mbd (second-stage repairs) failed. Rejected; SD_SCK open.
- 22-gnd, 23-gnd GND piece (F zone island round U1 E1, `logs/islands-07.log` poly 5, no via): `GND expanded 151 found False` both; walled by NRESET In1 (locked, under the stub), C7 pad (DECA) and L2 pad (ANT1_NODE, 0.25 RF clearance) on F; ripping NRESET's unlocked copper left NRESET open (`logs/drc-23-gnd.log` 9 / 17). Rejected.
- 24-vbus direct: `U1_VBUS expanded 216 found False`. 26-vbus (rip 0.5 round the H9 stub end, U1_VBUS first) then 27-usb3 (VDD_USB_3V3 from its stub end to C10) then 28-vbus (R1 pad 2 to the net) then 29-fixd (SPARE_P1_02 stub tip rejoined): `logs/drc-29-fixd.log` `Found 5 violations` / `Found 14 unconnected items`. U1_VBUS CLOSED (2 items). Items `u1_vbus-items.txt` (diff of steps 07-fixd to 29-fixd).
- 30-decd DECD C6 pad 1 to L1 pad 2 (one F track): `logs/drc-30-decd.log` `Found 5 violations` / `Found 13 unconnected items` (DECD 3 -> 2). Items `decd-c6-l1-items.txt`.
- 31..36-decd DECD from the A6 stub end (3.997,-1.365) F to L1: direct `DECD expanded 213 found False`; with rip 0.5/0.8 DECD is found but XL2 and DECA (and more at 0.8) cannot be relaid (`logs/drc-34-decd.log` 9 / 14, `logs/drc-36-decd.log` 15 / 16); DECD last: `FAILED DECD`. Rejected; DECD 2 items open.
- 37-vmot (In1 kept off the antenna line, hand.py switch RFKEEP=0.2, window 2 mm): not found. 38-vmot without that switch: found but In1 under the line (`logs/38-vmot-rf.log` -0.080 mm): NOT kept. 39-vmot (RFKEEP 0.2, window 5 mm): tail-A via to U11 pin 1, `logs/drc-39-vmot.log` 4 / 12; 41-vmot C84 to the net: `logs/drc-41-vmot.log` `Found 4 violations` / `Found 11 unconnected items`. VMOT CLOSED, no VMOT copper on In1 (`logs/41-vmot-rf.log`: B 0.015 mm plan-view from the line corner, In2 0.483, F 0.565). Items `vmot-items.txt` (74 added, nothing removed). Note: hand.py lays 0.100 mm tracks, also for this supply.
- 42..44-vbat U11 pin 4 start: `VBAT expanded 1` (pad start walled). 45-vbat (rip 0.5 round U11 pin 4, VBAT from C83 first, RFKEEP 0.2): `logs/drc-45-vbat.log` 4 / 10. 46..49-vbat tail-B via to C83: not found (also rip 1.0). 50-vbat (target any VBAT copper): found but 71 clearance errors (hand.py gave a PWR net only 0.125 to others; DRC's PWR gap is 0.10): REJECTED; hand.py fixed (PWR gap also when the routed net is PWR). 51-vbat same job: `logs/drc-51-vbat.log` 3 / 9.
- 53-vbat C21 to U4 A1 (rip 0.4 round A1, SGM_AVIN etc. relaid) 4 / 8, 54-fixd (SD_MISO leftover removed) `logs/drc-54-fixd.log` 3 / 8; 56-vbat U2 D1 stub tip (8.060,-2.130) to the net: 3 / 7; 58-vbat south group to C21: VBAT joined but its F track cut a ground island (U9 pad 8, `logs/islands-58.log`): GND 2, rejected alone; 59/60 with F barred there: not found; 61-gnd on the 58 board: U9 pad 8 F to a F-B ground via and B track: `logs/drc-61-gnd.log` `Found 3 violations` / `Found 6 unconnected items`. VBAT CLOSED (5 items). No VBAT copper on In1 within 0.648 mm of the line (`logs/61-vbat-rf.log`). Items `vbat-items.txt` (diff 41-vmot to 61-gnd, 75 removed, 280 added, no locked item removed; it includes VMOT relaid by 45-vbat). VBAT tracks are 0.100 mm.
- 62..66 MIC_A_CLK (locked MIC_A_DATA escape at F2 ripped, rip 0.3 round the stub end): MIC_A_CLK reaches U6 (F-B via at (2.290,0.275)), but that via sits on MIC_A_DATA's In1 row, and MIC_A_DATA then finds no way out of F2 (`MIC_A_DATA expanded 453 found False`, `logs/drc-66-mad.log` 4 / 6 with MIC_A_DATA open). Rejected; same wall as route-c step 11.
- 67..72-sck SD_SCK again on the 61 board, 6 job orders: each leaves DECA and 1 to 2 more neighbours open (`logs/67-sck.out` .. `logs/72-sck.out`, 7 to 8 unconnected). Rejected.
- 73-decd DECD FB1 pad 1 to C6 (joins FB1 to the L1/C6 group without the A6 stub): `logs/drc-73-decd.log` `Found 3 violations` / `Found 5 unconnected items` (DECD 2 -> 1). Items `decd-fb1-items.txt`. 74/75-decd A6 stub end to the net: direct `DECD expanded 232 found False`; with rip 0.5, three orders: DECA and SD_MOSI not relaid (6 unconnected). Rejected.
- 76..80 GND piece round U1 E1 with NRESET's locked In1 escape ripped: GND goes F-In2 via (2.325, 0.000), then NRESET finds no way from E2 to its via (2.000,-0.002) (`NRESET expanded 167 found False`), DECD and MIC_A_DATA reopen too (`logs/drc-78-gnd.log` 7 / 6). Rejected.

- After 09:46 on the 73 board: 81-sck (via in A9's own pad): PREV JSON had been gzipped, so the skip list was empty and the run tried every open net; board put back to 73 by hand (`logs/81-sck-note.log`); `SD_SCK expanded 2311 found False`. 82-sck (A9 pad start, rip 0.5): `SD_SCK expanded 4746 found False`, rejected. 83-decd + 84-deca (DECD first, then DECA repaired): DECA, SD_CS reopen (`logs/drc-84-deca.log` 12 / 8), rejected. Board put back to 73; re-check `logs/drc-final2.log` `Found 3 violations` / `Found 5 unconnected items`.

## Final (pcb/ring.kicad_pcb = steps/73-decd, 09:44)
- `logs/drc-final.log`: `Found 3 violations` / `Found 5 unconnected items` (base 7 / 18). By net (`logs/final-vs-base.log`): open `GND 1, DECD 1, MIC_A_CLK 2, SD_SCK 1`; newly open `{}`; the 3 violations are the track_dangling stubs of DECD, MIC_A_CLK, SD_SCK.
- Closed: SWIRE, XL2, U1_VBUS (2), VMOT (2), VBAT (5), DECD 2 of 3. SWIRE still one cluster with J1.6 and U4.C3 (`logs/verify-final.log`).
- `logs/finalcheck.log`: 100 footprints identical (no part moved); antenna nets 20 items and USB pair 24 items identical; locked items removed 0; added In1 copper within 0.2 mm plan view of antenna copper 0 (closest 0.211). Copper changed: removed 130, added 714 items in 27 nets (all unlocked), full list `all-items-base-to-final.txt` (the lead applies these, or takes this board file; per-net lists swire-, xl2-, u1_vbus-, decd-c6-l1-, vmot-, vbat-, decd-fb1-items.txt are step diffs).
- `pcb/check_board.py` (`logs/check_board-final2.log`): checks 1 to 6 pass (escapes RESULT PASS), check 7 `3 violations, 5 unconnected`, `RESULT: FAIL, 1 problems`, exit 1.
- XL2 closest other-net copper 0.081 mm (In1, XL1, its crystal partner), `logs/final-xl2-gap.log`. New supply tracks (VBAT, VMOT) are 0.100 mm wide (hand.py's width); current capacity not checked.
- What walls the rest: SD_SCK (A9 stub between the A8 DECA and A10 SPARE_P2_00 stubs; any SD_SCK exit via takes the via spot one of DECA, MIC_B_DATA, PMIC_SDA, SD_CS, XL1, PMIC_INT needs); DECD A6 stub (same strip; F blocked by the locked GND F track at x 4.323 to y -2.215, In1/In2 under A6 are XL1/LCD_TE locked escapes); MIC_A_CLK (C7 pad west, its exit via lands on MIC_A_DATA's In1 row); GND E1 piece (NRESET locked In1 under the stub, C7 DECA pad and L2 ANT1 pad on F with the 0.25 RF gap).
- Disk: every numbered step board (170, incl. 01-try and 73-decd) is packed byte-identical into `steps-boards.tar.xz` (`logs/pack_steps.log`: `members 170 verified identical 170`), the separate .gz copies then removed; step rules-check JSONs gzipped. Folder 43M (`du`). The final board is `pcb/ring.kicad_pcb` (= 73-decd.kicad_pcb in the archive); `steps/00-base.kicad_pcb` kept as is.
RESULT: blocked, 13 of the 18 items closed (SWIRE, XL2, U1_VBUS, VMOT, VBAT, 2 of DECD) and the rules check prints Found 3 violations and Found 5 unconnected items (base 7 and 18, logs/drc-final.log); SD_SCK, DECD (A6 stub), MIC_A_CLK and the U1 E1 ground piece stay walled by locked escapes in the U1 A-row strip and round C7.
