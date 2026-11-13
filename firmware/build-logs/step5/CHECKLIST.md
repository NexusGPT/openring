# Checklist, software step 5 (relay service)

Format: `- [ ] N. item`, closed as `[x] ... evidence: <file>` or `[-] ... not done: <measured limit>`.
Started 2026-11-12 19:24 (clock: `date`). Limit 5 hours (4 hours at 23:24).

## Bar a. The service exists as section 7.7 says
- [x] 1. service UUID a3c20000-5b7e-4f2a-9c1d-7e2b6f4d8a90, In a3c20001 (write with response), Out a3c20002 (notify), Info a3c20003 (read, 6 bytes) evidence: rrl_bt.c:22-25 and 47-52; step5/20261112-225014-os-relay.log line 9274; step5/20261112-225014-os-relay.log line 9282
- [x] 2. frames to In: HELLO 0x01 (version), PUT 0x02 (id u32, total u16, offset u16, data), REMOVE 0x03 (id u32), CLEAR 0x04 evidence: rrl.c:107, 118, 172, 182; every opcode: test_every_opcode (test_relay.c:195); two-device: step5/20261112-225014-os-relay.log line 9296
- [x] 3. frames on Out: READY 0x81 (1, 16), ACTION 0x82 (id u32, action u8), ERROR 0x83 (code u8, id u32) evidence: rrl.c:197; READY step5/20261112-225014-os-relay.log line 9296; ACTION step5/20261112-225014-os-relay.log line 9323; ERROR step5/20261112-225014-os-relay.log line 9359
- [x] 4. record format: category, flags (bits 0..4, others 0), fields type/length/bytes, types 1..4 once each, at least 2 and at most 512 bytes, texts cut at a character evidence: rrl.c:26; tests test_every_truncation_of_a_valid_record, test_texts_cut_at_a_character, test_fields_in_any_order_each_once, test_flags_and_category; step5/20261112-225014-os-relay.log line 2161
- [x] 5. refusal codes 1 to 7, ATT error 0x80, ERROR notified when subscribed, a refused frame changes nothing in the store evidence: rrl.h:40; rrl_bt.c:226, 221; step5/20261112-225014-os-relay.log line 9400; step5/20261112-225014-os-relay.log line 9244
- [x] 6. session rules: a link's notifications live for one link, HELLO empties the relay's entries, an unfinished PUT is dropped at link end evidence: rrl_bt.c:283; rip.c:1029; step5/20261112-225014-os-relay.log line 9261; step5/20261112-225014-os-relay.log line 9265
- [x] 7. one source per link: Apple's service found -> every relay frame code 7 evidence: rrl.c:98; rip.c:1309; scenario I step5/20261112-225014-os-relay.log line 9475
- [x] 8. actions: ACTION negative for a dismiss, store unchanged until REMOVE, an action the notification lacks is refused on the ring, no subscription to Out -> refused on the ring evidence: rip.c:1184 and relay_action rrl_bt.c:253; step5/20261112-225014-os-relay.log line 9220; step5/20261112-225014-os-relay.log line 9226
- [x] 9. security level 4 on every characteristic evidence: rrl_bt.c:47-52, 147, 235; step5/20261112-225014-os-relay.log line 9275; broken copy no_security_check step5/20261112-225014-os-relay.log line 11717
- [x] 10. read mark lives on the ring only; replace keeps place and read mark; new id to the front; the 17th pushes the oldest out evidence: tests test_replace_keeps_place_and_read_mark (1074), test_the_17th_pushes_the_oldest_out (1132); two-device step5/20261112-225014-os-relay.log line 9201
- [x] 11. any point of 7.7 that cannot be built is stopped, said in the notes, and the rest is built (section 7.7 is not changed) evidence: none stopped: no point of 7.7 was found wrong or unbuildable; readings listed in docs/relay-notes.md section 4

