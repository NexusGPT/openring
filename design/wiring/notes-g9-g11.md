# Notes G9 and G11 (2026-11-13)

All paths under design. Work folder: wiring/g9-g11-work/.

## G9: gap from E1 to the band's inner face

No file held the number, so wiring/g9-g11-work/e1_gap.py computed it from case/out/case_params.json (x_b 5.5201, cx and ri per size; log: wiring/g9-g11-work/e1_gap.log). E1 is on the front face of PCB2's inner island (x = x_b); the band's inner face at lateral offset y is x = cx - sqrt(ri^2 - y^2).

| Size | gap at strip centre line (y = 0) | gap at strip side edge (y = +-1.95) |
|---|---|---|
| US 7 | 2.197 | 1.975 |
| US 8 | 2.171 | 1.959 |
| US 9 | 2.145 | 1.942 |
| US 10 | 2.119 | 1.925 |
| US 11 | 2.093 | 1.907 |
| US 12 | 2.067 | 1.888 |
| US 13 | 2.041 | 1.868 |

Range: 2.04 to 2.20 mm at the centre line, 1.87 to 1.98 mm at the strip's edges (strip width 3.9 mm, board-notes.md conflict 7). Cross-check in the log: the face radius implied by the inner pin height (case_params.json lines 73 to 120) differs from ri by +0.0035 to +0.0037 mm only, so the band face is the bore.

The gap does not depend on the ring block's height: it uses only x_b (the pin board's place along X, set by the pin height at US 10) and the band's inner radius; the block is not in this path. It would change only if x_b moves, or if E1 moved out of the band's 8.0 mm width in Z.

Old value 2.28 to 2.42 mm was the C5d pin-height range, not a gap (the gap is the pin height plus 0.06 to 0.08 mm of band curvature at y = 0).

Lines changed (before, then after):
- case/case-architecture.md line 64: was `2.28 to 2.42 mm from the band's inner face (pin heights): bench B3 repeats | case.py`; now `2.04 to 2.20 mm from the band's inner face on the strip's centre line (1.87 to 1.98 mm at the strip's side edges) ... (REPLACED 2026-11-13 (was 2.28 to 2.42 mm "(pin heights)", the old C5d range)) ... | design/wiring/g9-g11-work/e1_gap.py and e1_gap.log`.
- case/case-architecture.md line 152: was `2.28 to 2.42 mm from the band's inner face: bench B3`; now `2.04 to 2.20 mm ... e1_gap.log; REPLACED 2026-11-13 (was 2.28 to 2.42 mm): bench B3`.
- case/case-architecture.md line 44 (Pads row): the same kind of stale value. Was `pin heights 2.280 to 2.418 mm, spread 0.138 mm`; now `1.980 to 2.150 mm, spread 0.170 mm (REPLACED 2026-11-13 (was ...))`, source out/case_params.json lines 118 to 120. (r3-fix-notes.md line 23 had named lines 42/204 as stale; those two are outside my Owns and still stale.)
- wiring/system-joints.csv row R16: gap text and the quote of the line-64 citation changed to 2.04 to 2.20 (old value kept in the cell as REPLACED). product-wiring.csv rebuilt with build_wiring.py (log: g9-g11-work/build.log); W058 now reads 2.04 to 2.20.
- Fourth place, not in the review: wiring/draw_wiring.py `carrier_label` had the gap hard-coded as "2.28-2.42 mm" and drew it on the sheet (W058 label). Now 2.04-2.20 (pdftotext: `W058 no conductor, gap 2.04-2.20 mm`, g9-g11-work/after3.txt).

## Findings outside my Owns (not changed)
- The holder's front wall in front of E1 is 1.6745 mm (case_params.json line 652), not "1.97 mm" (case-architecture.md lines 220 and 235, board-notes.md line 189, and the R16 cell "through the 1.97 mm pin holder wall", which cites line 235 and so was left to match it). Owner of case-architecture.md lines 220/235 and board-notes.md must correct; then R16 follows. The touch threshold depends on this wall too.
- case-architecture.md lines 42 and 204 still say the old pin spread/heights (see above).

## G11: cut label in box R8

