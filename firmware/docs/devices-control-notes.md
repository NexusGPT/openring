# Devices and control: notes (step 2 of the ring software)

Date: 2026-11-11. Helper: step2 builder. No git command was run. Specification: `design/software/os/design.md` sections 2 and 3 (DS below), `design/firmware.md` F6 section 7 (FW), SDK research `design/software/os/research-sdk.md` (RS). SDK paths below are in the server workspace `/root/ring-os/ws` (nRF Connect SDK v3.4.2, Zephyr 4.4.2). Raw evidence is in `firmware/build-logs/step2/` (called `step2/` below).

The code: `firmware/modules/ring_devices/`, `firmware/modules/ring_control/`, tests in `firmware/tests/control/`, `firmware/tests/devices/`, `firmware/tests/bsim/control/`.

## 1. Interfaces (one page)

**ring_devices** (`include/ring_devices/rdev.h`, Kconfig `CONFIG_RING_DEVICES`; the pure part is `rdev_logic.h`, `CONFIG_RING_DEVICES_LOGIC`)

| Call | What it does |
|---|---|
| `rdev_init(&callbacks)` | enables Bluetooth, loads bonds, makes local identities 1 and 2 when missing (identity 0 is the default), picks the active device (saved one, else the first paired slot), starts advertising to it |
| `rdev_pair_open(slot or RDEV_ANY, ms)` | opens the pairing window (product value `RDEV_PAIR_WINDOW_MS` = 60,000): the link of the active device ends, the ring advertises on the slot's identity, open to any device, every 100 ms. A device that pairs in time becomes the active one; on timeout the ring returns to the previous active device. `-ENOSPC` all three slots paired, `-EEXIST` slot paired |
| `rdev_pair_cancel()`, `rdev_pair_window_open()` | close or query the window |
| `rdev_switch(slot)`, `rdev_switch_next()` | make a paired slot active: link ends, identity changes, the ring advertises to the chosen device. `-ENOENT` empty slot, `-EINVAL` out of range; the active slot is a no-op |
| `rdev_remove(slot)` | ends the slot's link, `bt_unpair()` deletes the bond (all key sets of that pairing and its stored notification settings), the slot is free; if it was active the next paired slot becomes active |
| `rdev_active()`, `rdev_paired_mask()`, `rdev_link_up()`, `rdev_slot_peer(slot,&addr)` | state queries |
| `rdev_active_conn()` | the connection to the active device when it is encrypted with an authenticated key (security level 4), referenced (caller does `bt_conn_unref`); NULL otherwise |

Callbacks (`struct rdev_callbacks`, all optional): `passkey_show(slot, six_digit_number)` (the screens part shows `%06u`), `passkey_hide`, `paired`, `pairing_failed`, `window_closed`, `removed`, `active_changed`, `link(slot, up)`.

Pure logic (`rdev_logic.h`): `struct rdev_list` (paired mask, active slot), `rdev_list_choose_pair_slot`, `rdev_list_add/remove/next/switch/decide_switch`, and `rdev_plan_next(state)`, which gives the one step the Bluetooth part must take (idle, stay, disconnect, advertise on slot n open or not). The Bluetooth part (`rdev.c`) runs that plan under one mutex; it makes no other decision about links.

**ring_control** (`include/ring_control/rctl.h`, `CONFIG_RING_CONTROL`; pure part `rctl_report.h`, `rctl_modes.h`, `CONFIG_RING_CONTROL_LOGIC`)

| Call | What it does |
|---|---|
| `rctl_init()` | registers the HID service (call before `rdev_init`) |
| `rctl_set_mode(mode)`, `rctl_get_mode()`, `rctl_set_options({presenter_pages})` | the mode (media, presenter, pointer, agent) and the presenter Page keys option. The screens part will choose the mode |
| `rctl_action(action)` | one joystick action in the current mode: builds the reports and sends them to `rdev_active_conn()`. Returns the number of reports sent, 0 when the mode sends nothing, `-ENOTCONN` (no authenticated link), `-EACCES` (the device has not switched the report on) |
| `rctl_core_actions(&rc_actions)` | takes the list the core returned; only the five joystick actions of the screen shown (`RC_ACT_SCREEN_CENTRE/UP/DOWN/LEFT/RIGHT`) become keys, every other action is ignored (`rctl_from_core`) |
| `rctl_ready()`, `rctl_stats_get()` | all three reports switched on by the active device; counters |

