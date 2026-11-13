All rows that waited for C1, C2 and C13 are filled, and R4 now reads both new opening forms. check_joints.py now ends `RESULT FAIL 33` (it was 110). What is left waits for the board helper and for you. Notes: design/mfg/assembly/guide-joints-notes.md (last line is the RESULT line).

**1. Ribbon rows (commit a3492b1f)**
- **What landed:** every FLEX1 paste file has 12 openings and every FLEX2 file has 16. All 14 drawings carry the land numbers and nets.
- **Switch and disc rows:** the 12 switch rows and the 4 disc rows name the paste file of each of the 7 sizes for their land. R4 checks every one, and none fails.
- **Board rows:** P-flex1-usN and P-flex2-usN name every pasted land of their board.
- **Motor and tab rows:** their gaps are now empty.
- **Guide:** steps 6 and 8 (lines 135 and 153) now say the paste files exist. `check_assembly.py` and `check_docs.py` still end `RESULT PASS`.
- **Control:** a copy with the FLEX2 disc openings moved 2 mm off CP1 gives an R4 failure for CP1:1, so R4 really checks these rows.

**2. Rule R4 (granted)**
- **New forms:** R4 now also accepts a stroked circle and a filled region.
  - A ring must be centred on its land, within 0.02 mm.
  - A filled dot must lie wholly on its land. This is how the FLEX2 openings are drawn: four discs off the centre of each land, not centred.
  - A region must have its centre and its whole outline on the land.
- **No other rule changed.** The diff is in `logs/check_joints.diff`.
- **Tests:** I added three cases to the table helper's tests.
  - A ring moved 2.0 mm off its pad fails.
  - A region on its land passes.
  - The same region moved 1.0 mm off its land fails.
- **Expectations:** I appended them to expect.txt before the run.
- **Test runs:** the tests ran in place, so their kept files are in joint-table-work/tests/broken/. The first run crashed on the region case (a TypeError in my code). After the fix: `TESTS PASS 16 of 16 as expected`, with the 13 old cases unchanged.
- **Effect:** the 8 R4 failures on the spring-pin rows are gone.

**3. Hidden joints of the case main board**
- **No defined test:** neither board-notes.md nor case-architecture.md defines a first power-up or factory test of the case board. They have the module's BOOT, UART and EN test pads, but no procedure.
- **Row P-case_main:** its check of the joints under U1 and under the U2 thermal pad stays MISSING, and the row says so. You write the test.

**What the 33 failing lines wait for**

| Waits for | Rows | Lines |
|---|---|---|
| Board helper: the 15 J_BAND openings in ring-F_Paste.gbr | 15 | 30 |
| Board helper: change C3 | 1 | 1 |
| You: the case board test (P-case_main) | 1 | 2 |

**Other files**
- **joint-gaps.md:** rebuilt; it reports `gap lines 17 complete 82 unplaced 0 []`.
- **Guide citations in joints.csv:** all 786 checked, 0 problems.

When the ring board's fab folder is regenerated, I fill the 15 hot-bar rows and P-ring-B and rerun.

RESULT: blocked, check_joints.py ends `RESULT FAIL 33`: 31 lines wait for the board helper's ring board paste, 2 for your case board test.
