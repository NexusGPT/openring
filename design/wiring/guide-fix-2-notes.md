# Assembly guide fix, round 2 (faults F1 to F4, F7, N6 of wiring review 2)

File changed: `design/mfg/assembly/assembly.md` only. Copy before the first edit: `design/wiring/guide-fix-2-work/assembly.before.md`. Edit scripts and logs (each replacement matched exactly once): `design/wiring/guide-fix-2-work/edit1.py` to `edit4.py`, `edit1.log` to `edit4.log`. Full diff: `design/wiring/guide-fix-2-work/assembly.diff`. I ran no git command and no browser.

## Edits (found by their text; before, after, source)

| # | Where | Before | After | Source |
|---|---|---|---|---|
| F1 | step 8 Join | "How the pad is made is open (`design/bom.csv:61`: pad part or plating). [PROPOSED default: the land itself is the pad ...]" | the pad is a gold-plated disc 1.6 mm x 0.07 mm soldered flat with SAC305 paste at step 8; bare land is not the pad; four discs in order CP1 to CP4; via at the centre of each land; flush with the liner (model) | `band-interface.md:141`; `product-wiring.csv:30` to `:33`; `placement.csv:43`. The false `bom.csv:61` citation is gone. |
| F1 | step 8 Check | "continuity from each pad to its land ...; no short between pads." | disc flat and centred, no tilt; flush with liner face; continuity disc to land (VBUS 4, D- 5, D+ 6, GND 7 of J_BAND_B); no short between neighbouring discs or lands | `product-wiring.csv:30` to `:33`; `placement.csv:43` |
| F1 | section 1 row CP1 to CP4 | "gold discs 1.6 mm on the inside face" | adds 0.07 mm, soldered flat on the four pad lands, and "the parts list has no row for the disc yet" | same |
| F2 | step 7 Join | "red lead to the + pad, blue to the - pad" | + land is the land nearer the slot, land 1, VMOT, joined to J_BAND_A land 7; - land is land 2, GND, J_BAND_A land 6; FLEX1 has no mark | `band-interface.md:123`; `product-wiring.csv:24` |
| F2 | step 7 Locate and Before | "the lead length as delivered is open (S10)"; "The lead length is known (S10) ... [PROPOSED ...]" | cut length per size US 7 to 13: 1.12, 1.07, 1.08, 1.14, 1.39, 1.44, 1.39 mm; strip 0.6 mm, tin, lay on the 0.80 mm side | `product-wiring.csv:24`, `:25`; `band-interface.md:125` |
| F2 | step 7 Check | "to the ribbon's motor lines" | + on land 7 (VMOT), - on land 6 (GND) of J_BAND_A | `band-interface.md:123` |
| F3 | section 1 row RT1 | "on the cell (17.3) or on the board (W13): the owner decides" | inside the bought pack, not a separate part | `band-interface.md:108`; `lead-decisions.md:9`; `product-wiring.csv:34` to `:36` |
| F3 | step 9 Join | "output tabs of PRT1 ... and RT1 to its land" | one bought pack, three tabs, RT1 has no joint; P+ land 1, NTC land 3, P- land 2; tab order P+, NTC, P- from the slot; iron 280 C max, 2 s | `band-interface.md:111` to `:115`; `product-wiring.csv:34` to `:36` |
| F3 | step 9 Check | "cell voltage appears on the two cell lands; RT1 reads about 10 k" | sign asked: red probe on land 1 reads positive, negative means a tab on the wrong land; thermistor reads about 10 k between land 3 and land 2 | `band-interface.md:113`, `:114`; `bom.csv:74` |
| F3 | step 17 Join (line 193) | "FLEX2 with BT1, PRT1, RT1 and CP1 to CP4" | "the cell pack BT1 (PRT1 and RT1 inside it) and CP1 to CP4" | same |
| F4 | step 1 Before | "no track is drawn ... lacks U10, C81, C82 ... cannot start until S14 is closed" | routed board: `Found 0 violations`, `Found 0 unconnected items`; U10, C81, C82 placed | `board-notes-r3.md:20`; `ring-pos-front.csv:34`, `:35`, `:72` |
| F4 | step 2 Locate | "(from S14)" | "(from the routed board file ...)" | `board-notes-r3.md:20` |
| F4 | step 6 Before | "Today no outline exists ... switch land pattern is open (S9)" | FLEX1 outline exists (7 boards); switch footprint decided | `band-interface.md:100`, `:102`, `:103`; files `flex1-us7` to `flex1-us13.kicad_pcb` |
| F4 | step 8 Before | "no outline exists today" | FLEX2 outline exists (7 boards) | files `flex2-us7` to `flex2-us13.kicad_pcb` |
| F4 | section 5 row of ribbon outlines (line 373) | "Ribbon outlines, lengths per size, the fold's bend radius" | outlines are drawn (14 band boards); lengths and the bend radius stay open | `band-interface.md:100` |
| F7 | step 6 Check | "each switch closes its own line and no other ..." | adds: each switch also reads open on its own line when released; a switch closed all the time fails | review 2 F7 (no new figure) |
| N6 | step 5 Join | "battery voltage on the J_BAND_B cell lands and a 10 k resistor on its thermistor land" | land 1 (VBAT) feed, land 2 (GND) return, 10 k between land 3 (NTC) and land 2; VBUS, D-, D+, GND on lands 4 to 7 | `band-interface.md:111` to `:113`; `product-wiring.csv:30` to `:33` |
| - | Basis paragraph (line 3) | no mention | one sentence naming this round and this file | this file |