Reports (report map in `rctl_logic.c`, no boot protocol, no output report): ID 1 keyboard 8 bytes (modifiers, reserved, six keys); ID 2 consumer control 2 bytes (one 16-bit usage, 0 = release); ID 3 pointer 3 bytes (button 1, dx, dy as signed bytes). Key and consumer actions send a press report and then a release report; a pointer move is one report; a click is button down then up.

## 2. The four mode tables (`rctl_modes.h`, one header)

| Mode | centre (short) | up | down | left | right |
|---|---|---|---|---|---|
| media | play or pause (consumer 0x00CD) | volume up (0x00E9) | volume down (0x00EA) | previous (0x00B6) | next (0x00B5) |
| presenter | nothing | Left Arrow (0x50) | Right Arrow (0x4F) | Left Arrow | Right Arrow |
| presenter, Page keys option | nothing | Page Up (0x4B) | Page Down (0x4E) | Page Up | Page Down |
| pointer | click (button 1 down, up) | move (0, -16) | move (0, 16) | move (-16, 0) | move (16, 0) |
| agent | Return (0x28) | Up Arrow (0x52) | Down Arrow (0x51) | Escape (0x29) | Return (0x28) |

Choices not given in the brief: presenter centre sends nothing; the pointer step is 16 report units per direction event (`RCTL_POINTER_STEP`); a held direction repeats through the core (500 ms, then every 150 ms) in every mode, because the core's action list does not say whether an action is a repeat (`rctl_core_actions` sees only `RC_ACT_SCREEN_*`); in presenter a held key therefore flips slides every 150 ms after 500 ms. The centre long press is not in any table and `rctl_from_core` returns false for `RC_ACT_OPEN` and `RC_ACT_CLOSE`: no mode can use it, and nothing in these modules calls the core with an event, so nothing here can start or stop a recording.

## 3. Decisions and their sources

