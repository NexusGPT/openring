The case rows are filled and make_gaps.py is fixed. check_joints.py now ends `RESULT FAIL 110` (it was 114). The result stays blocked: 8 of those lines are a limit of check rule R4, not a missing file. Notes: design/mfg/assembly/guide-joints-notes.md.

**Case rows (commit 9e09f881)**
- Every case step number in the table is raised by one: old steps 3 to 9 are now 4 to 10.
- P-case_main is at case step 1, with the stencil lined up by its openings.
- The four spring-pin rows and P-case_pins are at case step 4, using the paste file `case_pins-F_Paste.gbr`.
- The citations of board-notes.md now point at the new lines; I mapped them from the case helper's before copy.
- The guide itself did not change, and it still says nothing about how the slits look (grille).

**What the 110 failing lines wait for**

| Waits for | Rows | Lines |
|---|---|---|
| Board helper: the 15 J_BAND paste openings | 15 | 30 |
| Board helper: change C3 | 1 | 1 |
| C1 | 7 | 14 |
| C1 and C13 | 12 | 24 |
| C13 | 10 | 10 |
| C2 and C13 | 4 | 8 |
| C2 | 7 | 14 |
| You: R4 cannot read the ring openings | 5 | 8 |
| You: P-case_main check of the hidden joints | 1 | 1 |

That is 101 lines waiting for other helpers and 9 waiting for you.

**Decision needed (R4):** R4 only counts paste openings stamped as single shapes. The case helper drew the four rings as outlined circles instead. My own reader `ring_openings.py` finds all of them: `RESULT ring openings on pin pads: 4 of 4`, each on its pin pad, 1.100 mm inside and 1.700 mm outside. A copy with P1 moved finds 3 of 4, so the reader does catch a missing ring. I did not edit check_joints.py. Either the table helper teaches R4 outlined circles, or the case helper stamps a ring shape at each pin.

**Case main board:** P-case_main keeps one open item. Case step 1 (e) itself leaves the hidden joints under U1 and the thermal pad of U2 without a check, and leaves the accept rule open, for you.

**make_gaps.py:** only the three changes you allowed (diff in `logs/make_gaps.diff`). joint-gaps.md now reports `gap lines 57 complete 42 unplaced 0 []`. I ran the 13 tests from a copy with the same sha256 in my work folder: `TESTS PASS 13 of 13 as expected`. They test check_joints.py; none of them covers make_gaps.py.

**Your order for steps 14 to 17:** it matches the guide as written, so nothing changed there.

**Other checks:** `check_assembly.py` still ends `RESULT PASS`. On the way, one run gave `RESULT FAIL 125`, because my renumbering raised one tag twice; I fixed it before the final run.

questions_for_owner: none

RESULT: blocked, check_joints.py ends `RESULT FAIL 110`: 101 lines wait for the board helper and changes C1, C2, C13, 8 for your decision on R4 and the ring openings, 1 for you on the hidden case board joints.
