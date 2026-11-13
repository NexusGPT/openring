# Wiring review of the ring and its case (independent, pinned b9ec3cfa)

Reviewer: independent judge (drew none of it). Written 2026-11-13 from 11:08 to 11:28 (Mac clock, `date`: 11:08:43 at the first command, 11:27:59 at the last check). Work folder: `design/wiring/review-work/` (scripts, logs, CHECKLIST.md). Nothing outside it was changed (`review-work/gitstatus-diff.log` is empty). HEAD moved to 46824af3 during the review; none of the judged files changed (`review-work/new-commits.log`).

## Verdict

**FAIL.** The wiring itself is right: every line of `product-wiring.csv` is true against the board files, the netlists and the screen drawing, all 17 boards pass KiCad's rules check with 0 violations and 0 unconnected items, the band tails mate land by land at all 7 sizes, and J1 is not mirrored. The bar fails on B4: the builder's order of work (`design/mfg/assembly/assembly.md`) still describes the board before 13 November, so a builder who follows it would put J1 and 8 other parts on the wrong face and run the screen cable the wrong way. 2 major faults, 4 minor faults, 6 notes.

| Bar line | Result | Checked (N of M) |
|---|---|---|
| B1 every connection once, both ends, carrier, join, marking, cut per size | pass | 67 of 67 lines; 67 of 67 end pairs once; 99 interface pins enumerated by me, 97 on a line (the 2 others are contact 3, no-connect, N1); 28 of 28 lead, wire, tab and cable lines with marking and 7 cut lengths or "not size dependent" |
| B2 each line true | pass | end nets: 59 lines, 262 board instances, 0 wrong; copper path: 25 lines at 7 sizes, 152 of 152; pin board copper 5 of 5; pad to spring pin pairing 28 of 28 (4 pads x 7 sizes) |
| B3 boards complete | pass with minor fault m4 | rules check 17 of 17 boards: 0 violations, 0 unconnected; pad nets: 888 pins match the netlists, 0 wrong; 5 pads with no netlist row |
| B4 nothing only in someone's head | FAIL | majors M1, M2; minors m1, m2, m3 |
| B5 interfaces agree | pass | J_BAND lands 14 of 14 band circuits; J1 15 of 15 pins, direction by coordinates; case wire pads 5 of 5 |

## Faults

| # | Severity | Where | What is wrong | Evidence |
|---|---|---|---|---|
| M1 | major | `design/mfg/assembly/assembly.md` lines 21, 55, 96, 120, 124 | The guide says every part is on the under face and the top face is bare ("the TOP face is bare and faces the screen", line 21; "parts on the under face only", line 55; step 2 reflows every part, J1 included, "to the under face of PCB1", line 96; the jig and the SWD pads are on "the under face", lines 120, 124). The board has 21 footprints on the screen face (B.Cu): C1, C14, C2, C5, C7, FB1, J1, R71, R72 and 12 test pads TP1, TP3 to TP6, TP12, TP14, TP15, TP17 to TP19, TP21. A builder doing one reflow on the under face cannot place these 9 parts (their lands are on the other face), and the test jig of step 5 meets no test pad. | `review-work/ring_sides.log` ("footprints on B (screen face): 21"); `review-work/assembly-quotes.log` |
| M2 | major | `design/mfg/assembly/assembly.md` line 201 (step 15) | "the screen's tail (`screen_tail`) folded round the board's hand end into J1 on the under face, latch closed". The design (lead-decisions.md row 65, layout C) turns the screen 180 degrees and bends the cable back under the panel at the fingertip end into J1 on the screen face, opening toward +X. The guide never says the screen is turned: the 4 lines of the file that match "180" or "turned" are about other things (lines 96, 145, 352, 369). A builder following it would try the hand-end route to an under-face J1 that does not exist, and could fit the screen unturned. The same step keeps FOAM1 as a frame, which layout C rules out (screen-cable-study.md line 207). | `review-work/assembly-quotes.log` line 201; `review-work/assembly-180.log` (4 hits, none about the screen); `review-work/check_j1.log` ("all on B.Cu (screen face): True", "opening faces +X") |
| m1 | minor | `product-wiring.csv` lines 41 to 54 (W040 to W053); no builder file | The cable's direction into J1 is right in the files but written nowhere a builder reads: contacts facing up (away from the board) after the two folds, cable entering from the fingertip side, contact 1 on the +Y side (tail B, antenna side). The csv says only "contact k of the screen cable on position k of J1" and "B.Cu". Found only by working it out from screen-cable-study.md section 4.3 and the maker drawing. | `review-work/check_j1.log`: J1 pad 1 at Y +2.097, pad 15 at Y -2.103, "Y falls from pad 1 to pad 15 (contact 1 at +Y): True"; `review-work/j1-direction-search.log` |
| m2 | minor | `design/ecad/case/pcb/case_pins.kicad_pcb` (PCB2 wings); `product-wiring.csv` W054 to W057 | P1 (VRING) and P4 (GND) sit on two separate wing pieces of the same 2.55 x 5.0 outline, each a 180 degree turn of the other; the board has no silkscreen (references on F.Fab only). Swapped wings put the case's VRING on the ring's GND pad. The right place is only a case-frame coordinate: P1 at y +3.521 (case-architecture.md line 205). The csv also does not say on which face of PCB2 the pin stands ("through hole,F.Cu,B.Cu"). Right in the files, hard to find. | `review-work/case_pins_outline.log` ("silk items: 0", wings 95.1 to 97.65 and 102.35 to 104.9); `review-work/quotes-misc.log` line 205 |
| m3 | minor | `product-wiring.csv` lines 64 to 68 (W063 to W067), column solder_first | The order of the 5 case wires is "not stated in the files": whether a wire goes on WP1 to WP7 before or after PCB2 is pressed into the holder and staked (case-architecture.md line 238 gives the pin and stake order only). | `product-wiring.csv` lines 64 to 68; `review-work/quotes-misc.log` |
| m4 | minor | `design/ecad/case/netlist.csv` against `case_pins.kicad_pcb` | The 5 wire pads WP1, WP2, WP3, WP4, WP7 carry nets on the board but have no row in the case netlist, so the netlist does not record which pin-board pad each wire starts from (the wiring table in board-notes.md does). | `review-work/check_parity.log`: "pads with a net but no netlist row 5" |
| N1 | note | `product-wiring.csv` | No line for screen contact 3 (MTP) in J1 position 3: both have no net (ring netlist.csv lines 381, 382, `no_connect`), and connections.md line 58 says so on purpose. The contact still touches position 3. | `review-work/check_cover.log` |
| N2 | note | `design/wiring/connections.md` lines 61, 65 | Stale text: E1 "copper 6 x 3 mm" (board: 3.9 x 1.15 front strip plus back pour); "SMT spring pin" (board pads go through all copper layers). | `review-work/quotes-misc.log`; `review-work/pads/case_pins.csv` |
| N3 | note | `design/ecad/band/band-interface.md` line 65 | "the pattern is NOT mirrored; the board footprint and the tail footprint use the same land numbers in the same places" holds in its own (u, v) frame only. Laid over each other as drawn, the two files are mirror images, which is what face-to-face mating needs; the mirror fit is exact and the no-mirror fit is 0.900 mm (FLEX1) and 1.292 mm (FLEX2) off. A reader overlaying the files could think a land is wrong. | `review-work/check_mating.log` |
| N4 | note | `product-wiring.csv` line 25 (W024) | Marking "blue insulation", while the motor maker allows "Black or Blue (-)" (band-interface.md line 122). | `review-work/quotes-misc.log` |
| N5 | note | `ring.kicad_pro`, `case_main.kicad_pro` | 5 rules set to ignore, none about connections: footprint_filters_mismatch, footprint_type_mismatch, missing_courtyard, track_not_centered_on_via, tuning_profile_track_geometries. | `review-work/ignored_rules.log` |
| N6 | note | ring netlist, csv W005 | The joystick's centre switch net is still named BTN_REC although the design has no record button. | `product-wiring.csv` line 6 |