1. **One local identity per paired device, one bond per identity.** nRF Desktop `ble_bond.rst` lines 48, 54, 57-58 (`/root/ring-os/ws/nrf/applications/nrf_desktop/doc/ble_bond.rst`): "uses multiple local identities", "Only one Bluetooth peer can be bonded with a given local identity", changing the peer "actually switches its own local identity. The old peer is disconnected by the application, Bluetooth advertising is started, and the new peer connects". DS section 2 item 2. `CONFIG_BT_ID_MAX=3`, `CONFIG_BT_MAX_PAIRED=3` (`zephyr/subsys/bluetooth/host/Kconfig` lines 886 and 1023).
2. **Identities 1 and 2 are made after `bt_enable` and `settings_load`, only when missing.** `zephyr/include/zephyr/bluetooth/bluetooth.h` lines 455-460 (the documented way to keep generated identity addresses in flash). `rdev_init`.
3. **The slot is paired when its identity has a bond** (`bt_foreach_bond(slot, ...)`), so the paired state cannot disagree with the stack's keys.
4. **One link at a time** (`CONFIG_BT_MAX_CONN=1`): FW 7.1 line 690; holding two devices is out of this step (DS section 2 item 2). A switch ends the link, waits for the disconnect, then advertises on the new identity (`rdev_plan_next`: disconnect first, advertise when no link).
5. **Pairing with a displayed passkey.** The ring has only `passkey_display` in `bt_conn_auth_cb` (display only, `zephyr/include/zephyr/bluetooth/conn.h` line 2876); `CONFIG_BT_SMP_SC_ONLY=y` (`host/Kconfig` line 658) as FW 7.4 line 722 says; the digits go to `passkey_show`. The HID reports need an authenticated key: `CONFIG_BT_HIDS_DEFAULT_PERM_RW_AUTHEN` (`nrf/subsys/bluetooth/services/Kconfig.hids` line 66; `hids.rst` lines 22-23 name the encrypt variant).
6. **Pairing only while the window is open.** `CONFIG_BT_SMP_APP_PAIRING_ACCEPT=y` (`host/Kconfig` line 638) and `pairing_accept` (`conn.h` line 2854) return `BT_SECURITY_ERR_PAIR_NOT_ALLOWED` outside the window: FW 7.4 line 723.
7. **Outside the window only the bonded device may stay connected.** The ring checks the peer address against the slot's bond when a link opens and drops a stranger. FW 7.3 line 714 asks for the filter accept list; not done (decision 11).
8. **Advertising data carries the HID service**: flags, appearance 961, complete list of 16-bit UUIDs with 0x1812; the name "Ring" is in the scan response. DS "Rules from Apple" line 28. Pairing window: 100 ms interval (FW 7.3 line 715). Reconnect: 100 ms for `CONFIG_RING_DEVICES_FAST_ADV_S` (30) seconds after a drop or switch, then 1,000 ms (FW 7.3 line 714).
9. **Removal deletes the whole bond** with `bt_unpair(slot, peer)`. Zephyr keeps the keys of one pairing (the peer's and the ring's own long term keys, identity and signing keys) in one record, so both sets go together; test C shows the effect on the wire. DS "Rules from Apple" line 30 ("deletes both sets"): this is my reading of that sentence; the notes do not claim to have inspected the key store itself.
10. **HID service and reports.** `BT_HIDS_DEF` and `bt_hids_init` (`nrf/include/bluetooth/services/hids.h` lines 68 and 601); report map with keyboard, consumer control and pointer: the mouse sample's map has a consumer collection at `peripheral_hids_mouse/src/main.c` lines 771-798 (RS section 3); the keyboard sample's map has none, so the map is written by hand. `bt_hids_inp_rep_send` returns `-EACCES` when the device has not switched the report on (`nrf/subsys/bluetooth/services/hids.c` lines 1588-1589), which is what `rctl_action` reports. `CONFIG_BT_GATT_AUTO_SEC_REQ=n` and `CONFIG_BT_AUTO_PHY_UPDATE=n` follow Nordic's mouse sample `prj.conf` (comment about procedure collisions with some computers).
11. **Not done in step 2, by choice:** privacy (resolvable private addresses) and the filter accept list: they need the controller's resolving list and a stand-in host that resolves addresses; the identities are static random addresses. The connection parameter request of FW 7.3 line 718 (30 to 50 ms, latency 4) is not set.
12. **A key is sent only for a real joystick action** (DS section 2 item 3, line 21, and the Apple rule at line 29): `rctl_from_core` maps five actions only; the screen-off wake (`RC_ACT_SCREEN_ON`) gives no key (checked in test A).
13. **The active slot survives a reset** when settings are on (`ring/dev/active`); the development kit configuration turns settings on (`app/boards/nrf54lm20dk_nrf54lm20a_cpuapp.conf`); the simulated builds keep bonds in RAM.
14. **The test host is the SDK's HID client** (`bt_hogp`, `nrf/include/bluetooth/services/hogp.h`; usage as in `central_hids/src/main.c` lines 425-481 and 1019-1050), not a hand-made GATT client. Its expected values are literals in `host_app/src/main.c`, separate from the ring's headers.

## 4. What the simulation does not prove

- Nothing was tried with a real iPhone, Android phone or Mac. iOS may refuse or ignore parts of the report map (consumer usages, relative pointer without AssistiveTouch: DS section 2 item 3), may ask for the keyboard LED output report, or may start pairing differently. Android and macOS behaviour with the three-report map is also unknown.
- Radio timing: the simulated connection interval, the 4 to 5 s a simulated passkey pairing takes at a 100 ms interval, and the 100 ms to 1,000 ms advertising behaviour are simulator values. The 1,000 ms advertising phase (after the first 30 s) is not exercised by the tests; neither is the 60 s window timeout, a pairing that fails, a wrong passkey, a refused pairing outside the window, or a pairing request while all three slots are full.
- The ring never sees the moment a reconnected host has switched its reports on again (the switches are restored from the bond), so test B waits 3 s after the link is ready. A real phone may need longer; keys sent too early are lost.
- Settings (bonds and the active slot kept across a reset) are built for the development kit only; no test restarts the ring.
- Privacy and the accept list (decision 11) are untested because absent.
- Real encryption is on in the simulation (`-RealEncryption=1`); BabbleSim's radio timing is still a model.

## 5. What FW section 7 must change (for F7)

