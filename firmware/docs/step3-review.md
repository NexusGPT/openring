# Step 3 review: the iPhone part and the inbox

Version judged: the files on disk under firmware/ on 2026-11-12 from 00:31 CET, which the lead names commit e455a9f. I ran no git, so I could not confirm that id. The builder's notes name another commit, 221746b (F/docs/iphone-notes.md:3). No file under F/modules, F/app, F/tests or F/tools is newer than the start of the builder's final run (2026-11-11 23:58:59). I ran no build, no simulation and no ssh. Every finding comes from reading the cited lines. Run-time statements come from LOG or LEAD below, or are marked "by reading".

Short names:
- F/ = firmware/
- LOG = F/build-logs/step3/20261111-235859-os-iphone.log (the builder's final run). I checked all 94 lines that the notes quote in section 10 against the log, and all 94 match.
- LEAD = F/build-logs/20261112-003019-lead-step3-rerun.log (the lead's rerun; it is in F/build-logs/, not in F/build-logs/step3/). It finished at 00:50 CET while I worked; see bar point k.
- RIP = F/modules/ring_iphone/src/rip.c, RIPL = F/modules/ring_iphone/src/ripl.c, INBOX = F/modules/ring_inbox/src/rinbox.c
- RING = F/tests/bsim/iphone/ring_app/src/main.c, PHONE = F/tests/bsim/iphone/host_app/src/main.c (the stand-in iPhone)
- RUN = F/tests/bsim/iphone/run.sh, EDIT = F/tests/bsim/iphone/broken_edit.py, APPLE = F/build-logs/step3/apple/, KIT = F/build-logs/step3/kit/
- DESIGN = design/software/os/design.md, FW = design/firmware.md

## 1. The bar, point by point

**a. Three or more notifications held exactly; the 200-byte message cut at a character, at most 160 bytes: met.**
- Test: the stand-in adds five notifications (PHONE:1066-1076). The ring compares every field with literals, including category, flags and date (RING:370-381). Entry 103 is the iPhone cutting at 160 bytes inside a character. Entry 105 is the iPhone ignoring the limit and sending 200 bytes. Both must hold 53 euro signs, 159 bytes (RING:246-253, :375-381).
- Code: the Data Source answer keeps at most 160 raw bytes (RIPL:141-145). The store then drops the half character at the end (INBOX:43-55).
- Log: LOG:3992-3997, all PASS.
- Weak spots:
  - The check "no message is longer than 160 bytes and none ends inside a character" looks at entries 0 and 2 only (RING:382-383).
  - The first branch of the cut (INBOX:38-42, a limit that falls inside the data) cannot be reached over Bluetooth, because RIPL:142 has already cut the data to 160 bytes. Only the logic test `test_utf8_cut_property` reaches it (F/tests/inbox/src/test_inbox.c:252-281).

**b. A change replaces the text, a removal deletes the entry, the 17th drops the oldest: met.**
- Test: RING:386-398. The check on the 17th compares indexes and also needs `inbox_dropped == 1`.
- Code: RIP:150-174, INBOX:114-137, INBOX:169-182.
- Log: LOG:3998-4003.

**c. A dismiss arrives at the stand-in as the negative action for that id; a positive action likewise; an action without its flag sends nothing: partly met.**
- What is met: the stand-in's own record shows the negative action for 122 and the positive action for 121, and nothing else (PHONE:1214-1216, LOG:4108). The action IDs are recorded on the stand-in side (PHONE:425-429).
- What is not met: "an action without its flag sends nothing" is proven only by the ring's own return code (RING:409-411) and its own counters (RING:414-415).
  - The stand-in refuses a flagless action with 0xA3 before it records anything (PHONE:422-424, before :425-430). So its "and no other" check cannot see such a send.
  - The builder's own broken run shows this. In the action_flag run the flag check (RIP:961) was removed, so the ring passed the flagless actions on to the kit's write instead of returning -ENOTSUP (its two checks at RING:409-411 said FAIL). The stand-in still printed only the actions for 122 and 121, and its check said "two actions arrived: negative for 122, positive for 121, and no other PASS" (bsim-iphone-broken stage of LOG, run "broken-action_flag"). LOG does not show whether those writes reached the stand-in, because the ring's own "rip:" lines are not copied into LOG. By reading PHONE:422-424, any that did arrive were refused before being recorded. The lead's rerun shows the same thing: the stand-in check says PASS in its action_flag run (LEAD:5042).
  - So the notes' claim "the stand-in saw no third command (same check line of the stand-in, `nactions == 2`)" (F/docs/iphone-notes.md:14) is not evidence for this point.
  - A copy that sends the action and then returns -ENOTSUP would pass every check (by reading: the "no error was counted" check at RING:475-477 does not include `action_failed`).
- Not built: no ring screen or key calls `rip_dismiss`. Only the test calls it (RING:403). A search of F/modules/ring_glue, F/app, ring_core, ring_devices and ring_control finds only `rip_init` (F/modules/ring_glue/src/rglue.c:66).

**d. After a dropped link and a reconnect the inbox is first empty, then holds what the stand-in sends again: met.**
- Test: RING:514-527. While the link was down the stand-in removed 202, edited 201 and added 203 (PHONE:1142-1154), so old data on the ring cannot pass the check.
- Code: RIP:729-753, then RIP:785 on the new session.
- Log: LOG:4129-4136.

**e. Service Changed: the ring stops, subscribes again and receives a new notification: met.**
- Test: RING:530-544. The stand-in removes and re-adds the service (PHONE:1159-1165) and counts three Notification Source subscriptions (PHONE:1232-1233).
- Code: RIP:401-412, RIP:711-721, RIP:605-646.
- Log: LOG:4137-4144 and LOG:4187.

**f. Track, artist and state follow the reports; the six commands arrive; the state does not change on a command alone: met.**
- Test: RING:420-430. The stand-in checks the IDs 0,1,3,4,5,6 in order (PHONE:1217-1219), and its rc_write changes no state (PHONE:515-530).
- Code: RIP:304-323 (stored only from the report), RIP:1008-1040 (stores nothing).
- Log: LOG:3987, LOG:4013, LOG:4020, LOG:4022, LOG:4109.

**g. The ring's clock equals the stand-in's time within 1 s after the link is ready, and follows a time change: met, with a deviation from the specification (part 5).**
- Test: RING:263-272, :363, :433. Both sides use the same base time literal (RING:264, PHONE:980), and the stand-in computes the civil date itself (PHONE:611-644).
- Log: LOG:3988, LOG:4023.
- The check runs about 4.6 s after the subscription (LOG:3988 t=11868 against the ANCS subscription at t=7294 in the stand-in log of LOG). It shows the clock is accurate to within 1 s. It does not show how quickly the time is taken after the link is ready.

**h. With a step 2 stand-in host (no Apple services) as the active device: no error, keys still work, the inbox stays empty: partly met.**
- The host used is the step 3 stand-in with the Apple services left out (PHONE:1252, :1278-1282), not the step 2 host program. The builder states this as deviation 3 (F/docs/iphone-notes.md:78).
- The check named "all three services and Service Changed were looked for and not found (not an error)" does not test Service Changed. Its condition is `ancs_missing == 1 && ams_missing == 1 && cts_missing == 1 && dm_errors == 0` (RING:563-564), with no `gattp_*` term. The stand-in has the GATT service with Service Changed on (F/tests/bsim/iphone/host_app/prj.conf, `CONFIG_BT_GATT_SERVICE_CHANGED=y`).
- "No error" is shown only by the ring's own counters.
- Log: LOG:4203, LOG:4205, LOG:4209, LOG:4225.

**i. Notifications, media and time during RECORDING and STANDBY change no core state and start or stop no recording: met.**
- Test: RING:436-468. The stand-in sends the events (PHONE:1099-1122). The stand-in's own check that exactly one key arrived during the whole run (PHONE:1225-1227) also covers "no key sent".
- Code: RIP includes no core or glue header (RIP:36-40).
- Log: LOG:4026-4036, LOG:4225 for P, and the N stand-in key check in LOG ("the ring's key arrived once (media centre: usage 0x00CD, then release) PASS (t=87294)").

**j. Logic tests of the inbox and clock on native_sim and on nrf54lm20bsim/nrf54lm20a/cpuapp; each Bluetooth test has a broken copy that fails on its own named check, counted only when the run ended normally: met.**
- Logic runs: LOG:1323, :1325, :1328 (native_sim) and LOG:1354, :1356, :1357 (bsim board).
- Counting rule: RUN:164-171. A run counts only with phy, ring and stand-in exit 0, both RESULT lines present, and the ring finished before the stand-in evaluated (RUN:94-116).
- Broken copies: N has 10, R has 2, P has 1 (EDIT:19-91). Each was caught on its named line (LOG:4393 to LOG:6073). Logic copies: LOG:6255, :6287, :6336, :6368, :6403, :6424.
- One citation error: the notes call LOG:4390 "The stage's own result" (F/docs/iphone-notes.md:28). LOG:4390 is the stand-in's RESULT line of the inbox_size copy. The stage's result is LOG:6074.

**k. The whole build and test command ends RESULT PASS with every step 1 and 2 stage still passing; the kit build's flash and RAM in the log: met.**
- Fourteen stages, each `exit 0`: LOG:858, :1295, :1303, :1340, :1369, :2244, :3966, :4230, :6075, :6145, :6211, :6289, :6370, :6426. Then "RESULT PASS" at LOG:6428 and "# remote exit code: 0" at LOG:6430.
- FLASH 184932 B and RAM 45196 B: LOG:543-544.
- LEAD (the lead's rerun on the files on disk; its line 6 says the source was copied from F/) ended while I worked: the same 14 stages, each `exit 0` (LEAD:860 to LEAD:6428), then "RESULT PASS" at LEAD:6430 and "# remote exit code: 0" at LEAD:6432. FLASH 184932 B and RAM 45196 B again (LEAD:849-850). I used LOG for the line citations above and checked that LEAD agrees.

**Fixed choices:**
- Inbox of 16, newest first: met (F/modules/ring_inbox/include/ring_inbox/rinbox.h:27, INBOX:114-137).
- Identifier 48, title 48, message 160, cut at a character: met (rinbox.h:28-30, INBOX:27-57; F/modules/ring_iphone/include/ring_iphone/ripl.h:36-38).
- Track title 64, artist 48: met in code (ripl.h:88-89). The product build cannot receive 64 bytes; see part 4, point 1.
- The Media mode keeps its keyboard-style keys: met (LOG:4037, PHONE:1225-1227 usage 0x00CD).
- Player state only from the iPhone's report: met (RIP:304-323). It is also reset to unknown when a session ends (RIP:628), which is the "no state across sessions" rule.

**Apple's rules in DESIGN section 2 (DESIGN:31-33):**
- Service Changed: met (bar e).
- No state across sessions: met (bar d).
- A written command is no proof: met (bar f).

Count: of the 11 bar points a to k, 9 are met (a, b, d, e, f, g, i, j, k), 2 are partly met (c, h) and 0 are not met.

## 2. The two-device scenarios and the broken copies

**Scenario N** (RING:339-479, PHONE:1060-1123, eval PHONE:1183-1228). Where it can pass for the wrong reason:
- c, the flagless action: the ring's own return code only; the stand-in is blind to it (bar c).
- "c: two commands were sent and three were refused", "f: six commands counted" and the two i checks on events arriving read the ring's own counters (RING:414-415, :429, :445-447, :461-463). The facts that matter are also checked by the stand-in (commands, actions, keys) or by stored values (media text, clock), except for the flagless action.
- "23 attribute requests (20 added, 3 modified)" (PHONE:1213) is an exact count that follows this implementation. The builder says so (F/docs/iphone-notes.md:120).
- The a check named "no message is longer than 160 bytes" covers two entries (RING:382-383).
- Timing margin: in the inbox_size copy the ring finished at 86802 ms and the stand-in evaluated at 87294 ms, 492 ms apart (LOG, the "ring script done" line of that copy). A slower fault could make a copy "not count". That fails safe: the stage would fail, not pass.

**Scenario R** (RING:500-547, PHONE:1125-1170, eval :1230-1236).
- "d: the inbox is empty when the link has ended" reads the ring's store 100 ms after its own link-down event (RING:514-516). That is the right place to look.
- "e: the ring stops" reads the ring's own flag (RING:530). The stand-in confirms the resubscriptions (LOG:4187 and the "Entity Update and Current Time four times" PASS in LOG).
- `sc_indications >= 1` is a count that would also hold if the indication did nothing. The effect is checked next to it (`ancs_down == 2`, emptied inbox).

**Scenario P** (RING:551-578, PHONE:1238-1244).
- The h check overclaims Service Changed (bar h).
- "No error" rests on the ring's counters (RING:564).
- The stand-in checks only that no Apple service was used and that the one key arrived.

**The 13 broken copies** (EDIT:19-91; the results come from the bsim-iphone-broken stage of LOG):

| Copy | Edits | Fails on (named) | Also failed | Can it pass for the wrong reason? |
|---|---|---|---|---|
| inbox_size | 1 (rinbox.h 16 to 17) | b: store holds 16 | 10 other ring checks | no |
| utf8_cut | **2** (both branches of the cut, EDIT:29-31) | a: 103 exact | a: 105, a: length | Needs two edits. By reading, the second edit alone (INBOX:52) would already be caught by 103 and 105. The first edit alone (INBOX:38) would not be caught by any Bluetooth check (unreachable, bar a); only the logic test catches it. |
| remove_ignored | 1 | b: removal | 3 others | no |
| modify_ignored | 1 | b: the change arrived | 3 other ring checks, and the phone count of 23 | no |
| action_flag | 1 | c: dismiss of 104 refused | 3 other ring checks (103 refused, the counts, no error) | **Yes.** It is caught only by the ring's return code. The stand-in's "no other" check PASSED in this run. |
| action_id | 1 (swaps both ids) | phone: two actions | ring: 122 not removed | A positive-only id fault is not separately broken (the builder says so, F/docs/iphone-notes.md:123). |
| reset_on_drop | 1 (RIP:124 removed from inbox_empty_locked) | d: empty when ended | e: emptied | The edit also breaks the Service Changed and ANCS-found paths. RIP:785 still clears on reconnect, so only the "first empty" timing check sees it. That is fine. |
| sc_ignored | 1 | e: the ring stops | 7 others | no |
| media_local | 1 (pause sets the state) | f: state unchanged | none | Only pause is modelled. A fault on play is invisible because the state is already playing. |
| time_ignored | 1 | g: follows the change | 5 others | no |
| core_touch | 1 (calls a test hook defined in RING:117-131) | i: still RECORDING | 2 others | It is a synthetic coupling. It shows the check can fail. The real proof is that RIP includes no core header (RIP:36-40). |
| request_len | 1 (160 to 120) | phone: 13 bytes | 3 ring a checks, and phone "each of the 20" | no |
| service_error | 1 (`dm_errors++` added to the not-found path) | h: not found, not an error | none | **Yes, in kind.** The fault exists only in the ring's own counter, and the check reads that counter. A real fault (endless retry, disconnect) would be caught by `ancs_missing == 1` or the key check, by reading. |

## 3. The stand-in iPhone against Apple's documents (F/docs/iphone-notes.md section 3)

I opened each cited line.

| Format | Saved Apple source | Stand-in / ring follow it? | Rests on |
|---|---|---|---|
| ANCS service and characteristic UUIDs | APPLE ancs-spec.txt:99 (all four UUIDs); adg-excerpt-16868-16873.txt (service UUID) | yes: PHONE:146-149; ring via KIT ancs_client.h:26-40 (same values) | Apple |
| Notification Source, 8 bytes | ancs-spec.txt:102 lists EventID, EventFlags, CategoryID, CategoryCount, NotificationUID. The byte sizes and order are in Figure 2-1, which is not in the saved text. | yes: PHONE:231-246 | **field sizes and the u32 little-endian order rest on the kit only** (KIT ancs_client.c) |
| EventID 0/1/2, flag bits 0-4 | ancs-appendix.txt:99 (EventID values and the silent flag), :101-107 (the other flags) | yes: PHONE:261, RIP:145-149 | Apple |
| Get Notification Attributes request | ancs-spec.txt:106 ("16-bit length parameter"), ancs-appendix.txt:116 (IDs; Title, Subtitle and Message take "a 2-bytes max length parameter") | yes: RIPL:10-28, PHONE:352-376 | Apple, except **little-endian u16 and u32: the kit only** |
| Its answer: tuples, no NUL, request order, fragments spliced | ancs-spec.txt:106 ("not NULL-terminated", "always in the same order", "splicing each fragment") | yes: PHONE:361-410, RIPL:82-165 | Apple, except the byte order of the length (the kit) |
| Date `yyyyMMdd'T'HHmmSS` | ancs-appendix.txt:122 | yes (15 characters) | Apple |
| Perform Notification Action, errors 0xA2 and 0xA3 | ancs-spec.txt:112-125 (byte table), :151-152; ancs-appendix.txt:114, :124 | yes: PHONE:413-437. The stand-in's own rule of answering 0xA3 for a missing flag is its choice, and that choice is what blinds the check in bar c. | Apple |
| Sessions | ancs-spec.txt:146 | yes: RIP:729-753 | Apple |
| Service Changed | ancs-spec.txt:99, ams-spec.txt:99 | yes | Apple |
| AMS UUIDs | ams-spec.txt:99, :117-119 | yes: PHONE:150-153 | Apple |
| Remote Command, one byte | ams-spec.txt:126-134 | yes | Apple for the layout; **the ID values rest on the kit only** (KIT ams_client.h:82-98, implicit enum 0..6) |
| Entity Update write and notification layout | ams-spec.txt:147-175 | yes: PHONE:451-477, :532-567 | Apple. **The truncated flag as bit 0 rests on the kit only**; ams-spec.txt:177 says only that a flag can say "truncated". |
| Entity and attribute IDs | none saved | yes | **the kit only** (KIT ams_client.h:100-142) |
| PlaybackInfo `<state>,<rate>,<elapsed>` | none saved | yes: RIPL:193-211 | **the kit's sample README only** (KIT ams_sample_readme_excerpt.txt) |
| 0xA0 Entity Update before subscribing | ams-spec.txt:206 | yes: PHONE:540-543 | Apple |
| CTS Current Time, 10 bytes | none saved (Bluetooth SIG) | yes: PHONE:627-644 | **the kit only** (KIT cts_client.c:19-25) |
| CTS day of week | none | stand-in only | **nothing** (the notes say so) |
| CTS adjust reason | adg-excerpt-16868-16873.txt line 5 says the iPhone's time service gives no Adjust Reason when the current time changes | **the stand-in differs**: it sends reason 1 on a change (PHONE:671). The ring ignores the field (RIP:355-366), so nothing depends on it. | ADG contradicts the stand-in |
| The kit's 32-byte attribute limit | n/a | KIT ancs_client.h:50, ancs_client.c:479 | the kit |

Formats that rest only on the kit or on nothing:
- the byte sizes and little-endian order of the ANCS messages;
- the AMS command IDs;
- the AMS entity and attribute IDs;
- the truncated flag bit;
- PlaybackInfo;
- the CTS layout;
- the CTS day of week (nothing at all).

A shared wrong reading of these would pass on both sides.

## 4. Faults and risks in the code, most serious first

1. **The product build lacks the settings the tests ran with (seen in the files, effect by reading).**
   - F/app/prj.conf has no `CONFIG_BT_L2CAP_TX_MTU`, `CONFIG_BT_BUF_ACL_RX_SIZE` or `CONFIG_BT_BUF_ACL_TX_SIZE`. The test ring sets them to 247/251/251 (F/tests/bsim/iphone/ring_app/prj.conf:37-39). A search of F/app finds none of them.
   - The notes say the opposite: "`app/prj.conf` and the test ring set `CONFIG_BT_L2CAP_TX_MTU=247`" (F/docs/iphone-notes.md:79). That claim is false.
   - FW:716 asks for ATT MTU 247.
   - Effect, by reading: the product keeps Zephyr's default MTU (its value is unverified; no .config is in LOG). The iPhone cuts each Entity Update value to MTU minus 6 bytes (the stand-in does the same at PHONE:460-466). The ring ignores the truncated flag and never reads Entity Attribute (F/docs/iphone-notes.md:94), so the 64-byte track title cannot arrive in the product.
   - The system workqueue, where every iPhone work item runs (RIP:858-861), is 2048 bytes in the product (F/app/prj.conf:7) and 3072 in the test ring (ring_app/prj.conf:44). The product's stack margin is not shown by any run. The product's bsim-run stage only boots (LOG:1296-1303).

2. **A late Data Source fragment desynchronises every later fetch (by reading).**
   - After a 3 s timeout (RIP:287, :290-300) the next request starts and `fetch_busy` is true again. A late fragment of the abandoned answer is then fed into the new request (RIP:199-203). It fails the command or uid check (RIPL:90-107), and the request is abandoned for the next one (RIP:210-213).
   - The answer to that abandoned request then arrives during the following request and fails in the same way. Each answer lands one request late until the queue is empty.
   - There is no retry. Entries keep `text_ready == false` for the rest of the session (RIP:258 skips only removed ids; a failed uid is not queued again).
   - No run reaches this: "(`fetch_timeouts` stays 0 in every run)" (F/docs/iphone-notes.md:114). The logic test of a mismatched stream (F/tests/iphone/src/test_iphone.c:148) covers one stream, not the sequence.

3. **The flagless-action guarantee has no outside witness.** See bar c. Also, by reading: `rip_action` releases the lock before the write (RIP:971-975). An action can therefore be sent after the link ended or the service stopped between the check and the call. The kit's write then fails (-ENOTCONN), which is counted as `action_errors`. That is harmless, but it is not -ENOTCONN from the ring's own check.

4. **A link that ends during discovery (by reading, unverified).**
   - `end_session` clears `dm_busy` (RIP:737), but it cannot release the kit's discovery manager.
   - If that manager is still busy when the next session starts, `bt_gatt_dm_start` fails, and the ring gives up after 5 tries 300 ms apart (RIP:676-690, DM_RETRY_MAX at RIP:44). The service is then skipped for the whole session, counted only as `dm_errors`.
   - Whether the kit's manager frees itself on a disconnect is not in the saved KIT excerpt. No run ends a link during discovery (F/docs/iphone-notes.md:114).

5. **Unlocked shared flags (by reading, low).** `ds_subscribed` is written outside the mutex (RIP:458), and `sconn` is read outside it (RIP:776). The header promises one mutex for the flags (RIP:17-18). Today's callers run in the Bluetooth receive thread and the system workqueue, so a real race needs a preemption at that point.

6. **The queue size has no bound (by reading, low).** `CONFIG_RING_IPHONE_FETCH_QUEUE` is an `int` with no `range` (F/modules/ring_iphone/Kconfig:25-27). The indexes are `uint8_t` (RIP:76). A value above 255 breaks the ring buffer.

7. **Memory (seen in the log).** RAM 45196 B and FLASH 184932 B (LOG:543-544). The inbox is 16 entries of about 283 bytes, and `rip_inbox_get` copies one entry to the caller's stack (RIP:910-923).

Checked and not a fault:
- Buffer bounds of the Data Source reassembly: every byte write is guarded by `kept < cap`, and the buffers are cap+1 (RIPL:141-149, ripl.h:61-64).
- AMS text: cut to the buffer at a character (RIPL:175-185).
- CTS length: checked by the kit (KIT cts_client.c, `current_time_decode`, length must be 10).
- A repeated Added id replaces the entry and moves it to the front (INBOX:119-121). The fetch queue skips duplicates (RIP:96-109).
- Kit subscription state after a drop: `bt_ancs_handles_assign`, `bt_ams_handles_assign` and `bt_cts_handles_assign` reset the kit's state (KIT ancs_client.c:151-160 called at :177, ams_client.c:36-45 called at :63, cts_client.c:32 called at :66), so the resubscription after a reconnect works, as LOG shows (Notification Source "#2").

## 5. Not built against the specification, and what I could not check

Not built, and whether it breaks a bar point:
- **The clock holds the iPhone's local time, labelled UTC** (RIP:361 `rtime_set(ms, 0)`; F/modules/ring_time/include/ring_time/rtime.h:1-3 says UTC). FW:938 defines wall time as uptime plus a UTC offset. The ADG excerpt says the iPhone's time service also has "local time information", which the ring does not read. This does not break g as worded. It does break FW 9.1: recordings would carry local time stamped as UTC.
- **ATT MTU 247 (FW:716) is not set in the product** (part 4, point 1). It breaks no bar point in the tested build. In the product it breaks the fixed choice "track title 64" (by reading).
- No ring control calls `rip_dismiss` or `rip_media_command`, so the bar's dismiss chosen on the ring exists only as an API (bar c).
- DESIGN:44 lists "read and dismissed marks" for the inbox. A read mark exists but nothing sets it. There is no dismissed mark.
- Not built (stated in the notes): Entity Attribute read of truncated values, Remote Command notifications, the FW 7.2 Time characteristic, the FW 9.1 saved time, persistence, the Android relay, Mac notifications, two links at once.

What I could not check:
- The commit id e455a9f. Git is forbidden by the brief.
- Anything that needs a build or a run: the fakes proposed in parts 1 to 4 (send-then-return-ENOTSUP, late fragments, a drop during discovery) were not run, because builds and simulations are forbidden. The product's real MTU (no .config in the log) and the product's workqueue stack use were not checked either.
- A real iPhone (the stand-in shares the builder's reading; part 3).
- The kit's discovery manager behaviour on a disconnect (not in the saved excerpt).
- The source of the CTS day of week and of the AMS appendix values (not saved anywhere).

RESULT: done, of 11 bar points 9 are met (a, b, d, e, f, g, i, j, k), 2 partly met (c: the stand-in cannot see a flagless action, shown by the action_flag run; h: the step 3 stand-in replaces the step 2 host and the check does not test Service Changed) and 0 not met; the main new issues are that the product prj.conf lacks the MTU 247 settings the notes claim and the tests use, and that a late Data Source fragment desynchronises all later fetches.