## Bar b. Pure logic tests (native_sim and the simulated chip)
- [x] 12. every opcode (0x01..0x04, every other value refused) evidence: test_every_opcode (test_relay.c:195); step5/20261112-225014-os-relay.log line 2161; step5/20261112-225014-os-relay.log line 2511
- [x] 13. every refusal code 1 to 7 evidence: test_code_1..test_code_7 (test_relay.c:248-491); step5/20261112-225014-os-relay.log line 2161; step5/20261112-225014-os-relay.log line 2511
- [x] 14. pieces of every size from 1 byte up evidence: test_pieces_of_every_size (630), test_record_of_2_and_512_and_513 (681); step5/20261112-225014-os-relay.log line 2161
- [x] 15. record of exactly 2 bytes stored, exactly 512 stored, 513 refused evidence: test_record_of_2_and_512_and_513 (test_relay.c:681); two-device step5/20261112-225014-os-relay.log line 9265
- [x] 16. every truncation of a valid record refused or handled as 7.7 says evidence: test_every_truncation_of_a_valid_record (748), test_every_truncation_of_the_largest_record (837); step5/20261112-225014-os-relay.log line 2161
- [x] 17. texts cut at a character evidence: test_texts_cut_at_a_character (test_relay.c:893); broken copy text_cut_inside_char step5/20261112-225014-os-relay.log line 14187; two-device step5/20261112-225014-os-relay.log line 9191
- [x] 18. replace keeps place and read mark evidence: test_replace_keeps_place_and_read_mark (test_relay.c:1074); broken copy replace_moves_front step5/20261112-225014-os-relay.log line 14459
- [x] 19. the 17th pushes the oldest out evidence: test_the_17th_pushes_the_oldest_out (test_relay.c:1132); broken copy store_17 step5/20261112-225014-os-relay.log line 14527
- [x] 20. the suite runs on native_sim and on nrf54lm20bsim/nrf54lm20a/cpuapp evidence: step5/20261112-225014-os-relay.log line 2161 (native_sim) and step5/20261112-225014-os-relay.log line 2511 (nrf54lm20bsim/nrf54lm20a/cpuapp)

## Bar c. Two-device test on BabbleSim
- [x] 21. the stand-in helper (written for this project) is the GATT client; real encryption; passkey pairing evidence: host_app/src/main.c written for this project; step5/20261112-225014-os-relay.log line 9180; step5/20261112-225014-os-relay.log line 9281
- [x] 22. finds the relay service, reads Info, subscribes to Out, HELLO -> READY evidence: step5/20261112-225014-os-relay.log line 9282; step5/20261112-225014-os-relay.log line 9296
- [x] 23. at least four notifications; one record needs several pieces at ATT payload 20; one multi-byte text longer than its limit evidence: step5/20261112-225014-os-relay.log line 9190; record 1002 has a 60-byte title and a 200-byte message (step5/20261112-225014-os-relay.log line 9298)
- [x] 24. the ring's store holds them exactly evidence: step5/20261112-225014-os-relay.log line 9191
- [x] 25. screens: the list shows them, the detail opens evidence: step5/20261112-225014-os-relay.log line 9193; step5/20261112-225014-os-relay.log line 9195
- [x] 26. dismiss with the joystick -> ACTION negative at the stand-in; the stand-in sends REMOVE; the entry leaves the store evidence: step5/20261112-225014-os-relay.log line 9323; step5/20261112-225014-os-relay.log line 9327; step5/20261112-225014-os-relay.log line 9222
- [x] 27. positive action -> ACTION positive at the stand-in evidence: step5/20261112-225014-os-relay.log line 9318
- [x] 28. an action the notification does not have sends nothing; the stand-in confirms it received nothing evidence: step5/20261112-225014-os-relay.log line 9309; step5/20261112-225014-os-relay.log line 9313
- [x] 29. link drop: the store is empty; after reconnect and a new HELLO the store is rebuilt evidence: step5/20261112-225014-os-relay.log line 9261; step5/20261112-225014-os-relay.log line 9265
- [x] 30. a write before security level 4 fails evidence: step5/20261112-225014-os-relay.log line 9275; step5/20261112-225014-os-relay.log line 9276; step5/20261112-225014-os-relay.log line 9277
- [x] 31. each malformed frame of 7.7 is refused with its code and leaves the store unchanged evidence: step5/20261112-225014-os-relay.log line 9359 to step5/20261112-225014-os-relay.log line 9400; step5/20261112-225014-os-relay.log line 9244
- [x] 32. while the core is in RECORDING, relay frames change nothing in the core evidence: step5/20261112-225014-os-relay.log line 9234; step5/20261112-225014-os-relay.log line 9235