1. 7.1: add the HID over GATT service (0x1812) to the services; one connection at a time stays; "the link protocol is being specified separately" line no longer the only Bluetooth text: standard keyboard, media remote and pointer come first (DS section 2 item 1).
2. 7.2: add the HID service with its report map (ID 1 keyboard 8 bytes, ID 2 consumer 2 bytes, ID 3 pointer 3 bytes, input only, report protocol only) and its permission: authenticated and encrypted (security level 4 with LE Secure Connections only). The ring service table is untouched by this step.
3. 7.3: advertising data = flags, appearance 961, HID service UUID; the name is in the scan response and is "Ring" (the "plus last 4 hex digits of the device id" of F6 is not built); pairing window 100 ms; after a drop or switch 100 ms for 30 s, then 1,000 ms; the window now belongs to a slot (identity), not to the ring as a whole.
4. 7.4: bonds are 3, not 2 (`CONFIG_BT_MAX_PAIRED=3`, `CONFIG_BT_ID_MAX=3`); the "third pairing asks on SCR_CONFIRM to remove the oldest bond" line becomes "a fourth pairing is refused (`-ENOSPC`) until the wearer removes one"; a pairing is made on the identity of a free slot and becomes the active device; removal of a pairing is a wearer action that deletes the bond and ends the link; add a "device picker" action: switch the active device (disconnect, change identity, advertise).
5. 7.4: "only bonded devices may connect (filter accept list)" and "Privacy on, RPA 900 s" are not met by this step (decision 11): either keep them as requirements for a later step or relax them; the ring checks the bond address at connection time instead.
6. New text (7.5 or a new section): the four control modes and their tables (section 2 here), the rule that the control uses only the five screen actions and never the centre long press, and that a held direction repeats.
7. Add "Bluetooth cannot start or stop a recording" also for HID: no HID report is ever read as a command (the ring has no output report).

## 6. How to run, and results

All from the project folder on the Mac; `RING_REMOTE_SRC=/root/ring-os/src-step2` keeps my copy apart; `RING_LOG_DIR` chooses the log folder.

| What | Command | Last line (final run) |
|---|---|---|
| everything (the bar) | `sh firmware/tools/remote.sh step2-all "tools/build_all.sh"` | `RESULT PASS` (`step2/20261111-133920-step2-all-final.log`, exit 0) |
| logic suites on native_sim | `west twister -T tests/control -T tests/devices -p native_sim` (in build_all stage 3) | `ring_control.logic` 7 of 7, `ring_devices.logic` 7 of 7 passed |
| two-device tests A, B, C | `sh firmware/tools/remote.sh bsim-control "tests/bsim/control/run.sh"` (one test: `... run.sh A`) | `RESULT PASS` after `TEST A RESULT PASS (72 checks passed)`, `TEST B RESULT PASS (43 checks passed)`, `TEST C RESULT PASS (28 checks passed)` |
| broken copy must fail A | `sh firmware/tools/remote.sh bsim-broken "tests/bsim/control/run.sh --broken"` | `TEST A RESULT FAIL (71 checks passed; host1-result 1-failed-checks)`, then `broken copy: test A failed as required`, `RESULT PASS` |
| logic suites can fail | `sh firmware/tools/remote.sh control-broken "tests/control/broken_run.sh"` and `devices-broken "tests/devices/broken_run.sh"` | `RESULT PASS` (the broken copy failed `test_mode_tables`, `test_switch_decision`; `step2/20261111-133801-mut.log`) |

Each device prints `RING CHECK <name> PASS|FAIL` or `HOST H<n> CHECK <name> PASS|FAIL` per check and one `RING RESULT ...` or `HOST H<n> RESULT ...` line; `run.sh` prints `TEST <s> RESULT PASS|FAIL` per test and one final `RESULT` line. A test passes only when the phy and every device exit 0, every device's RESULT is PASS, no check line says FAIL, and the ring finished its script before the host evaluated (`ring script done at ... ms, host 1 evaluated at ... ms`).

