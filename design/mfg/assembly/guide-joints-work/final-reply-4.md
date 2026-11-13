The joint table is complete: all 99 rows have every field and check_joints.py passes. One thing waits for your answer: two old tests of the table helper now fail, because a land they use as their bad example has its paste opening since your ring board commit. Notes: design/mfg/assembly/guide-joints-notes.md.

**Last lines, as asked**
- check_joints.py: `RESULT PASS joints 99`
- make_gaps.py: `gap lines 0 complete 99 unplaced 0 []`
- check_assembly.py and check_docs.py both still end `RESULT PASS`. The 786 guide citations in the table and the 25 case citations and quotes check out with 0 problems.

**What I did after the ring board landed (commit 796a0086)**
- **Pad copy:** I copied the 17 board files into joint-table-work/boards and ran dump_pads.py. No land moved. What changed: paste layer flags, and R73 and C90 are now on the ring board.
- **Paste files:** ring-F_Paste.gbr has an opening on all 15 ribbon lands. ring-B_Paste.gbr has J1's 17 openings and none on the 12 test pads.
- **Rows filled:** the 15 hot-bar rows, P-ring-F (all parts, the ribbon lands included) and P-ring-B (all parts except the 12 test pads). P-case_main was already filled from case step 1 (g).
- **Guide:** step 2 now says these openings are in the delivered files, and that R73 and C90 sit on the parts face. Section 5 no longer lists the openings as open.

**A fix inside my own R4 code**
- **What happened:** the first run gave `RESULT FAIL 17`, all on J1. The pad copy records each pad's size but not its rotation, and J1's pads are turned 90 degrees on the board, so its openings did not fit the unturned size.
- **The fix:** a region or a filled dot may now fit its pad either way round. After that, `RESULT PASS joints 99`.
- **Control:** with the ring board's regions moved 1.0 mm, R4 fails 1 line on J-W001-A and 17 on P-ring-B. So R4 still catches openings that are off their land.

**Decision needed: the two old tests**
- **Result:** the table helper's tests now end `TESTS FAIL 14 of 16 as expected`.
- **Why:** the two "paste_no_opening" cases use land J_BAND_A:1 as their example of a land without paste. Since your ring board commit that land has its opening, so the cases no longer fail as they should.
- **My proposal:** point the example at TP1:1 of ring-B_Paste.gbr, which the design leaves bare on purpose. That edits an existing test, so I asked you by message and have not done it.

**Moved guide citations in other files**
- **Corrected:** I changed a citation only where the citing line quotes text found on both the old and the new guide line. I did this in the two live specifications only:
  - process.md line 55: 144 became 150.
  - process.md line 163: 253 became 262.
  - board-notes.md line 293: 99 became 103.
- **Not changed:** process.md lines 73 and 178 and board-notes.md line 318. Their quotes describe text my rewrite replaced, or the quote is not on the old line.
- **Records not edited:** reviews, triage tables and state records cite the guide as it was when they were written. Changing them would make them wrong for that version. Over all design files the scan found 8 more citations it could have corrected safely and 85 it could not; all are listed in logs/fix_cites-dry.log for you.

RESULT: blocked, check_joints.py ends `RESULT PASS joints 99` and make_gaps.py `gap lines 0 complete 99 unplaced 0 []`; the table helper's tests end `TESTS FAIL 14 of 16 as expected` until you allow moving one old test example to TP1:1.
