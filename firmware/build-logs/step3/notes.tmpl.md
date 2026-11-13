# Step 3: the iPhone part and the inbox

Version: round 1 on firmware/ at commit 221746b and design/ at commit 9818c7e; round 2 on the files of commit e455a9f; round 3 on commit 1e7ccd8; plus the step 3 files listed in section 2. I ran no git. Written 2026-11-11 and 2026-11-12. Paths are under `firmware/` unless they start with `design/`.

Bar command, round 3 (my own run, on my own server copy `RING_REMOTE_SRC=/root/ring-os/src-step3r3f`): `sh firmware/tools/remote.sh os-iphone-r3 "tools/build_all.sh"`. The answers below are from that run. Round 1 and round 2 runs are described in section 7; changes and answers to the reviews are in `docs/step3-round2.md` and `docs/step3-round3.md`.
Log ("the log" below): `[[LOGPATH]]`. The last line build_all printed is `[[LASTLINE]]`; remote.sh then wrote `[[EXITLINE]]`. A citation `LOG:n` is line n of that file; `file:n` is a line of a source file as delivered.

## 1. Answers to the bar, a to k

[[BAR]]

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

[[KITONLY]]

## 4. Deviations from the brief and from design/firmware.md

[[DEVIATIONS]]

## 5. Decisions the brief left open (one fixed choice each)

[[DECISIONS]]

## 6. Not built and not proven

[[NOTBUILT]]

## 7. Earlier runs and findings

[[RUNS]]

## 8. Text for the behaviour rules

Ready to paste as section 7.6 of `design/firmware.md` (I did not touch `design/`).

[[RULES]]

## 9. Cleanup

[[CLEANUP]]