What each test does (simulated time):
- **A** (ring + host 1): the pairing window opens; the host pairs with the passkey the ring shows (the ring writes it to a file the host reads: no screen yet) and reaches security level 4; then the test hook injects switch edges into the real core for each of the five actions in media, presenter (arrows), presenter (Page keys), pointer and agent; the host checks every report and its release against its own literal table (25 steps), a pointer right held 1.1 s repeats (4 or more reports), a direction with the screen off sends nothing, a centre double press sends nothing, then the host ends the link at 40 s and reconnects by itself and one more key arrives.
- **B** (ring + two hosts): host 1 pairs on slot 0 and gets 2 keys; the ring opens the window for slot 1, host 2 pairs and gets 2 keys while host 1 gets none; `rdev_switch(0)`: host 1 reconnects and gets 2 keys, host 2 none; `rdev_switch(1)`: host 2 gets 1 key; host totals are compared at the end (host 1: 4 steps, host 2: 3 steps, nothing extra); three distinct identity addresses; a switch to an empty slot is refused.
- **C** (ring + host): pair, one key, `rdev_remove(0)` (link ends, bond gone, no active device); the host with its old keys reconnects once the window is open and the ring refuses it (`security failed err 2`, pin or key missing); a key sent while no one is paired is not sent (`-ENOTCONN`); the host drops its old keys, pairs again with a new passkey and receives a key.

Resources (development kit, `nrf54lm20dk/nrf54lm20a/cpuapp`, sysbuild with MCUboot; `step2-all-final.log` lines 851-857): app FLASH 159,460 B (16.36% of 974,704 B), RAM 34,452 B (6.58% of 511 KB); MCUboot unchanged at FLASH 45,656 B, RAM 21,968 B. The skeleton before this step was FLASH 34,304 B, RAM 6,024 B (`infra-notes.md`). The size is with the SoftDevice Controller, the HID service, the pairing code and the core; no figures were found for the parts separately.

Core tests: `ring_core.logic` passes with 216 cases on native_sim and on the simulated chip (`step2/console-counts.txt`, read from the `twister.json` files of the final run; the brief said 214, the core has grown by 2).

### 6.1 Problems met

1. **Pairing completes on the simulated nRF54LM20A with real encryption (corrected in round 2).** Earlier runs failed on `nrf54lm20bsim/nrf54lm20a/cpuapp` (and `nrf54l15bsim`): the first encrypted packet failed its MIC check, disconnect reason 0x3d (`step2/console-peek.txt`, `step2/20261111-131822-peek5.log`). The cause was BabbleSim's default plain-text mode, not the chip model as a whole and not our code: with `-RealEncryption=1` on the ring and host command lines (and `LD_LIBRARY_PATH=/ws/tools/bsim/lib` on those two lines only, for `libCryptov1.so`) the same tests pass (`docs/nrf54-pairing-probe.md`, measured by another helper). `tests/bsim/control/run.sh` now uses that board and flag by default; round 2 run: `step2/20261111-214828-r2-all3.log`, tests A 76, B 44, C 28, D 31, F 22, T 22 checks passed on `nrf54lm20bsim/nrf54lm20a/cpuapp`, `RESULT PASS`. My earlier statements that the nRF54 radio and encryption models cannot finish a pairing, and the suspicion about the CCM model, were wrong for real-encryption mode. `CTRL_BOARD=nrf52_bsim/native` selects the simulated nRF52 (not run in round 2: the first round ran it, `step2/20261111-133920-step2-all-final.log`).
2. The first version of test B passed too early: after `rdev_pair_open(1)` the old link of slot 0 was still up, so `rctl_ready()` was true. `wait_ready` now waits for the expected slot to be active.
3. After a reconnect the host's notification switches are restored from the bond, so the ring sees "ready" before the host's client is ready again and the first keys were lost (test B, reports of the switch back). Now a 3 s wait; see section 4.
4. twister cannot run a test of several simulated devices; the two-device tests are a stage of `build_all.sh` (section 7).
5. `tests/core` counted 216, not 214 (section 6).

## 7. Files changed outside my own folders (smallest change)