## Bar d. One source per link, earlier steps
- [x] 33. on a link with the stand-in iPhone (Apple's notification service found) a relay frame is refused with code 7, the iPhone's notifications untouched evidence: scenario I step5/20261112-225014-os-relay.log line 9475; step5/20261112-225014-os-relay.log line 9477; scenario B step5/20261112-225014-os-relay.log line 9543
- [x] 34. every test of steps 1 to 4 still passes, assertions unchanged (or each changed assertion listed) evidence: 27 stage end lines in step5/20261112-225014-os-relay.log, 0 with an exit code other than 0; no test file of steps 1 to 4 changed (docs/relay-notes.md section 5)

## Bar e. Broken copies
- [x] 35. at least 8 broken copies (logic and Bluetooth together), each failing on its own named check, wired into the build evidence: 26 copies: step5/20261112-225014-os-relay.log lines 9574 to 13207 (14, RESULT PASS line 13206) and step5/20261112-225014-os-relay.log lines 14015 to 14833 (12, RESULT PASS line 14832)
- [x] 36. includes: a PUT stored before its last piece evidence: put_early: logic step5/20261112-225014-os-relay.log line 14051, two-device step5/20261112-225014-os-relay.log line 11140
- [x] 37. includes: a refused frame that still changes the store evidence: refused_changes_store: logic step5/20261112-225014-os-relay.log line 14119, two-device step5/20261112-225014-os-relay.log line 11426
- [x] 38. includes: a relay frame that reaches the core evidence: relay_reaches_core: two-device step5/20261112-225014-os-relay.log line 9873
- [x] 39. includes: code 7 not enforced evidence: code7_not_enforced: logic step5/20261112-225014-os-relay.log line 14663, two-device step5/20261112-225014-os-relay.log line 9950
- [x] 40. includes: an action sent without its flag evidence: action_without_flag: two-device step5/20261112-225014-os-relay.log line 10245
- [x] 41. includes: the store not emptied at link end evidence: store_not_emptied_at_link_end: two-device step5/20261112-225014-os-relay.log line 10540
- [x] 42. includes: a text cut inside a character evidence: text_cut_inside_char: logic step5/20261112-225014-os-relay.log line 14187 and step5/20261112-225014-os-relay.log line 14219
- [x] 43. includes: REMOVE ignored evidence: remove_ignored: logic step5/20261112-225014-os-relay.log line 14255, two-device step5/20261112-225014-os-relay.log line 10833

## Bar f. Product build
- [x] 44. the real build for the development kit target compiles; flash and RAM reported from the build output evidence: stage dk step5/20261112-225014-os-relay.log lines 10 to 1263: FLASH step5/20261112-225014-os-relay.log line 1277, RAM step5/20261112-225014-os-relay.log line 1278 (flash 522148 bytes, RAM 183072 bytes)

## Bar g. One command
- [x] 45. `tools/build_all.sh` runs every stage of steps 1 to 5; last line `RESULT PASS`; the server command exits 0 (run once at the end, `RING_REMOTE_SRC=/root/ring-os/src-os-relay nice -n 19 sh firmware/tools/remote.sh os-relay "tools/build_all.sh"`) evidence: RESULT PASS step5/20261112-225014-os-relay.log line 15371; remote exit code 0 step5/20261112-225014-os-relay.log line 15373; copy of the log step5/20261112-225014-os-relay.log
- [x] 46. single-stage runs during the work use RING_REMOTE_SRC=/root/ring-os/src-os-relay and names starting s5- evidence: single-stage runs s5-*.log in step5/ (RING_REMOTE_SRC=/root/ring-os/src-os-relay, names start with s5-); listed in docs/relay-notes.md section 8

## Rulings of the lead
- [x] 47. ruling 1: module firmware/modules/ring_relay/ with a pure part and a Bluetooth part evidence: modules/ring_relay/src/rrl.c (pure) and rrl_bt.c (Bluetooth); relay-no-core step5/20261112-225014-os-relay.log line 13591
- [x] 48. ruling 2: one store for both sources; mechanism and lock order described in the notes; the screens do not learn the source; rscr_real.c unchanged or changed only for this evidence: docs/relay-notes.md section 3; rip.c:80-1371; rscr_real.c unchanged; scenario I and H share the screens: step5/20261112-225014-os-relay.log line 9453, step5/20261112-225014-os-relay.log line 9524
- [x] 49. ruling 3: the source of a link is fixed by its first user (Apple's service found, or a relay HELLO) and ends with the link evidence: rip.c:573, 1309, 939; scenario I step5/20261112-225014-os-relay.log line 9524, scenario B step5/20261112-225014-os-relay.log line 9571; broken copy source_not_fixed step5/20261112-225014-os-relay.log line 13205
- [x] 50. ruling 4: the relay part calls nothing in ring_core and never wakes the screen evidence: relay-no-core step5/20261112-225014-os-relay.log line 13591 and step5/20261112-225014-os-relay.log line 13592; step5/20261112-225014-os-relay.log line 9254; broken copies relay_reaches_core step5/20261112-225014-os-relay.log line 9873, relay_wakes_screen step5/20261112-225014-os-relay.log line 13152
- [x] 51. ruling 5: the tests take the product's Bluetooth build settings; the link-settings stage is extended to the new test evidence: link-settings step5/20261112-225014-os-relay.log lines 13528 to 13589: relay self test step5/20261112-225014-os-relay.log line 13549, relay ring step5/20261112-225014-os-relay.log line 13550, products step5/20261112-225014-os-relay.log line 13555, step5/20261112-225014-os-relay.log line 13560
- [x] 52. ruling 6: no Android code, no helper app, no helper specification evidence: no Android code, no helper app, no helper specification written (new files listed in docs/relay-notes.md section 6)

## Standing rules
- [x] 53. no browser; no git; no secret printed, copied or read evidence: step5/rules-search.txt (key, browser and git searches of the saved files); I ran no git and no browser
- [x] 54. no source text of Nordic's kit or Zephyr in any file or log written (own code, headers and settings only) evidence: step5/rules-search.txt (search for the Zephyr lines I had read); two lookup logs deleted, said in docs/relay-notes.md section 8
- [x] 55. no other company's logo or product name on a screen; no outside font or file evidence: no screen file changed (rscr_real.c and all of ring_screens untouched); test data names are made up (com.example.*)
- [x] 56. stderr never sent to /dev/null; heavy commands at nice -n 19; no foreground sleep; clock times from `date` evidence: step5/rules-search.txt (no /dev/null in delivered scripts); commands used 2>&1 or log files; until loops for waiting; clock from date
- [x] 57. on the server delete only one exact folder created by my own run, one per command; nothing with "lead" in its name; remove what I made outside the output folder before ending and save the listing evidence: step5/server-cleanup.txt
- [x] 58. notes: plain words, short sentences, bullets, no em dashes evidence: step5/rules-search.txt (no em dash in docs/relay-notes.md)

## Deliverable
- [x] 59. firmware/docs/relay-notes.md: bar a to g point by point with file and line, test name, log name and log line; files built; mechanism of ruling 2 with lock order; every deviation from 7.7 or the rulings; every changed assertion of an earlier step; what is not built and not proven; flash and RAM; last line `RESULT: <done|blocked>, <one sentence>` evidence: docs/relay-notes.md (231 lines)
- [x] 60. README.md updated for step 5 evidence: README.md rows and notes for step 5
- [x] 61. final audit (claims in the final reply and notes matched to saved evidence) saved evidence: step5/audit-final.txt line 534 (claims checked 510, matched 510, unmatched 0), audit exit 0

## Added after the lead's clarifications of 7.7 (Details bullet)
- [x] 62. the seven clarifications are built: date stored as received, PUT at least 1 data byte and any piece size, CLEAR at any time in a session, HELLO without a subscription to Out (READY not delivered), order of arrival, the positive action tested through the screen (Right), advertising unchanged evidence: docs/relay-notes.md section 4 (Details); step5/20261112-225014-os-relay.log line 9560; step5/20261112-225014-os-relay.log line 9212; test_helper_example_bytes (test_relay.c:1250)
- [x] 63. the worked example of design/software/os/android-helper-example.py (Info, HELLO, READY, the 62-byte record as six PUT frames at 20 bytes and as one frame, REMOVE, ACTION, ERROR) is used byte for byte in the pure tests and in the stand-in helper evidence: test_helper_example_bytes (test_relay.c:1250); step5/20261112-225014-os-relay.log line 9442; step5/20261112-225014-os-relay.log line 9442; step5/20261112-225014-os-relay.log line 9265
