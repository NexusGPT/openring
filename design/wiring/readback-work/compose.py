import os, datetime
W = os.path.dirname(os.path.abspath(__file__))
pre = open(W + '/board_readback_prereg_frozen_copy.md').read() if os.path.exists(W + '/board_readback_prereg_frozen_copy.md') else open(W + '/board-readback_prereg_frozen_copy.md').read()
tables = open(W + '/results/tables.md').read()
LL = ['logs/p1_ring.log', 'logs/p3_ring.log', 'logs/p3_band.log', 'logs/p3_case.log', 'logs/p4p5.log', 'logs/pilot_all.log', 'logs/pilot_scorer_rerun.log', 'logs/pilot_solver.log', 'logs/hand_check.log', 'logs/expected_vs_found.log', 'logs/p2_ipc_diff.log', 'logs/xcheck_clear.log', 'logs/xcheck_sw.log', 'logs/version_check.log', 'logs/audit_prev.log']
def _last(f):
    ls = [l for l in open(W + '/' + f, errors='ignore').read().splitlines() if l.strip()]
    return '- %s: `%s`' % (f, ls[-1][:230] if ls else '(empty)')
lastlines = '\n'.join(_last(f) for f in LL)
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
body = '''
## 1. Results (computed %(now)s; tables rebuilt from results/*.json by readback-work/make_tables.py; log lines in readback-work/logs/)

Everything is computed from the fabrication files (Gerber copper, Excellon drill, IPC-D-356) by readback-work/rb_lib.py (reader, rasteriser, connectivity), rb_res.py (mesh resistance, drawn-copper graph, impedance formulas), run_p1.py (P1 and P2), p3_ring.py, p3_band.py, p3_case.py (P3), p4p5.py (P4 and P5). A pixel is 0.005 mm (ring, band) or 0.010 mm (case boards, and 0.050 mm for the case GND solve); a clearance read from a pixel raster reads slightly high (0.125 against 0.122 at the antenna in the board-file cross-check below).

Short answer: on none of the 17 boards does the fabrication copper join two nets or split one (shorts 0, opens 0; the ring board agrees on the IPC-D-356 route too). Both planted faults were found by the Gerber route and neither by the IPC-D-356 route. The power paths meet every limit the design writes. The controlled lines do not meet the plan: antenna clearance and ground reference, the USB pair gap, one crystal length and all four crystal clearances.

%(tables)s

### How to read the P1 and P2 verdicts
- P1 verdict words follow the frozen rule (section 0.2): a board is FAIL if shorts, opens or missing pads are not zero, and I counted a reference of the netlist that is in no fab file of any board of that netlist as missing. That is why ring (BT1, DISP1, RT1: the cell, the screen, the cell thermistor; 19 netlist rows, logs/p1_global.log) and case_main (BT1, 2 rows) are FAIL with 0 shorts and 0 opens, and why the 7 flex1 boards are FAIL with 8 missing pads each (SW1, SW3, SW4, SW5 pins 1 and 2). Cause checked: the board file footprint Alps_SKTAAAE010_pads34 holds only pads 3 and 4 (logs/xcheck_sw.log), and band-interface.md line 103 says terminals 1 and 2 are not soldered because the part joins 1 to 3 and 2 to 4 inside. So these FAILs are a netlist-versus-footprint difference that the design already documents, not a copper fault. By the lead's own words (no two nets joined, no net split) all 17 boards are clean.
- P2 detection criteria are met (cut copy: exactly one open, LCD_SCK; join copy: exactly one short, LCD_MOSI with LCD_SCK; nothing else differs from the control). The formal P2 line FAILs only on its first clause, "control passes P1", because the control is the ring board again and inherits the ring's P1 FAIL from the three off-board references above. The control and the re-saved control have 0 shorts, 0 opens and 0 missing pads on the ring's own pads.
- IPC-D-356 route: the .ipc356 files of the control, the re-saved copy, the cut copy and the join copy are identical (0 differing lines, logs/p2_ipc_diff.log) while the Gerber copper layer of the edited layer differs by 2 lines. The IPC-D-356 file KiCad writes lists pad and via net assignments, not copper, so it cannot see an opened track or a joined pair of nets (as written in M9 before the run). Also found: its reference field is 6 characters, so J_BAND_A and J_BAND_B both read "J_BAND" (15 records); I resolved them by the pad coordinates (ipc_truncated_refs_resolved in results/p1_ring.json).
- Cut: segment of LCD_SCK, 1.675 mm on In2.Cu from (101.750, 97.450) to (103.425, 97.450), first in descending length whose removal raised KiCad's unconnected count by one (logs/p2_make_cut.log). Join: one 0.285 mm segment on In1.Cu from (104.973, 101.074) to (104.692, 101.122), width 0.100 mm (logs/p2_make_join.log); KiCad's own count stayed 0 after the join, so KiCad's connectivity does not flag it either.

### Reading of P3, P4, P5 verdicts (stricter reading where the text read two ways)
- P3: the mesh figure and the track-sum figure agree where both exist (ring VBAT to U11 pin 4: 92.18 and 93.66 mohm; ring VMOT: 205.26 and 210.55 mohm; band US 13 VMOT: 47.33 and 49.67 mohm). The mesh includes pads and via lands, the track-sum does not. 6 ring loads of VDD_1V8 and 14 band lines have no track-sum figure (the drawn-track graph did not reach both pads, mostly GND copper drawn as wide strokes); the mesh figure stands alone there. The via steps are the brief's 1 mohm per layer step; the ring has no figure for the barrel plating. The case boards' stackup is not in their board files; I used the design's own power_width.py line 3 (outer 35 um, inner 17.5 um), deviation D2.
- P3 VMOT sum: ring VMOT plus band VMOT plus band GND at US 13; the ring GND plane return is not solved (not asked), so the sum is a lower bound on the true loop; the sum stays far under the 264 mV limit (55.33 mV at 175 mA, table above).
- P4.4: the plan's own check (91.4 ohm at 0.100 / 0.075) is reproduced (logs/pilot_solver.log, expected_vs_found.log). The drawn pair is wider apart: gap 0.0778 mm at the tightest, 0.1387 median, 0.175 modal; Zdiff 92.10 / 101.90 / 104.70 ohm. The text of P4.4 did not say which gap; I took the stricter reading (all three inside 81 to 99), so FAIL. Under the min-gap reading alone it would be PASS.
- P5.XL1: the shortest drawn path pad to pad is 9.697 mm: 8.897 mm of track (equal to the 8.90 mm of board-notes-r3.md line 54) the last track end sits on the corner of the X2 pad 1 land, 0.794 mm from the pad centre (logs/dbg_xl2.log, logs/dbg_xl.log), and the path ends at the pad centre. By the frozen path rule FAIL; on track only (8.897 mm) it would be PASS.
- Cross-check of the clearances from the board file through pcbnew (logs/xcheck_clear.log, tracks, vias and pad outlines, zone fills excluded): antenna 0.122 mm (raster 0.125), XL1 0.0850 (0.0873), XL2 In1 0.0896 (0.0919), XL2 B.Cu 0.0911 (0.0939), XC1 0.1010 (0.105), XC2 0.1018 (0.103). The XL2 F.Cu figure differs (0.1376 against 0.0990) because the Gerber copper includes the L1 ground pour, which the cross-check leaves out. So the failures do not come from the raster.
- Already there: board-notes-r3.md line 54 states the crystal clearances 0.085 and 0.090 mm and "Plan d.4 (0.20 mm) is not met"; the same figures are found here from the fabrication files.
- Antenna reference (P4.3): two uncovered spots under the line draws: 255 pixels at x 101.928 to 102.043, y -99.663 to -99.568 (0.7 mm from ball C1) and 2846 pixels at x 90.643 to 91.243, y -105.958 to -105.843, which lies inside the plan's copper-free antenna zone (R2.0 point 2, X -13.60 to -8.75; the plan's ball C1 at X 2.698 is X 102.698 in the Gerber, so the offset is 100 and this cluster lies inside the zone; logs/limit_quotes2.log). The plan says both "L2 solid ground under the whole line" (d.1) and a copper-free zone there (R2.0): the plan disagrees with itself at the end of the line.
- Also found, not a pass line: the USB pair has L2 ground under only 16.877 percent of its pixels and 19144 pixels of other-net L2 copper under it (results/p4p5.json P4_3u), against plan d.2 "reference L2 solid"; its nearest other-net L1 copper is 0.0900 mm. The crystal lines are drawn on other layers than the plan says: XL1 only on L2, XL2 on L1, L2 and L4, XC1 and XC2 on L3 (plan d.4 says XL on L2 then L3).
- Antenna Z0 sensitivity to the dielectric constant (not on file for the 106 prepreg; plan value 4.1, the board file's stackup block also says 4.1): 50.38 ohm at 3.9 and 47.36 ohm at 4.5, both inside 45 to 55.

## 2. Deviations and changes after the freeze (each reason, and what it redid)
- D1 (pilot finding, before the P1 main run): the pin board's wire pads are named WP1 to WP7 in the fab data while the netlist names the wires W1 to W7; with only P1 to P4 and E1 expected, no net of case_pins had two pads, so a planted open could not show (logs/pilot_all.log before the fix). I added the pairing of build_boards.py line 61 (WP1 to W1 and so on) as expected pads. case_pins went from 5 to 10 pads compared; the earlier result is kept in results/v2_before_D1/.
- D2: the case boards' files hold no stackup block (M5 said to read it there). I used power_width.py line 3 (35 um outer, 17.5 um inner). The case P3 figures depend on it.
- D3: after the pilot showed that the first rasteriser (PIL polygon fill) made every track one pixel wider (about 3 percent too low a resistance against the analytic value on a straight test track; the log of that first pilot run, logs/pilot_solver.log, was overwritten by the rerun, so that raw record is lost and the figure is not repeated here), I replaced it with an exact pixel-centre rasteriser (mesh 1.0000; 45 degree test 1.0199). Redone with it: every P1 and P2 run, the pilots (pilot_scorer, pilot_all, hand_check, pilot_solver), all P3 and P4/P5 runs. Earlier logs and results are in logs/v1_pil_raster/ and results/v1_pil_raster/; no P1 result changed.
- D4: the drawn-track graph (used for lengths and the track-sum cross-check) was corrected five times after first runs showed paths missing: pad chords at zero resistance, flashes as nodes, snapping of end points within 3 um, joining overlapping lands, joining an end point lying inside another track. Earlier logs are in logs/v1_chord_R/. These changed only the cross-check figures and the lengths (XL1, XL2 got a path); the mesh resistances did not change.
- D5 (clarification of M2): PRT1 is not in the ring netlist; its pads were expected as pad 1 VBAT, pad 2 GND, pad 3 NTC (band-interface.md lines 111 to 113, build_band.py line 345).
- D6: the USB "nearest other-net copper" was first computed for D+ only (logs/v1_chord_R/p4p5_v6_usb_dp_only.log: 0.1200 mm); the board-file cross-check showed 0.0850 mm for the pair, so I redid it for both legs (0.0900 mm).
- D7: P4.4 and P5.XL1 readings as stated in section 1; they were not fixed in the freeze text.
- D8: the working tree of design/ecad/case was being edited by another agent while I ran (55 files differ from b9ec3cfa; logs/version_check.log). The case boards and netlist are therefore read from a git archive of b9ec3cfa extracted into readback-work/src_b9ec3cfa (a read of the repository, no write to it). The first case runs (working tree) are kept in logs/v3_worktree_case/ and results/v3_worktree_case/; they gave the same P1 figures and the same P3 case figures. The ring and band inputs have no difference between b9ec3cfa and the working tree (logs/version_check.log).
- Open finding (case_pins VRING, WP1 to P1): mesh 0.44 mohm against 2.15 mohm for the track sum, a factor of about five at sub-milliohm scale; cause not found; the verdict (0.17 mV from the mesh figure; the track-sum figure of 2.15 mohm is below 1 mV at 0.400 A; limit 901 mV for both boards) is the same under either figure.
- Not blind: the expectation file expected_vs_found.py was written after the runs from the design documents' own stated values (its first lines say so); the blind expectations were those of M9 and the pilot checks.
- Git: I ran no git write (the brief forbids it); the freeze text is saved as readback-work/board-readback_prereg_frozen_copy.md for the lead's commit; the pre-registration commit before the first run did not happen and the lead must commit.

## 3. What was not run, and why
- Route A (IPC-D-356) for the case boards and the 14 band boards: no .ipc356 in their fab/ folders; I did not export one.
- A broken-copy test on boards other than the ring (the brief asks for the ring only).
- The ring GND plane (not asked); ring VMOT sum therefore lacks the ring GND return.
- Ring VBAT drop: no written limit in the files read, so REPORT. Case cell lines: no written limit, REPORT.
- Wires, the cell, connector and pogo-pin contact resistance, and the cell tabs: not in fab files.
- Nothing measured on hardware. The dielectric constant 4.1 is the plan's assumption (a coupon measures it).
- The 14 flex*-drc.rpt files and check_band.py were not touched or run. No browser, no web request.

## 4. Proof files
Scripts, logs and results in design/wiring/readback-work/ (size in logs/misc_counts.log): logs/p1_*.log, logs/p3_*.log, logs/p4p5.log, logs/pilot_*.log, logs/hand_check.log (22 of 22 hand labels agree; labels in hand_labels.csv, excerpts in logs/hand_excerpts.log), logs/limit_quotes.log (the quoted limit lines), results/verdicts.json (every verdict with its source field), results/tables.md, CHECKLIST.md, the audit script audit.py with its output audit.log (its last line is quoted below).

### Last line of each proof file cited (verbatim, read by compose.py when this report was written)
%(lastlines)s

## 5. questions_for_owner
1. Should off-board references (cell BT1, screen DISP1, thermistor RT1) and the unsoldered switch terminals (SW pins 1 and 2 on four switches) count as "missing" in a fab-versus-netlist check, or be listed as known off-board parts? It decides whether P1 reads 17 of 17 or 8 of 17.
2. Which USB gap is the design gap, the plan's 0.075 mm or the drawn 0.14 to 0.175 mm? At 0.175 mm the pair is about 105 ohm differential, outside the plan's 90 ohm plus or minus 10 percent.
3. Is the antenna feed's reference to be solid under its last 0.6 mm (plan d.1) or copper-free (plan R2.0)?
4. What are the copper weights ordered for the case boards (I used 35 um outer, 17.5 um inner)?
''' % dict(now=now, tables=tables, lastlines=lastlines)
RESULT = 'RESULT: done, 1 of 5 pass lines met (P3) and 4 failed (P1, P2, P4, P5); by item 28 met, 18 failed, 25 reported only; no short or open on any of the 17 boards and both planted faults were found by the Gerber route.'
open(W + '/../board-readback.md', 'w').write(pre.rstrip('\n') + '\n' + body.rstrip('\n') + '\n\n' + RESULT + '\n')
print('composed', len(pre), len(body))