- `firmware/tools/build_all.sh`: header comment line for stage 4, and a new "Stage 4" block before the final `echo "build_all: logs in $OUT"`: for every `tests/bsim/<name>/run.sh` it runs the script (stage `bsim-<name>`) and, when the script mentions `--broken`, runs it again with `--broken` (stage `bsim-<name>-broken`); failures add `bsim-<name>` to the failed list. Nothing else in the file changed.
- `firmware/app/CMakeLists.txt`: a loop that adds `modules/ring_devices` and `modules/ring_control` to `ZEPHYR_EXTRA_MODULES` when their `zephyr/module.yml` exists (same rule as ring_core).
- `firmware/app/prj.conf`: Bluetooth peripheral, SMP (LE Secure Connections only), HID service, `BT_MAX_PAIRED=3`, `BT_ID_MAX=3`, `RING_CORE`, `RING_DEVICES`, `RING_CONTROL`.
- `firmware/app/Kconfig`: option `RING_PAIR_WINDOW_AT_BOOT` (default off), a stand-in for the pairing screen on the development kit.
- `firmware/app/boards/nrf54lm20dk_nrf54lm20a_cpuapp.conf` (new): settings on for the kit.
- `firmware/app/src/main.c`: calls `rctl_init()` and `rdev_init()` after the start line (the start line is unchanged and still first).

## 8. Not done, and open points

- Test D to F ideas: pairing refused outside the window, wrong passkey, window timeout, the 1,000 ms advertising phase, reset with settings (section 4).
- The pairing screen, the device picker, the mode choice and the joystick source do not exist yet; `rctl_core_actions` is ready for the place where the core's actions are handled.
- Section 6.1 item 1 is open for the owner of the simulator.

## 9. Round 2 changes (answers to the independent review; details in `step2-round2.md`)

- **One shared glue module** `modules/ring_glue/` (`rglue.h`): joystick edge, core, control, recording hook. The product application (`app/src/main.c`) and the test ring application (`tests/bsim/control/ring_app/src/main.c`) both run it; no copy stays in the test app. A tick thread runs the core's deadlines. The recording hook (`rglue_ops.action`) receives every action in order; the recorder part will act on `RC_ACT_OPEN` and `RC_ACT_CLOSE` there.
- **Control active switch**: `rctl_set_active()`; off at start. A core action becomes a key only through `rctl_core_filter()` (control active and one of the five screen actions). The screens part sets it while a control screen is shown, so a menu move never types on the host.
- **Security level 4** is the gate for sending (`rdev.c` `on_security_changed`, `rdev_active_conn`), as FW 7.4 says.
- **Key release is retried**: when the release report of a key fails to send, it is retried every 50 ms up to 20 times; the next action waits (`-EBUSY`) until it is out; if the link is gone the host drops the key with the link (`rctl.c`).
- **Switch window**: `rdev_link_usable()` (pure, `rdev_logic.c`) allows keys only on an authenticated link of the active device.
- **A fourth mode, "agent", is a deviation from the three modes of the plan and of DS section 2 item 3** (the plan and DS say three: media, presenter, pointer). It stays at the owner's words "You can even control claude code with it": right Return (accept), left Escape (decline), up and down arrow keys, centre Return, keys only, no text. For the lead to write into the design (DS section 2 item 3 and the FW control text): four modes.
- **Two devices at the same time**: tried once (test T, `tests/bsim/control/trial_app`): two hosts paired on identities 0 and 1 and linked together; each received only its own keys. It holds in the simulation. It is not wired into the product: the product's plan keeps one link; holding two needs a decision on which device gets the keys and which gets notifications (step 3).
- **Recording state**: in `RECORDING` a short centre press is a highlight (core), so play or pause, click and Return do nothing while recording; the centre hold still starts and stops it (test D).

## 10. Text for the F7 Bluetooth section (ready to paste; section 7 of `design/firmware.md`)

