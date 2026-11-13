# Step 3 review 2 (second independent review of round 2)

Reviewer: the second independent reviewer. I started at 2026-11-12 07:52:57 and resumed at 08:10 after a dropped connection. Version: the files on disk under F/, which the lead now names commit 1e7ccd8. I ran no git, so I could not confirm that id myself. No file under F/modules, F/app, F/tests or F/tools is newer than the builder's run start (01:41:23). I checked this with a `find -newer` and it listed nothing. Newest: run.sh and host_app main.c at 01:41:04, rip.c at 01:04:17. I ran no build, no simulation and no ssh, and I changed no file of the software. Run-time statements come from the logs below. Anything else is marked "by reading".

Short names:
- F/ = firmware/
- LOG = F/build-logs/step3/20261112-014123-os-iphone-r2.log (the builder's final run, 7302 lines up to RESULT PASS)
- LEAD = F/build-logs/step3/20261112-073536-lead-step3-r2-rerun.log (the lead's rerun, complete, 7305 lines). I used it for point 10. Its line numbers match LOG for every line I compared (544, 545, 4248, 4273, 6934 to 6943).
- RIP = F/modules/ring_iphone/src/rip.c, RIPL = F/modules/ring_iphone/src/ripl.c, RING = F/tests/bsim/iphone/ring_app/src/main.c, PHONE = F/tests/bsim/iphone/host_app/src/main.c, EDIT = F/tests/bsim/iphone/broken_edit.py, RUN = F/tests/bsim/iphone/run.sh, R2 = F/docs/step3-round2.md, NOTES = F/docs/iphone-notes.md, FW = design/firmware.md

## Part 1. The bar, point by point

**1. One shared file for the link settings, and a build that fails when they differ: closed.**
- File: F/modules/ring_iphone/ring_iphone_link.conf:6-11 holds MTU 247, ACL RX/TX 251, workqueue 3072 and DM_MAX_ATTRS 35.
- The product includes it at F/app/CMakeLists.txt:34. The test ring includes it at F/tests/bsim/iphone/ring_app/CMakeLists.txt:16, always from the real module path, even when a broken copy is built.
- A search of both prj.conf files for MTU, ACL and WORKQUEUE finds nothing.
- Only two applications enable CONFIG_RING_IPHONE: app/prj.conf:45 and ring_app/prj.conf:39. Both include the file. The step 2 control ring (tests/bsim/control/ring_app/prj.conf) does not enable it, and RING_GLUE does not select it (modules/ring_glue/Kconfig:1-7).
- Check: tools/check_link_settings.sh:11-19 compares the four values of two built .config files and fails on any difference or on a missing value. build_all.sh:159-186 runs it on the kit and simulated-chip product builds against the iPhone test ring, after a self test with the MTU changed to 23.
- Log: LOG:6933 (DIFFERENT, the self test refused), LOG:6934 to :6942 (every value 247/251/251/3072 on both sides), LOG:6943 (exit 0). LEAD has the same lines at 6933 to 6943.
- Remaining weaknesses (none breaks the bar):
  - (a) CONFIG_BT_GATT_DM_MAX_ATTRS=35 is in the shared file but is not among the compared keys (check_link_settings.sh:11).
  - (b) The check tests equality only. If the shared file were changed to MTU 23, both sides would agree and the check would pass. Nothing pins the value to FW:716.
  - (c) A future application that enables CONFIG_RING_IPHONE without the file is not caught. The rule lives in two CMakeLists, not in the module.

**2. Late answer fragment, retry, two-device test, broken copy: partly closed.**
- Code, by reading: RIPL:90-137 searches the stream byte by byte. A non-matching id or a wrong first attribute is searched again, and the recursion depth is bounded (part 3). RIP:126-138 retries once at the front of the queue. The retry is called from the timeout (RIP:319; R2 cites :318, the line above), the answer error (:233), the write callback (:251) and the write start (:305).
- Logic test: F/tests/iphone/src/test_iphone.c:163-242, every fragment size, the "05 00 00" false header, the middle of a stale answer, another command id. The two "05 00 00" blocks (:192-202 and :205-215) feed the same bytes; only their assertions differ.
- Two-device scenario L: passes, with a retry proven at the stand-in (LOG:4248-4252, LOG:4277-4278, "6 requests, 2 for 401" at LOG:4276).
- What is open: **the late answer never reaches the parser over Bluetooth**.
  - The ring has all four texts at t=12775 (LOG:4248). The held answer is sent at t=12845 (LOG:4273). Notification 405 only comes at t=21294 (LOG:4274).
  - So when the late bytes arrive, no request is in flight. By reading they are dropped by `if (!fetch_busy)` at RIP:220-222, before ripl_ds_feed.
  - Why: the retry for 401 is answered at once (PHONE:481-490 holds only the first answer), so 402 to 404 finish within the 500 ms gap.
  - The round 1 fault (a late answer landing inside a later request and shifting it) is therefore not exercised in any two-device run. LEAD shows the same times (LEAD:4248, :4273).
- The broken copy `late_fragment` (EDIT:92-100) restores both halves together. It fails on 401 never being asked again: "5 requests, 1 for 401" (LOG:6331, PHONE CHECK "asked for 401 twice" FAIL), and its named check fails at LOG:6302.
  - By reading, a copy that keeps the retry but restores the round 1 parser would pass L, because the late bytes are dropped before the parser.
  - No logic broken copy targets the parser rule either. The broken-iphone stage breaks test_media_playback_state (LEAD, broken-iphone stage).
- So "a broken copy fails on that check" holds only for the retry half.

**3. A witness outside the ring for "an action without its flag sends nothing": closed.**
- PHONE:499-509 records every Perform Notification Action write before any refusal, and counts `flagless_cmds` with no cap (`ncmds` is capped at 16).
- Check: PHONE:1329 `ncmds == 2 && flagless_cmds == 0`, LOG:4117 PASS. The ring's no-error check now includes `action_failed` (RING:534-536, LOG:4044).
- Broken copy `action_sent` (EDIT:101-107) sends and still returns -ENOTSUP:
  - the ring's refusal checks pass (LOG:6389, :6390);
  - the stand-in check fails (LOG:6505);
  - the ring's no-error check fails too (LOG:6422).
- Gap, by reading: a write to the control point that is not 6 bytes with command 2 is not recorded (PHONE:493). The kit's encoder makes that unlikely.

**4. The plain-host check tests what its name says: closed.** RING:697-700 now requires `gattp_found == 1 && gattp_missing == 0` with the three missing services and `dm_errors == 0`, and its name says Service Changed was looked for and found. LOG:4213 PASS. Broken copy `service_error` is caught on it (LOG:6246). Still true from review 1: "no error" rests on the ring's own counters, and the stand-in's key check (LOG:4122 for N; LOG:4235 for P) is the outside witness.

**5. The clock holds UTC plus the zone offset, or the local time with "zone not known": closed, with untested paths.**
- Code: RIP:391-417 sets `rtime_set(ms - zm*60000, zm, true)` with a zone and `rtime_set(ms, 0, false)` without one. RIPL:257-282 gives tz x 15 + daylight (0/30/60/120); -128, 255, out of range and undefined codes mean unknown. The clock keeps the flag (F/modules/ring_time/src/rtime_logic.c:16-23, rtime.h:18-22).
- The signs are right: local = UTC + zone + daylight (ripl.h:117-123).
- Logic tests: test_iphone.c:346-367 and test_time.c:47-66.
- With a zone (N: tz 4, daylight 4, PHONE:1441-1442): LOG:3990, :3991, :4028, :4030, :4118. RING:270 subtracts 2 h.
- Without a zone (R: the stand-in defaults tz -128 and daylight 255, PHONE:749-750): LOG:4136.
- Broken copies:
  - `zone_ignored` fails at LOG:6670.
  - `zone_assumed` fails at LOG:6763. It is caught by the flag only, because ripl_cts_zone leaves m at 0 for unknown values.
- Not tested over Bluetooth: a CTS service without the Local Time Information characteristic (RIP:636 and :652; no scenario lacks it, since PHONE:204 always serves it), a failed read of it (RIP:430 and :436), and a zone change while linked.

**6. A link that ends during discovery, tested over Bluetooth, with the three services found next session: closed.**
- The stand-in ends the link 60 ms after the Data Source subscription (PHONE:321-326). The stand-in confirms no Entity Update or Current Time subscription happened before the drop (LOG:4311, :4321).
- In the next session (LOG:4294, :4295, :4322) the INFO line says missing 0/0/0, dm_stale 1 (LOG:4297), and the checks pass at LOG:4298-4299.
- The before state is the builder's `console-r2-third.txt` (missing 0/1/0). I did not open it; R2:47 describes it.
- Limit (R2:48): only a drop during the Media discovery is tried. There is no broken copy for D.

**7. The small points: closed (6 of 6).**
- (a) Flags under the lock: `ds_subscribed` is written under the lock at RIP:564-566, and `sconn` is read under it at RIP:939-946. By reading only.
- (b) The queue range: F/modules/ring_iphone/Kconfig:28 `range 1 255` fits the `uint8_t` indexes (RIP:77-78).
- (c) The 160-byte check covers every entry: RING:314-328 (with its own UTF-8 checker at :293-311, and false on an empty inbox), LOG:4000.
- (d) No adjust reason: PHONE:741 and :777 send reason 0.
- (e) The play case: RING:484-488, LOG:4116; broken copy `media_local_play` fails at LOG:6929, and `media_local` still fails at LOG:5692.
- (f) The citation: NOTES:28 now names LOG:6930 (RESULT PASS of bsim-iphone-broken, stage end at :6931).

**8. The notes name every data format that rests only on the kit or on nothing: closed.** The NOTES:76-91 table (copied at R2:63-74) covers what review 1 listed and adds Local Time Information. I found no other format that rests only on the kit or on nothing. Local Time Information's UUID 0x2A0F comes from a Zephyr header (NOTES:72), and that is named.

**9. Claims of R2 checked by opening the cited line: 105 of 107 citations hold. Separately, 3 false claims in NOTES.**
- I opened every `path:line` citation in R2 with a script and read each line against its claim: 107 citations, 105 hold.
- The two that do not hold exactly:
  - R2:21 "Called from the timeout (rip.c:318)": :318 is the counter, and the call is at :319 (off by one).
  - R2:57 "LOG:4390": by R2's own definition of LOG (R2:5) it opens an unrelated line, "RING CHECK f: media command 1 is sent PASS". The text means the round 1 log.
- Other claims of R2 that I checked and that hold:
  - the 15 stage ends, all exit 0 (LOG);
  - the counts N 79, R 33, P 19, L 16, D 19 (LOG:4125, :4202, :4238, :4281, :4326);
  - round 1's FLASH 184932 and RAM 45196 (lines 543-544 of the old log);
  - the two files in files-changed-after-r2-start.txt with mtime 01:41:04, before the start at 01:41:23 (LOG head).
- R2:12 says the search "finds nothing but a comment". It finds nothing at all, which is harmless.
- False claims in the other notes file, NOTES:
  - NOTES:133 still says "the fetch timeout (`fetch_timeouts` stays 0 in every run)" and "a link that ends during discovery" are reached by no run. L (RING:642-643) and D now reach both.
  - NOTES:28 says "every Bluetooth test has a broken copy" and "N, R, P, L and D have 18 broken copies". D has none (R2:48; EDIT has no SCEN "D").
  - NOTES:14 (bar c) still rests on `nactions == 2`, which review 1 showed is no evidence, and does not cite the new check at LOG:4117.
- Stale code comments contradict round 2:
  - F/modules/ring_iphone/include/ring_iphone/ripl.h:129-131: "the ring does not read the zone ... holds the iPhone's local time".
  - PHONE:42: "Not served: Local Time Information (the ring does not read it)".

**10. The whole build and test command ends RESULT PASS in the lead's own run: closed.** LEAD: 15 stages, each `exit 0` (LEAD:859, 1297, 1305, 1342, 1371, 2246, 3968, 4328, 6931, 6943, 7013, 7079, 7157, 7238, 7300). Then "RESULT PASS" at LEAD:7302 and "# remote exit code: 0" at LEAD:7304. FLASH 186072 B and RAM 51240 B at LEAD:544-545. LEAD:6 says the source was copied from F/.

Count: of 10 bar points, 9 are closed (1, 3, 4, 5, 6, 7, 8, 9, 10), 1 is partly closed (2) and 0 are open. Point 9 is closed for R2 (105 of 107 citations exact, the 2 misses minor); the 3 false NOTES claims are listed above.

## Part 2. The new and changed two-device scenarios and broken copies

| Scenario / copy | Fails on | Can it pass for the wrong reason? |
|---|---|---|
| L (RING:627-648, PHONE:1341-1356) | four texts in place; 1 timeout, 1 retry, 0 failed; 405 gets its text; no wrong answer; the stand-in sees 2 requests for 401 | **Yes.** The held answer arrives when no request is in flight (Part 1, point 2), so the byte search and the "no shift" property are not exercised. The pass rests on the retry alone. `ds.skipped` is never reported, so no check shows that bytes were skipped. |
| D (RING:657-681, PHONE:1357-) | ended_in_discovery, three services next session, 301's text, ams_up == 1 and cts_up == 1, dm_stale >= 1, nothing missing | Mostly no: the stand-in confirms the timing (LOG:4311, :4321). Only a Media-phase drop is tried, and there is no broken copy, so the `gone` test at RIP:684 is protected only by the "missing 0/0/0" check. By reading, that check would catch its removal, as in the before run. |
| N changes | action record (LOG:4117), zone checks (LOG:3990-3991, :4030), play while paused (RING:484-488), every-entry limits (LOG:4000) | The zone check uses the same constant on both sides (RING:265 and PHONE:1441-1442). A shared wrong reading of the Local Time Information layout would pass (named in NOTES:90). |
| R changes | the zone-unknown check (LOG:4136) | It covers only the "unknown values" path. A missing characteristic and a failed read are never served. |
| P changes | the Service Changed terms (LOG:4213) | `service_error` is still a counter-only fault (review 1). |
| late_fragment (EDIT:92-100) | LOG:6302 named, LOG:6337 counted | **Yes, partly:** it fails because the retry was removed. The parser half is not shown to be caught (Part 1, point 2). |
| action_sent (EDIT:101-107) | the stand-in check (LOG:6505) | no |
| zone_ignored (EDIT:108-112) | N clock as UTC (LOG:6670) | no |
| zone_assumed (EDIT:113-117) | R zone-unknown (LOG:6763) | It is caught by the flag only; the clock value is unchanged in this copy. That is fine, since the flag is the point. |
| media_local_play (EDIT:118-123) | N play (LOG:6929) | no |
| time_ignored, changed (EDIT:70-74) | N g (LOG:5858) | It now also drops the Local Time Information refresh. Still caught on its named check. |

Counting rule: RUN:169-177 counts a copy only without INFRA and with the exact named line FAIL. All 18 copies were caught (LOG:6930 RESULT PASS; LEAD the same stage, exit 0 at :6931).

## Part 3. New faults and risks that round 2 added, most serious first

1. **The clock is set back after every Current Time notification (by reading, medium).** cts_notify_cb applies the time and then calls lti_refresh (RIP:481-486). When the zone read returns, lti_read_cb re-applies the *stored* last_ct (RIP:438-442). cts_apply turns that old civil time into ms and rtime_set pairs it with the uptime *now* (rtime.c:13). So the clock ends up behind by the read's round-trip on every notification. The size is about one or two connection intervals: tens of ms at the FW 7.3 interval of 30-50 ms with latency 4, more with latency. It is within the tests' 1 s tolerance (RING:274), so no run can show it.
2. **A failed Local Time Information read turns a UTC clock into local time (by reading, medium-low).** On a read error or a wrong length, `known = false` (RIP:430-437) and the stored time is re-applied as local with the flag off. The clock jumps by the zone offset (for example 2 h) until the next good read. FW:802 counts "an unreadable value" as "no zone", so this follows the rule, but one transient error is enough. Untested.
3. **The late-answer fix is not exercised over Bluetooth** (Part 1, point 2; seen in the log, LOG:4248 against :4273).
4. **The byte search can accept a false header in rare streams (by reading, low).** A false header must read `00 <our uid LE> 00`. Text holds no 0x00, so the zeros must come from command, attribute-id and length bytes. Example: our uid is 0 and a stale answer ends in an empty date (`05 00 00`). The stream `05 00 00 | 00 00 00 00 00 00 L0 L1` is matched from the stale length bytes. The parser then reads our attribute id 00 as len_lo and L0 as len_hi, which makes a length of L0x256 that swallows the answer. The result is a timeout, then a retry, so it recovers unless the retry collides too.
   - Checked and not a fault: the recursion depth is at most 2 (a 4-byte refeed cannot complete a new header; a 5-byte refeed can recurse once more into 4 bytes). `hdr[4]` is written only at indexes 0-3, because hdr_n is reset at each command byte. Every loop pass advances `i`, so there is no endless loop. DS_DATA writes are bounded by `kept < cap` (RIPL:170).
5. **The retry is bounded and in order (by reading, no fault found).** `cur_try` 0 to 1, then fetch_failed (RIP:129-137). The retry goes to the head only when the queue has room and the id is still held and not queued. A uid that is Modified while in flight and is already re-queued counts as `fetch_failed` while still queued. That is a misleading counter, not a lost fetch.
6. **The stale discovery drop (by reading, low).** A real "not found" is dropped only when the link is not connected, `sconn` is NULL or the session number differs (RIP:684-687). On a live link of the current session it is never dropped. A stale answer clears `dm_busy` (RIP:690) even if a newer session's discovery were running. The kit's discovery manager runs one discovery at a time, so by reading this cannot overlap. The generation is shifted into the upper 24 bits of a pointer-sized context (RIP:675). The comparison `(ctx >> 8) != session_gen` would break after 2^24 sessions on a 32-bit target, which is harmless.
7. **The shared settings file (seen in the files and the log):** see Part 1, point 1 (a) to (c). The RAM cost is now 51240 B against 45196 B (LOG:545 against the old log line 544). The stack margin of the 3072-byte workqueue on the chip is still unmeasured (R2:16).
8. **Stale comments and notes:** ripl.h:129-131, PHONE:42, NOTES:28, NOTES:133 (Part 1, point 9).

## Part 4. Still not built against FW 7.6 and 9.1, and what I could not check

Not built:
- FW 7.6, "Where it shows": no screen and no control calls rip_dismiss, rip_action or rip_media_command. FW:804 defers this to step 4. NOTES:124 says the read mark is set by nothing.
- FW 7.6 Media: no Entity Attribute read for truncated values (NOTES:123). This is now less important, because the product has MTU 247 (LOG:6935).
- FW 9.1: no Bluetooth Time characteristic, no USB SET_TIME source in this step, no time saved in RRAM, and no "time not set" after a boot. The clock is RAM only (NOTES:102, :125). "A recording started then carries the flag" is not wired: nothing in ring_core reads rtime_zone_known (by reading of the RIP includes only; I did not search ring_core).
- FW 7.6 Time: the "no such characteristic" and "unreadable value" paths exist in code (RIP:636, :652, :430) but no test reaches them.
- FW 7.6 "Not proven": nothing ran against a real iPhone. The Local Time Information layout rests on no saved document (NOTES:90).

What I could not check:
- The commit id 1e7ccd8. The brief forbids git.
- Any run of the fakes I propose (a retry-kept, parser-restored copy for L; a late answer that lands inside a request; a missing Local Time Information characteristic; a failed zone read; the clock lag), because builds and simulations are forbidden.
- The builder's console-r2-third.txt "before" run for D. I relied on R2:47 for its content.
- The kit's discovery-manager internals (not saved), and whether a real iPhone sends Local Time Information at all.

RESULT: done, 9 of 10 bar points closed, 1 partly closed (2: the late answer is sent after the ring had all four texts, so the byte search and "no shift" are never exercised over Bluetooth, and the broken copy fails only because of the retry), 0 open; main new issues: the clock is set back by the zone read's round-trip after every Current Time notification, a failed zone read flips a UTC clock to local time, and NOTES:28 and :133 hold false claims (D has no broken copy; the timeout and the drop during discovery are now reached).
