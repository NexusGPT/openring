# Review of software step 5 (relay service), commit f79baaf

Reviewer: os-relay-review (independent; I did not write the work). Started 2026-11-12 22:40 CET, this file begun 22:50 CET (both from `date`).
Version judged: f79baaf. The base is 1aae4da. I ran no git, no build and no test. I ran the worked example script once (python3) and small read-only scripts.

Pin check. Every new file of step 5 in the working folder equals the new side of the diff `step5-code.diff`, except two that changed during this review:
- `firmware/docs/relay-notes.md`, modified 22:43: line 103 ("about 250 bytes" became "240 bytes" with the chain named) and line 124 ("`rip_*`" became "the rip_relay functions"), plus a blank line at the end.
- `firmware/tests/relay/src/test_relay.c`, modified 22:49: 1245 lines at the pin, 1330 lines now, a 23rd case `test_helper_example_bytes` added after the pin.
- `firmware/tests/bsim/relay/host_app/src/main.c` and `firmware/tests/bsim/relay/ring_app/src/main.c`, modified 22:49 (1318 and 819 lines at the pin).
- `design/firmware.md`, modified 22:54: section 7.7 now says a category above 11 is stored, that the first user of a link fixes its source, and that the date is stored like every text. These touch faults 6, 7 and 9 below; the new text is not judged here.
I judge the pinned versions. I read the three test files before they changed (my reads matched the pin); every line number below for them is from copies of the pinned files rebuilt from the diff, kept in my scratch folder. Every quote of section 7.7 below is from my read of it at 22:41, before the 22:54 change; I kept no file copy of that text. The code files rrl.c, rrl_bt.c, rip.c and rinbox.c still match the pin (sha256 taken twice). I told the lead both times.

Words: "not proven" = the code exists but no test would fail if it were broken. "H", "I", "B" = the scenarios of `tests/bsim/relay`. "Log" = `firmware/build-logs/step5/20261112-213132-os-relay.log`.

## 1. Bar A: rule coverage of section 7.7

