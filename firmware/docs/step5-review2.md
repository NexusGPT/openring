# Second review of software step 5 (relay service), round 2, commit d58ca1c

Reviewer: an independent judge (I wrote neither the work nor the first review). Started 2026-11-13 00:38:53 CET (from `date`).
I ran no git, no build, no test and no server command. I ran the worked example script once with python3 and small read-only scripts. My raw outputs are in the scratch folder `<scratch>/s5r2judge/` (named below by file name only).

Pin check. Every file of the round 2 diff (`step5-r2-code.diff`) under `firmware/`, docs included, equals the new side of the diff in the working folder: 64 hunks, 0 differ (`pincheck-docs.txt`, 00:47:09; code only `pincheck-1.txt`, 00:44:45). A fake that renames `out_epoch` in memory is caught (`pincheck-fake.txt`: 3 hunks differ). I cannot check the commit id itself without git: "d58ca1c" rests on the lead's word that the diff is that commit. No file changed during the review (the same hashes in both runs).

Words: "H", "I", "B", "Q" are the two-device scenarios of `tests/bsim/relay`. "ring main.c" and "host main.c" are `tests/bsim/relay/ring_app/src/main.c` and `host_app/src/main.c`. "relay-1", "broken-1", "regress-1", "broken-2" are the four `r2-` logs. "Fixed by reading" means no test would fail if the fix were undone.

## 1. Bar A: the 14 faults of the first review

