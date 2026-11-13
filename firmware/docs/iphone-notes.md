# Step 3: the iPhone part and the inbox

Version: round 1 on firmware/ at commit 221746b and design/ at commit 9818c7e; round 2 on the files of commit e455a9f; round 3 on commit 1e7ccd8; plus the step 3 files listed in section 2. I ran no git. Written 2026-11-11 and 2026-11-12. Paths are under `firmware/` unless they start with `design/`.

Bar command, round 3 (my own run, on my own server copy `RING_REMOTE_SRC=/root/ring-os/src-step3r3f`): `sh firmware/tools/remote.sh os-iphone-r3 "tools/build_all.sh"`. The answers below are from that run. Round 1 and round 2 runs are described in section 7; changes and answers to the reviews are in `docs/step3-round2.md` and `docs/step3-round3.md`.
Log ("the log" below): `build-logs/step3/20261112-090932-os-iphone-r3.log`. The last line build_all printed is `RESULT PASS`; remote.sh then wrote `# remote exit code: 0`. A citation `LOG:n` is line n of that file; `file:n` is a line of a source file as delivered.

## 1. Answers to the bar, a to k

**a. Three or more notifications, exact text and flags, the 200-byte message cut on a character: yes.** The stand-in sends five (`script_n`, `tests/bsim/iphone/host_app/src/main.c:1221` to `tests/bsim/iphone/host_app/src/main.c:1231`). The ring's checks hold literals for app identifier, title, message, date, category and flags (`tests/bsim/iphone/ring_app/src/main.c:443` to `tests/bsim/iphone/ring_app/src/main.c:453`). Log: `LOG:3997`, `LOG:3998`, `LOG:3999`, `LOG:4000`, `LOG:4001`, `LOG:4002`. 103 is the case where the iPhone cuts at the 160 bytes the ring asked for, inside a character (so the ring drops the half character); 105 is the case where the iPhone ignores the maximum length and sends 200 bytes. The cut is `modules/ring_inbox/src/rinbox.c:27`; its logic test `test_utf8_cut_property` (`tests/inbox/src/test_inbox.c`) tries every length and limit of a mixed string. Broken copies that must fail here: `utf8_cut` -> `LOG:4764`; `request_len` -> `LOG:6287`.

**b. A change replaces the text, a removal deletes the entry, the 17th drops the oldest: yes.** `LOG:4003`, `LOG:4004`, `LOG:4005`, `LOG:4007`, `LOG:4008` (it also checks that `inbox_dropped` is exactly 1). Code: `modules/ring_iphone/src/rip.c:154`, `modules/ring_inbox/src/rinbox.c:114`. Broken copies: `inbox_size` -> `LOG:4573`, `remove_ignored` -> `LOG:4931`, `modify_ignored` -> `LOG:5098`.

**c. A dismiss chosen on the ring arrives as the negative action, a positive action likewise, an action without its flag sends nothing: yes.** `LOG:4010`, `LOG:4012`; the stand-in's own record: `LOG:4119` (its log line for the command: `LOG:4083`). Refusals: `LOG:4013`, `LOG:4014`, `LOG:4016` and the stand-in's own witness: it records every action command before it can refuse one, and `LOG:4121` (`ncmds == 2 && flagless_cmds == 0`). The inbox does not change on the ring's own command: `LOG:4011`; it changes when the iPhone reports the removal: `LOG:4017`. Code: `modules/ring_iphone/src/rip.c:1121`. Broken copies: `action_flag` -> `LOG:5267`, `action_id` -> `LOG:5436`.

**d. After a dropped link and a reconnect the inbox is first empty, then holds what the stand-in sends again: yes.** Scenario R. `LOG:4143`, `LOG:4144`, `LOG:4149`, `LOG:4150`. The stand-in removed 202, edited 201 and added 203 while the link was down, so the new content cannot be old data kept by the ring; the stand-in's replay carries the pre-existing flag, which the ring's stored flags show (0x1C and 0x04). Code: `modules/ring_iphone/src/rip.c:896`. Broken copy `reset_on_drop` -> `LOG:5528`.

**e. The service removed and added again while linked (Service Changed): the ring stops, then subscribes again and receives a new notification: yes.** Scenario R. `LOG:4151`, `LOG:4152`, `LOG:4153`, `LOG:4155`, `LOG:4156`, `LOG:4158`. The stand-in's side: `LOG:4188`, `LOG:4192`, `LOG:4201`. Code: `modules/ring_iphone/src/rip.c:512`, `modules/ring_iphone/src/rip.c:768`. Broken copy `sc_ignored` -> `LOG:5611`.

**f. Track title, artist and player state follow the stand-in's reports; the six media commands arrive; the stored state does not change on a command alone: yes.** `LOG:3991`, `LOG:4018`, `LOG:4025`, `LOG:4027`. The commands at the stand-in: `LOG:4120` (its log lines `LOG:4089` to `LOG:4094`). The stand-in never changes its player state because of a command (`rc_write`, `tests/bsim/iphone/host_app/src/main.c:167`). Code: `modules/ring_iphone/src/rip.c:333`, `modules/ring_iphone/src/ripl.c:215`. Broken copy `media_local` -> `LOG:5779`.