> ### 7.1 Stack and role
> Peripheral role only, one connection at a time (a trial with two simultaneous links holds in simulation but is not part of F7). Zephyr Bluetooth host with the nRF Connect SDK SoftDevice Controller. LE Secure Connections only. HID over GATT first: the ring is a Bluetooth keyboard, media remote and pointer to the active device.
>
> ### 7.2 Services
> HID service 0x1812 (`CONFIG_BT_HIDS`): report map with three input reports, no output report, no boot protocol: ID 1 keyboard (8 bytes), ID 2 consumer control (2 bytes, one 16-bit usage), ID 3 pointer (3 bytes: button 1, dx, dy). Every report characteristic needs an authenticated, encrypted link (security level 4; `CONFIG_BT_HIDS_DEFAULT_PERM_RW_AUTHEN`). A host write to the HID control point is counted and has no effect; no HID report is a command. Battery, Device Information and the ring service stay as in F6 (not built by step 2).
>
> ### 7.3 Advertising
> Advertising data: flags, appearance 961 (HID keyboard), complete list of 16-bit service UUIDs with 0x1812. The complete local name "Ring" is in the scan response (the "plus last 4 hex digits" and the ring service UUID are not in step 2). Intervals: pairing window 100 ms; after a drop, a switch or a boot with a paired device 100 ms for 30 s (`CONFIG_RING_DEVICES_FAST_ADV_S`), then 1,000 ms. The ring advertises on the local identity of the slot it is connecting to: identity n for slot n. Advertising per core state (none in `SHIP`, `OFF`, `BOOT`, `RECOVERY`, `CHARGING`, `TRANSFER`, `ERR_CHARGER`, `FACTORY_TEST`) is not built: the devices part does not read the state yet. Connection parameters (30 to 50 ms, latency 4, supervision 4 s), TX power, data length and ATT MTU are not set in step 2.
>
> ### 7.4 Pairing, bonding, security
> LE Secure Connections only (`CONFIG_BT_SMP_SC_ONLY`), IO capability display only: the ring shows a six-digit passkey (given to the screen through `passkey_show`), the phone user types it; the result is an authenticated, encrypted link, security level 4. Pairing is accepted only while the pairing window is open (60 s, for one free slot; `CONFIG_BT_SMP_APP_PAIRING_ACCEPT`); outside it a pairing request is refused. Up to three paired devices (`CONFIG_BT_MAX_PAIRED=3`, `CONFIG_BT_ID_MAX=3`), one local identity and one bond per device, stored with Zephyr settings. A fourth pairing is refused until the wearer removes one: no bond is removed automatically. Removing a pairing deletes its bond (the keys of both sides) and ends its link. One device is active; switching it ends the link, changes the identity and advertises to the chosen device; a key is sent only over an authenticated link of the active device.
> Filter accept list and privacy: not built in step 2. Instead, when a link opens outside the pairing window, the ring checks the peer address against the slot's bond and drops a stranger. This works with the fixed (static random) identity addresses of the simulation; it is not shown to work with resolvable private addresses, which real phones use. `CONFIG_BT_FILTER_ACCEPT_LIST` and `CONFIG_BT_PRIVACY` (resolvable address renewed every 15 minutes) remain requirements for the step that has a real chip or a controller model with a resolving list.
>
> ### 7.5 Control modes
> Four modes (the plan's three and the owner's "agent"): media, presenter (Page keys option), pointer, agent; tables in `rctl_modes.h`. Control uses only the five joystick actions of the screen shown (centre short, four directions), only while a control screen is shown, and never the centre long press, which belongs to recording in every mode. A held direction repeats through the core (500 ms, then every 150 ms). Every key press is followed by its release report; a failed release is retried.

## 11. Round 3 notes

- **The 1 s "busy" drop is by design.** While the release report of a key waits to be sent (the send failed), the wearer's next action is refused (`-EBUSY`) for at most `RCTL_RETRY_MAX` x `RCTL_RETRY_MS` = 20 x 50 ms = 1 s, then the wait ends. Why: a new press must never go out before the old key is up, or the host's key state is wrong. The rule is the pure `struct rctl_wait` in `rctl_report.h`; test `test_release_wait_wearer_side` (`tests/control/src/test_control.c`): an action during the wait is refused, the next one after the release passes, and the wait cannot block for ever.
- **`rglue_input()` is for thread context only** (`rglue.h`): it holds a mutex while reports are sent.
- **Three devices over Bluetooth:** test G (three hosts pair in turn on slots 0, 1, 2; the ring switches to each; each gets its own key and the others none; a fourth pairing is refused: `rdev_pair_open(RDEV_ANY)` returns `-ENOSPC`, and a fourth host that tries gets no bond).
- **`rdev.c` `on_connected`:** the `disconnecting` flag is set only when `bt_conn_disconnect` succeeded, so `update_fn` retries a failed call; after a `bt_conn_get_info` error the link is ended and `update_fn` is asked again so advertising restarts. The second path is not reachable in a test (`bt_conn_get_info` does not fail on a live link in the simulation): checked by reading only.

RESULT: done, ring_devices, ring_control and the new ring_glue are proven by logic suites, tests A, B, C, D, F and T and eight broken copies with build_all RESULT PASS on the simulated nRF54LM20A with real encryption.
