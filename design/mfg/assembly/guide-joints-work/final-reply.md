My part of the guide rewrite is finished. Rows of the joint table still wait for other helpers, so the result is blocked. Notes: design/mfg/assembly/guide-joints-notes.md. Logs: design/mfg/assembly/guide-joints-work/logs/.

**What changed in assembly.md**
- **Step 2:** stencils of 0.10 and 0.075 mm, NP505-HR paste, the profile written out, and paste on the 15 ribbon lands in pass 2. The board is never reflowed a third time (Hirose allows 2 cycles). The stencil is lined up by its openings. The eight accept rules are in plain words. R73 and C90 are now named.
- **Step 4:** inspection only, no washing and no brushing.
- **Steps 6 to 9:** solder, flux, tool and heat from the sheet. The probe points are named by land number. The disc height is 0.070 to 0.112 mm, and the flush check moved to step 21.
- **Hot-bar joint:** now step 14 (was 16), made on the bench on the fixture.
- **Threading:** now step 15 (was 14). Each neck slides sideways into its side slit.
- **Screen:** now step 16 (was 15), with the tool line and the T-SCREEN and T-SIGN proof before step 17.
- **Other steps:** steps 10, 19 and 21, section 4 row 10, and sections 1, 3, 5 and 6 are brought in line. K-A6 is answered. Step 25 now sends FACTORY_EXIT before reading the boot count (H19).

**Bar 1**
- `check_assembly.py` ends `RESULT PASS`. Before my edit it ended `RESULT FAIL A2`, because R73 and C90 were in no step.
- `check_docs.py` ends `RESULT PASS`.
- check_assembly.py was not changed.

**Bar 2 (check_joints.py)**
- It went from `RESULT FAIL 160` to `RESULT FAIL 114`. 62 rows have a gap and 37 are complete.
- What the 114 failing lines wait for:

| Waits for | Rows | Lines |
|---|---|---|
| Board helper: the 15 J_BAND paste openings | 15 | 30 |
| Board helper: change C3 | 1 | 1 |
| C1 | 7 | 14 |
| C1 and C13 | 12 | 24 |
| C13 | 10 | 10 |
| C2 and C13 | 4 | 8 |
| C2 | 7 | 14 |
| C6 | 5 | 10 |
| C5 | 1 | 3 |

**Bar 3 (review 3)**
- G1 to G6 each have a closing sentence; the notes quote each with its line. Example for G6, guide line 100: "So the ring board never goes through an oven a third time."
- G8 and G10 were already closed. G7 is closed by change C1, G9 by the case helper, and G11 by the wiring drawing helper (not checked).

**Bar 4 (citations by line)**
- I corrected the 786 guide citations in joints.csv; 0 problems.
- In other files 129 citations moved: 117 in design files, listed with their new lines in the notes, and 12 in logs. 21 others cite an older version of the guide.

**For you**
1. **make_gaps.py:** it groups rows by the old step numbers 16 and 15. Because of that it leaves the 15 hot-bar rows out of joint-gaps.md, and its "complete 52" should be 37. Its two tests need to become step 14 and step 16.
2. **Your confirmation:** in step 15 I lay the board into the cavity as the necks go in, because the ribbons have no free length. Step 17 then presses it down. Please confirm.
3. **Slit size:** written as "as the body drawing gives it", with no number.
4. **Old step numbers:** process.md and hotbar-joint.md still use 14, 15 and 16 in their old meaning; the notes list the lines.

questions_for_owner: none

RESULT: blocked, check_joints.py ends `RESULT FAIL 114`, waiting for the board helper's paste openings and changes C1, C2, C13, C6 and C5.