| # | Rule of 7.7 | Code | Test that fails if it breaks | Verdict |
|---|---|---|---|---|
| 1 | Relay service UUID a3c20000-..., ring is GATT server | rrl_bt.c:22, 47-48 | stand-in finds it by its own literal UUID (host main.c:118, check at log 9274) | correct |
| 2 | Every characteristic needs security level 4 | rrl_bt.c:49, 51, 52 (AUTHEN permissions), :147 and :235 (level 4 check) | H write/subscribe/read before level 4 fail (log 9275-9277); broken copy no_security_check (log 11693) | correct |
| 3 | In: write with response | rrl_bt.c:49 (BT_GATT_CHRC_WRITE) | every H write uses write with response | correct |
| 4 | Out: notify | rrl_bt.c:50-51 | READY, ACTION, ERROR seen by stand-in (log 9296, 9318) | correct |
| 5 | Info: read, 6 bytes 01 10 30 30 A0 0F | rrl.c:221-229, rrl_bt.c:231-243 | test_info_and_out_frames (test_relay.c:171); H check log 9282 | correct |
| 6 | All numbers little endian | rrl.c:8-24 | test_every_opcode id 0xA1B2C3D4 (test_relay.c:218-221); stand-in uses sys_put_le32 | correct |
| 7 | HELLO 0x01 version u8: starts a session, ring empties what the relay stored, answers READY | rrl.c:107-117, rrl_bt.c:169-178, rip.c:1309-1327 | H "store holds 2003, 2002, 2001 (HELLO emptied ...)" log line of copy hello_keeps_store 12273; READY log 9296 | correct |
| 8 | PUT 0x02 id, total, offset, data; pieces in order; offset 0 drops an unfinished record; stored when offset+len = total | rrl.c:118-171 | test_code_3_order, test_a_new_record_at_offset_0_drops_the_unfinished_one, test_put_not_stored_before_its_last_piece; copies put_early, order_ignored | correct |
| 9 | REMOVE 0x03 id | rrl.c:172-181, rrl_bt.c:191-199, rip.c:1357-1369 | H "REMOVE arrived: 1002 left the store" (log 9222); copy remove_ignored (log 10819) | correct |
| 10 | CLEAR 0x04: empties what the relay stored | rrl.c:182-190, rrl_bt.c:200-208, rip.c:1371-1383 | H "CLEAR emptied the store" (log 9250). No broken copy breaks CLEAR; the logic check (test_relay.c:1197) runs the test's own `apply()`, not rip.c | correct, weakly proven (H only) |
| 11 | Record: category u8 0..11 | rrl.c:41 stores any value | test_flags_and_category covers 0..11 only; nothing for 12..255 | not proven; see fault 7 |
| 12 | Record: flags, bits above 4 must be 0 | rrl.c:38 | test_code_5_malformed_record, test_flags_and_category (all 256 values); copy flag_bit5_ok | correct |
| 13 | Fields type/length/bytes, types 1..4, each at most once, any order, missing = empty | rrl.c:43-62 | test_fields_in_any_order_each_once (24 orders), test_code_5; copy repeat_type_ok | correct |
| 14 | Record 2..512 bytes | rrl.c:135 | test_code_4_total, test_record_of_2_and_512_and_513; copies total_min_1, total_max_513 | correct |
| 15 | Text longer than its limit cut at a character | rinbox.c:27-74 via rinbox_upsert rinbox.c:169 | test_texts_cut_at_a_character; H 1002 and 3005 (log 9191, 9265); copy text_cut_inside_char | correct |
| 16 | PUT of a stored id replaces it, keeps place and read mark | rinbox.c:175-177 | test_replace_keeps_place_and_read_mark; H log 9201; copies replace_moves_front (both suites) | correct |
| 17 | New id to the front, 17th pushes the oldest out | rinbox.c:178-179 (rinbox_add) | test_the_17th_pushes_the_oldest_out; copy store_17. Not run in the two-device test (H holds at most 7) | correct (logic only) |
| 18 | READY 0x81 version 1, store 16 | rrl.c:197-203 | test_info_and_out_frames; log 9296 | correct |
| 19 | ACTION 0x82 id u32, action u8 | rrl.c:205-211, rrl_bt.c:263 | H log 9318, 9323; copy action_id (log 11983) | correct |
| 20 | ERROR 0x83 code u8, id u32 (0 when none) | rrl.c:213-219, rrl.c:86-92 | 21 malformed frames each checked byte by byte (host main.c:652-663, log 9359-9400); copy error_not_notified | correct |
| 21 | A refused frame changes nothing in the store | rrl_bt.c:168-215 (no store call on RRL_ACT_ERROR) | H store digest unchanged after 21 refusals (ring main.c:676-678, log 9244). The logic check test_refused_frames_change_nothing cannot fail on this point (fault 2) | correct (proven by H) |
| 22 | Refused write answered with ATT error 0x80 | rrl_bt.c:225-226 | every expect_refused (host main.c:661) | correct |
| 23 | ERROR notified when the helper has subscribed to Out | rrl_bt.c:221, :94-101 | subscribed: log 9359-9400; unsubscribed: ring check log 9227 (out_dropped == 1) | correct |
| 24 | Code 1: unknown opcode or wrong frame length | rrl.c:102-105, 108-109, 123-125, 173-174, 183-184, 191-193 | test_every_opcode (all 252 other opcodes), test_code_1_wrong_length; H M1-M3, M6-M9 | correct |
| 25 | Code 2: no HELLO in this session | rrl.c:131-133, 175-176, 185-186 | test_code_2_no_hello; H log 9188 and 9266 | correct |
| 26 | Code 3: piece out of order or beyond total | rrl.c:145-154 | test_code_3_order; H M13-M15; copy order_ignored | correct |
| 27 | Code 4: total under 2 or over 512 | rrl.c:135-139 | test_code_4_total; H M10-M12; copies total_min_1, total_max_513 | correct |
| 28 | Code 5: record malformed | rrl.c:161-166 with rrl_parse | test_code_5, every truncation tests (test_relay.c:748, 837); H M16-M21 | correct |
| 29 | Code 6: version not supported | rrl.c:110-111 | test_code_6_version (all 256 values); H M4, M5 | correct |
| 30 | Code 7: the link's notifications come from Apple's service | rrl.c:98-101 fed by rrl_bt.c:166; backstops rrl_bt.c:170-175, 186, 195, 204 | test_code_7_one_source_per_link; I (log 9472, 9500-9508); copies code7_not_enforced (both) | correct for the order "Apple first"; see fault 6 for the other order |
| 31 | Sessions: notifications live for one link; emptied when the link ends | rip.c:1029-1040, rrl_bt.c:283-300 | H "link dropped: the store is empty" (log 9261); copy store_not_emptied_at_link_end (log 10529) | correct |
| 32 | Sessions: helper sends HELLO and notifications again after reconnect | rrl_bt.c:157-164 (new link, new session) | H reconnect: frames before HELLO refused code 2 (log 9266), store rebuilt (log 9265) | correct |
| 33 | Sessions: a PUT not finished when the link ends is dropped | rrl_bt.c:163, :291 | H: after reconnect and HELLO the next piece of the old record gets code 3 (log 9266) | correct |
| 34 | One store for both sources; screens do not know the source | rip.c (store `inbox`), rscr_real.c not in the diff | I and H both read the store through rip_inbox_get | correct |
| 35 | On a link where Apple's service was found, every relay frame refused with code 7 | as row 30 | I scenario | correct for that order; in conflict for order B (fault 6) |
| 36 | On a link with a relay session Apple's service is not there | rip.c:568-585 (Apple's service found later is ignored) | B (log 9540); copy source_not_fixed (log 13167) | built as the builder's reading (notes section 4 row 13) |
| 37 | Actions: a dismiss on the ring is the negative action | rip.c:1225-1228, 1189-1204 | H log 9323 | correct |
| 38 | Actions: ring notifies ACTION and changes nothing in the store; entry leaves on REMOVE | rip.c:1189-1204 (no store write) | H "1002 is still in the store until REMOVE" (log 9220) | correct |
| 39 | Actions: an action the notification does not have is refused and sends nothing | rip.c:1184-1188 | H log 9205, stand-in log 9309, 9313; copy action_without_flag (log 10237) | correct |
| 40 | Actions: with no subscription to Out the action is refused on the ring | rrl_bt.c:259-262 | H log 9226 | correct |
| 41 | Read mark lives on the ring only | no frame carries it (rrl.c); rinbox.c:200 | H log 9197, 9201 | correct |
| 42 | Details: date is local time; ring stores the 15 characters as received, does not read them | rinbox.c:59-74 (put: stops at a NUL, UTF-8 cut, 15 bytes) | H dates compared as strings (log 9191). A date that is not valid UTF-8 or holds a NUL is changed (fault 9) | correct for any ASCII date; not proven for other bytes at the pin |
| 43 | Details: a PUT carries at least 1 data byte, as many as the link allows; ring accepts every piece size | rrl.c:123 (10 bytes minimum), rrl_bt.c:153-155 (long writes refused) | test_pieces_of_every_size, test_record_of_2_and_512_and_513 (pieces 1..520); H frames of 20 and 244 bytes | correct for one ATT write; long writes refused (notes reading 11) |
| 44 | Details: CLEAR may be sent at any time in a session | rrl.c:182-190 (no state check besides HELLO) | test_remove_clear_and_hello (CLEAR mid session); H CLEAR (log 9250) | correct |
| 45 | Details: HELLO starts a session also without a subscription; READY not delivered | rrl_bt.c:169-178 and :94-101 | none: no test sends HELLO before subscribing | not proven (fault 4) |
| 46 | Details: no sort by date; order of arrival, newest first | rinbox.c:114-137 | test_replace_keeps_place_and_read_mark (3, 2, 1); H ids order (log 9191) | correct |
| 47 | Details: positive action reachable: Right on SCR_NOTIF | step 4 screens, rip.c:1189-1204 | H "positive action on 1003 went out" (log 9212), stand-in log 9318 | correct |
| 48 | Details: advertising of 7.3 unchanged | no file of ring_devices in the diff | the diff file list | correct |
| 49 | Nothing here starts or stops a recording; relay calls nothing in the core | rrl.c, rrl_bt.c include only rip.h, rrl.h, rinbox.h (saved include list) | H log 9235; stage relay-no-core log 13553-13554; copy relay_reaches_core (log 9868) | correct |
| 50 | Not built in step 5: helper app, media and time from Android, status/time/file characteristics | nothing built | n/a | correct (nothing claimed) |

