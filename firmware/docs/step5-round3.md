# Step 5, round 3: answers to the second review

Builder: os-relay. I ran no git. Brief: `docs/step5-round3-brief.md`; review: `docs/step5-review2.md`. Targeted runs only. Logs in `build-logs/step5/`, names starting `r3-`. Unlike round 2, these logs hold every check line, PASS lines too (point 10).

Runs (all exit 0 unless said):
- `20261113-005135-r3-guard-first.log`: copy `session_start_clears_relay` against the round 2 scenario B, before any hook (point 3).
- `20261113-005427-r3-relay-1.log`: logic suite on both boards (46 of 46 = 23 per board) and scenarios H (156 checks, line 329), I (39, line 400), B (37, line 466), Q (33, line 535).
- `20261113-005659-r3-broken-1.log`: all two-device copies and all 13 logic copies. Two copies (`error_not_notified`, `hello_keeps_queue`) said "the edit could not be made", because my change of `q_push_locked` changed the text they edit; I fixed the two edits and ran them again in `20261113-012353-r3-broken-2.log` (both fail their named checks).
- `20261113-012706-r3-regress-1.log`: the earlier steps' two-device tests (all `RESULT PASS`), all native_sim suites (346 of 346), the development kit build, `link_settings` and `relay_no_core`. Application image: flash 522,212 bytes, RAM 183,080 bytes (the same as round 2: the hooks are off in the product).

## 1. New fault 1: three logic checks that cannot fail
Removed the three lines (`rinbox_count(&b)` after `apply()` of an ERROR result twice, and after a NONE result) in `tests/relay/src/test_relay.c`. `test_put_not_stored_before_its_last_piece` now has the comment that names the proof: the ring check "H: two more pieces were taken, nothing was stored" (store digest) and the copy `put_early`. The logic suite passes (23 cases on both boards, `r3-relay-1.log`) and every logic copy still fails its named case (`r3-broken-1.log`).

## 2. New fault 2: the example observed on the ring
Scenario H now has three stages in the example block: the stand-in sends the 7 notifications and the ring checks them (stage 141); the six 20-byte frames, then the ring checks entry 0x000100a5 field by field, in front, count 8 (check "H: the example's six frames stored entry 0x000100a5 field by field", `r3-relay-1.log` line 119); REMOVE, then the ring checks the id is gone and the count fell from 8 to 7 (line 122); then the 71-byte frame and the checks that existed. The existing copy `remove_ignored` already fails the new stage: in `r3-broken-1.log` line 1157 the check "H: the example's REMOVE took the entry out" says FAIL in that copy's run (its named check, "REMOVE arrived: 1002 left the store", fails first at line 1365). So I added no new copy.

## 3. Fault 3, second half: session start after a relay HELLO (`rip.c`, the guard of `ready_fn`)
First step as the brief says: copy `session_start_clears_relay` (the guard removed) against the round 2 scenario B: B passed with the guard removed (`r3-guard-first.log`: `TEST B RESULT PASS`, "the named check line did not say FAIL"). So the branch was not proven. Second step: hook `rip_test_hold_session_start` (`modules/ring_iphone/src/rip.c`, `rip.h`), compiled only under `CONFIG_RING_RELAY_TEST_HOOKS` (test ring only; the product guard is point 5). In scenario B the ring holds the iPhone part's session start, the stand-in sends HELLO and PUT 401, the ring checks sessions is 0, releases the hold, and checks that the session started and 401 is still in the store (check "B: the session start after a relay HELLO kept the entries", `r3-relay-1.log` line 421). The copy `session_start_clears_relay` now fails exactly that check (`r3-broken-1.log` line 4210).

## 4. Note 6: waits
Both programs have a `WAIT` macro: a wait prints `RING WAIT` or `HELPER WAIT`, is not counted in the checks, and a timed-out wait fails the run. 28 stand-in waits and 20 ring waits were converted; the log holds 56 wait lines (`r3-relay-1.log`). The check totals above (156, 39, 37, 33) no longer count waits. `run.sh` also counts a failed wait as a failure.

## 5. Note 7: self test of the hook guard
`tools/build_all.sh`: the guard is now a function `hook_guard`; `link_settings` runs it on both product builds and then on a tampered copy of the product `.config` with the option on, which must be refused (log lines "DIFFERENT CONFIG_RING_RELAY_TEST_HOOKS is on in self-test-hooks-on" and "self test ok: a product settings file with the relay test hooks on was refused", `r3-regress-1.log`). The guard also covers the new rip.c hook, which uses the same option.

## 6. Note 4: refused action counted once
`q_push_locked` takes `count_drop`; a full queue counts `out_dropped` for READY and ERROR only; `relay_action` passes false, so the refused action is counted only in `actions_refused`. Comments at `rrl_bt.h` corrected (`out_dropped` and `actions_refused`). Scenario Q checks both counts after the refused action: `actions_refused` is 1 and `out_dropped` stays 4 (`r3-relay-1.log` line 490).

## 7. Note 5: an Apple notification in B
The stand-in offers an Apple notification (added, id 999) after the ring found Apple's service on the relay's link. It cannot be delivered because the ring never subscribed to the Notification Source: the stand-in's notify call fails (check at line 451) and the ring checks that 999 is not in the store (line 427, together with the relay's PUT 402 being accepted). This proves the ring's refusal by not subscribing; it cannot show what the ring would do with an Apple event, because none can arrive.

## 8. Notes 3 and 8
No code change. Note 3 (a frame in flight when HELLO is accepted may arrive before READY) is now in 7.7 "Details". Note 8 is NOT BUILT: the wearer gets no sign when an action is refused (`rscr.c` drops the return value; a change would be in ring_screens, which I may not touch).

## 9. Numbers and notes
Two-device copies: 19 (the 18 of the brief plus `session_start_clears_relay`); logic copies: 13; 32 in all. Q drops no READY. `relay-notes.md` has a new section "State after round 3" with the true counts.

## 10. Logs
The saved logs now hold every check line (the run script prints them; I no longer filter them out): see `r3-relay-1.log` and `r3-broken-1.log`.

## Left open
- Note 8 (no sign to the wearer on a refused action): not built, ring_screens is outside my files.
- Note 3: kept as written in 7.7.
- Point 7 shows the ring's refusal only by never subscribing (see above).
- Faults 10, 11 and 12 of round 2 are still fixed in code without a test that can reach them.

RESULT: done, the 2 minor faults and the open half of fault 3 are closed (the branch is now proven by a hook and a copy that fails it); left open: note 8 not built, and the limit of point 7.