| # | Fault (review 1) | State at d58ca1c | Where it shows | Test that would fail if it came back | My reading |
|---|---|---|---|---|---|
| 1 | worked example not used | closed | logic case test_relay.c:1249-1328 (bytes 1251-1271); stand-in host main.c:1191-1230; ring c_rebuilt ring main.c:474-481 and the dismiss ring main.c:729-742 | logic `test_helper_example_bytes` (test_relay.c:1294, 1304, 1310); H "the dismiss arrived as exactly the ACTION of the example" (host main.c:1227) and "the store was rebuilt exactly" (ring main.c:720) | agrees; but in H the six-frame copy and the REMOVE are never observed (new fault 2) |
| 2 | logic store checks that cannot fail | partly closed | the memcmp checks are gone, but test_relay.c:617, :627 and :886 are count checks after `apply()` of an ERROR or NONE result, which does nothing (test_relay.c:116-134) | none for those three lines; the rule is held by H "the malformed frames changed nothing" (ring main.c:683) and "two more pieces were taken, nothing was stored" (ring main.c:707) | new fault 1 |
| 3 | two rip.c branches without a test | partly closed | Service Changed half: guard rip.c:151, check ring main.c:813-814, host main.c:1319 | B "Service Changed was indicated and the ring still holds the relay's entries" (ring main.c:813); copy `sc_clears_relay_entries` fails it (broken-1 line 15) | Service Changed half agrees. Session-start half (rip.c:993) still open; the reason given ("without a test hook in the product code") is weak: a Kconfig-gated test hook of the same kind as `rrl_test_block_out` was accepted for fault 5 |
| 4 | HELLO before a subscription not proven | closed | host main.c:1300 (HELLO before subscribe), :1305 (PUT accepted), :1306 (subscribe after); ring main.c:795-797 | B ring main.c:796 (`out_dropped == 1`, `by_code[2] == 0`, `out_sent == 0`); host main.c:1305 | agrees; no broken copy for it, and no per-check line of B is in the saved log |
| 5 | full Out queue drops READY and ACTION | closed | rrl_bt.c:207-208 (reset, then READY, same lock section 184-254); rrl_bt.c:294-297 (-EBUSY, not counted as sent); rip.c:1195-1201 (relay_actions not counted on error) | Q host main.c:1359 and :1362, ring main.c:839; copies `hello_keeps_queue` (broken-1 line 16) and `action_counted_when_queue_full` (broken-1 line 17) | agrees; new notes 3 and 4 |
| 6 | order B against the literal 7.7 text | closed (by ruling) | no code change; 7.7 now says the first user fixes the source | B ring main.c:806-808 (PUT 402 stored, `by_code[7] == 0`); host main.c:1315; copy `source_not_fixed` (broken-2 line 24) | agrees; new note 5 on "nothing of Apple's service reached the store" |
| 7 | category above 11 | closed | test_relay.c:1005-1013, all 256 values through `rinbox_upsert` | logic `test_flags_and_category` (test_relay.c:1010, 1012); copy `category_above_11_refused` (broken-1 lines 9, 10) | agrees; the store call is the test's `apply()`, not `rip_relay_put` (rip.c:1338-1355), which passes the byte through unchanged by my reading |
| 8 | two-device checks that pass whatever the ring does | closed | host checks removed (diff host hunks at 953, 1021, 1187); ring waits renamed (ring main.c:594, 604, 611, 627, 637, 644 and more, `waits.txt`) | ring-side counts: ring main.c:642 (`out_dropped == 1`), :639-641 (`actions_refused`), :796 (READY dropped) | agrees; host-side waits are still named as confirmations (new note 6) |
| 9 | date with NUL or a cut character | closed (by ruling) | 7.7 now says the date is stored like every text | test_relay.c:1327 ("not a date at a") | agrees |
| 10 | `out_try` left at 1 after a link ends | closed, fixed by reading, not proven by a test | rrl_bt.c:66-72 (`out_try = 0` with the queue, under the lock), :129-134 (no write to `out_try` after an epoch change) | none | agrees: every write of `out_try` is under the lock and after the epoch check |
| 11 | out_fn pops a frame it did not send | closed, fixed by reading, not proven by a test | rrl_bt.c:124 (epoch read under the lock), :129-134 (no pop when the epoch changed) | none | agrees for the pop; the frame in flight is still delivered (new note 1) |
| 12 | source not cleared when the iPhone part is not started | closed, fixed by reading, not proven by a test | rip.c:1024-1046; `lk` is `K_MUTEX_DEFINE` (rip.c:52), so it is valid before `rip_init`; `ready_work` cancel is behind `inited` (rip.c:1043-1045); `rinbox_clear` is a memset (rinbox.c:81-84) | none | agrees; it clears only when `conn == src_conn` (rip.c:1027), so not another link's source; `rglue.c:90` ignores the result of `rip_init`, so the case is real |
| 13 | relay accepts any level 4 link | open by the lead's ruling ("no change") | rrl_bt.c:175 | none | as ruled |
| 14 | two broken copies off their named fault | closed | new copy `refused_frame_changes_store` (bsim broken_edit.py, anchor at rrl_bt.c:247); `store_not_emptied_at_link_end` now edits rip.c:1027 and :938 only | broken-1 line 14 (store digest check ring main.c:683), line 13 (ring main.c:711) | agrees, see bar D |

Totals of the table: 11 closed (1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14; of these 10, 11 and 12 by reading only), 2 partly closed (2, 3), 1 open by ruling (13).

## 2. New faults in the round 2 changes

0 major, 2 minor, 6 notes. I searched for a major in each place bar B names; the result for each is under "Searched, no fault" below.

1. **minor. Round 2 replaced the logic checks that cannot fail with new ones that cannot fail either.** test_relay.c:617 and :627 (`zassert_equal(rinbox_count(&b), 3)` after `apply()` of results already asserted to be ERROR at :573, :622, :625) and test_relay.c:886 (`rinbox_count(&b) == 0` after `apply()` of a result asserted NONE at :884). `apply()` (test_relay.c:116-134) does nothing for ERROR and NONE, so these three lines pass whatever rrl_bt.c or rip.c do. Rule: brief point 2 ("Remove each check that cannot fail"). Scenario: change rip_relay_put to store on every piece; :886 still passes. The builder's text says "Each now has a comment saying that the store behaviour is proven by the two-device test": `test_put_not_stored_before_its_last_piece` (test_relay.c:866-890) has no such comment. Test that catches the real fault: H ring main.c:707 (digest after two pieces) and :683; the three logic lines should be removed.