## 2. Faults

No fault of the first kind (memory, a recording, wrong store data) was found. Bar B was searched as follows, with the result for each:
- Parser bounds: rrl.c:123 needs 10 bytes before reading id, total and offset; rrl.c:150 checks `off + dlen > total` in size_t (no wrap: off and total are u16, dlen is at most the ATT length) before the memcpy at :155; total is at most 512 = sizeof buf (rrl.h:80). rrl_parse checks `p + 2 > len` (rrl.c:47) before reading the length and `p + 2 + l > len` (rrl.c:52) before using the field. A piece longer than what is left: code 3 at rrl.c:150. No read or write outside a buffer found.
- Connection pointers: `src_conn` (rip.c:81) is only compared, never dereferenced (rip.c:573, 938, 993, 1029, 1302, 1314, 1332). `rl_conn` holds a reference (rrl_bt.c:162) and is released at :160 and :292. CONFIG_BT_MAX_CONN=1 in the product and the test ring.
- Lock order relay then iPhone: rrl_bt.c holds `rl` around rip_src_of, rip_relay_open/put/remove/clear (:156-223); rip_action drops `lk` before calling the hook (rip.c:1194-1196); nothing takes `rl` with `lk` held. bt_gatt_notify runs with no lock (rrl_bt.c:103-104). No break found.
- Path to the core, the screen or a recording: rrl.c and rrl_bt.c include only zephyr headers, rip.h, rrl.h, rrl_bt.h and rinbox.h; rip_relay_* touch only `inbox` and counters. No path found.

