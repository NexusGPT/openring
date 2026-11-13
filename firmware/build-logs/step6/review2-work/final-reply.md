Verdict: PASS against the pass line. 0 blocker and 0 major are open; the fix round adds 10 minor findings and 3 notes.

Review: firmware/docs/step6-review-2.md
Raw outputs: firmware/build-logs/step6/review2-work/

- **Pin:** the export SRC is commit c26ae988. I compared each of the 38 files (the 37 of the diff plus design/firmware.md) with `git show c26ae988:<path>`: 38 of 38 equal. The diff af085a68 to c26ae988, made again, is byte-identical to fix-round.diff (37 files, 1283 lines added, 80 removed).
- **Bar A (R6-01 to R6-06): all 6 CLOSED.** In each case the code matches the cited FW lines. Each has a case with numbers typed from the specification and a broken copy whose text matches once in the pinned rrec.c. In run u3 each copy fails its named case on both boards.
- **Bar B: all closed.** R6-07, R6-08, R6-09, R6-10, R6-12, R6-13, R6-14, F1, F2 and R6-17 are CLOSED. R6-11 is RULED by the changed FW l.218 and l.1065.
- **Bar C:** I read every hunk (37 files). The six B2 safety rules still hold. New minor findings:
  - R2-01: the unmount retry runs without the glue's lock and waits up to 5 s. A step on another thread can move the state to RECORDING meanwhile, and the retry then unmounts the card that RECORDING needs.
  - R2-02: the end record 0x0290 can carry a stale errno 0, against FW l.1234.
  - R2-03: one step can now hold the glue's lock for about 15 s (5 s finish, then two 5 s unmount waits).
  - R2-04: ship mode goes on after a failed unmount.
  - R2-05: ship mode now waits for the screens thread with no time limit (rscr.c:554 to 556).
  - R2-06: a latched VBUS_OUT can be handled after a later VBUS_IN.
  - R2-07: the T-SIGN case checks the recording lengths only from below and has no broken copy.
  - R2-08: the FW l.179 case has no broken copy of its own. It failed under unmount_result_dropped only because the case before it failed.
- **Bar D:** R2-09 (minor): FW l.1204 still says "the same 26 codes", but the new row l.1234 is a 27th code.
- **Bar E:** 65 of 66 sampled citations match. The miss (R2-10, minor): the notes put the abort's `rxf_finish` at rrec.c:533; it is at rrec.c:509. An earlier look gave 59 of 66, because my own probes used case names with the `test_` prefix that twister drops; I fixed the probes and ran it again.
- **Rests on reading only:** no build or run (the brief forbids them). Every pass and every failing copy comes from the logs fix1-rec-u2, u3, c1 and c2. I could show that the server ran the pinned files for rrec.c only, through the line numbers in u3's copy diffs. R2-01 and R2-03 to R2-06 come from reading the code and the thread model.
- **Audit:** the final audit of the review file found every claim matched (audit.run3.out). Its last line, verbatim: `AUDIT 198 claims checked, 0 without a match`. Earlier looks: audit.run1.out had 91 misses and audit.run2.out had 1, all faults of my audit script or a citation I then fixed.

questions_for_owner: none
