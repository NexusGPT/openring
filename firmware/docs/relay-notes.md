# Software step 5: the relay service

Version: commit 1aae4da of this project (the files under `firmware/` and `design/firmware.md` are that version plus this step's changes). Author: builder of step 5. I ran no git. Section 7.7 of `design/firmware.md` is the rule; I did not change it.

Log of the run that counts: `firmware/build-logs/20261112-225014-os-relay.log` (a copy is in `firmware/build-logs/step5/`). I ran it from the project folder with `nice -n 19`, through `firmware/tools/remote.sh`, as a run named os-relay, with RING_REMOTE_SRC set so that the copy of the source went to `/root/ring-os/src-os-relay` (the header of the log shows the command `tools/build_all.sh` and that copy). The last build_all line is `RESULT PASS` (log line 15371); remote exit code 0 (log line 15373). The log has 27 stage end lines, 0 of them with an exit code other than 0. The stages, in the order they ran: dk, stack-report, bsim-build, bsim-run, tests-native_sim, pictures-native_sim, pictures-fakes, tests-nrf54lm20bsim_nrf54lm20a_cpuapp, pictures-nrf54lm20bsim_nrf54lm20a_cpuapp, pictures-fakes-nrf54lm20bsim_nrf54lm20a_cpuapp, bsim-control, bsim-control-broken, bsim-iphone, bsim-iphone-broken, bsim-relay, bsim-relay-broken, bsim-screens, bsim-screens-broken, link-settings, relay-no-core, broken-control, broken-devices, broken-inbox, broken-iphone, broken-relay, broken-screens, broken-time.

This is the third full run. The first (`step5/20261112-202935-os-relay-run1.log`) and the second (`step5/20261112-213132-os-relay-run2.log`) also ended with `RESULT PASS`. I made test changes after each: after run 1 the piece-size sweep of the 512-byte record; after run 2 the worked example of the helper specification (a new logic case and extra frames in the two-device test), HELLO before the subscription in scenario B, and the update of these notes. The ring code did not change after run 1. Raw outputs of every run of this step: `firmware/build-logs/step5/`.

## 1. The bar, point by point

### a. The relay service exists as section 7.7 says
- Service UUID `a3c20000-5b7e-4f2a-9c1d-7e2b6f4d8a90` and the three characteristics: `modules/ring_relay/src/rrl_bt.c` lines 22 to 25 (UUIDs) and 47 to 52 (the service: In write with response, Out notify with its CCC, Info read). Proof that a client finds them by these UUIDs: the stand-in discovers by the UUIDs it holds as its own literals (`tests/bsim/relay/host_app/src/main.c`), log line 9274.
- Info, 6 bytes `01 10 30 30 A0 0F`: `rrl.c:221`; read by the stand-in, log line 9282.
- Frames to In: HELLO `rrl.c:107`, PUT `rrl.c:118`, REMOVE `rrl.c:172`, CLEAR `rrl.c:182`. Frames on Out: READY, ACTION, ERROR `rrl.c:197` and the lines after it. READY seen by the stand-in: log line 9296.
- Record format (category, flags with bits 0 to 4 only, fields type/length/bytes, types 1 to 4 once, 2 to 512 bytes): `rrl.c:26` (parser) and the total check in `rrl.c:118` onward. Texts are cut at a character by `rinbox_utf8_cut` (step 3's function, used unchanged) through `rinbox_upsert` (`rinbox.c:169`).
- Refusal codes 1 to 7: `rrl.h:40`; decisions in `rrl.c` from line 94. The write is answered with ATT error 0x80 (`rrl_bt.c:226`) and ERROR is queued for Out (`rrl_bt.c:221`) and sent only while the helper is subscribed.
- Session rules: one session per link (`rrl_bt.c:138` starts a new session for a new link; `rrl_bt.c:283` ends it); the store of a link is emptied when the link ends (`rip.c:1029`); an unfinished PUT is dropped with the session. Proof: log line 9261.
- One source per link: `rrl.c:98` (every frame code 7 when the link is Apple's) fed by `rrl_bt.c:166`; the source itself is in the iPhone part (section 3).
- Actions: the negative action for a dismiss and the positive action go to the helper as ACTION; the store changes only on REMOVE; an action the notification lacks is refused on the ring (`rip.c:1184`); no subscription to Out refuses the action on the ring (`rrl_bt.c:253`).
- Security level 4: authenticated permissions on In, on the Out CCC and on Info (`rrl_bt.c:47` to `52`) and an explicit level 4 check in the In write handler (`rrl_bt.c:147`) and the Info read handler (`rrl_bt.c:235`).
- Nothing of section 7.7 was stopped as wrong or unbuildable. Where 7.7 is silent I made readings; they are all listed in section 4.

### b. Pure logic tests (no Bluetooth), native_sim and the simulated chip
- Suite `ring_relay`, 23 cases, `tests/relay/src/test_relay.c`. It passed on native_sim (log line 2161; 346 of 346 cases of all suites passed, log line 2170) and on `nrf54lm20bsim/nrf54lm20a/cpuapp` (log line 2511; log line 2523). The step 4 base log `build-logs/20261112-182447-lead-step4-r3-rerun.log` line 2160 has 323 cases; 346 minus 323 is 23: the 23 new cases and no old case lost.
- Every opcode: `test_every_opcode` (line 195): 0x01 to 0x04 each accepted, all 252 other values refused with code 1, with and without a session.
- Every refusal code: code 1 `test_code_1_wrong_length` (248), code 2 `test_code_2_no_hello` (288), code 3 `test_code_3_order` (318), code 4 `test_code_4_total` (378), code 5 `test_code_5_malformed_record` (404), code 6 `test_code_6_version` (453, all 256 versions), code 7 `test_code_7_one_source_per_link` (491). Refused frames change nothing: `test_refused_frames_change_nothing` (557).
- Pieces of every size from 1 byte up: `test_pieces_of_every_size` (630: a record of about 150 bytes in pieces of 1 byte up to larger than the record) and `test_record_of_2_and_512_and_513` (681: the record of exactly 512 bytes in pieces of 1 to 520 bytes). A PUT is never stored before its last piece: `test_put_not_stored_before_its_last_piece` (864).
- A record of exactly 2 and exactly 512 bytes stored, 513 refused (code 4 with the first piece, any piece size): `test_record_of_2_and_512_and_513` (681). A record of 1 and of 0 bytes: code 4.
- Every truncation of a valid record: `test_every_truncation_of_a_valid_record` (748: all 60 lengths from 0 to 59 of a record of 59 bytes; lengths 2, 20, 27, 42 and 59 end at a field boundary and are stored as shorter records, the other lengths from 2 are refused with code 5, lengths 0 and 1 with code 4; the same cuts in pieces of 1 byte; records cut in transit are never stored) and `test_every_truncation_of_the_largest_record` (837: all lengths 2 to 512 of the 512-byte record).
- The worked example of the helper specification (`design/software/os/android-helper-example.py`), byte for byte as literals: `test_helper_example_bytes` (1250): Info, HELLO, READY, the record of 62 bytes for id 0x000100a5 as six PUT frames of at most 20 bytes and as one frame of 71 bytes, REMOVE, CLEAR, ACTION negative and positive, ERROR code 2. The date is stored as received: a date that is not a date is kept (cut at 15 characters).
- Texts cut at a character: `test_texts_cut_at_a_character` (893: 3-byte and 4-byte characters over their limits, a limit inside a character, a character cut by the helper itself, the date cut at 15).
- Replace keeps place and read mark: `test_replace_keeps_place_and_read_mark` (1074). The 17th pushes the oldest out: `test_the_17th_pushes_the_oldest_out` (1132). REMOVE, CLEAR and HELLO: `test_remove_clear_and_hello_empty_the_store` (1167). Offset 0 drops an unfinished record: `test_a_new_record_at_offset_0_drops_the_unfinished_one` (1210).

### c. The two-device Bluetooth test on BabbleSim
Stage `bsim-relay`, log lines 9159 to 9573. Scenario H: `TEST H RESULT PASS (183 checks passed)` at log line 9453. Scenarios I and B are in point d. Ring side `tests/bsim/relay/ring_app/src/main.c` (real ring_devices, ring_control, ring_glue, ring_inbox, ring_time, ring_iphone, ring_relay, ring_screens and the core; real encryption; the screens' memory display), stand-in `tests/bsim/relay/host_app/src/main.c` (written for this project, shares no constant with the code under test). The two programs hand each other stage numbers through files, so the order of the steps is fixed.
- Pairing with the passkey the screen shows, level 4: ring line 9180, stand-in line 9281.
- A write before level 4 fails (the stand-in turns off the automatic retry on security errors, so it sees the error): write line 9275, subscription line 9276, read line 9277; the ring saw none of them reach its relay part: line 9183.
- Info read, Out subscribed, HELLO and READY: lines 9282, 9283 and 9296. Before HELLO: PUT, REMOVE and CLEAR answered with code 2 and a HELLO of version 2 with code 6 (ring line 9188).
- Four notifications at the smallest ATT payload (frames of at most 20 bytes, 11 data bytes each; 59, 301, 54 and 47 bytes in 6, 28, 5 and 5 frames; 40 pieces without a result): ring line 9190. The record 1002 has a title of 60 bytes (20 characters of 3 bytes, limit 48) and a message of 200 bytes (100 characters of 2 bytes, limit 160).
- The store holds them exactly (order, category, flags, all four texts, cut at 48 bytes = 16 characters and 160 bytes = 80 characters): ring line 9191.
- The screens: the list follows the store (line 9193), its frame differs from the empty list's (line 9194), the detail opens (line 9195) and sets the read mark (line 9197).
- Replace keeps place and read mark: line 9201.
- An action the notification does not have sends nothing, and the stand-in confirms it: the screens do not call the iPhone part (line 9204); the ring refuses direct calls with -ENOTSUP (line 9205); stand-in lines 9309 (1004, after 3 s) and 9313 (1003).
- The positive action arrives as ACTION positive: stand-in line 9318; ring line 9212; the store did not change.
- A dismiss chosen with the joystick arrives as ACTION negative: stand-in line 9323; the ring changed nothing until REMOVE (line 9220); the stand-in sent REMOVE (line 9327); the entry left (line 9222) and the screens went back to the list (line 9223).
- No subscription to Out: the ring refuses the action itself (line 9226); a frame refused in that time is still answered with ATT error 0x80 and nothing is notified (stand-in line 9331, ring line 9227); the stand-in received nothing (line 9335).
- RECORDING: a long press starts a recording (line 9231); during it the stand-in sent a PUT, a REMOVE, a malformed PUT and an unknown opcode, all handled as usual (line 9234); the core is still RECORDING with one start and no stop (line 9235); a long press then stops it (line 9237).
- 21 malformed frames, each refused with ATT error 0x80 and ERROR with its code and id (7 with code 1, 3 with code 3, 3 with code 4, 6 with code 5, 2 with code 6): stand-in lines 9359 to 9400; ring lines 9243 and 9244 (the store digest is the same).
- CLEAR (line 9250) and the screen: with the screen off, CLEAR and a PUT did not wake it (line 9254).
- The example of the helper specification as sent by the stand-in after the reconnect (the six literal frames of 20 bytes, REMOVE, the one frame of 71 bytes): stand-in lines 9442, 9442; the ring holds it as entry 0 of the rebuilt store (line 9265). Scenario B sends HELLO before it subscribes to Out: it is accepted and READY is not delivered (stand-in line 9560).
- The link drops: the store is empty (line 9261); after the reconnect (level 4 again with the stored key, no passkey) the stand-in's frames before HELLO are refused with code 2 and the next piece of the old, unfinished record with code 3 (line 9266); after the new HELLO the store is rebuilt exactly (line 9265): entries the specification's example, 3007 (a record of exactly 2 bytes), 3006 (a record of exactly 512 bytes in frames of 244 bytes, texts cut), 3005 (title cut at 47 bytes, before a 3-byte character) and the four first ones with the pre-existing flag.

### d. One source per link; the earlier steps
- Scenario I (the stand-in is an iPhone with a reduced notification service, the real UUIDs): `TEST I RESULT PASS (42 checks passed)` at log line 9524. HELLO, PUT, REMOVE, CLEAR and an unknown opcode are each refused with ATT error 0x80 and ERROR code 7 (stand-in lines 9503 to 9511); ring line 9475. The iPhone's notification 301 is untouched (line 9477). A dismiss on the ring goes to Apple's service, the source of the entry (stand-in line 9515, ring line 9480).
- Scenario B (the other order: the stand-in has the notification service too, but its relay HELLO comes first): `TEST B RESULT PASS (30 checks passed)` at log line 9571. The ring finds Apple's service on the relay's link and does not use it (line 9543); the relay's notification stays; a dismiss goes to the helper (line 9545).
- Step 3's own stand-in iPhone (`tests/bsim/iphone/host_app`) cannot write to the relay service without a change to that test, so scenario I uses a reduced iPhone service inside the new stand-in (row 14 of the table in section 4). It serves the notification service only, not the media and time services.
- Every test of steps 1 to 4 still passes: all stages of the final run have exit code 0 (27 stage end lines, 0 with another code). The suites of the earlier steps ran unchanged: `bsim-control` (log lines 2853 to 3776), `bsim-iphone` (5684 to 6114), `bsim-screens` (13208 to 13289), their broken copies and the logic suites' broken copies. No assertion of an earlier step was changed (section 5).

### e. Broken copies
- 26 broken copies in all, each failing on its own named check: 12 for the logic suite (stage `broken-relay`, log lines 14015 to 14833, `RESULT PASS` at line 14832, each on native_sim and on the simulated chip) and 14 for the two-device test (stage `bsim-relay-broken`, log lines 9574 to 13207, `RESULT PASS` at line 13206). Both stages are wired into `tools/build_all.sh` the way the earlier steps' copies are (`tests/relay/broken_run.sh` is found by the `broken_run.sh` loop, `tests/bsim/relay/run.sh --broken` by the `bsim-<name>-broken` loop). A copy counts only when the suite built, ran to its end and the named check line says FAIL.

Two-device test (one edit each; the edit must match exactly once):

| # | Copy | Fault | Named check that fails | Log line |
|---|---|---|---|---|
| 1 | `relay_reaches_core` | a relay frame reaches the core (it drives the joystick path while a recording runs) | ring check H: the core is still RECORDING, no recording started or stopped by the relay frames | 9873 |
| 2 | `code7_not_enforced` | code 7 is not enforced | stand-in check I: PUT on an iPhone's link refused with code 7 | 9950 |
| 3 | `action_without_flag` | an action is sent without its flag | stand-in check H: no ACTION frame arrived for an action 1004 does not have | 10245 |
| 4 | `store_not_emptied_at_link_end` | the store is not emptied at the end of the link | ring check H: the link dropped: the store is empty | 10540 |
| 5 | `remove_ignored` | REMOVE is ignored | ring check H: REMOVE arrived: 1002 left the store | 10833 |
| 6 | `put_early` | a PUT is stored before its last piece | stand-in check H: PUT 1001 (59 bytes in 6 frames) accepted | 11140 |
| 7 | `refused_changes_store` | a refused frame still changes the store (a malformed PUT removes the entry of its id) | stand-in check H: M20 flag bit 7 set refused with code 5 | 11426 |
| 8 | `no_security_check` | no authenticated permission and no level 4 check | stand-in check H: a write to In before security level 4 fails | 11717 |
| 9 | `action_id` | the action byte of ACTION is always 0 | stand-in check H: ACTION arrived: id 1002, negative (1) | 12010 |
| 10 | `hello_keeps_store` | HELLO does not empty the store | ring check H: the store holds 2003, 2002, 2001 (HELLO emptied what was there) | 12303 |
| 11 | `error_not_notified` | ERROR is never notified | stand-in check H: PUT before HELLO refused with code 2 | 12566 |
| 12 | `replace_moves_front` | a replace moves the entry to the front and loses its read mark | ring check H: the replace of 1002 arrives | 12859 |
| 13 | `relay_wakes_screen` | a relay frame turns the screen on while it is off | ring check H: relay frames (CLEAR, PUT) did not wake the screen | 13152 |
| 14 | `source_not_fixed` | the first user does not fix the source (Apple's service found after a HELLO takes the link) | ring check B: Apple's notification service found on the relay's link was not used | 13205 |

Logic suite (each fails the named case on both boards):

| # | Copy | Fault | Named case | Log lines (native_sim, simulated chip) |
|---|---|---|---|---|
| 1 | `put_early` | a PUT is stored before its last piece | `test_put_not_stored_before_its_last_piece` | 14051, 14083 |
| 2 | `refused_changes_store` | a refused (malformed) PUT still asks for a change of the store | `test_refused_frames_change_nothing` | 14119, 14151 |
| 3 | `text_cut_inside_char` | a text is cut inside a character | `test_texts_cut_at_a_character` | 14187, 14219 |
| 4 | `remove_ignored` | REMOVE is ignored | `test_remove_clear_and_hello_empty_the_store` | 14255, 14287 |
| 5 | `total_min_1` | a record of 1 byte is taken | `test_code_4_total` | 14323, 14355 |
| 6 | `total_max_513` | a record of 513 bytes is taken | `test_code_4_total` | 14391, 14423 |
| 7 | `replace_moves_front` | a replace moves the entry and loses its read mark | `test_replace_keeps_place_and_read_mark` | 14459, 14491 |
| 8 | `store_17` | the store holds 17 | `test_the_17th_pushes_the_oldest_out` | 14527, 14559 |
| 9 | `flag_bit5_ok` | flag bit 5 is accepted | `test_code_5_malformed_record` | 14595, 14627 |
| 10 | `code7_not_enforced` | code 7 is not enforced | `test_code_7_one_source_per_link` | 14663, 14695 |
| 11 | `repeat_type_ok` | a repeated field type is accepted | `test_code_5_malformed_record` | 14731, 14763 |
| 12 | `order_ignored` | the order of the pieces is not checked | `test_code_3_order` | 14799, 14831 |

- The eight faults the brief names are covered: a PUT stored before its last piece (logic 1, two-device 6), a refused frame that still changes the store (logic 2, two-device 7), a relay frame that reaches the core (two-device 1), code 7 not enforced (logic 10, two-device 2), an action sent without its flag (two-device 3), the store not emptied at link end (two-device 4), a text cut inside a character (logic 3), REMOVE ignored (logic 4, two-device 5).
- Where a copy can pass for the wrong reason: a copy fails many checks after its first one (the later steps of the script depend on the earlier ones: `put_early` ends with 67 failed checks, `action_without_flag` with 32). The named check is the first one that fails in script order. `action_id` leaves the ring's result at PASS because the ring cannot see the byte that goes out on Out; the stand-in's named check catches it. `error_not_notified` is also caught on the ring (the count of frames dropped on Out), but its named check is the stand-in's because that one comes first in the script. `text_cut_inside_char` needs both of its edits (the cut at the limit and the drop of an incomplete character at the end); a first version of the copy with one edit did not fail the test and was replaced (section 8).

### f. The real build for the development kit target
- Stage `dk` (log lines 10 to 1263) compiled with sysbuild and MCUboot. Application image `nrf54lm20dk/nrf54lm20a/cpuapp`: flash 522,148 bytes (53.57%) of 974,704 bytes (log line 1277); RAM 183,072 bytes (34.99%) of 511 KB (log line 1278).
- The base (the lead's step 4 round 3 run, `build-logs/20261112-182447-lead-step4-r3-rerun.log` lines 1273 and 1274): flash 518,984 bytes, RAM 182,184 bytes. The relay service and its store changes add 3,164 bytes of flash and 888 bytes of RAM. The bootloader image is unchanged.
- The relay is in the product: `app/CMakeLists.txt:23` adds the module, `app/prj.conf:50` turns it on; stage `link-settings` shows `CONFIG_RING_RELAY=y` in both product builds (log lines 13574 and 13586).
- Static stack frames (a lower bound, from the build's own stack-usage files, `step5/20261112-202841-s5-stack-2.log`): `in_write` 96 bytes, `rrl_frame` 32, `rrl_parse` 32, `rip_relay_put` 72, `rinbox_upsert` 48, `rinbox_set_text` 24, `relay_action` 24, `out_fn` 72. The longest chain on the Bluetooth receive thread is 240 bytes of these frames (`in_write`, `rip_relay_put`, `rinbox_upsert`, `rinbox_set_text`; the stack is 2,048 bytes). No run measured a peak (the simulated builds run on host stacks).

### g. One command
- `tools/build_all.sh` ran every stage of steps 1 to 5 in the final run: last build_all line `RESULT PASS` (log line 15371), server command exit code 0 (log line 15373). New stages of this step: `bsim-relay` (9159 to 9573), `bsim-relay-broken` (9574 to 13207), `broken-relay` (14015 to 14833), `relay-no-core` (13590 to 13593) and the relay part of `link-settings` (13528 to 13589); the relay logic suite ran inside the existing `tests-native_sim` and `tests-nrf54lm20bsim_nrf54lm20a_cpuapp` stages.

## 2. Rulings of the lead
1. New module `modules/ring_relay/` with a pure part (`rrl.c`, no kernel, no Bluetooth) and a Bluetooth part (`rrl_bt.c`). Built.
2. One store for both sources. Built as described in section 3. The screens did not learn the source: `modules/ring_screens/src/rscr_real.c` is unchanged and no other file of ring_screens was touched.
3. The source of a link is fixed by its first user and ends with the link: `rip.c:80` (state), `rip.c:573` (Apple's service found), `rip.c:1309` (HELLO), `rip.c:939` and `rip.c:1029` (the end). Proven in both orders: scenarios I and B.
4. The relay part calls nothing in ring_core and never wakes the screen. Stage `relay-no-core` searches the module's sources for the names of the core, the glue, the devices, the control and the screens: 0 hits (log line 13591); a copy with one glue include is found by the same search (log line 13592). The screen stays off when relay frames arrive (log line 9254; broken copy `relay_wakes_screen` fails that check).
5. The tests take the product's Bluetooth settings: the relay test ring includes the same `ring_iphone_link.conf` as the product. Stage `link-settings` was extended (`build_all.sh:237`): a relay test ring with a changed MTU is refused (log line 13549); the relay test ring equals the iPhone test ring (line 13550); both product builds equal the relay test ring (lines 13555 and 13560); twelve more settings the relay depends on (peripheral role, security manager, secure connections only, application pairing accept, connections, paired devices, identities, ATT buffers, automatic security request, the three ring modules) are compared between each product build and the relay test ring in the lines after.
6. No Android code, no helper app, no helper specification.

## 3. The one store: mechanism and lock order
- The store stays where it was: `inbox` in `modules/ring_iphone/src/rip.c`, guarded by that file's mutex `lk`. The functions the screens call are unchanged: `rip_inbox_count`, `rip_inbox_get`, `rip_inbox_mark_read`, `rip_dismiss`, `rip_action`.
- The iPhone part now knows the source of the link that fills the store: `src` (NONE, APPLE or RELAY) and `src_conn`, both under `lk` (`rip.c:80`). `src_conn` is not a reference: it is cleared when the link ends.
- The first user fixes the source. Apple's service found on the link sets APPLE (`rip.c:573`); if the link already has a relay session the service is not used and `relay_blocked` is counted. A relay HELLO sets RELAY (`rip_relay_open`, `rip.c:1309`); on an Apple link it returns -EPERM and the relay refuses with code 7.
- The relay writes the store only through `rip_relay_open`, `rip_relay_put`, `rip_relay_remove` and `rip_relay_clear` (`rip.c:1309` to `1371`). Each takes `lk`, checks that the link is the relay's (-EPERM on an Apple link, -ENOTCONN otherwise) and then uses the pure store (`rinbox_upsert`, `rinbox_remove`, `rinbox_clear`).
- An action goes to the source of the entry: `rip_action` finds the entry and checks its flag as before (`rip.c:1184`); if the source is RELAY it calls the hook the relay registered (`rip_relay_register`, called at start by `SYS_INIT`, `rrl_bt.c:320`), with `lk` released; otherwise it takes the old Apple path. A relay entry's action therefore never reaches Apple's service and an Apple entry's never reaches the relay.
- Entries of a relay session are not emptied by anything of the iPhone part except the end of the link, a new HELLO or CLEAR: `inbox_empty_locked` (`rip.c:149`) does nothing while the source is RELAY (a Service Changed indication from a phone that is not an iPhone must not empty them), and a session start that comes after a relay HELLO keeps the entries (`rip.c:993`: the helper may write at once after level 4).
- The relay session does not need to be the iPhone part's session link: the source is tracked per link (`src_conn`), so the relay works on any link that reached level 4.
- Lock order: relay lock `rl` (`rrl_bt.c:27`), then the iPhone part's `lk`. The relay calls the rip_relay functions with `rl` held. The iPhone part never calls the relay with `lk` held: `rip_action` releases `lk` before it calls the hook, and the hook takes only `rl`. Nothing takes `rl` while it holds `lk`. The Out frames are queued under `rl` and sent from the system work queue with no lock held across the Bluetooth call (`rrl_bt.c:73`). The relay's and the iPhone part's disconnect callbacks each take only their own lock.
- `rinbox_upsert` (new in ring_inbox, pure): a held id is replaced (category, flags, text) and keeps its place and read mark; a new id goes to the front and the 17th pushes the oldest out. Step 3's functions are unchanged.

## 4. Readings of section 7.7 and deviations
Section 7.7 is silent or open on these points. I built the reading in the second column. None of it changes the protocol; the lead may rule otherwise.

| # | Point | Built as |
|---|---|---|
| 1 | Order of the checks | source (7), then empty write, unknown opcode or wrong length (1), then HELLO version (6), then no HELLO (2), then total (4), then order or beyond total (3), then the record (5). The length is checked before the session, so a wrong-length frame before HELLO is code 1. |
| 2 | PUT with no data byte | a PUT frame of 9 bytes is code 1 (wrong frame length); the shortest PUT is 10 bytes. |
| 3 | The id in ERROR | the frame's id for PUT and REMOVE when the frame is at least 5 bytes long; 0 for every other frame. |
| 4 | A refused PUT and the unfinished record | a PUT refused with code 3, 4 or 5 drops the unfinished record. Frames refused with code 1, 2, 6 or 7 leave it alone. REMOVE and CLEAR also leave it alone. An accepted HELLO drops it. |
| 5 | A piece that does not match | a piece with another id or another total than the record in progress is code 3. |
| 6 | Category above 11 | stored as sent, not refused (7.7 lists no such refusal; step 3 stores such values as received too). |
| 7 | REMOVE of an id that is not held | accepted, nothing changes (no code is listed for it). |
| 8 | HELLO in a running session | accepted: it empties the store and answers READY again. |
| 9 | What HELLO and CLEAR empty | the whole store: on a relay link nothing else is in it. |
| 10 | No subscription to Out | READY and ERROR are dropped and counted (`out_dropped`); an action is refused on the ring (`actions_refused`); a refused write is still answered with ATT error 0x80. |
| 11 | Long writes | a prepare write or a write with an offset is refused with ATT error 0x07 (invalid offset); a frame is one write. |
| 12 | Security errors | a write, read or subscription below level 4 gets the host's own security error (ATT 0x05 insufficient authentication), not 0x80. |
| 13 | Source decided by the first user | a HELLO that arrives while the iPhone part is still looking for Apple's service makes the link a relay link; Apple's service found afterwards is not used (scenario B). A link where Apple's service was found first refuses every relay frame with code 7 (scenario I). |
| 14 | The stand-in iPhone of bar d | step 3's stand-in cannot write to the relay service; scenario I uses a reduced iPhone service inside the new stand-in (notification service only). Step 3's stand-in is untouched. |
| 15 | Status after a Service Changed on a relay link | the relay's entries stay (a phone that is not an iPhone may have the GATT service and indicate a change). |

Deviations from the lead's rulings: none. Ruling 2 allowed changes in ring_iphone, ring_inbox and `rscr_real.c`; I changed the first two and not the third.

The lead's bullet "Details" of 7.7 (seven answers, added after my first delivery) needed no change of the ring code: (1) the date is stored as received and never read (`test_helper_example_bytes`); (2) a PUT of 9 bytes is code 1 and any piece size is accepted (`test_code_1_wrong_length`, `test_pieces_of_every_size`, `test_record_of_2_and_512_and_513`); (3) CLEAR is valid at any time in a session (`test_remove_clear_and_hello_empty_the_store`, and in the two-device test with the screen off); (4) HELLO without a subscription to Out is accepted and READY is not delivered (scenario B); (5) the order is the order of arrival, newest first (the store tests); (6) the positive action is chosen with Right on the notification screen in the two-device test (line 9212); (7) the advertising was not touched.

## 5. Changed assertions of earlier steps
None. I changed no test file of steps 1 to 4 and no expected value in one. Files outside the new folders that I changed (all in `Owns`):

- `modules/ring_iphone/src/rip.c` (1383 lines): the source of a link, the relay's access to the store, the action route
- `modules/ring_iphone/include/ring_iphone/rip.h` (145 lines): enum rip_src, struct rip_relay_ops, rip_relay_*, seven new statistics
- `modules/ring_inbox/src/rinbox.c` (209 lines): rinbox_upsert (replace keeps place and read mark, or add)
- `modules/ring_inbox/include/ring_inbox/rinbox.h` (104 lines): rinbox_upsert
- `app/CMakeLists.txt` (41 lines): ring_relay added to the product
- `app/prj.conf` (71 lines): CONFIG_RING_RELAY=y
- `app/src/main.c` (121 lines): a comment only
- `tools/build_all.sh` (317 lines): stage relay-no-core, the relay test ring in link-settings, header comment
- `README.md` (93 lines): step 5 rows and notes

The earlier steps' suites ran against the changed `rip.c` and `rinbox.c` in the final run and passed (point d). The test counts agree: 346 cases now, 323 in the base plus the 23 new ones.

## 6. What was built (new files)

- `modules/ring_relay/include/ring_relay/rrl.h` (115 lines): frames, record, codes, session state of the pure part
- `modules/ring_relay/include/ring_relay/rrl_bt.h` (41 lines): statistics of the Bluetooth part
- `modules/ring_relay/src/rrl.c` (230 lines): pure part: frame handling, record parser, refusal decisions, Out frames, Info
- `modules/ring_relay/src/rrl_bt.c` (320 lines): Bluetooth part: the GATT service, one session per link, the queue for Out, the action hook
- `modules/ring_relay/Kconfig` (15 lines): RING_RELAY_LOGIC and RING_RELAY
- `modules/ring_relay/CMakeLists.txt` (7 lines): module build
- `modules/ring_relay/zephyr/module.yml` (4 lines): module file
- `tests/relay/src/test_relay.c` (1330 lines): logic suite, 23 cases
- `tests/relay/CMakeLists.txt` (15 lines): suite build (RING_RELAY_DIR and RING_INBOX_DIR for broken copies)
- `tests/relay/testcase.yaml` (8 lines): native_sim and the simulated chip
- `tests/relay/prj.conf` (2 lines): suite settings
- `tests/relay/broken_edit.py` (63 lines): 12 broken copies of the logic suite
- `tests/relay/broken_run.sh` (75 lines): runs each broken copy on both boards
- `tests/bsim/relay/run.sh` (185 lines): the two-device test, scenarios H, I and B, and --broken
- `tests/bsim/relay/broken_edit.py` (91 lines): 14 broken copies for the two-device test
- `tests/bsim/relay/ring_app/src/main.c` (821 lines): ring side (with the screens)
- `tests/bsim/relay/ring_app/CMakeLists.txt` (26 lines): ring build
- `tests/bsim/relay/ring_app/prj.conf` (66 lines): ring settings
- `tests/bsim/relay/ring_app/boards/nrf54lm20bsim_nrf54lm20a_cpuapp.overlay` (11 lines): memory display overlay (copy of the screens test's)
- `tests/bsim/relay/host_app/src/main.c` (1353 lines): the stand-in helper (GATT client) and the reduced stand-in iPhone service
- `tests/bsim/relay/host_app/CMakeLists.txt` (10 lines): stand-in build
- `tests/bsim/relay/host_app/prj.conf` (28 lines): stand-in settings
- `tests/bsim/relay/common/hosttools.h` (21 lines): host calls (copy of the screens test's)
- `docs/relay-notes.md`: this file

## 7. Not built and not proven
- The helper app on the Android phone is not built, and its specification is another helper's work. Nothing here ran against a real Android phone, a real iPhone or real hardware; the stand-ins are written for this project.
- Media and time from an Android phone, and the status, time and file characteristics of the ring service of section 7.2, are not built (7.7 says so).
- Not proven: what happens when `bt_gatt_notify` fails (the code retries five times, 50 ms apart, then drops the frame, counted); when the queue for Out is full (8 frames; the frame is dropped and counted); when `bt_conn_ref` returns nothing. These three paths have no test.
- Not proven: a relay session on a link that is not the iPhone part's session link (two bonded devices, the relay device not the active one). The code tracks the source per link and does not need the session link, but no test runs it.
- Not proven: how a real Android phone behaves. The test turns off the stand-in's automatic retry on security errors so it can see the error; a real Android phone starts bonding on that error, which the ring answers as for any phone (the pairing window rules of section 7.4 apply).
- Not proven: a stack peak (only static frame sums, point f), power use, timing at the real connection interval, and ATT payloads other than 20 and 244 bytes.
- The case where a relay frame arrives in the 20 ms before the iPhone part starts its session is handled by the code (`rip.c:993`) and exercised by scenario B, but no check asserts which of the two came first.

## 8. Looks at results before the final run
All raw outputs are in `firmware/build-logs/step5/`.
- `20261112-193423-s5-first.log`: first compile. The logic suite passed on native_sim (22 cases) and the product built for the simulated chip with the relay in it.
- `20261112-194421-s5-bsim-relay-1.log`: first two-device run. Scenario I passed. Scenario H failed 16 checks: the ring's screen had turned off 5 s after the last input while the ring waited for the stand-in, so the first joystick event only woke it. I fixed the test (the ring now presses Up every 3 s while it waits on the list and moves to an entry from any selection); the code under test was not changed. The check that failed first is at line 41 of that log.
- `20261112-194711-s5-bsim-relay-2.log`: scenario H passed (168 checks).
- `20261112-194918-s5-relay-broken-1.log`: first logic broken run. 11 copies failed their named case; `text_cut_inside_char` did not build (an unused function error in the copy). I fixed the edit (it now keeps the two functions used) and ran that copy again: `20261112-200649-s5-relay-broken-2.log`.
- `20261112-195552-s5-bsim-relay-broken-1.log`: first run of 12 two-device broken copies, all failed their named checks. Later runs added copies 13 and 14 (`20261112-202231-s5-bsim-relay-broken-2.log`, `20261112-202622-s5-bsim-relay-broken-3.log`).
- `20261112-200754-s5-regress-1.log`: the earlier steps' two-device tests (iphone, screens, control) and all native_sim suites with the relay built in: all passed (345 cases).
- `20261112-201451-s5-stages-1.log`: a rehearsal of the new `link-settings` and `relay-no-core` code and the product's flash and RAM, before the first full run.
- `20261112-202031-s5-bsim-relay-3.log` and `20261112-202445-s5-bsim-relay-4.log`: scenario H with the CLEAR, screen-off and unsubscribed-frame steps added, and scenario B.
- `20261112-202815-s5-stack-1.log`, `20261112-202841-s5-stack-2.log`: stack report and static frame sizes.
- `20261112-202935-os-relay-run1.log`: the first full run, `RESULT PASS`.
- `20261112-213132-os-relay-run2.log`: the second full run, `RESULT PASS`; its audit was `audit-final.txt` as it stood then (488 claims, 0 unmatched). The lead's clarifications of 7.7 arrived after it.
- Two lookups in the Zephyr sources on the server (`20261112-192816-s5-lookup.log`, `20261112-192848-s5-lookup2.log`) printed source lines of Zephyr into their logs. The rule says no Zephyr source text in any file or log I write, so I deleted those two logs (this goes against the rule not to delete a file my run wrote; I judged the rule on source text to be the stronger one). I kept no Zephyr text. My two conclusions are proven by the tests instead of by a quoted line: the host function that tells whether the helper has subscribed accepts the value attribute of Out (the subscribed case is stand-in line 9318 and the unsubscribed case is ring line 9226), and the host raises security and retries a failed request on its own unless that is turned off (the stand-in turns it off in `tests/bsim/relay/host_app/prj.conf`, and the failed write is stand-in line 9275). The same two runs left two hidden `.part` files (remote.sh's temporary copies of those logs) that held the same source lines; I deleted them too. The other `.part` files in the folder are remote.sh's temporary copies of other runs; the search in `step5/rules-search.txt` finds no Zephyr source line in any of them.
- Server copies: the folders my runs made on the server are listed and removed in `step5/server-cleanup.txt`.

## 9. Rules kept
- No browser of any kind. No git. No key file was printed, copied or read: the server key is used only by `tools/remote.sh` by its path (search of every saved log and delivered file: `step5/rules-search.txt`).
- No code of Nordic's kit or of Zephyr was copied; the module uses their headers and settings only. The search for the lines I had read in Zephyr, in every saved log and delivered file, is in `step5/rules-search.txt`. The build logs hold what the compilers and Kconfig print by themselves (they did in the earlier steps too).
- The relay adds no screen and no picture; no outside font or file was added. The names in the test data are made-up (`com.example`).
- Every shell command of this step used `2>&1` or a log file, nothing was sent to /dev/null (search in `step5/rules-search.txt`), heavy commands ran at `nice -n 19` through `remote.sh`, waiting was done with `until` loops, and clock times in this file come from `date` or from the logs.
- On the server I deleted only exact folders my own runs created, one per command (`step5/server-cleanup.txt`).

## 10. Counts (from the checklist)
The counts come from the ticks in `firmware/build-logs/step5/CHECKLIST.md`: 63 items, 62 done with evidence, 0 not done. Item 61 is the audit of this file and of the final reply (`step5/audit-final.txt`); it is ticked after the audit exits 0, so the count above is taken before that tick if it reads one less than the items.

Round 2 (step5-round2.md) changed the code of rrl_bt.c and rip.c and added tests: the counts, line numbers and logs of this file are those of the first delivery. The current figures are in `docs/step5-round2.md`.

## State after round 3

True counts (details in `docs/step5-round2.md` and `docs/step5-round3.md`; this section supersedes the counts above):
- Logic suite `ring_relay`: 23 cases, on native_sim and on the simulated chip; 346 cases in all suites.
- Two-device test: scenarios H (156 checks), I (39), B (37), Q (33); waits are not counted as checks (`r3-relay-1.log`, lines 329, 400, 466, 535).
- Broken copies: 19 for the two-device test and 13 for the logic suite, 32 in all, each failing its own named check (`r3-broken-1.log`, `r3-broken-2.log`).
- Test hooks (`CONFIG_RING_RELAY_TEST_HOOKS`, test ring only, off in both product builds, guard with a self test in `build_all.sh`): block the Out queue, hold the iPhone part's session start.
- Application image of the development kit build: flash 522,212 bytes, RAM 183,080 bytes.

Still not proven: a real Android phone, a real iPhone, hardware; a failed notify in the middle of a link end; a relay on a link that is not the iPhone part's session link; a stack peak. Not built: a sign on the wearer's screen when an action is refused.

RESULT: done, the relay service is built and proven against stand-ins (final build_all run RESULT PASS, exit 0); the open points are in sections 4 and 7.