2. **minor. In H the worked example's six-frame copy and its REMOVE are never observed on the ring.** host main.c:1212-1217 sends the six 20-byte frames, then `03 a5 00 01 00`, then the 71-byte frame, with no stage between them; the ring looks only at the final store (ring main.c:716-725, item 0 via c_rebuilt ring main.c:478). Rule: brief point 1 ("The ring checks the stored entry field by field"). Scenario: if the six-frame path stored wrong texts for id 0x000100a5, or if REMOVE of 0x000100a5 left the entry, the 71-byte PUT replaces the same id in the same place with the same read mark (rule "keeps its place and its read mark"), so the final store and every H check are the same. The count check `r1.removes - rl.removes == 1` (ring main.c:728) counts the accepted REMOVE frame, not its effect: `rip_relay_remove` counts even when the id is not held (rip.c:1363-1366). The logic case does check the six-frame result (test_relay.c:1294) and the REMOVE (test_relay.c:1300), through the test's own `apply()`. Test that would catch it: a ring stage after the six frames that checks item 0 field by field, and one after REMOVE that checks the id is gone.

3. **note. A frame in flight when a HELLO is accepted still reaches the helper, before READY.** rrl_bt.c:124-134 and :206-208. Order: the helper writes `7E` (ERROR `83 01 00 00 00 00` queued, out_fn calls `bt_gatt_notify` with no lock); the helper writes `01 01`; in_write resets the queue and queues READY; out_fn returns, sees the epoch changed, and then sends READY. The helper gets `83 01 ...` after its HELLO was accepted and before `81 01 10`. Rule 7.7 "drops every frame that still waits": the frame in flight does not wait, so the rule is kept as written. The frame is then counted neither in `out_sent` nor in `out_dropped` (rrl_bt.c:129-134). The window is one notify; a helper that follows spec R14 waits for each write response, so it is narrow. Test: none possible without a hook inside the notify.

4. **note. A refused action is also counted as a dropped Out frame, and the stats comment is stale.** `q_push_locked` adds 1 to `out_dropped` when full (rrl_bt.c:76-78), then relay_action adds 1 to `actions_refused` (rrl_bt.c:296). The comment of `actions_refused` (rrl_bt.h:32) still says "(no session, no subscription to Out)". Q checks `out_dropped == 4` before the action (ring main.c:837), so the test does not see it.

5. **note. The B check "nothing of Apple's service reached the store" has no Apple notification to attack it.** ring main.c:806-808. The stand-in sends Apple notifications only in I (`ns_send` at host main.c:1252 and :1281; none in script_b, host main.c:1290-1325). So the store half of the check cannot fail by an Apple notification; it can fail only through `ancs_up`, `ns_added` (no event is ever offered in B) or the store being emptied. The real guard of the ruling is ring main.c:800 (`relay_blocked == 1`, not subscribed) and copy `source_not_fixed`.

6. **note. Host-side stage waits are still named as confirmations and counted as checks.** 22 host CHECK lines whose whole condition is `wait_ring(...)` and whose name is not a wait (H 18, I 2, B 1, Q 1; 28 wait-only lines, 6 named as waits; `waits.txt`, `waits-count.txt`), for example host main.c:1020 "H: the ring saw the entry leave (stage 70)" and :1253 "I: the ring has the notification with its text (stage 10)". They count in "185 checks" (H), "42" (I), "39" (B) and "40" (Q). Brief point 8 asked that a check that only waits is named as a wait; the builder renamed the ring side only.

7. **note. The new product guard for the test hook has no self test.** build_all.sh:271-277 greps each product `.config` for `CONFIG_RING_RELAY_TEST_HOOKS=y`; unlike the MTU guards (build_all.sh:201-213) no tampered copy shows the DIFFERENT branch fires. regress-1 lines 41-42 show only the "is off" branch.

