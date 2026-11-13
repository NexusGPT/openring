# Step 5, round 2: answers to the review

Builder: os-relay. I ran no git. Brief: `docs/step5-round2-brief.md`. Review: `docs/step5-review.md` (commit f79baaf). Targeted runs only; logs in `build-logs/step5/`, names starting `r2-`. The lead runs the full command.

Runs (all exit 0):
- `20261112-235844-r2-relay-1.log`: the logic suite on native_sim and on the simulated chip (line 5 of the verdicts: 46 of 46 cases = 23 per board) and the two-device test, scenarios H (185 checks, line 44), I (42, line 50), B (39, line 51), Q (40, line 53).
- `20261113-000139-r2-broken-1.log`: the new and changed broken copies (named-check lines 13 to 17; logic copy lines 9 and 10).
- `20261113-000801-r2-regress-1.log`: the earlier steps' two-device tests (iphone, screens, control: all `RESULT PASS`), all native_sim suites (346 of 346), the development kit build, `link_settings` and `relay_no_core` of `build_all.sh`. Application image: flash 522,212 bytes, RAM 183,080 bytes (line 28 and 29; round 1: 522,148 and 183,072).
- `20261113-001637-r2-broken-2.log`: all 13 earlier two-device copies and all 13 logic copies once more (26 named-case lines, `RESULT PASS` both).
Per-check lines of the two-device scenarios were printed to the server run folder, not to the saved log; the saved verdict line `TEST <x> RESULT PASS` means no check of that scenario said FAIL (the run script fails on any FAIL line).

## Fault 1: worked example
Logic case `test_helper_example_bytes` kept (`tests/relay/src/test_relay.c:1249`). In scenario H the stand-in sends the six 20-byte frames, REMOVE `03 a5 00 01 00` and the 71-byte frame as literals after the reconnect (`tests/bsim/relay/host_app/src/main.c`, block before `helper_stage(141)`); the ring then checks the entry field by field (`c_rebuilt`, ring `main.c`), opens it on the screen, dismisses it with the joystick, and the stand-in compares what arrives with exactly `82 a5 00 01 00 01` (host `main.c:1227`). Ring side: wait for the verdict line 44.

## Fault 2: logic checks that cannot fail
In `test_refused_frames_change_nothing`, `test_put_not_stored_before_its_last_piece` and `test_remove_clear_and_hello_empty_the_store` I removed the `memcmp` checks that ran the test's own `apply()` and replaced them with what the case really proves (every frame is a refusal with its code; no entry before the last piece; the decision CLEAR or HELLO). Each now has a comment saying that the store behaviour is proven by the two-device test and naming the checks: "H: the malformed frames changed nothing" (with the store digest; copy `refused_frame_changes_store`), "H: CLEAR emptied the store" and "H: the store holds 2003, 2002, 2001 (HELLO emptied what was there)" (copy `hello_keeps_store`).

## Fault 3: Service Changed and session start
Scenario B now removes the stand-in's notification service while the relay holds 2 entries: the stand-in indicates Service Changed; the ring checks that `sc_indications` rose and that both entries are still there. New copy `sc_clears_relay_entries` (removes the guard at `rip.c:151`): fails "B: Service Changed was indicated and the ring still holds the relay's entries" (`r2-broken-1.log` line 15). The session-start order (`rip.c:993`) stays NOT PROVEN: the 20 ms between level 4 and the iPhone part's session start cannot be hit on purpose in the simulation without a test hook in the product code, and I did not add one.

## Fault 4: HELLO before a subscription to Out
Scenario B: HELLO is written before the stand-in subscribes; then a PUT is accepted (not code 2). Ring checks: entry 401 is in the store; `out_dropped` is 1 (READY dropped), `by_code[2]` is 0, `out_sent` is 0.

