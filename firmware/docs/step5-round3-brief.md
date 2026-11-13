# Step 5, round 3: the lead's rulings on the second review

For: the builder of step 5 (os-relay). From: the lead, 2026-11-13.
Second review: `firmware/docs/step5-review2.md` (commit d58ca1c: 11 of 14 closed, 2 partly, 1 open by ruling; new: 0 major, 2 minor, 6 notes). Read it in full first.
Version you work on: commit d58ca1c (the working folder equals it for firmware/).
Rule text changed again: read `design/firmware.md` section 7.7 "Details" (a frame already being sent when HELLO is accepted may arrive before READY and the helper ignores it; an ACTION that cannot be sent after its retries is lost).

Residual of this round: 2 minor faults and the open half of fault 3. Target: 0, or each one left open named with its reason.

1. New fault 1: remove the three logic checks that cannot fail (`test_relay.c:617`, `:627`, `:886`) and put the comment that names the two-device checks into `test_put_not_stored_before_its_last_piece` too.
2. New fault 2: in scenario H put a stage after the six 20-byte frames (the ring checks entry 0x000100a5 field by field) and a stage after REMOVE (the ring checks the id is gone and the count fell by one), then the 71-byte frame and the checks that exist. Add one broken copy that makes REMOVE of a held id do nothing only for this id's path if the existing copy `remove_ignored` does not already fail the new stage; say which.
3. Fault 3, second half (the session start after a relay HELLO, `rip.c:993`): first make a broken copy that removes that guard and run scenario B: if a named check fails, the branch is proven and you name the check. If nothing fails, add a hook under the existing option `CONFIG_RING_RELAY_TEST_HOOKS` (test ring only, as the hook of fault 5) that lets the test put the HELLO before the iPhone part's session start, add the check that the entries are kept, and show the broken copy fail it.
4. Note 6: rename the 22 stand-in checks that only wait for a stage as waits, and do not count a wait as a check in the totals.
5. Note 7: give the product guard for the test hook option a self test in `build_all.sh` (a tampered copy of a product `.config` with the option on must make the stage fail, as the MTU guards do).
6. Note 4: an action refused because the queue is full is counted once (`actions_refused`), not also in `out_dropped`; correct the comment at `rrl_bt.h:32`; Q checks both counts after the refused action.
7. Note 5: in scenario B the stand-in offers one Apple notification after the ring found Apple's service on the relay's link; the ring checks that it did not reach the store.
8. Notes 3 and 8: no code change. (Note 8, no sign to the wearer when an action is refused, goes into the step report as not built.)
9. Corrections of numbers: the two-device copies are 18 (31 in all with the 13 logic copies) plus what this round adds; Q does not drop a READY; `relay-notes.md` gets a short section "State after round 3" with the true counts (cases, scenarios with their check counts, copies) and what stays not proven.
10. Logs: the saved logs of the two-device scenarios must hold every check line (PASS lines too), so a reader can find each check named in your notes.

Rules: as in round 2. Owns: the same files as before. Must not touch: `design/`, the two review files, the brief files, every test file of steps 1 to 4. You never run git. Shell: never send stderr to /dev/null; use 2>&1. Targeted runs only, logs in `firmware/build-logs/step5/` with names starting `r3-`; the lead runs the full command (a full run of the lead is live on the server until about 01:30: delete nothing by pattern, never touch a folder whose name holds "lead"). No Zephyr or kit source text in any file or log you keep.
Writes to: `firmware/docs/step5-round3.md`, one section per point above, a list "Left open", last line `RESULT: <done|blocked>, <one sentence>`.
Done when: `tail -1 firmware/docs/step5-round3.md` starts with `RESULT:`.
Limit: 90 minutes. Your final reply is your report; do not send it a second time by message.