8. **note. The wearer gets no sign when an action is refused with -EBUSY.** rscr.c:110 drops the return of the dismiss call (and of the positive action). The entry stays and the screen does not change. 7.7 asks only that the action is refused; the same holds for -ENOTCONN, which existed before round 2 (by reading; I did not run the base).

Searched, no fault:
- `out_reset_locked` and `out_epoch`: every caller holds `rl` (rrl_bt.c:192, 207, 335). The retry path (rrl_bt.c:149-152) runs only when the epoch did not change. READY is queued after the reset in the same lock section as the HELLO (rrl_bt.c:184-254). Work after the link ended: on_disconnected resets the queue and bumps the epoch under `rl` (rrl_bt.c:327-337); a running out_fn then finds the epoch changed, loops, and returns at `rl_conn == NULL` (rrl_bt.c:104).
- -EBUSY: the count is right (`actions_refused` +1, `actions_sent` unchanged, rrl_bt.c:294-297); the caller is told (rip_action returns the error and counts `actions_refused`, not `relay_actions`, rip.c:1195-1201); no store change (Q ring main.c:842).
- rip.c on_disconnected when not started: `lk` is static (rip.c:52); `inited` is written only in rip_init; only the link's own source is cleared (rip.c:1027).
- Lock order: changed paths take `rl` then `lk` (rrl_bt.c:199 rip_relay_open, :212, :223, :232) or one lock only (rip.c:1025-1039, rrl_bt.c:289-301). rip_action drops `lk` before the relay hook (rip.c:1194-1196). No path takes `rl` with `lk` held.
- Test hook: declared and defined only under `CONFIG_RING_RELAY_TEST_HOOKS` (rrl_bt.h:38-41, rrl_bt.c:38-40, 96-101, 308-316); default n (Kconfig:17-22); set only in the relay test ring (ring_app/prj.conf:67); called only from ring main.c:833 and :846 (`hooks-grep.txt`). With the option off nothing of it is compiled; with it on and the flag false, out_fn is unchanged. The test ring of H, I and B also has it on, so those scenarios run a binary that differs from the product by this dead branch.

## 3. Answers to bars C to G

### C. The worked example
- Bytes: the six 20-byte frames (the sixth 16 bytes), the 71-byte frame, REMOVE `03 a5 00 01 00` and ACTION `82 a5 00 01 00 01` are static literals in both test_relay.c (1254, 1262, 1268, 1269) and host main.c (1194, 1203, 1209, 1225). A script compared all 13 literal arrays with the output of `android-helper-example.py`: 0 differ (`cmp_example.txt`, `example-out.txt`). None comes from the code under test; the host includes no project module (first review, unchanged by the diff).
- Logic case: frames go through the real `rrl_frame`; the entry is compared field by field (`expect_item` test_relay.c:154-167: id, category, flags, the four texts) at :1294 and :1304; the Out bytes are compared byte for byte at :1310 (ACTION negative), plus positive, ERROR 2, Info and READY. The store is the test's `apply()` with the real `rinbox_upsert`.
- Stand-in: the ring compares item 0 field by field (`item_is`, ring main.c:292-301, includes `text_ready`) at ring main.c:478 and :735; the stand-in compares all 6 ACTION bytes (host main.c:1227-1228). Gap: new fault 2. The order of the brief (six frames, 71-byte frame, REMOVE) differs from the code (six frames, REMOVE, 71-byte frame); the code's order leaves the entry in place for the dismiss, which is needed.