1. minor. The worked example is not used at the pin. Files: tests/relay/src/test_relay.c (all of it), tests/bsim/relay/host_app/src/main.c (all of it). Rule: the lead's request (bar E). Scenario: a search of both test folders for 0x000100a5, 0xa5, "Anna", "Lunch", the noodle bytes and "191500" finds nothing; "com.example.chat" appears only in other records (test_relay.c:637, host main.c:711, 726). So no test feeds the six 20-byte frames, the 71-byte frame, REMOVE `03 a5 00 01 00` or compares ACTION `82 a5 00 01 00 01`. The notes do not say the request was skipped. Test that catches it: a logic case that feeds those exact frames through rrl_frame and compares the stored entry and the Out bytes, and the same frames sent by the stand-in. Such a case (`test_helper_example_bytes`) appeared in the working file at 22:49, after the pin; it has not run in any log I read.

2. minor. Store checks of the logic suite that cannot fail. File test_relay.c:116-134 (`apply()`), :615, :625, :885, :1197, :1207, :742-743. Rule: "a refused frame changes nothing in the store"; HELLO and CLEAR empty the store. Scenario: `apply()` is the test's own copy of what rrl_bt.c and rip.c do. It does nothing for RRL_ACT_ERROR and RRL_ACT_NONE, so once :574 has checked `act == RRL_ACT_ERROR`, the memcmp at :615 and :625 cannot fail; the same for :885 after :883. At :1197 and :1207 the store is emptied by `apply()` calling rinbox_clear, so "HELLO empties the store" passes whatever rip_relay_open (rip.c:1309) does. The notes (section 1b) cite these cases as proof of those rules. The rules are proven instead by H (store digest, log 9244; copy hello_keeps_store, log 12273). Test that catches a real fault: none in the logic suite; H does.

3. minor. Two step 5 branches of rip.c have no test. rip.c:151-154 (Service Changed on a relay link keeps the entries) and rip.c:993-996 (a session start after a relay HELLO keeps the entries). Rule: Sessions ("live for one link"). Scenario for :151: helper sends HELLO and 3 PUTs, then the phone indicates Service Changed; the code keeps the 3 entries, but if the guard were removed the store would be emptied and no test would see it (H and B never indicate Service Changed). Scenario for :993: helper sends HELLO before ready_fn runs (20 ms after level 4); notes section 7 say no check asserts this order. Test that catches it: a two-device case where the stand-in indicates Service Changed after PUTs and the ring checks the count; a case that sends HELLO within 20 ms of level 4 and checks the store after the session start.

4. minor. "HELLO starts a session also when the helper has not subscribed to Out" is not proven. Code rrl_bt.c:169-178 and :94-101. Scenario: no test writes HELLO before subscribing (H subscribes at host main.c:962 before HELLO at :977; B at :1264 before :1265). Test that catches it: HELLO with Out off, then a PUT accepted (not code 2), and the ring's out_dropped up by one.

5. minor. A full Out queue drops READY and ACTION with no sign to the helper. rrl_bt.c:61-66, :177, :263-266. Rule: HELLO "answers READY on Out". Scenario: while notifications fail (for example no TX buffer), each queued frame is retried 5 times 50 ms apart (:107-125), so 8 refused frames hold the queue for up to about 2 s; a HELLO in that time is accepted (write returns success) but READY is not queued (:177 ignores the result); a helper that follows spec R9 waits 5 s and drops the link. Also: an ACTION queued while subscribed and dropped at :94-101 because the helper unsubscribed before it was sent is counted as sent (rip.c:1197-1198). The notes (section 7) say these paths have no test. Test that catches it: a ring-side case that fills the queue (notifications forced to fail) and checks that HELLO is refused or READY still goes out.

6. minor. Order B breaks the first sentence of "One source per link" as written. rip.c:568-585 and rip.c:1329-1336. Rule: "On a link where Apple's notification service was found, every relay frame is refused with code 7." Scenario B (log 9540): the ring finds Apple's service on the link after the relay HELLO, counts relay_blocked, and from then on accepts relay frames (relay_link_locked returns 0 for RIP_SRC_RELAY), for example a REMOVE `03 91 01 00 00` would be accepted. The second sentence of 7.7 says this case does not occur ("Apple's service is not there"); the code picks "first user wins" (notes reading 13). The lead must rule which sentence governs. Test that catches the literal rule: in B, a relay frame after relay_blocked becomes 1 must be refused with code 7.