## How I checked (my own scripts, not the project's checks)

- Rules check: `kicad-cli pcb drc --severity-all --all-track-errors` from each board's own folder, 17 boards one at a time at `nice -n 19` (`review-work/run_drc.sh`). Each prints "Found 0 violations" and "Found 0 unconnected items" (`review-work/drc-summary.log`). Control: a copy with the JOY_UP tracks removed prints "Found 2 unconnected items" (`review-work/broken/drc-broken.log`).
- Pads, nets and copper clusters read with KiCad's Python (`review-work/dump_pads.py` through `design/ecad/ring/pcb/run_kipy.sh`; clusters are a search over KiCad's connected items). Control: in the broken copy, J_BAND_A:1 and SW1:3 fall into different clusters (`review-work/broken/pads-broken.csv`).
- `review-work/check_lines.py`: each csv line against the board pads, the netlists, the copper clusters at all 7 sizes, once-only, cut and marking. Last line of `check_lines.log`: "lines read 67", 0 FAIL rows. A faulty csv (wrong pin, wrong signal, missing cut, duplicate line, missing part) is caught 5 of 5 (`review-work/fakes/fake1.log`).
- `review-work/check_parity.py`: board pads against netlists; a faked wrong net and a missing land are both caught (`review-work/fakes/parity/run.log`).
- `review-work/check_mating.py`: best rigid fit of each tail's lands onto the main board's lands of the same number, with and without a mirror; the face-to-face joint needs the mirror. Also checks that the rest of each tail lies outward toward the slot. Last line: "RESULT mating fails=0 of 14".
- `review-work/check_j1.py`: J1 pad positions in the ring frame, against the screen drawing (page 5, front view labelled "15 ... 1" with the cable end down, read by me) and layout C. Last line: "RESULT j1 PASS". The same check on a mirrored J1 prints "RESULT j1 FAIL" (`review-work/fakes/j1/run.log`). That the long lands are the cable side of FH35C is my reading of catalogue pages 3 and 4.
- `review-work/check_pairing.py`: pads VBUS, D-, D+, GND from the inside model's rule (thin.py lines 733, 734, 740; bore per size from SIZE_TABLE) and each FLEX2 board's pad order, against the pin board's pin positions and nets. Last line: "RESULT pairing fails=0 of 28". My lateral offsets equal the tip_to_pad column of ring-case-contact.csv (0.024 and 0.001 mm at US 7).

## What I could not check

- Pin heights and the in_range column of `ring-case-contact.csv` at each size: they need the case and ring solids (case_check.py); I checked which pin meets which pad, not how hard.
- The mapping of PCB2's KiCad x to the case's y (P1 at x 96.479 to y +3.521) is the one case-architecture.md line 205 states and case.py line 807 enforces; I did not re-derive the view of PCB2 in the holder.
- Whether FH35C has top contacts at every position (needed with the cable's contacts facing up): taken from screen-cable-study.md line 54 (catalogue page 1, "dual-sided"); I read catalogue pages 3 and 4 only.
- product-wiring.pdf was not read page by page; it was written from the csv at the same minute (both 11:07).
- No built part, no supplier contact, no browser (brief).

## questions_for_owner

none

RESULT: done, FAIL on the bar with 2 major faults (the assembly guide puts J1 and 8 other parts on the wrong face and routes the screen cable the old way), while every one of the 67 wiring lines is true against the files.