### D. Tests that cannot fail (changed and new tests only)
- Logic, edited cases: `test_refused_frames_change_nothing` :617 and :627 cannot fail; `test_put_not_stored_before_its_last_piece` :886 cannot fail (new fault 1). `test_remove_clear_and_hello_empty_the_store` :1205 can fail (it checks the act; `(void)r` at :1206 is dead). `test_flags_and_category` :1010 and :1012 can fail. `test_helper_example_bytes`: every check can fail.
- Scenario Q: every ring and host check can fail except the four ring waits and the four host waits (named as waits). Q blocks out_fn before it pops a frame, so it proves the queue reset and the -EBUSY path, not the retry and drop path of a notify that fails.
- New parts of H: all can fail; new fault 2 is a gap, not a check that cannot fail.
- New parts of B: all can fail; note 5 on the Apple half.
- Broken copies (anchors each found once, `anchors.txt`; named lines from the logs, `logclaims2.txt`):
  - `refused_frame_changes_store`: yes. The edit keeps the refusal and adds a store call on the error path (rrl_bt.c:247). M20 carries id 2003, which the store holds (host main.c:1112-1113), so the digest and the id list change. The same check line also compares `relay_removes`, which rises even for an id not held, so the line fails partly through a counter. broken-1 line 14.
  - `store_not_emptied_at_link_end`: yes, one fault (the link's source does not end with the link) at its two sites, rip.c:1027 and :938. Both are needed: with only the first, end_session would clear the source and stop_services would empty the store. `inbox_empty_locked` is not touched. broken-1 line 13.
  - `sc_clears_relay_entries`: yes; it removes the guard at rip.c:151. broken-1 line 15.
  - `hello_keeps_queue`: yes; without the reset the full queue refuses READY and an old ERROR comes first. broken-1 line 16 (host main.c:1359).
  - `action_counted_when_queue_full`: yes; rip_dismiss then returns 0, not -EBUSY. broken-1 line 17 (ring main.c:839).
  - `category_above_11_refused`: yes; rrl.c:41 refuses a category above 11 with code 5, so test_relay.c:1010 fails on both boards. broken-1 lines 9 and 10.

### E. Earlier steps
- The diff changes no test file of steps 1 to 4. Its files: docs, rip.c, the ring_relay module, tests/relay, tests/bsim/relay, build_all.sh.
- iPhone link: the only rip.c change is on_disconnected. With `inited` true (every build that calls rglue_init), `mine`, the source branch and the cancel of `ready_work` act exactly as before. With `inited` false there is no iPhone session to change. rrl_bt.c changes touch only the relay's own queue. So no behaviour of an iPhone link changes, by reading.
- Runs: regress-1 lines 9, 11 and 13 (bsim iphone, screens, control: `RESULT PASS`); line 16 (346 of 346 native_sim cases).

### F. The numbers of step5-round2.md

| Claim | Evidence | Verdict |
|---|---|---|
| relay-1: 46 of 46 cases, 23 per board | relay-1 line 11; 23 `ZTEST(ring_relay` in test_relay.c (`counts.txt`) | matches; the pointer "line 5 of the verdicts" is not a clear line (it is file line 11) |
| H 185 checks, line 44 | relay-1 line 44 | matches |
| I 42, line 50 | relay-1 line 50 | matches |
| B 39, line 51 | relay-1 line 51 | matches |
| Q 40, line 53 | relay-1 line 53 | matches |
| broken-1: named-check lines 13 to 17; logic copy lines 9 and 10 | broken-1 lines 9, 10, 13 to 17 | matches |
| regress-1: iphone, screens, control `RESULT PASS`; 346 of 346 | regress-1 lines 9, 11, 13, 16 | matches |
| flash 522,212 B, RAM 183,080 B, lines 28 and 29; round 1 522,148 and 183,072 | regress-1 lines 28, 29; review 1 row G | matches |
| TEST_HOOKS off in both product builds | regress-1 lines 41, 42 | matches |
| broken-2: 13 earlier two-device copies, 13 logic copies, 26 named-case lines, `RESULT PASS` both | broken-2 lines 9, 10, 12 to 24, 25 | matches |
| "Two-device copies: 17; logic copies: 13; 30 in all" | run.sh VARIANTS 18, bsim broken_edit.py 18 keys, logic 13 (`counts.txt`) | does not match: 18 two-device, 31 in all |
| `test_helper_example_bytes` at test_relay.c:1249 | test_relay.c:1249 | matches |
| stand-in compares the ACTION at host main.c:1227 | host main.c:1227 | matches |
| guard at rip.c:151; session start at rip.c:993 | rip.c:151, :993 | matches |
| fault 2: "Each now has a comment" naming the H checks | test_relay.c:614-616 and :1202-1204 have it; :866-890 has none | does not match for one of three cases |
| fault 8: `out_dropped` kept for READY in "scenario B, Q" | B ring main.c:796 checks READY dropped; Q ring main.c:837 checks `out_dropped == 4` for ERROR frames, no READY is dropped in Q | does not match for Q |
| "relay-notes.md ... its counts (22 cases and the 26 copies)" | relay-notes.md:24 says 23 cases; :60 says 26 copies | does not match for the cases |
| Q: 12 refused frames leave 8 queued and 4 dropped | ring main.c:837 (`by_code[1] == 12`, `out_dropped == 4`); OUTQ 8 (rrl_bt.c:19) | matches |

What the saved logs do not show: per-check lines are in the saved relay-1 log only when the line holds the word "error" or says FAIL (the grep of relay-1 line 2). Counts of PASS check lines in relay-1: H 31, I 5, B 0, Q 1 (`logclaims.txt`). So no saved line shows any of the new H example checks, any B check (old or new), or any Q check but host main.c:1352. Their passing rests on the verdict lines 44, 51 and 53 and on the run script's rule that any FAIL line fails the scenario. The two-device broken runs show only the named FAIL line of each copy, not whether other checks failed too. The lead's full run is not in my sources.

### G. An app built only from android-helper-spec.md, after round 2
1. R9 (READY within 5 s): now holds when the Out queue is full (fault 5 closed). READY can still be lost if the notify fails 6 times in a row: out_fn drops a frame after 5 retries 50 ms apart (rrl_bt.c:135-145, unchanged since round 1). The app then drops the link after 5 s. Whether the stack's notify can fail that way I did not check.
2. A stale frame between HELLO and READY (new note 3): spec R9 and 5.5 do not say what to do with an ERROR or ACTION that arrives before READY; an ERROR code 2 there would make a 5.5 app send HELLO again.
3. An ACTION that was queued but then dropped after 5 failed notifies is counted as sent on the ring (rrl_bt.c:299, rip.c:1198); the app sees nothing and the wearer gets no sign (note 8). Spec line 56 covers only "cannot be queued".
4. Spec section 6 line 270 says "Whether the ring test uses the same bytes: not checked here": now stale, the ring tests use them (bar C).
5. Writes longer than the payload: now in the spec (line 56, ATT error 0x07); 5.5 has no row for it, but R15 prevents it.
I found no frame, size or order of sections 2, 4 and 5 that this ring refuses. Nothing ran on a phone.

## 4. Not checked
- The commit id d58ca1c (no git allowed); I checked the working files against the diff only.
- Any run: I ran no build, test or server command. Every pass I cite comes from the builder's four logs. The lead's full run was not in my sources.
- The base (f79baaf) behaviour of note 8 (-ENOTCONN also gives no sign): by reading only.
- Zephyr and Nordic behaviour: whether `bt_gatt_notify` can block or fail in the system workqueue (G1, note 3), and the order in which the two disconnected callbacks run.
- rip.c beyond lines 52-161, 520-600, 795-1091, 1160-1229 and 1286-1383.
- rrl.c beyond line 41 (unchanged in round 2); rinbox.c beyond lines 76-89.
- ring main.c and host main.c outside the lines cited; the pairing helper `pair_through_the_screens`.
- relay-notes.md beyond the lines found by my search (`counts.txt`).
- Whether B already hits the session-start order of rip.c:993 (fault 3, second half): no copy removes that guard, so I cannot tell.

RESULT: done, of the 14 faults 11 are closed (3 of them by reading only), 2 partly closed and 1 open by the lead's ruling; round 2 adds 0 major and 2 minor faults (plus 6 notes).