Cause (draw_wiring.py, old line 178): label lines were cut to `nlines = int(box height / 2.3)`, which is 1 for a one-row box. The probe (g9-g11-work/draw_probe.py, probe.log) found 13 boxes losing text, not only R8 (R3 B, R4 A and B, R7 A and B, R8 A, R11 A, C1 A and B, C2 A and B, GAP A and B): R8's lost "one purchased part" and "RT1"; the others lost the reference line (e.g. "SW2").
Change: new functions `block_list` (the label lines, never cut) and `panel_row` (the panel's row height grows to hold the longest label: lines x 2.6 mm + 1.2 mm per box); drawing uses it. Old copy: g9-g11-work/draw_wiring.before.py; old PDF: g9-g11-work/product-wiring.before.pdf.
Regenerated with `design/.venv/bin/python design/wiring/draw_wiring.py` (log draw3.log: 67 lines, 66 conductors drawn, 1 gap; columns 283.4 and 248.6 mm of 297): wiring/product-wiring.pdf and product-wiring.svg.
Extracted label (pdftotext, after3.txt lines 82-83, 98-99): `cell pack BT1 + PRT1 + RT1,` / `one purchased part` (R8 also shows `RT1` as the third line in the picture).
Picture (pdftoppm, g9-g11-work/full-1.png whole page, r8final-1.png crop at 250 dpi): box R8 shows three full lines, "cell pack BT1 + PRT1 + RT1," / "one purchased part" / "RT1", with margin inside the frame; the right box "inside the pack" intact; the panels above (R7) and below (R9, R10) are not overlapped; all other boxes show their reference line (SW2, J_BAND_A, PRT1, ANT1, BT1, W5, E1 ...). Picture r8final-1.png was rendered before the W058 text change (a label only, same size); final-1.png is the final page render and was not re-read.

## Bar
- case/check_case_docs.py: last line `RESULT PASS (0 findings)`, exit 0 (g9-g11-work/check_case_docs.log).
- wiring/check_wiring.py --require-complete: exit 0, last line `RESULT PASS lines 67 (66 conductors, 1 sensing gap), ... problems 0` (check_wiring.log). Input changed (system-joints.csv R16), list rebuilt.
- mfg/tools/check_docs.py: last line `RESULT PASS`, exit 0 (check_mfg_docs.log).

Not done: bench B3 is unchanged; the touch threshold was not re-estimated for 2.04 to 2.20 mm.


## Second pass (lead's grant)

1. Holder wall. case_params.json line 652, key `pin_holder.wall_in_front_of_E1` = 1.6744946. case.py line 877 computes `(x_b - g) - interp(0, ys_h, xf_h)`: from the holder's front face at y = 0 to the front of the inner island's pocket (g = 0.02 mm), the LCP in front of E1. The old 1.9745 (case-model-r4-notes.md line 42) was the same distance at x_b 5.8201; x_b is now 5.5201 (case_params.json), 0.30 mm less: 1.9745 - 0.30 = 1.6745. So 1.97 was stale, not a different distance. Corrected to 1.67 (old kept as REPLACED 2026-11-13): case-architecture.md line 235 (the line 220 the lead named holds no 1.97 now; its quote is in c5d-open-points-handover.md line 44), board-notes.md line 189 (three places: wall, key value, limit sentence), system-joints.csv R16 cell and its line-235 quote; product-wiring.csv rebuilt.
2. case-architecture.md: the stale pin heights and spread are at line 57 (lines 42 and 204 do not hold them now): now 1.980 to 2.150, spread 0.170, stroke 0.370 (case_params.json lines 118 to 121), old kept. Line 44 was done in the first pass.
3. Search (g9-g11-work/find_stale.py, hits g9-g11-work/grep_hits.log, case hits grep_case_hits.log). Corrected: the lines above. LISTED only, not changed:
   - design/case/case-architecture.md lines 219 (history of C5d, already marked as history) and 221 (pitch study at C5 figures: 0.148 to 0.138, "2.28 mm available"; a past study from out/work_c4);
   - design/case/case-notes.md lines 41 and 70 (C5d section, 0.144 / 2.277 to 2.421, design height 2.35: history of that round);
   - design/case/case-model-r4-notes.md line 42, design/case/r3-fix-notes.md line 23 (records); design/case/c5d-open-points-handover.md line 44 ("1.97 mm LCP wall"; a record, and w11-item-values.md line 168 and deferred-items.md line 97 quote it);
   - design/wiring/connections.md lines 61 and 414 (2.28 to 2.42, and "1.97 mm pin holder wall" on line 61), deferred-items.md lines 97 and 276, deferred-triage.csv line 88 (1.97), case-marks-2-notes.md line 11, wiring-review-2.md line 40, wiring-review-3.md line 46 (records), board-notes copies in design/mfg/assembly/guide-joints-work/ (snapshots), design/mfg/assembly/guide-joints-notes.md line 68 ("G9 (touch gap 2.28 to 2.42 mm): open");
   - explorer/dist/files/design/case/* and look/* (copies of the case files: case-architecture.md lines 15, 28, 35, 122, 123, 190, 192; case-notes.md lines 23, 52; look/c4_* ; out/work_c4/sec7.md) : stale until the explorer is rebuilt.
   Not case values (no action): design/architecture.md line 80 (2.42 mA), board-readback.md lines 160 and 191, firmware-evidence b5_pin.md, thin-notes.md line 290, parts/ui-pass3.md line 196, node_modules.
   Owner needed for: connections.md 61/414 and deferred-items/triage (wiring docs outside my grant) and the explorer copies.
4. Rebuilt with build_wiring.py (build2.log) and draw_wiring.py (draw4.log: 67 lines, 66 conductors, 1 gap). Final page render g9-g11-work/final2-1.png (130 dpi, after the last change), read by me: every box has its full text (R8 three lines "cell pack BT1 + PRT1 + RT1," / "one purchased part" / "RT1"; R10 the same plus "BT1, RT1"; SW2, J_BAND_A, PRT1, ANT1, BT1/W5, TH1, E1 all shown), no box text overlaps a frame or another panel, W058 reads "no conductor, gap 2.04-2.20 mm", both columns end above the footer.
5. Last lines (logs *2.log, check_boards.log in g9-g11-work/):
   - check_case_docs.py: `RESULT PASS (0 findings)`, exit 0.
   - check_wiring.py --require-complete: `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 25, specified and landed 41, drawn, not routed 0, stated in text only 1, not drawn 0, complete 66 of 66 conductors (100 percent), problems 0`, exit 0.
   - mfg/tools/check_docs.py: `RESULT PASS`, exit 0.
   - ecad/case/pcb/check_boards.py (CHECK_BOARDS_TMP=g9-g11-work/cb_tmp, KiCad Python via the script's own re-exec): `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0.

RESULT: done, wall (1.67 mm), pin heights and gap corrected in the case files, drawing re-read, four checks pass; listed stale copies remain in records, wiring docs and the explorer.