7. note. Category values above 11 are stored. rrl.c:41, rinbox.c:134. Rule: the record text says "category u8 (the values of section 7.6, 0 to 11)", but code 5 lists no category check. Scenario: record `0C 00` (category 12) is stored. The screens read no category (a search of ring_screens for "category" has 0 hits), so there is no memory risk. No test either way (test_relay.c:1003 covers 0..11 only, and test_relay.c:1005, an `apply()` of RRL_ACT_NONE, does nothing).

8. minor. Checks of the two-device test that pass whatever the ring does. host main.c:956 ("nothing came on Out from those attempts": the subscription failed with a security error, so out_notify is not registered; my reading of the client, not run); host main.c:1029-1030 and :1034 (the "nothing is notified" halves come after bt_gatt_unsubscribe, so the stand-in's stack no longer hands notifications to out_notify; my reading of the client, not run); host main.c:1190 ("the large record is exactly 512 bytes" checks the test's own r.n); host main.c:1024 (the return of a local call). On the ring, the checks that only wait for a stand-in stage pass whatever the stand-in saw, yet are named as confirmations: ring main.c:587 "the stand-in confirmed it received nothing", :597, :604 "the stand-in received ACTION positive for 1003", :620, :630, :637. The real proof for each is another check (host main.c:1000, host main.c:1004, host main.c:1009, host main.c:1015; ring main.c:635, log 9227). Test that catches the gap: a ring-side count of frames notified on Out while unsubscribed (the out_dropped check at ring main.c:635 already does this for ERROR; nothing does it for READY or ACTION).

9. note. "The ring stores the 15 characters as received" holds only for text without NUL and valid UTF-8 at the end. rinbox.c:59-74 (put stops at a NUL, rinbox_utf8_cut drops an incomplete last character). Scenario: date field `04 0f 32 30 32 36 31 31 31 32 54 31 39 31 35 30 e2` is stored as 14 characters. A helper that follows R19 sends ASCII digits, so no effect in practice.

10. note. `out_try` can stay at 1 after a link ends. rrl_bt.c:103-125 and :296. Scenario: bt_gatt_notify fails while the link drops; on_disconnected sets out_try = 0 (:296); out_fn then takes the lock and sets out_try = 1 (:121); the next link's first failing frame gets 4 retries, not 5.

11. note. out_fn pops a frame it did not send after a link change. rrl_bt.c:106-111. Scenario: frame X is being notified with no lock held; the link ends and on_disconnected empties the queue; a new frame Y is queued before out_fn takes the lock again; out_fn pops Y as sent. The new link needs pairing and a HELLO first, so the window is far shorter than that; no realistic order found.

12. note. rip.c:1024-1026 returns before clearing `src_conn` when the iPhone part is not started (`inited` false), while rip_relay_open (rip.c:1309) works without it. Scenario: if rip_init was not called, a stale `src_conn` equal to a reused bt_conn object would give the next link the old source and keep the old entries. In the product rglue_init starts the iPhone part (app/src/main.c comment); I did not check that rglue_init stops on a failed rip_init.

13. note. The relay accepts frames on any level 4 link, not only the active device's (rrl_bt.c:147; notes section 3 says so). With one connection and the stranger rule of 7.3 the time such a link lasts is short. I did not check how long a newly paired, not active device stays linked.

14. minor. Two broken copies do not model the fault their name gives. tests/bsim/relay/broken_edit.py:39-41 and tests/relay/broken_edit.py:14-16 (`refused_changes_store`): the edit sets `act = RRL_ACT_REMOVE` after the refusal, so the frame is accepted (no ATT error 0x80, no ERROR) and the named check fails because the frame was not refused. A fault where the frame IS refused (0x80 and ERROR) and the store still changes (for example rrl_bt.c calling rip_relay_remove on RRL_ACT_ERROR) is modeled by no copy; the H digest check (ring main.c:676-678) would see it but was never shown to. tests/bsim/relay/broken_edit.py:28-31 (`store_not_emptied_at_link_end`) makes two faults: it also makes inbox_empty_locked never empty the store for any source, against "one named fault per variant". Test that catches it: a copy that keeps the refusal and adds a store call on the error path, named on ring main.c:676.

## 3. Answers to bars C, D, E, F and G