**g. The ring's clock equals the stand-in's time within 1 s after the link is ready, and follows a time change: yes; since round 2 the clock holds UTC (the iPhone's zone is read and taken off), or the local time with "zone not known" when the iPhone gives no zone (section 4, point 2).** `LOG:3992`, `LOG:4030`. The ring's check compares `rtime_utc_ms()` with a literal base (2026-11-11T22:05:46 local, 1794434746000 ms) minus the stand-in's +2 h zone plus the simulated uptime (`tests/bsim/iphone/ring_app/src/main.c:268`); the stand-in serves that time as Current Time with its own civil-date code (`tests/bsim/iphone/host_app/src/main.c:741`). Logic tests of the clock and of the date conversion: `tests/time/src/test_time.c`. Code: `modules/ring_iphone/src/rip.c:411`. Broken copy `time_ignored` -> `LOG:5946`.

**h. With a host that serves no Apple service as the active device: no error, keys still work, the inbox stays empty: yes (stand-in in plain mode, section 4, point 3).** Scenario P. `LOG:4217`, `LOG:4219`, `LOG:4223`, `LOG:4239`. Also in scenario N, with the iPhone as the active device: `LOG:4046`. Broken copy `service_error` -> `LOG:6338`.

**i. A notification, a media report and a time change during RECORDING and during STANDBY change no core state and start or stop no recording: yes.** Scenario N. `LOG:4035`, `LOG:4036`, `LOG:4039`, `LOG:4041`, `LOG:4042`, `LOG:4045`. By construction too: `modules/ring_iphone` includes no header of the core or the glue (`rip.c` includes: `modules/ring_iphone/src/rip.c:36` to `modules/ring_iphone/src/rip.c:40`). Broken copy `core_touch` (a time change presses the centre while a recording runs) -> `LOG:6118`.

**j. Logic tests of the inbox and the clock on native_sim and on the ring chip board; every Bluetooth test has a broken copy that fails on its own named check: yes.** Logic suites on native_sim: `LOG:1328`, `LOG:1329`, `LOG:1330`; on `nrf54lm20bsim/nrf54lm20a/cpuapp`: `LOG:1360`, `LOG:1358`, `LOG:1359`. Broken copies of the logic suites (the named case must fail on each board; stages `broken-inbox`, `broken-time`, `broken-iphone`): `LOG:7645` and `LOG:7677` (inbox); `LOG:7922` and `LOG:7946` (time); `LOG:7716` and `LOG:7748` (iPhone logic). Bluetooth: scenarios N, R, P, L, D, Z and W have 23 broken copies in stage `bsim-iphone-broken` (listed in section 1, a to i; the run counts one only when both devices ran to their RESULT line, the ring finished before the stand-in evaluated, and the exact named check line says FAIL: `tests/bsim/iphone/run.sh`, `tests/bsim/iphone/run.sh:177`); each one's diff is in `tests/bsim/iphone/broken_edit.py` and in the log. The stage's own result: `LOG:7444`.

**k. `sh firmware/tools/remote.sh os-iphone "tools/build_all.sh"` ends with the last line RESULT PASS, every step 1 and step 2 stage still passing, flash and RAM use in the log: yes.** The last build_all line is `LOG:7950`; 15 stages ended, 0 with a non-zero exit. The step 1 and step 2 stages are `dk`, `bsim-build`, `bsim-run`, `tests-native_sim`, `tests-nrf54lm20bsim_nrf54lm20a_cpuapp`, `bsim-control`, `bsim-control-broken`, `broken-control`, `broken-devices`; their end lines: dk `LOG:861`, bsim-build `LOG:1299`, bsim-run `LOG:1307`, tests-native_sim `LOG:1344`, tests-nrf54lm20bsim_nrf54lm20a_cpuapp `LOG:1373`, bsim-control `LOG:2248`, bsim-control-broken `LOG:3970`, broken-control `LOG:7535`, broken-devices `LOG:7601`. Kit build for `nrf54lm20dk/nrf54lm20a/cpuapp` (the application with MCUboot, sysbuild): FLASH 186,232 B of 974,704 B (19.11%), `LOG:850`; RAM 51,264 B of 511 KB (9.80%), `LOG:851` (application image); step 2's figure was FLASH 168,592 B (`docs/step2-round3.md`).

Scenario results (both devices' checks counted): N 80 checks passed `LOG:4129`, R 33 `LOG:4206`, P 19 `LOG:4242`, L 17 `LOG:4290`, D 19 `LOG:4335`.

## 2. What was built (files)

| Part | Files | What |
|---|---|---|
| Inbox (pure) | `modules/ring_inbox/include/ring_inbox/rinbox.h`, `src/rinbox.c`, `Kconfig`, `CMakeLists.txt`, `zephyr/module.yml` | 16 entries, newest first, oldest dropped when full; text cut on a UTF-8 character boundary (`rinbox_utf8_cut`) |
| Clock (pure + kernel wrapper) | `modules/ring_time/include/ring_time/rtime_logic.h`, `rtime.h`, `src/rtime_logic.c`, `src/rtime.c`, `Kconfig`, `CMakeLists.txt`, `zephyr/module.yml` | UTC ms and a "time is set" flag; civil date to ms |
| iPhone part, pure | `modules/ring_iphone/include/ring_iphone/ripl.h`, `src/ripl.c` | request builder, reassembly of the notification attribute answer, media decoder |
| iPhone part, Bluetooth | `modules/ring_iphone/include/ring_iphone/rip.h`, `src/rip.c`, `Kconfig`, `CMakeLists.txt`, `zephyr/module.yml` | discovery, subscriptions, Service Changed, actions, media commands, time |
| Join | `modules/ring_glue/src/rglue.c` (calls `rip_init()` when `CONFIG_RING_IPHONE`), `app/CMakeLists.txt`, `app/prj.conf`, `app/src/main.c` (comment only), `tools/build_all.sh` (comments only), `README.md` | the product application and the glue start the iPhone part |
| Logic tests | `tests/inbox`, `tests/time`, `tests/iphone` (each with `testcase.yaml`, `CMakeLists.txt`, `prj.conf`, `src/`, `broken_run.sh`) | native_sim and `nrf54lm20bsim/nrf54lm20a/cpuapp` |
| Bluetooth tests | `tests/bsim/iphone/run.sh`, `tests/bsim/iphone/broken_edit.py`, `host_app/` (the stand-in iPhone), `ring_app/`, `common/hosttools.h` | scenarios N, R, P, L, D, Z, W and 24 broken copies |
| Join, round 2 | `modules/ring_iphone/ring_iphone_link.conf`, `tools/check_link_settings.sh`, stage `link-settings` in `tools/build_all.sh` | link and stack settings in one file; check of the built product |
| Notes | `docs/iphone-notes.md` (this file), `docs/step3-round2.md`, `build-logs/step3/` | |

I changed nothing in `modules/ring_core`, `ring_devices`, `ring_control` or their tests, nothing in `docs/step2-*.md`, `docs/devices-control-notes.md` or `docs/PRD.md`, and nothing outside `firmware/`. `ring_devices` needed no change: the iPhone part learns "the link is ready" from `rdev_active_conn()` (`modules/ring_devices/include/ring_devices/rdev.h`) after its own security callback, see section 5, point 1.

## 3. Where every data format comes from

The stand-in iPhone (`tests/bsim/iphone/host_app/src/main.c`) writes its UUIDs and layouts from the documents, not from the kit headers the ring uses (header comment of that file, lines 1-46). The saved copies are in `build-logs/step3/apple/` (Apple pages, text from the 2026-11-11 research) and `build-logs/step3/kit/` (nRF Connect SDK v3.4.2 files, copied from the server's workspace).

| Format | Source |
|---|---|
| ANCS service and characteristic UUIDs | `apple/ancs-spec.txt:99`; ADG `apple/adg-excerpt-16868-16873.txt` (adg.txt:16872); kit `kit/ancs_client.h:26-40` |
| Notification Source message, 8 bytes: EventID, EventFlags, CategoryID, CategoryCount, NotificationUID u32 LE | `apple/ancs-spec.txt:102` (the field list; the figure is not in the text); kit `kit/ancs_client.c:26-35,60-110` |
| EventID 0 added, 1 modified, 2 removed; flag bits silent 0, important 1, pre-existing 2, positive 3, negative 4 | `apple/ancs-appendix.txt:99-107`; kit `kit/ancs_client.h:68-87,130-138` |
| Get Notification Attributes request: CommandID 0, uid u32 LE, attribute ids, Title/Subtitle/Message followed by u16 LE maximum length | `apple/ancs-spec.txt:106`; `apple/ancs-appendix.txt:116`; kit encoder `kit/ancs_client.c:409-453` |
| Its answer: CommandID 0, uid, tuples id, u16 LE length, data (no NUL), in the order of the request, in fragments | `apple/ancs-spec.txt:106` |
| Date string `yyyyMMdd'T'HHmmSS` | `apple/ancs-appendix.txt:122` |
| Perform Notification Action: CommandID 2, uid u32 LE, ActionID (positive 0, negative 1); errors 0xA2 invalid parameter, 0xA3 action failed | `apple/ancs-spec.txt:112-125,151-152`; `apple/ancs-appendix.txt:114,124`; kit `kit/ancs_client.c:344-355` |
| A session ends when the client unsubscribes or the link ends; the client must drop what it stored | `apple/ancs-spec.txt:146` |
| Service Changed: look for the service again | `apple/ancs-spec.txt:99`; `apple/ams-spec.txt:99` |
| AMS UUIDs | `apple/ams-spec.txt:99,117-119`; kit `kit/ams_client.h:26-47` |
| AMS Remote Command: one byte; play 0, pause 1, next 3, previous 4, volume up 5, volume down 6 | `apple/ams-spec.txt:126-134`; kit `kit/ams_client.h:82-98` (the Apple appendix page is not saved) |
| AMS Entity Update write: EntityID, AttributeIDs; notification: EntityID, AttributeID, flags, value; flag bit 0 truncated | `apple/ams-spec.txt:147-175`; kit `kit/ams_client.h:49-59`, `kit/ams_client.c:197-239` |
| AMS entity ids player 0, queue 1, track 2; player attribute PlaybackInfo 1; track artist 0, album 1, title 2, duration 3 | kit `kit/ams_client.h:100-142` |
| PlaybackInfo value `<state>,<rate>,<elapsed>`; `1,1.0,0.014` playing, `0,0.0,0.000` paused | the kit's AMS sample README (samples/bluetooth/peripheral_ams_client/README.rst on the server, lines 150-225 and 370-415), saved as `kit/ams_sample_readme_excerpt.txt` |
| Entity Update written before subscribing: error 0xA0 | `apple/ams-spec.txt:206` |
| CTS Current Time value, 10 bytes: year u16 LE, month, day, hours, minutes, seconds, day of week, fractions256, adjust reason | kit `kit/cts_client.c:19-25,103-135` |
| Local Time Information: 2 bytes, zone int8 (15-minute units east of UTC, -128 unknown), daylight offset uint8 (0, 2, 4, 8 = 0, +0.5, +1, +2 h; 255 unknown) | Bluetooth SIG characteristic 0x2A0F (Zephyr `BT_UUID_GATT_LTI_VAL`): **unverified, no saved document or kit file holds the layout** |
| CTS day of week 1 Monday to 7 Sunday; service 0x1805; characteristic 0x2A2B | Bluetooth SIG numbers as in the kit's `BT_UUID_CTS_VAL`; the day-of-week meaning is not in a kit file or in the saved Apple pages: **unverified** (it affects only the stand-in; the ring ignores the field) |
| Kit's limit of 32 bytes per attribute | kit `kit/ancs_client.h:50`, `kit/ancs_client.c:479` |

### Formats that rest only on the kit, or on nothing

A shared wrong reading of these would pass on both sides of the tests; a real iPhone must still confirm each (review `docs/step3-review.md` part 3).

| Format | Rests on | What a real iPhone must confirm |
|---|---|---|
| ANCS Notification Source: byte sizes and little-endian order of the fields and of the u32 id | the kit's parser (`kit/ancs_client.c:60-110`); Apple's text lists the fields, the figure with the sizes is not saved | the 8-byte layout and the byte order |
| ANCS Get Notification Attributes request and answer: u16 little-endian lengths, u32 little-endian id | the kit's encoder (`kit/ancs_client.c:409-453`); Apple's text names a "16-bit length parameter" | the byte order of the lengths and the id in the request and in the answer |
| AMS Remote Command ids (play 0, pause 1, next 3, previous 4, volume up 5, volume down 6) | the kit's enum (`kit/ams_client.h:82-98`, values implicit 0..6); the Apple appendix is not saved | each id does what its name says |
| AMS entity and attribute ids (player 0, track 2; PlaybackInfo 1; artist 0, title 2) | the kit's enums (`kit/ams_client.h:100-142`) | the ids |
| AMS Entity Update flag bit 0 = truncated | the kit's header (`kit/ams_client.h:58-59`); Apple's text only says a flag can say "truncated" | the bit (the ring ignores the flag) |
| AMS PlaybackInfo `<state>,<rate>,<elapsed>`, state 0 paused, 1 playing | the kit's sample README (`kit/ams_sample_readme_excerpt.txt`); no Apple page saved | the format and the state numbers (2 and 3 are ignored) |
| CTS Current Time, 10 bytes | the kit (`kit/cts_client.c:19-25,103-135`); Bluetooth SIG, not saved | the layout |
| CTS day of week (1 Monday to 7 Sunday) | nothing (stand-in only; the ring ignores the field) | not needed by the ring |
| Local Time Information, 2 bytes: zone and daylight offset | nothing saved: the author's reading of the Bluetooth SIG specification | the layout, the units (15 minutes), the daylight codes (0, 2, 4, 8) and the "unknown" values; that the iPhone serves the characteristic at all |
| Behaviour: the replay of held notifications flagged pre-existing when the ring subscribes; Removed after a dismiss; time notifications on a change | the stand-in's choices (Apple's appendix has the flag; nothing says the replay) | all three |

## 4. Deviations from the brief and from design/firmware.md

1. **The kit's attribute parser is not used.** The kit's ANCS client keeps at most 32 bytes per attribute: `BT_ANCS_ATTR_DATA_MAX 32` (`build-logs/step3/kit/ancs_client.h:50`) and `bt_ancs_register_attr` refuses a longer buffer (`kit/ancs_client.c:479`). The brief asks for 48 bytes of identifier, 48 of title and 160 of message. This is not a build error (the kit's parts build for the ring chip target, section 7), so I did not stop; I wrote the Data Source reassembly myself (`modules/ring_iphone/src/ripl.c`, `ripl_ds_feed`, with its own logic tests) and the ring subscribes to the Data Source and writes the Get Notification Attributes request itself (`modules/ring_iphone/src/rip.c`, `ancs_found`, `ds_notify`, `fetch_fn`). The kit is still used for: finding the service and its handles (`bt_ancs_handles_assign`), the Notification Source subscription and its message parser (`bt_ancs_subscribe_notification_source`), and Perform Notification Action (`bt_ancs_notification_action`). Also from the kit: the Media, Current Time and GATT service clients (`bt_ams_*`, `bt_cts_*`, `bt_gattp_*`).
2. **The clock holds UTC when the iPhone gives its zone, and its local time when it does not (changed in round 2).** Round 1 stored the iPhone's local time as UTC. Now the iPhone part reads Local Time Information (zone and daylight offset) next to Current Time, stores UTC = local time minus zone minus daylight offset together with the offset in minutes (`rtime_tz_min()`), and sets `rtime_zone_known()`. When the iPhone gives no zone (no such characteristic, an unreadable value, or an "unknown" value) the clock keeps the local time and `rtime_zone_known()` returns false (`docs/step3-round2.md`, point 5). The format of Local Time Information (2 bytes: zone int8 in 15-minute units, daylight offset uint8) is the author's reading of the Bluetooth SIG specification and rests on no saved document (section 3).
3. **Test P uses the stand-in iPhone in plain mode, not the step 2 host program.** The step 2 host (`tests/bsim/control/host_app`) evaluates fixed key sequences of its own scenarios A to G, none of which fits "pair, wait, one key"; I may not change it. The stand-in of step 3 contains the same pairing and HID client code (copied from it) and in scenario P serves no Apple service, which is what a step 2 host is.
4. **ATT MTU 247 and the system workqueue stack, in one shared file (changed in round 2).** FW 7.1 asks for MTU 247; step 2 had the default. Round 1 of these notes claimed that `app/prj.conf` set the MTU and buffer sizes; that was false: only the test ring set them. Now `modules/ring_iphone/ring_iphone_link.conf` holds `CONFIG_BT_L2CAP_TX_MTU=247`, `CONFIG_BT_BUF_ACL_RX_SIZE=251`, `CONFIG_BT_BUF_ACL_TX_SIZE=251`, `CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE=3072` and `CONFIG_BT_GATT_DM_MAX_ATTRS=35`; `app/CMakeLists.txt` and `tests/bsim/iphone/ring_app/CMakeLists.txt` both add it with `EXTRA_CONF_FILE`, and the build stage `link-settings` of `tools/build_all.sh` fails when the built product's settings differ from the test ring's (`docs/step3-round2.md`, point 1).
5. **Extras beyond the brief:** a `broken_run.sh` for each of the three logic suites (inbox, time, iPhone logic); `text_ready` in an inbox entry (the entry exists from the Added event, its text a moment later); `CONFIG_RING_IPHONE_FETCH_QUEUE` (32); the `ring_iphone` logic split in `ripl.c`.
6. **No change to `ring_devices`.** The brief allowed a minimal one; none was needed (section 5, point 1).
7. **GATT client on the peripheral link.** FW 7.1 says "Peripheral role only". The link role stays peripheral; on that link the ring now also acts as a GATT client (discovery, subscriptions, writes) toward the iPhone, as Nordic's ANCS, AMS and CTS samples do (`kit/sample_prj_confs.txt`). The proposed section 7.6 says so. FW 7.2's ring service (Time characteristic and the rest) is not touched: this step reads time from Apple's service, not from our own.
8. **FW 7.2's Time characteristic and FW 9.1's saved time (RRAM, "time not set" after a boot) are not built or changed.** The new clock lives in RAM only.

## 5. Decisions the brief left open (one fixed choice each)

1. **When the iPhone part starts:** on the ring's own `security_changed` callback with level 4 and on `pairing_complete`, it asks `rdev_active_conn()` after 20 ms; when that is still NULL it asks again every 300 ms, at most 10 times (`rip.c`, `trigger_ready`, `ready_fn`). Reason: on a first pairing the devices part marks the slot active in `pairing_complete`, which can come after the level 4 callback.
2. **Order of discovery**, one at a time (the kit's discovery manager allows one): GATT service (Service Changed), Notification Center, Media, Current Time. A start error is retried 5 times, 300 ms apart, then the service counts as not found.
3. **ANCS subscription order:** Data Source first, then Notification Source, so the answers to the notifications the iPhone sends at once can be heard.
4. **Attribute request:** application identifier, title (maximum length 48), message (maximum length 160), date; 13 bytes. One request at a time; at most 32 waiting (`CONFIG_RING_IPHONE_FETCH_QUEUE`, range 1 to 255). A request that gets no answer in 3,000 ms, gets a wrong answer or whose write fails is asked for once more, at the front of the queue; after a second failure it is given up (counted in `fetch_failed`). Bytes that are not the answer to the request in flight (a late answer of an earlier request) are skipped, not an error (round 2).
5. **Events:** Added with a known id replaces the entry and moves it to the front; Modified for an unknown id (pushed out earlier, or never held) is ignored and counted; Removed for an unknown id is ignored.
6. **Service Changed:** the ring stops the three services, empties the inbox and the media record, then looks for Notification Center, Media and Current Time again (not for the GATT service). It ignores the handle range of the indication.
7. **Actions:** an action does not change the inbox; the iPhone's Removed event does (stand-in: sent 300 ms after the negative action, as an iPhone does when a notification is dismissed). Nothing is sent for an id that is not held (-ENOENT), for a missing flag (-ENOTSUP) or when the service is not up (-ENOTCONN).
8. **Media registration:** Player: PlaybackInfo; Track: Artist and Title (two Entity Update writes, the second after the first is answered). The Remote Command notification (the list of supported commands) is not subscribed. The truncated flag of an Entity Update is not used.
9. **Player state:** state 0 is paused, state 1 is playing; any other first field (for example 2 and 3) changes nothing and is counted. Unknown until the first report and again after the session or the service ends.
10. **Time:** after the Current Time service is subscribed the ring reads Local Time Information first and then Current Time; the clock is set from that, and again at every Current Time notification (the zone is read again after each notification). UTC = local time - (zone x 15 min + daylight offset); zone -128 or daylight offset 255 or a value out of range means "zone not known" (the local time is kept, the flag is false). Fractions of 1/256 s become milliseconds rounded down.
11. **Text limits:** application identifier 48 bytes, title 48, message 160, date 15, track title 64, artist 48; always cut at a character boundary; a byte that is not valid UTF-8 counts as a character of one byte; an incomplete character at the end of what the iPhone sent is dropped; a NUL ends a string.
12. **Discovery that ends with the link:** each discovery carries the number of the session that started it; the answer of a discovery whose session has ended, or whose link is no longer connected, is dropped and counted (`dm_stale`): it counts no service as missing, attaches no client and does not move the next session's phase (round 2, `docs/step3-round2.md` point 6).
13. **Locking:** one mutex guards the inbox, media record, flags and counters; no Bluetooth call is made while it is held except `bt_conn_ref` bookkeeping that cannot block. `rip_action` and `rip_media_command` may be called from any thread.

## 6. Not built and not proven

Not built:
- Entity Attribute read for a value the iPhone marked truncated; the Remote Command notification; the Queue entity; Get App Attributes (the application's display name); Subtitle, Message Size, and the action labels of the notification.
- The screens that show the inbox and the media state; the "read" mark is set only by `rip_inbox_mark_read` and nothing calls it yet.
- Persistence: the inbox, media record and the clock's offset are not saved (the inbox is rebuilt from the iPhone at each link, by rule). The clock is lost at reset.
- Android helper app relay and any Mac notification path (design.md section 1).
- Holding two links at once.

Not proven (the stand-in shares my reading of the documents; nothing ran against a real iPhone):
- Everything about a real iPhone: that it sends the notifications it holds, flagged pre-existing, when the ring subscribes (the flag exists in Apple's appendix; the replay is the stand-in's behaviour); that it sends Removed after a dismiss; how iOS fragments the Data Source answer; whether iOS asks the user before it shares notifications with a new accessory; that it sends Current Time notifications on a change (the ADG says the service is available, `apple/adg-excerpt-16868-16873.txt`, not when it notifies).
- CTS day-of-week meaning and the Local Time Information format (both unverified, section 3) and the fraction rounding.
- The effect of the iPhone's GATT database caching (Database Hash): the ring does not read the hash; the stand-in has caching off (`CONFIG_BT_GATT_CACHING=n`).
- Paths that no run reaches (round 3 state): the discovery error branch (`dm_errors` stays 0 in every run), an ATT error 0xA3 from the iPhone (`action_failed`), `-EBUSY` from the kit's write for two quick actions, more than 32 notifications waiting, a drop during the first (GATT service) or last (Current Time) discovery. Reached since round 2: the fetch timeout (scenario L: `fetch_timeouts` is 1) and a link that ends during the Media discovery (scenario D). A Data Source stream that does not match the request is reached over Bluetooth in scenario L (late bytes, counted in `ds_skipped`) and by the logic tests.
- Real radio, range, power, memory beyond the build figure.
- Bonds and the stored notification settings after a reset (the simulation keeps bonds in RAM, as in step 2).

Known weaknesses of my own tests (for the reviewer):
- The stand-in and the ring share one person's reading of Apple's documents; every format is cited in section 3, but a wrong reading would pass on both sides. The two points I could not source are named there (CTS day of week; the Apple AMS appendix).
- Some checks are counts that follow my implementation: 23 attribute requests (`PHONE CHECK 23 attribute requests (20 added, 3 modified)`), `ancs_down == 2`, four Entity Update subscriptions in scenario R. They are exact on purpose (a fetch that repeats or a stop that does not happen shows), but they will need an edit if the design of the requests changes.
- Three checks use "at least": the clock was set at least once or twice (`rtime_updates() >= 1`, `>= 2`) and Service Changed was indicated at least once (`sc_indications >= 1`). The exact effects (the clock's value, the stopped and restarted services) are checked next to them.
- `core_touch` models "an iPhone message reaches the joystick path" with a hook that presses the centre while a recording runs; it shows the check can fail, it is not a proof that no other path exists. The proof of "nothing from the iPhone starts a recording" is the absence of any call into the core or the glue in `modules/ring_iphone`, plus the checks of scenario N.
- Not every promise has its own broken copy: none breaks "subscribe only at level 4", "keys go only to the active device" (step 2's tests do) or the positive action's id on its own (`action_id` swaps both ids).
- The simulation is deterministic and runs without radio noise: nothing here measures timing margins.

## 7. Earlier runs and findings

Every look at a result before the final run, in order (all files are in `build-logs/step3/`; every run used my own server copy, a folder under `/root/ring-os/` named `src-step3`, `src-step3b`, `src-step3-final` or `src-step3-final2`):

1. `20261111-231630-os-iphone-logic1.log`: twister on `tests/inbox`, `tests/time`, `tests/iphone` on native_sim: 3 of 3 scenarios, 34 of 34 cases passed. It ran before any broken copy had been run against these suites.
2. `20261111-231721-os-iphone-appbsim.log`: the product application for `nrf54lm20bsim/nrf54lm20a/cpuapp` with the iPhone part. It built, so the kit's Notification Center, Media, Current Time and GATT service clients build for the ring chip target. One compiler warning from my code (`rip.c`, a pointer to a UUID made inside a `switch` block); fixed with static UUID objects.
3. `20261111-232804-os-iphone-bsim-n1.log`: `run.sh N` stopped with exit 126 (the new `run.sh` had no execute bit); nothing ran.
4. `20261111-232822-os-iphone-bsim-n2.log`: scenario N ran. All checks of the stand-in passed; the ring had 3 failed checks out of 73 (`nothing in the inbox before the iPhone sends` and the two checks of events during RECORDING and STANDBY). Cause, from the log: the ring started its script clock after `wait_ready()`, which includes a 3 s wait, so its clock ran about 3 s behind the stand-in's and the stand-in's first notification had already arrived. Fixed in the test (`ring_app/src/main.c`, `run_n`: the ring's zero is the moment the notification service is subscribed). Not a fault of the modules.
5. `20261111-233044-os-iphone-bsim-all1.log`: scenarios N, R, P all passed (73, 32 and 19 checks).
6. `20261111-233223-os-iphone-bsim-broken1.log`: the 13 broken copies. Twelve were caught on their named check. `utf8_cut` was not counted (`RESULT FAIL utf8_cut(not-caught)`): the ring's diagnostic line printed the cut message raw, the `printk` line came out garbled and glued into the next line, so the named check line could not be read. Fixed in the test (the diagnostic now prints the length and the last bytes in hex); no module change.
7. `20261111-233247-os-iphone-dk1.log`: the application for the development kit with sysbuild built (figures in the final log).
8. `20261111-233721-os-iphone.log`: a full run of the bar command started before the fixes of point 6 and before the label and comment edits of the tests; it is not the final run. I stopped it myself (my `remote.sh` process killed, then `docker stop` on its container, which took several minutes) at the `bsim-control-broken` stage; the log ends where it was stopped.
9. `20261111-234115-os-iphone-logic-broken1.log`: the three `broken_run.sh` of the logic suites on both boards: all six named cases failed as required.
10. `20261111-234347-os-iphone-final.log`: an aborted start of a run: I had named it `os-iphone-final` instead of `os-iphone`, killed my local `remote.sh` during the copy, and nothing ran on the server.
11. `20261111-234407-os-iphone.log`: the bar command, started after the fixes of points 6 and 8. About 8 minutes into it (stage `tests-nrf54lm20bsim_nrf54lm20a_cpuapp` done, `bsim-control` running) I found that citations of line numbers in source comments were off by a few lines (`cts_client.c` in two files, `ancs-appendix.txt` in one), corrected the comments, and stopped this run (my `remote.sh` killed) to run the command again on the corrected files; its container did not stop at once (`docker stop` and `docker kill` timed out on the loaded server; it stopped after several minutes). The log ends where it was stopped. The run that counts is the last one, section 1.
12. `editcheck/`: before the Bluetooth broken copies ran, I applied each of the 13 edits of `tests/bsim/iphone/broken_edit.py` locally to a copy of the modules (`editcheck/<variant>/out.txt` holds the diff): each matched exactly once.

Findings about the kit and Zephyr, in the order I met them:
- The kit's ANCS attribute parser keeps 32 bytes per attribute (deviation 1).
- `bt_gatt_dm_conn_get` adds no reference to the link (`kit/gatt_dm_and_zephyr_gatt_excerpt.txt`, first lines): the kit's clients keep the raw pointer of the link, so the iPhone part clears its flags when the link ends and never uses a client after that.
- `bt_gatt_service_unregister` calls `sc_indicate` (same file): the stand-in's GATT server indicates Service Changed to a client that subscribed. With `CONFIG_BT_GATT_CACHING=y` a bonded client would also have to read the Database Hash, which the ring does not do (section 6).
- A raw cut multi-byte character in a `printk` line corrupts the log line; the tests print such text in hex.

Round 2 (review `docs/step3-review.md`, answers in `docs/step3-round2.md`): the sections above were corrected and the answers to the bar regenerated from the round 2 log. Changes: link and stack settings in one shared file with a check in the build (deviation 4; the round 1 claim that the product set them was false); a late answer fragment is skipped and a failed request is asked for once more; the flagless-action check is made by the stand-in; the clock holds UTC with the zone (deviation 2); discovery that ends with the link is dropped (decision 12); five new broken copies and two new Bluetooth scenarios (L, D).

Round 3 (review `docs/step3-review-2.md`, answers in `docs/step3-round3.md`): the clock keeps the Current Time arrival uptime and the last known zone of the link (a delayed zone read no longer moves the clock; a failed read changes nothing); scenario L now lands the late bytes inside a later request and counts the skipped bytes; new scenarios Z and W (zone change, no Local Time Information); five new Bluetooth broken copies (late_parser, zone_read_failed, dm_gone, zone_not_reread, no_lti_known; the earlier ones are kept) and two logic copies (clock_drift, clock_failed_read); the settings check compares five values, pins the MTU to at least 247 and the module refuses to build below 247; the false header for notification id 0 is explained, not fixed (round 3 point 5: one retry is the cost).

## 8. Text for the behaviour rules

Ready to paste as section 7.6 of `design/firmware.md` (I did not touch `design/`).

### 7.6 Apple's services (the iPhone part)

The ring is the Bluetooth client of the iPhone for three Apple services. Apple's documents give the data formats; the nRF Connect SDK v3.4.2 gives the client code. Nothing here starts or stops a recording: the iPhone part calls nothing in the core (rule of section 7.1).

- **When.** After the link of the active device reaches security level 4 (section 7.4) the ring looks, one after the other, for the GATT service (to subscribe to Service Changed), Apple Notification Center Service (UUID 7905F431-B5CE-4E99-A40F-4B1E122D00D0), Apple Media Service (89D3502B-0F36-433A-8EF4-C502AD55F8DC) and Current Time Service (0x1805). A service that is not there (an Android phone, a Mac) is "not found": no error, no retry, the inbox stays empty, an action returns "no such notification" and a media command returns "not connected".
- **Discovery and links.** A discovery that is running when the link ends is dropped with its session: it counts no service as missing and does not move the next session, which looks for the three services again.
- **Service Changed.** When it is indicated the ring stops the three services (unsubscribes; the inbox and the media record are emptied), then looks for the three services again and subscribes to those it finds. Apple: the Notification Center Service is not guaranteed to be present at any time.
- **Sessions.** The inbox, the media record and the services' subscriptions live for one link (or until Service Changed). When the link ends everything stored from the iPhone is emptied. After a reconnect the ring subscribes again and rebuilds the inbox from the notifications the iPhone sends again (Apple: the service keeps no state across sessions). The clock is not emptied.
- **Inbox.** The last 16 notifications, newest first; the 17th pushes the oldest out. Per notification: the iPhone's id (u32), category (0..11), flags (silent, important, pre-existing, has a positive action, has a negative action: Apple's EventFlags bits 0 to 4), application identifier (at most 48 bytes), title (48), message (160), date (15 characters, `yyyyMMdd'T'HHmmSS`), a read mark. All strings are UTF-8, NUL terminated and cut at a character boundary, never inside one. Added makes a new entry (the same id replaces the old entry and moves it to the front); Modified replaces category, flags and text and keeps the place (an id that is not held is ignored); Removed deletes the entry.
- **Attributes.** For each Added or Modified event the ring asks for the application identifier, the title (maximum length 48), the message (maximum length 160) and the date, one request at a time, 13 bytes; the answer may come in any number of fragments and is spliced. A request without an answer in 3 s, with a wrong answer or whose write fails is asked for once more; after the second failure it is given up. Bytes that are not the answer to the request in flight (for example a late answer of the earlier request) are skipped.
- **Actions.** `rip_action(id, positive|negative)` sends Perform Notification Action (CommandID 2, id, ActionID 0 or 1). A dismiss chosen on the ring is the negative action. An action for a notification that does not have that action (its flag is not set) is refused and sends nothing. The ring's inbox changes only when the iPhone reports the removal.
- **Media.** The ring registers for the player's PlaybackInfo and the track's artist and title. It stores the track title (at most 64 bytes), the artist (48) and the player state (paused or playing: state 0 or 1 of PlaybackInfo) as the iPhone reports them. `rip_media_command` sends Remote Command play 0, pause 1, next track 3, previous track 4, volume up 5, volume down 6. The stored state changes only on the iPhone's report, never on the ring's own command (Apple: a written command does not prove that the player acted). The Media control mode of section 7.5 keeps its keyboard-style keys.
- **Time.** After the link is ready the ring subscribes to Current Time, reads Local Time Information (zone in 15-minute units, daylight saving offset) and then Current Time. The ring's clock (milliseconds, a "time is set" flag and a "zone known" flag, section 9.1) holds UTC = the iPhone's local time minus zone minus daylight offset, with the offset in minutes, and is set again at each Current Time notification (the zone is read again after each). When the iPhone gives no zone (no such characteristic, an unreadable or unknown value) the clock keeps the local time and the "zone known" flag is false.
- **Link settings.** ATT MTU 247 (section 7.1); attribute answers are fragmented by the sender to the negotiated MTU.

## 9. Cleanup

What I made outside `build-logs/step3/` and removed (rounds 1 and 2):
- On the server, my own copies and outputs only. Round 1: the source folders `/root/ring-os/src-step3`, `src-step3b`, `src-step3-final`, `src-step3-final2`; build outputs `/root/ring-os/ws/out/20261111-*-os-iphone*` and `step3-*`; run files `20261111-23*-os-iphone*` in `/root/ring-os/logs` and `/root/ring-os/runs` (listings: `build-logs/step3/cleanup-final.txt`, `cleanup-interim-1.txt`). Round 2: the source folders `/root/ring-os/src-step3r2`, `r2b`, `r2c`, `r2d`, `r2e`; build outputs `/root/ring-os/ws/out/r2-logic*`, `r2-dk*` and `20261112-*` for the runs named `r2-first`, `r2-second`, `r2-third`, `r2-fourth`, `r2-dk`, `os-iphone-r2`, `r2-newbroken`, `r2-newbroken2`; their run files. The listing before and after is `build-logs/step3/cleanup-round2.txt` (the after-listing shows nothing of mine left and 0 of my containers running).
- No process of mine is left. Several containers of stopped runs took minutes to stop because the server was loaded (section 7).
- Locally: `__pycache__` folders that syntax checks had made (deleted; not evidence).
- Not removed, because they are my evidence: everything in `build-logs/step3/` (logs, `kit/`, `apple/`, `editcheck/`, `editcheck2/`, the scripts that made the notes).
- Round 3: server copies `/root/ring-os/src-step3r3` to `r3f`, outputs `ws/out/r3-*` and `20261112-*` of my runs (`r3-first`, `r3-a`, `r3-b`, `r3-c`, `r3-mtu`, `r3-mtu2`, `os-iphone-r3`) and their run files are removed; the listing (`cleanup-round3.txt`) shows only files of earlier days that belong to other helpers; 0 containers of mine are running.

## 10. The cited log lines

Each `LOG:n` above is line n of `build-logs/step3/20261112-090932-os-iphone-r3.log`; the text of those lines (the simulator's time stamp prefix cut off):

- `LOG:850`: FLASH:      186232 B     974704 B     19.11%
- `LOG:851`: RAM:       51264 B       511 KB      9.80%
- `LOG:861`: === stage dk end 2026-11-12T08:10:37Z exit 0
- `LOG:1299`: === stage bsim-build end 2026-11-12T08:11:00Z exit 0
- `LOG:1307`: === stage bsim-run end 2026-11-12T08:11:00Z exit 0
- `LOG:1328`: INFO    - 2/7 native_sim/native         ring_inbox.logic                                   PASSED (native 0.012s <host/gnu>)
- `LOG:1329`: INFO    - 3/7 native_sim/native         ring_time.logic                                    PASSED (native 0.007s <host/gnu>)
- `LOG:1330`: INFO    - 4/7 native_sim/native         ring_iphone.logic                                  PASSED (native 0.015s <host/gnu>)
- `LOG:1344`: === stage tests-native_sim end 2026-11-12T08:11:33Z exit 0
- `LOG:1358`: INFO    - 3/7 nrf54lm20bsim/nrf54lm20a/cpuapp ring_time.logic                              PASSED (native 0.009s <host/gnu>)
- `LOG:1359`: INFO    - 4/7 nrf54lm20bsim/nrf54lm20a/cpuapp ring_iphone.logic                            PASSED (native 0.014s <host/gnu>)
- `LOG:1360`: INFO    - 5/7 nrf54lm20bsim/nrf54lm20a/cpuapp ring_inbox.logic                             PASSED (native 0.012s <host/gnu>)
- `LOG:1373`: === stage tests-nrf54lm20bsim_nrf54lm20a_cpuapp end 2026-11-12T08:12:27Z exit 0
- `LOG:2248`: === stage bsim-control end 2026-11-12T08:13:49Z exit 0
- `LOG:3970`: === stage bsim-control-broken end 2026-11-12T08:20:23Z exit 0
- `LOG:3991`: RING CHECK the player state and track follow the iPhone's first report (paused, Bohemian Rhapsody, Queen) PASS (t=11868)
- `LOG:3992`: RING CHECK the ring's clock equals the iPhone's time within 1 s, as UTC (the iPhone's zone +2 h taken off) PASS (t=11868)
- `LOG:3997`: RING CHECK a: 101 exact (SMS: category 4, flags important+positive+negative) PASS (t=13521)
- `LOG:3998`: RING CHECK a: 102 exact (mail: category 6, negative action) PASS (t=13521)
- `LOG:3999`: RING CHECK a: 103 exact: identifier cut at 48 bytes, title at 48, the 200-byte message cut to 159 bytes on a character PASS (t=13521)
- `LOG:4000`: RING CHECK a: 104 exact (no actions, empty message) PASS (t=13521)
- `LOG:4001`: RING CHECK a: 105 exact (the iPhone sent all 200 bytes: kept 160 and cut at a character) PASS (t=13521)
- `LOG:4002`: RING CHECK a: no message is longer than 160 bytes and none ends inside a character (every entry) PASS (t=13521)
- `LOG:4003`: RING CHECK b: the change arrived PASS (t=16477)
- `LOG:4004`: RING CHECK b: the changed notification keeps its place and has the new flags (positive action gone) PASS (t=16477)
- `LOG:4005`: RING CHECK b: the removal deletes the entry PASS (t=18381)
- `LOG:4007`: RING CHECK b: thirteen more arrive: the store holds 16 PASS (t=26447)
- `LOG:4008`: RING CHECK b: the 17th notification dropped the oldest (101) and only that one PASS (t=26447)
- `LOG:4010`: RING CHECK c: dismiss chosen on the ring for 122 is sent PASS (t=30164)
- `LOG:4011`: RING CHECK c: the inbox does not change on the ring's own command (122 is still there) PASS (t=30164)
- `LOG:4012`: RING CHECK c: positive action for 121 is sent PASS (t=30664)
- `LOG:4013`: RING CHECK c: an action without its flag is refused: dismiss of 104 (no actions) PASS (t=31164)
- `LOG:4014`: RING CHECK c: an action without its flag is refused: positive action of 103 (negative only) PASS (t=31164)
- `LOG:4016`: RING CHECK c: two commands were sent and three were refused PASS (t=31164)
- `LOG:4017`: RING CHECK c: the iPhone reports the dismissed notification removed: 122 leaves the inbox PASS (t=31164)
- `LOG:4018`: RING CHECK f: a new track and the playing state arrive from the iPhone PASS (t=35372)
- `LOG:4025`: RING CHECK f: the stored state did not change on the commands alone (pause was sent, the state is still playing) PASS (t=38373)
- `LOG:4027`: RING CHECK f: the stored state follows the iPhone's next report (paused) PASS (t=45337)
- `LOG:4030`: RING CHECK g: the ring's clock follows the iPhone's time change (two hours) PASS (t=47339)
- `LOG:4035`: RING CHECK i: a long press starts a recording PASS (t=53965)
- `LOG:4036`: RING CHECK i: events arrived during RECORDING (one added, one modified, one removed, a track, a state, a time) PASS (t=63164)
- `LOG:4039`: RING CHECK i: the core is still RECORDING, no recording started or stopped, no key sent PASS (t=63164)
- `LOG:4041`: RING CHECK i: a long press stops the recording PASS (t=64964)
- `LOG:4042`: RING CHECK i: events arrived during STANDBY (one added, one modified, one removed, a track, a state, a time) PASS (t=73164)
- `LOG:4045`: RING CHECK i: the core is still STANDBY, no recording started or stopped, no key sent PASS (t=73164)
- `LOG:4046`: RING CHECK keys still go to the active device: media centre sends 2 reports PASS (t=73864)
- `LOG:4083`: PHONE INFO action 1 for notification 122
- `LOG:4089`: PHONE INFO remote command 0
- `LOG:4094`: PHONE INFO remote command 6
- `LOG:4119`: PHONE CHECK two actions arrived: negative for 122, positive for 121, and no other PASS (t=102294)
- `LOG:4120`: PHONE CHECK the six media commands arrived: play, pause, next, previous, volume up, volume down (ids 0,1,3,4,5,6), then play again (id 0) PASS (t=102294)
- `LOG:4121`: PHONE CHECK no action command arrived for a notification that does not have that action (every command is recorded before it can be refused) PASS (t=102294)
- `LOG:4129`: TEST N RESULT PASS (80 checks passed)
- `LOG:4143`: RING CHECK d: the link drops PASS (t=16382)
- `LOG:4144`: RING CHECK d: the inbox is empty when the link has ended PASS (t=16483)
- `LOG:4149`: RING CHECK d: the inbox holds what the iPhone sends again PASS (t=28557)
- `LOG:4150`: RING CHECK d: rebuilt from the iPhone: 203 then 201 with the pre-existing mark, the edited text; 202 is gone PASS (t=28557)
- `LOG:4151`: RING CHECK e: the ring stops when the service goes away PASS (t=36122)
- `LOG:4152`: RING CHECK e: the inbox is emptied when the service ends PASS (t=36122)
- `LOG:4153`: RING CHECK e: Service Changed was indicated and the services were stopped (twice: the drop and the removal) PASS (t=36122)
- `LOG:4155`: RING CHECK e: the ring subscribes again when the service is back PASS (t=45290)
- `LOG:4156`: RING CHECK e: a new notification arrives and is stored exactly PASS (t=49599)
- `LOG:4158`: RING CHECK e: subscribed three times in all (start, after the drop, after Service Changed) PASS (t=49599)
- `LOG:4188`: PHONE INFO the Notification Center Service is removed (t=36015)
- `LOG:4192`: PHONE INFO the Notification Center Service is added again (t=44015)
- `LOG:4201`: PHONE CHECK the ring subscribed to the Notification Source three times (start, after the drop, after Service Changed) PASS (t=64469)
- `LOG:4206`: TEST R RESULT PASS (33 checks passed)
- `LOG:4217`: RING CHECK h: Service Changed was looked for and found (the host has the GATT service), the three Apple services were looked for and not found (not an error) PASS (t=21707)
- `LOG:4219`: RING CHECK h: the inbox stays empty PASS (t=21707)
- `LOG:4223`: RING CHECK h: keys still work: media centre sends 2 reports PASS (t=22407)
- `LOG:4239`: PHONE CHECK the ring's key arrived once (media centre: usage 0x00CD, then release) PASS (t=46444)
- `LOG:4242`: TEST P RESULT PASS (19 checks passed)
- `LOG:4290`: TEST L RESULT PASS (17 checks passed)
- `LOG:4335`: TEST D RESULT PASS (19 checks passed)
- `LOG:4573`: broken inbox_size: test N failed on its named check, as required: d_00: @00:00:43.431027  RING CHECK b: thirteen more arrive: the store holds 16 FAIL (t=43431)
- `LOG:4764`: broken utf8_cut: test N failed on its named check, as required: d_00: @00:00:13.521327  RING CHECK a: 103 exact: identifier cut at 48 bytes, title at 48, the 200-byte message cut to 159 bytes on a character FAIL (t=13521)
- `LOG:4931`: broken remove_ignored: test N failed on its named check, as required: d_00: @00:00:28.501227  RING CHECK b: the removal deletes the entry FAIL (t=28501)
- `LOG:5098`: broken modify_ignored: test N failed on its named check, as required: d_00: @00:00:25.545327  RING CHECK b: the change arrived FAIL (t=25545)
- `LOG:5267`: broken action_flag: test N failed on its named check, as required: d_00: @00:00:31.164427  RING CHECK c: an action without its flag is refused: dismiss of 104 (no actions) FAIL (t=31164)
- `LOG:5436`: broken action_id: test N failed on its named check, as required: d_01: @00:01:42.294497  PHONE CHECK two actions arrived: negative for 122, positive for 121, and no other FAIL (t=102294)
- `LOG:5528`: broken reset_on_drop: test R failed on its named check, as required: d_00: @00:00:16.483027  RING CHECK d: the inbox is empty when the link has ended FAIL (t=16483)
- `LOG:5611`: broken sc_ignored: test R failed on its named check, as required: d_00: @00:00:48.597131  RING CHECK e: the ring stops when the service goes away FAIL (t=48597)
- `LOG:5779`: broken media_local: test N failed on its named check, as required: d_00: @00:00:38.373427  RING CHECK f: the stored state did not change on the commands alone (pause was sent, the state is still playing) FAIL (t=38373)
- `LOG:5946`: broken time_ignored: test N failed on its named check, as required: d_00: @00:00:56.157427  RING CHECK g: the ring's clock follows the iPhone's time change (two hours) FAIL (t=56157)
- `LOG:6118`: broken core_touch: test N failed on its named check, as required: d_00: @00:01:03.164391  RING CHECK i: the core is still RECORDING, no recording started or stopped, no key sent FAIL (t=63164)
- `LOG:6287`: broken request_len: test N failed on its named check, as required: d_01: @00:01:42.294497  PHONE CHECK every Get Notification Attributes request is the 13 bytes Apple's format and the kit's encoder give FAIL (t=102294)
- `LOG:6338`: broken service_error: test P failed on its named check, as required: d_00: @00:00:21.707195  RING CHECK h: Service Changed was looked for and found (the host has the GATT service), the three Apple services were looked for and not 
- `LOG:7444`: RESULT PASS
- `LOG:7535`: === stage broken-control end 2026-11-12T08:32:18Z exit 0
- `LOG:7601`: === stage broken-devices end 2026-11-12T08:32:46Z exit 0
- `LOG:7645`: native_sim: the named case failed, as required:  - FAIL - [ring_inbox.test_full_drops_oldest] duration = 0.000 seconds (failed cases listed: 1)
- `LOG:7677`: nrf54lm20bsim/nrf54lm20a/cpuapp: the named case failed, as required: d_00: @00:00:00.000093   - FAIL - [ring_inbox.test_full_drops_oldest] duration = 0.000 seconds (failed cases listed: 1)
- `LOG:7716`: media_state on native_sim: the named case failed, as required:  - FAIL - [ring_iphone.test_media_playback_state] duration = 0.000 seconds (failed cases listed: 1)
- `LOG:7748`: media_state on nrf54lm20bsim/nrf54lm20a/cpuapp: the named case failed, as required: d_00: @00:00:00.000093   - FAIL - [ring_iphone.test_media_playback_state] duration = 0.000 seconds (failed cases listed: 1)
- `LOG:7922`: native_sim: the named case failed, as required:  - FAIL - [ring_time.test_set_then_follows_uptime] duration = 0.000 seconds (failed cases listed: 3)
- `LOG:7946`: nrf54lm20bsim/nrf54lm20a/cpuapp: the named case failed, as required: d_00: @00:00:00.000093   - FAIL - [ring_time.test_set_then_follows_uptime] duration = 0.000 seconds (failed cases listed: 3)
- `LOG:7950`: RESULT PASS

RESULT: done, the round 3 bar command ends RESULT PASS with every stage passing; a to k are answered from that log, with the deviations and what is unproven listed (changes of rounds 2 and 3 in docs/step3-round2.md and docs/step3-round3.md).