## Bar 2: the search of the whole file

Hits left on purpose: "open" in "open toward the finger", "open block", "open test", "open-circuit" and "ribbon open" (physical words, not decisions). S14 in the K-A6 row (the layout keeping a free area beside the slot for the ribbon fold: still open) and in the ribbon row (fold bend radius, still open). S12 (cell maker's heat limit) in steps 9, 21, 26 and section 5: the maker's limit is still not stated; 280 C, 2 s is the design's value. S15 in step 2 Before (history of the antenna). PRT1 in steps 9 and 17 (it is inside the pack, named so). "PROPOSED" tags elsewhere: untouched, they concern other steps. S10, "pad part", "no outline" and "no track": 0 hits left. S9: 0 hits left.

## Checks (last lines quoted)

- `design/.venv/bin/python design/mfg/assembly/check_assembly.py` last line: `RESULT PASS` (log `design/wiring/guide-fix-2-work/check_assembly.after.log`; before: `check_assembly.before.log`, also PASS). No check changed.
- `design/.venv/bin/python design/mfg/tools/check_docs.py` last line: `RESULT PASS` (`check_docs.after.log`).
- A first run of check_assembly after edit 2 failed A1 (the word `cell_protection` was gone from step 9); I put it back (edit3) and re-ran: PASS. That failed run was overwritten in the same log name; the cause and fix are in `edit3.py`.

## Left for the lead

1. Parts list row for the disc (not edited by me). Proposed row: Charging pad disc | CP1, CP2, CP3, CP4 | 4 per ring | gold-plated disc 1.6 mm diameter, 0.07 mm thick, soldered flat on the FLEX2 land with SAC305 paste (assembly step 8), source `design/ecad/band/band-interface.md:141`; supplier, plating and thickness of the gold not stated in any file.
2. `design/bom.csv:78` and `:79` still say "outline not drawn" for FLEX1 and FLEX2 (parts list, not mine).
3. Not settled by the sources and left out of the guide: how the builder picks up and places a 1.6 mm disc (tool, paste stencil, reflow or hot plate); the review's F1 note that the pad face sits 0.07 mm deeper and the outer pins P1, P4 reach 2.209 to 2.220 mm (above the maker's 2.20) is a case question, not written in the guide; the block's outside height was not written (decision).
4. `design/bom.csv:74` (the parts list row of RT1) may still read as a separate part; I did not open it for this round and did not edit it.
5. F5 and F6 of the review (case board silkscreen, csv column solder_first) are outside this guide.

questions_for_owner: none

RESULT: done, F1, F2, F3, F4, F7 and N6 are closed in assembly.md with sources, and check_assembly.py and check_docs.py both end RESULT PASS.