### C. Earlier steps
- rip.c: the diff removes one line (`rinbox_clear(&inbox);` in ready_fn) and adds branches that act only when `src == RIP_SRC_RELAY` or for `src_conn`. On an iPhone link `src` is NONE until Apple's service is found and APPLE after (rip.c:574-576), so: Service Changed still empties the store (inbox_empty_locked, rip.c:151 skips only for RELAY); session start still empties it (rip.c:993); dismiss and actions take the old path (rip.c:1189 only for RELAY); link end still empties it through end_session and stop_services. The one change on an iPhone link: if a relay HELLO arrives on it before Apple's service is found, Apple's service is not used (fault 6). Counter `ancs_missing` also counts a blocked service (rip.c:579).
- rinbox.c: only rinbox_upsert was added (rinbox.c:169-183); no line was removed.
- Tests of steps 1 to 4: the diff touches no file under tests/ except tests/relay/ and tests/bsim/relay/, so no assertion of an earlier step was changed. The earlier suites ran in the final run and passed: 27 stage end lines, none with an exit code other than 0; bsim-iphone, bsim-screens, bsim-control and their broken copies among them.

### D. Tests that cannot fail
Logic suite, 22 cases at the pin (test_relay.c):

| Case (line) | Every check can fail? |
|---|---|
| test_info_and_out_frames (171) | yes |
| test_every_opcode (195) | yes |
| test_code_1_wrong_length (248) | yes |
| test_code_2_no_hello (288) | yes |
| test_code_3_order (318) | yes |
| test_code_4_total (378) | yes |
| test_code_5_malformed_record (404) | yes |
| test_code_6_version (453) | yes |
| test_code_7_one_source_per_link (491) | yes (also compares the session before and after) |
| test_refused_frames_change_nothing (557) | partly: :615 and :625 cannot fail after :574 (fault 2); :614 counts the test's own TRY calls |
| test_pieces_of_every_size (630) | yes |
| test_record_of_2_and_512_and_513 (681) | partly: :742-743 cannot fail, the refused frames were never applied |
| test_every_truncation_of_a_valid_record (748) | partly: :804-806 count the test's own branches, decided by its own table `ok_at` |
| test_every_truncation_of_the_largest_record (837) | yes |
| test_put_not_stored_before_its_last_piece (864) | partly: :885 cannot fail after :883 |
| test_texts_cut_at_a_character (893) | yes (real rinbox code) |
| test_flags_and_category (979) | partly: categories 0..11 check only `act` (:1006); :1005 does nothing |
| test_fields_in_any_order_each_once (1010) | yes |
| test_replace_keeps_place_and_read_mark (1074) | yes (real rinbox_upsert) |
| test_the_17th_pushes_the_oldest_out (1132) | yes |
| test_remove_clear_and_hello_empty_the_store (1167) | partly: :1197 and :1207 test the test's own `apply()` |
| test_a_new_record_at_offset_0_drops_the_unfinished_one (1210) | yes |

Scenarios: H has the checks of fault 8 that cannot fail; the rest compare the ring's real store, counters and Out bytes with literals. I: every check can fail (the refusals are checked byte by byte, the store and the action route on the ring). B: host main.c:1271 ("the ring did not subscribe within 8 s") also passes if the ring never looks for the service; the ring check at ring main.c:776 (relay_blocked == 1, log 9540) is the real proof.

Broken copies (26: 12 logic, 14 two-device; each named check line found in the log, section G):
- Fail because of the fault, as named: logic put_early, text_cut_inside_char, remove_ignored, total_min_1, total_max_513, replace_moves_front, store_17, flag_bit5_ok, code7_not_enforced, repeat_type_ok, order_ignored; two-device relay_reaches_core, action_without_flag, remove_ignored, no_security_check, action_id, hello_keeps_store, error_not_notified, replace_moves_front, relay_wakes_screen, source_not_fixed.
- Fail for a reason next to the named fault: logic and two-device refused_changes_store (the frame is accepted, so the refusal check fails; fault 14); two-device put_early (the named check fails because a later piece is refused with code 3 after the early "store", not because an early entry was seen); two-device code7_not_enforced (HELLO is still refused with code 7 by the backstop at rrl_bt.c:170-175; the PUT then gets code 2, which fails the named check); two-device store_not_emptied_at_link_end (two faults, fault 14).
- relay_reaches_core and relay_wakes_screen call hooks that the test ring itself defines (ring main.c:203-222); they prove the checks can see a long press and a wake, not that a real path is caught.
- Stand-in independence: host_app includes only zephyr headers, gatt_dm.h and its own hosttools.h; its CMakeLists adds no module of the project; a search for RRL_, RINBOX_, rrl_, rip_, ring_relay and ring_inbox in host main.c has 0 hits. UUIDs (host main.c:118-121), opcodes and codes are its own literals.

