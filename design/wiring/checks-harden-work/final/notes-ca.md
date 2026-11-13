
## 3. check_assembly.py (fault I3)

Rules added (`check_assembly.py` lines 263 to 526; header items (l), (m), (n)); the script takes `--joints FILE` and `--wiring FILE` besides the guide path:

| rule | what it compares | data |
|---|---|---|
| T1 (c) citation holds what its sentence names | for a `file:N` citation: the designators, part names, nets and part models of its item of the sentence (or of its table row) against line N of the cited file | `.csv` tables (not line 1): designators and part names must be in the row's key cells (columns ref, reference, part, item, net, name, *_ref), nets and models anywhere on the row; groups "a, b" and ranges "a to b" share the text before them; the end line of a range is read against the group; finding ids (F6, K15, W12) are no designators. Prose files: only band-interface.md, process.md, hotbar-joint.md (a token or a shared content word of the item). `TOKEN_FORMS`, `PROSE_FILES` |
| P1 (a) paste on the ribbon lands | from joints.csv: the J_BAND land rows (15), their group sizes (J_BAND_A 8, J_BAND_B 7), "paste printed ... in pass P of step S"; the guide step S must say the lands get paste, name PASS P and the two group sizes, and the Join of the hot bar step must say "on the solder layer that step S put on the N lands" (N the total) | read from joints.csv |
| L1 (b) which land gets which tab, lead, disc | from product-wiring.csv: tab P+/NTC/P- to land and net; the lands order; motor lands (+ red, joined to tail land 7; - to 6); disc lands (VBUS 4, D- 5, D+ 6, GND 7); the same facts in the orientation text of joints.csv; guide steps 7, 8 and 9 must say the same, in the forms the check reads (an unreadable form fails) | read from the two tables |

Reviewer's faults: result before and after.

| reviewer's copy | before (`fakes-check_assembly.log`) | after (isolated copies made from the live guide, same text change; table below) |
|---|---|---|
| G1 reintroduced (no paste on ribbon lands, step 14 on bare lands) | passed | `G1_reintroduced_both_steps`: `P1 FAIL step 2 says the ribbon lands get no paste, joints.csv says they get paste`; each half alone also fails (`G1_step2_only_no_paste`, `G1_step14_only_bare_lands`) |
| three cell tabs on swapped lands | passed | `cell_tabs_swapped`: `L1 FAIL step 9 puts tab P+ on land 2 (GND), product-wiring.csv has land 1 (VBAT) ...` |
| citation to a line that holds other text | passed | `citation_prose_wrong_line` (band-interface.md:123 to :3): `TOKEN line 141: ... band-interface.md:3 holds none of GND`; also `citation_bom_other_row`, `citation_placement_final_other_row`, `citation_netlist_other_row` |
| the 5 other fakes | failed | all still exit 1 (`rev_nocheck rev_noresult rev_flood rev_empty rev_cite2`, and the isolated `step_without_check_field`, `no_result_line`, `steps_twice`, `empty_file`, `citation_past_end`) |

The reviewer's own three files (`rev_g1`, `rev_tabs`, `rev_cite`) were made from the guide of review 4; they now fail on many lines of the live repository (45 stale bom citations and the rows added to placement.csv), so they do not show the new rules alone: the isolated copies do.

The 45 wrong `design/bom.csv:N` citations of fault H5 (reviewer's list `review4-work/bom-cites-judged.csv`) against the guide of review 4 (`review4-work/fakes-ca/honest.md`, the reviewer's honest copy): `assembly/bom-cites-45-list.log` ends `wrong citations 45, rejected by T1 41, not rejected 4`; none of the 5 right citations is rejected (`assembly/compare-bom-cites.log`: `right but rejected (false alarms): []`). The 4 it does not reject: `96 bom.csv:67`, `96 bom.csv:69` (a range inside a long list in which the wrong row's own designator C71 is also named), `162 bom.csv:48` (the sentence "The protection limits are known from the cell maker" names no part), `402 bom.csv:55` (the table row names the dam by words only). The live guide no longer cites those 45 (guide-fix4 corrected them): at the end `T1` finds 26 other citations wrong (below).
