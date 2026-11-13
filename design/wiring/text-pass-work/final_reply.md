Text pass done: 197 edits in 18 files, 80 sheets redrawn; notes in design/wiring/text-pass-notes.md (edit table in section 5, work folder design/wiring/text-pass-work/).

Checks (before and after, logs in the work folder): check_docs.py RESULT PASS; check_parts.py RESULT PASS files=104; firmware-check.py 0 failures; check_assembly.py before RESULT FAIL A2 (bom has LT1 and C89, no step named them), after RESULT PASS (I named them in step 2); check_case_docs.py RESULT PASS (0 findings); check_bom.py identical before and after, one failure, designator RC1 (the lead's row).

Redraw: draw.py final run draw_r3.log ends "80 drawn, 0 failed". Foot stiffener sheets now keep their own names. I deleted 4 stale duplicates (flex-tail-thumb-footstiffener and flex-tail-away-footstiffener, .svg and .pdf, v7 title, written by the model helper). The KEYDIMS slot line is changed but no sheet carries it (ring-assembly is not drawn by default).

Search: search_replaced.py, 32 patterns, final run 23 OPEN and 62 HISTORY hits; each OPEN hit is explained in notes section 4 (my own text, section 16 draft, correct pointers, the dam material still open).

Open, need the lead:
1. Test pad count: decision row of 05:26 drops TP2, TP13, TP16, TP22 and parts.csv holds 15 pads, but main-board.md line 6 and its last section (model helper lines) still say 19. Left at 19; everything else I wrote as 15.
2. Test pad face: decisions and main-board.md put the pads on the screen face; assembly.md (line 21, steps 4 and 5, K-A1, step 17) still says under face. That is a procedure change, left as written and listed.
Both questions were sent by message; no answer had arrived.

Not done on purpose: dimensions.csv has no comment line (exterior.py reads it, ring.py rewrites it, many documents cite its lines); the notice is in ring.py line 2, and on line 1 of mech-notes.md and CHECKLIST.md (so "mech-notes.md line 7" still opens). Screen cable, cable fold pocket and block height lines are untouched and listed. Decisions older than 03:24 (for example RT1 on the protection circuit) are not applied; listed.

Rows missing in design/bom.csv: 12 items in notes (RC1; LNR1 resin and 7.0 wide; MEM1/MEM2 Saati Acoustex 010a on tesa 61305; GSK2/GSK3 Nitto SCF, no PSA; SEAL1 tesa 61305; ADH1 tesa 69404; FOAM1 Nitto SCF AN010; GL1 AGC Dragontrail Pro; HSG1 and FRM1 coating BALINIT DLC; SEAL2 and slot sealant DP420 Black; PCB1 4 layers and 15 pads; C84 4.7 uF).

questions_for_owner: none

RESULT: done, 197 edits in 18 files (and 80 redrawn sheets); six checks end in their pass lines (check_bom fails only on RC1, as before); two questions to the lead (test pad count, test pad face) have no answer yet and their lines are left as listed in section 6.