### E. The worked example
- Used at the pin: no (fault 1). The six 20-byte frames, the 71-byte frame, REMOVE and ACTION of the example appear in no test.
- Hand walk through rrl.c at the pin. HELLO `01 01`: len 2, version 1, act HELLO (:107-116). Frame 1: len 20 >= 10; id le32(a5 00 01 00) = 0x000100a5; total 0x003e = 62; off 0; dlen 11; total in 2..512; off 0 starts the record; 0 + 11 <= 62; got 11; act NONE. Frames 2 to 5: off 0x0b, 0x16, 0x21, 0x2c each equals got (11, 22, 33, 44), same id and total; got 22, 33, 44, 55; act NONE. Frame 6: len 16, dlen 7, off 0x37 = 55 = got; 55 + 7 = 62 = total; parse: flags 0x12 & ~0x1F = 0; fields at p = 2 (type 1, len 16, ends 20), 20 (type 2, len 4, ends 26), 26 (type 3, len 17, ends 45), 45 (type 4, len 15, ends 62); p = 62 ends the loop; act PUT, id 0x000100a5. The message keeps all 17 bytes (rinbox_utf8_cut: the last character f0 9f 8d 9c is whole). The 71-byte frame: dlen 62 at offset 0, the same parse. REMOVE `03 a5 00 01 00`: len 5, act REMOVE, id 0x000100a5. Out: rrl_out_action(0x000100a5, 1) writes `82 a5 00 01 00 01`; rrl_out_error(2, 0) writes `83 02 00 00 00 00`; Info and READY equal the example (`01 10 30 30 a0 0f`, `81 01 10`). The flags 0x12 include bit 4, so a dismiss on the ring is allowed and a positive action is refused (rip.c:1184). Result: the code would accept exactly those bytes. This is my reading, not a run.

### F. The 15 readings of notes section 4

| # | Reading | 7.7 and android-helper-spec.md | Verdict |
|---|---|---|---|
| 1 | Order of checks; wrong length before HELLO is code 1 | 7.7 gives no order; spec 5.5 acts per code only | consistent |
| 2 | PUT of 9 bytes is code 1 | 7.7 Details: "A PUT carries at least 1 data byte" | consistent |
| 3 | Id in ERROR: the frame's id for PUT and REMOVE of 5 bytes or more, else 0 | 7.7: "id u32 (0 when none)"; spec example "ERROR code 2 (no HELLO), no id : 83 02 00 00 00 00" | consistent |
| 4 | Codes 3, 4, 5 drop the unfinished record | 7.7: "A frame that is refused changes nothing in the store" (the unfinished record is not the store); spec R14 never interleaves records; spec 5.5 code 3 "send that record again once from offset 0" | consistent |
| 5 | Another id or total mid record: code 3 | 7.7 code 3 "PUT piece out of order" | consistent |
| 6 | Category above 11 stored | 7.7: "category u8 (the values of section 7.6, 0 to 11)"; code 5 list has no category; spec table: "any other or missing: 0" | open: the record text and the code 5 list differ; a spec app never sends it (fault 7) |
| 7 | REMOVE of an id not held: accepted | 7.7 lists no code for it; spec R12 | consistent |
| 8 | HELLO in a running session: empties, READY again | 7.7 HELLO row; spec R17 "emptied at the end of a session with HELLO" | consistent |
| 9 | HELLO and CLEAR empty the whole store | 7.7: "empties what the relay stored"; one source per link | consistent |
| 10 | No subscription: READY and ERROR dropped, action refused, 0x80 still returned | 7.7 Refusals and Details; spec R8 | consistent (HELLO without subscription not proven, fault 4) |
| 11 | Long writes refused with 0x07 | 7.7 Details: "may carry as many as the link allows; the ring accepts every piece size"; spec section 4: "At 244 it is at most 244 bytes (ATT MTU 247, the ring's MTU, minus 3)"; spec R15 | consistent for a spec app (it never writes more than MTU minus 3); "every piece size" holds only up to one ATT write |
| 12 | Below level 4 the host's 0x05, not 0x80 | 7.7: 0x80 is for refused frames; spec R3 | consistent |
| 13 | First user fixes the source | 7.7: "On a link where Apple's notification service was found, every relay frame is refused with code 7. On a link with a relay session, Apple's service is not there"; spec section 2 repeats only the first sentence | in conflict with the first sentence in order B (fault 6); no effect on an Android phone |
| 14 | Reduced stand-in iPhone | not a protocol point | not a reading of 7.7 |
| 15 | Service Changed on a relay link keeps the entries | 7.7: "live for one link, as in section 7.6"; 7.6 empties the inbox on Service Changed for Apple's services | consistent reading, not proven (fault 3) |

