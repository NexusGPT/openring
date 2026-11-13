# Step 5, round 2: the lead's rulings on the review

For: the builder of step 5 (os-relay). From: the lead, 2026-11-12.
Review: `firmware/docs/step5-review.md` (0 major, 8 minor, 6 notes at commit f79baaf; the reviewer corrected its count after the first read: faults 1, 2, 3, 4, 5, 6, 8 and 14 are minor). Read it in full first. Its fault numbers are used below.
Version you work on: the working folder as it is now (commit f79baaf plus your own changes since: the example-bytes case and the notes edits).
The rule text changed: read `design/firmware.md` section 7.7 again, the bullets "One source per link" and "Details", and the record sentence (category). Four rulings are written there.

Residual of this round: 8 minor faults open. Target: 0 open, or each one left open named with its reason.

## What to do, per fault

1. Fault 1 (worked example). Keep your new logic case with the bytes of `design/software/os/android-helper-example.py`. Add the same frames to the stand-in in scenario H: the six 20-byte PUT frames, the one 71-byte frame, REMOVE `03 a5 00 01 00`, and a dismiss on the ring that must arrive as exactly `82 a5 00 01 00 01`. The ring checks the stored entry field by field.
2. Fault 2 (logic store checks that cannot fail). Remove each check that cannot fail, or make it call the real code. Where the rule is proven only by the two-device test, the notes say so and name that check.
3. Fault 3 (two branches of rip.c without a test). Add a two-device check: the stand-in indicates Service Changed after PUTs on a relay link, and the ring still holds the entries. Add a broken copy that removes that guard. For the session-start order (rip.c:993): add a check that can fail, or write in the notes that it stays not proven and why.
4. Fault 4 (HELLO before a subscription to Out). Add a two-device check: HELLO with Out not subscribed, then a PUT is accepted (not code 2), the ring's dropped count goes up by one, and the entry is in the store.
5. Fault 5 (full Out queue). Change the code as section 7.7 "Details" now says: an accepted HELLO drops every frame that still waits for Out, then queues READY, so READY always has room. An action whose ACTION frame cannot be queued is refused on the ring (the call returns an error and the action is not counted as sent). Add a test that can fail for both. A test-only hook that makes the notify call fail is allowed in the test ring, never in the product build.
6. Fault 6 (order B). No code change. The lead's ruling is in 7.7: the first user of a link fixes its source. Add to scenario B: after the ring has found Apple's service on the relay's link, a relay frame is still accepted, and nothing of Apple's service reaches the store.
7. Fault 7 (category above 11). No code change: stored as received (7.7). Add a logic check through the real store code for the values 12 to 255.
8. Fault 8 (two-device checks that pass whatever the ring does). Remove them or replace them with a ring-side count that can fail (frames given to Out while not subscribed, for READY and ACTION as it exists for ERROR). A check that only waits for a stage is named as a wait, not as a confirmation.
9. Fault 9: no code change (7.7 "Details" now says the date is stored like every text).
10. Faults 10 and 11 (the retry count and a frame popped after a link change). Fix both: the retry count is reset under the lock, and the send work pops a frame only when it belongs to the session that queued it.
11. Fault 12: clear the source of the link at link end also when the iPhone part is not started.
12. Fault 13: no change. Say in the notes that the relay works on any link at level 4.
13. Fault 14 (broken copies). Add a copy where the frame IS refused (0x80 and ERROR) and the store still changes; its named check is the ring's store digest. Make `store_not_emptied_at_link_end` one fault only.

## Rules of this round

- Owns: the same files as in your first brief. Must not touch: `design/firmware.md`, `firmware/docs/step5-review.md`, this file, every test file of steps 1 to 4.
- You never run git.
- Shell: never send stderr to /dev/null; use 2>&1.
- Targeted runs only (the changed suites, the changed scenarios, the new and changed broken copies, the earlier steps' two-device tests once because rip.c and rrl_bt.c change, and the development kit build). The lead runs the full command. Your own server copy and run names as before; logs in `firmware/build-logs/step5/`, names starting with `r2-`.
- The lead's full run is on the server now (run name `lead-step5-rerun`) until about 23:30. On the server delete nothing with a pattern, only one exact folder of your own per command, never a folder whose name holds "lead".
- No Zephyr or kit source text in any file or log you keep.
- Writes to: `firmware/docs/step5-round2.md`: one section per fault number above (what changed, file and line, the test, the log line), a list "Left open", and the last line `RESULT: <done|blocked>, <one sentence with the count of faults closed and left open>`. Update `firmware/docs/relay-notes.md` where a sentence is no longer true (counts, the 22 cases, line numbers).
- Done when: `tail -1 firmware/docs/step5-round2.md` starts with `RESULT:`.
- Limit: 2 hours.
- When you finish, your final reply is your report: it reaches the lead automatically. Keep it under 3,500 characters and put anything longer in a file it names. Do not also send it with SendMessage; use SendMessage only for a question or news while you keep working.