## Fault 5: full Out queue
Code (`modules/ring_relay/src/rrl_bt.c`): an accepted HELLO now drops every queued frame (`out_reset_locked`, called at HELLO) and then queues READY; an action whose frame cannot be queued returns -EBUSY and is not counted as sent (that branch already existed; the test now proves it). Test hook `rrl_test_block_out` (only with `CONFIG_RING_RELAY_TEST_HOOKS`, set in the relay test ring only; `build_all.sh` `link_settings` checks that both product builds have it off: log `r2-regress-1` lines about `CONFIG_RING_RELAY_TEST_HOOKS is off`). New scenario Q: 12 refused frames with Out blocked leave 8 queued and 4 dropped; the action is refused (-EBUSY, `actions_sent` 0); the second HELLO is accepted; the stand-in sees READY as the first frame and nothing from before (2 frames in all). Copies `hello_keeps_queue` (fails the READY-first check) and `action_counted_when_queue_full` (fails the -EBUSY check).

## Fault 6: order B
No code change. Scenario B: after the ring found Apple's service on the relay's link (stage 10), a PUT 402 is accepted; the ring checks 402 is stored, no code 7 was given, `ns_added` and `ancs_up` are 0. Copy `source_not_fixed` still fails its named check (`r2-broken-2.log`).

## Fault 7: category above 11
No code change. `test_flags_and_category` now sends every category 0 to 255 through the real store code (`rinbox_upsert`) and checks it is stored as received. New logic copy `category_above_11_refused` fails it on both boards (`r2-broken-1.log` lines 9 and 10).

## Fault 8: checks that pass whatever the ring does
Removed from the stand-in: "nothing came on Out from those attempts", "nothing is notified", "nothing arrived: the ring refused the action itself", "the large record is exactly 512 bytes" (the test's own length). Kept as ring-side counts that can fail: `out_dropped` for READY (scenario B, Q), for a frame while not subscribed (H: `out_dropped` is 1), `actions_refused`. The ring checks that only wait for a stand-in stage are renamed "wait for the stand-in's stage N (...)": they are waits, not confirmations; the proof is the stand-in's own check.

## Fault 9: date
No code change (7.7 now says the date is stored like every text). `test_helper_example_bytes` keeps a date that is not a date and cuts it at 15.

## Faults 10 and 11: retry count and a frame popped after a link change
`out_epoch` (changed by every emptying of the queue) is read before the notify and compared after it under the lock; if it changed, the frame is not popped and the retry count is not touched. `out_try` is reset in `out_reset_locked`, under the lock, together with the queue. Not separately tested (no hook can end a link in the middle of a notify): left as "fixed by reading, not proven by a test".

## Fault 12
`on_disconnected` of `rip.c` now clears `src` and `src_conn` also when the iPhone part is not started (`mine` and the work cancel stay behind `inited`). Not separately tested: the test rings always start the part. Fixed by reading, not proven.

## Fault 13
No change. The relay works on any link at level 4, not only the active device's (said in `relay-notes.md` section 3).

## Fault 14: broken copies
New `refused_frame_changes_store`: the frame IS refused (0x80 and ERROR) and the error path removes the entry of its id; named check: the ring's store digest ("H: the malformed frames changed nothing", line 14 of `r2-broken-1.log`). `store_not_emptied_at_link_end` is now one fault only (the link's source does not end with the link; `inbox_empty_locked` is no longer touched), still fails "H: the link dropped: the store is empty" (line 13). Two-device copies: 17; logic copies: 13; 30 in all.

## Left open
- Session-start order (`rip.c:993`), fault 3 second half: not proven, reason above.
- Faults 10, 11 and 12: fixed in code, no test can reach them in the simulation.
- Fault 13: left as designed.
- `relay-notes.md` was not rewritten: it carries a pointer to this file at its end; its counts (22 cases and the 26 copies) are those of the first delivery and are superseded here (23 cases, 30 copies, scenarios H I B Q).

RESULT: done, 7 of the 8 minor faults closed (1, 2, 4, 5, 6, 8, 14) and fault 3 closed in one half; open: the session-start order of fault 3, not testable in the simulation without a product hook.