An app built from the specification alone: I found no frame, size or order in sections 2, 4 and 5 of the spec that this ring refuses. The places where such an app could fail against this ring: (a) spec R9: READY may never come when the Out queue is full (fault 5); the app then drops the link after 5 s; (b) an app that does not follow R15 and writes more than MTU minus 3 bytes gets ATT error 0x07, not 0x80, and spec 5.5 has no row for it (reading 11); (c) spec 5.5 code 7 cannot happen on Android. Nothing ran on a phone.

### G. The notes' numbers
Log lines checked (each printed from the log by a script; all match the notes): 1277 (FLASH 522148 B, 53.57%), 1278 (RAM 183072 B), 2160 (ring_relay.logic PASSED, native_sim), 2170 (345 of 345), 2514, 2523, 9180, 9183, 9188, 9190, 9191, 9193, 9194, 9195, 9197, 9201, 9204, 9205, 9212, 9220, 9222, 9223, 9226, 9227, 9231, 9234, 9235, 9237, 9243, 9244, 9250, 9254, 9261, 9265, 9266, 9274, 9275, 9276, 9277, 9281, 9282, 9283, 9296, 9309, 9313, 9318, 9323, 9327, 9331, 9335, 9359, 9400, 9450 (TEST H RESULT PASS (180 checks passed)), 9472, 9474, 9477, 9500, 9508, 9512, 9521 (42 checks), 9540, 9542, 9569 (30 checks), the 14 two-device copy lines 9868 to 13167, 13168, 13511, 13512, 13517, 13522, 13536, 13548, 13553, 13554, the 24 logic copy lines 14013 to 14793, 14794, 15333 (RESULT PASS), 15335 (remote exit code 0). Stage ranges 9159-9571, 9572-13169, 13490-13551, 13552-13555, 13977-14795, 10-1263: match. Base log lines 1273 (518984 B), 1274 (182184 B), 2160 (323 of 323): match; 3,164 and 888 follow. 27 stage end lines, 0 not exit 0, stage order: match. 180 PASS check lines in H: match.
Code lines checked (all match): rip.c:80, 149, 573, 939, 993, 1029, 1184, 1309, 1371; rrl_bt.c:22-25, 27, 47-52, 73, 138, 147, 166, 221, 226, 235, 253, 283, 320; rrl.c:26, 94, 98, 107, 118, 172, 182, 197, 221; rrl.h:40; rinbox.c:169; app/CMakeLists.txt:23; app/prj.conf:50; build_all.sh:237; the 19 test_relay.c case lines of notes section 1b. Line counts of notes sections 5 and 6 (rip.c 1383, rip.h 145, rinbox.c 209, rinbox.h 104, rrl.c 230, rrl_bt.c 320, host main.c 1318, ring main.c 819, run.sh 185, broken_edit.py 63 and 91): match. test_relay.c "1245 lines" matched the pin; the working file now has 1330.
Does not match: none of the numbers. Two notes sentences changed after the pin (line 103 and line 124, see the top). Notes section 1d says "Every test of steps 1 to 4 still passes" and section 1b counts "22 cases": true at the pin, not for the working file now.

## 4. Not checked
- rip.c in full: I read lines 1-48, 149-215, 515-625, 795-1070, 1120-1230 and every hunk of the diff; the fetch, media and time code was not read.
- The full log (15,336 lines): I printed 131 cited lines of it and counted stage lines; the run 1 log and the other step5 logs were not read.
- Zephyr behaviour I rely on and did not check in its source: that a GATT client hands no notification to a callback after unsubscribe (fault 8), how the host treats a Write Command or a prepare write to In, whether bt_gatt_notify refuses an unsubscribed peer.
- ring_glue (whether it stops when rip_init fails, fault 12), ring_screens beyond a search for "category", ring_devices (stranger rule timing, fault 13).
- tests/bsim/relay/ring_app/prj.conf, host and common files beyond what is cited, testcase.yaml, the overlay, README.md diff.
- The source of android-helper-example.py (I ran it; its output equals spec section 4).
- Everything changed after the pin: the new case test_helper_example_bytes, the edits of host_app and ring_app main.c, the notes edits, and section 7.7 as changed at 22:54.

RESULT: done, 0 major and 8 minor faults (plus 6 notes) in step 5 at f79baaf; of the 50 rule rows of bar A, 2 are not proven and 1 is in conflict with the literal text of 7.7 in order B.
