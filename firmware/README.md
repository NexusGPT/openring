# Ring firmware

Firmware for the smart ring on the Nordic nRF54LM20A chip, on nRF Connect SDK
v3.4.2 (Zephyr). Design: `design/software/os/design.md`. Built so far: the core
(step 1), devices and control (step 2), the iPhone part and the inbox (step 3,
`docs/iphone-notes.md`), the screens (step 4, `docs/screens-notes.md`), the relay
service for an Android helper app (step 5, `docs/relay-notes.md`), the recorder parts
(step 6: microphones, storage, USB transfer, power, motor, system, factory, and the recorder that joins them,
`docs/step6-plan.md`, `docs/recorder-notes.md`), written against simulated drivers.

## Build and test

Everything is compiled and tested on the Linux build server, inside Nordic's
toolchain image. Nothing runs on the Mac: it holds the source and receives the
logs. From the project folder on the Mac:

```sh
sh firmware/tools/remote.sh build-all "tools/build_all.sh"
```

It copies `firmware/` to the server, builds and tests, streams the output, saves
it to `firmware/build-logs/<date-time>-build-all.log`, and exits with the
server's exit code. The last line is `RESULT PASS` or `RESULT FAIL <stages>`.

`tools/build_all.sh` does three stages:

1. `app/` for the development kit, `nrf54lm20dk/nrf54lm20a/cpuapp`, with
   sysbuild and MCUboot; prints flash and RAM use (the linker's memory report).
2. `app/` for the simulated chip, `nrf54lm20bsim/nrf54lm20a/cpuapp`; runs it for
   2 simulated seconds and checks the line `ring-os start:`, and (step 6) the line
   `ring-os recorder: boot done, state STANDBY`: the product boots through the recorder on the simulated drivers.
3. twister on every test under `tests/` on `native_sim`, and on each simulated
   chip board a test names in its `platform_allow`.
   Step 5 adds: `tests/relay` (the relay's frames and records, logic) and
   `tests/bsim/relay` (the ring against a stand-in helper; also with `--broken`), the stages
   `relay-no-core` and (in `link-settings`) the relay test ring's settings.
   Step 6 adds: the suites `tests/rhw`, `core`, `store`, `audio`, `xfer`, `power`, `motor`, `sys`, `factory`,
   `recorder` and their `broken_run.sh` (they join by their files), and the stages `recorder-one-mic-path`,
   `recorder-no-start-path`, `recorder-no-raw-pins`, `recorder-product-drivers` (each with a self test) and the recorder's
   threads in `stack-report`. The targeted run of one unit: `bash tools/unit_run.sh tests/<name>`
   (`RING_REMOTE_SRC=/root/ring-os/src-u-<name> sh firmware/tools/remote.sh u-<name> "bash tools/unit_run.sh tests/<name>"`).
   Step 4 adds: the screens' pictures (`RING_PICS`) are checked as PNG files and
   listed in `pictures/manifest-<board>.md` by `tools/pictures_manifest.py`; every
   `tests/bsim/<name>/run.sh` runs (control, iphone, screens) with its `--broken`
   copies; every `tests/<name>/broken_run.sh` runs (control, devices, inbox, time,
   iphone, screens).

Other commands:

```sh
sh firmware/tools/remote.sh kit-samples "tools/kit_samples.sh"   # Nordic samples for the chip
sh firmware/tools/remote.sh bsim-hr "tools/bsim_hr_demo.sh"      # two simulated devices
sh firmware/tools/remote.sh -H setup "bash tools/setup_server.sh" # one-time server setup
```

`-H` runs the command on the server itself instead of in the container.
`RING_REMOTE_SRC=/root/ring-os/src-<label>` sends a test copy to its own server
folder, so the shared `/root/ring-os/src` is not changed. `RING_LOG_DIR` sets
where the log is saved.

The simulated chip target at SDK v3.4.2 is `nrf54lm20bsim/nrf54lm20a/cpuapp`
(with the `a`); `nrf54lm20bsim/nrf54lm20/cpuapp` is refused by Zephyr.

## Step 7: the ring's board files

What exists: the Zephyr board `ringrec/nrf54lm20a/cpuapp` (folder `boards/ringrec`: devicetree with every pin of the
main chip from `design/ecad/ring/netlist.csv`, the power chip nPM1304 with its two load switches and charger, the SD
card on `spi00`, the microphones on `pdm20`, the screen's bus on `spi21`, USB, watchdog, the 1 KB crash record in
retained RAM, the flash layout of `design/firmware.md` 9.2; a cell model for the fuel gauge that is NOT THE RING'S
CELL (Nordic's 20 mAh sample, a stand-in); a copy of the netlist, which `tools/remote.sh` compares with
`design/ecad/ring/netlist.csv` before every run where that file exists two folders above `firmware/`, refusing to run
when they differ or when no sha256 can be made; in an export of `firmware/` alone it says the comparison was skipped), the application's settings for it
(`app/boards/ringrec_nrf54lm20a_cpuapp.conf` and `.overlay`), the production settings without the debug port
(`app/ringrec_production.conf`, `boards/ringrec/ringrec_production.overlay` and `_mcuboot.conf`), and
`tools/check_ring_pins.py`, which compares the built devicetree with the netlist. Notes: `docs/board-notes.md`.

How to build it: `tools/build_all.sh` stage 6 (`ring`, then `ring-drivers`, `ring-ram`, `ring-pins`,
`ring-pins-broken`, `ring-production`, `ring-production-check`). By hand, in the container:
`west build -b ringrec/nrf54lm20a/cpuapp --sysbuild -d <out> app -- -DBOARD_ROOT=/ws/firmware`.

What is unproven: everything that needs a ring. It compiles and its pins match the netlist; no ring has run it. The
power part's real file compiles and is on (`CONFIG_RING_POWER_REAL=y`), with a cell model that is NOT THE RING'S CELL;
the screen has no panel driver (the memory display stands in); the joystick has no driver. MCUboot is signed with the
SDK's debug key ("for debug use only and is not secure"): NOT FOR SHIPPING; the production key is made at the factory
step (no key is changed here).

One file is not in the public repository: `boards/ringrec/include/ring_battery_model_20mAh.inc`. It is Nordic's
battery model data file, under Nordic's own licence. To build for the ring board from the public repository, copy it
from the nRF Connect SDK v3.4.2: `nrf/samples/pmic/native/npm13xx_fuel_gauge/src/battery_model_20mAh.inc`, under that
name. It is a stand-in and NOT THE RING'S CELL.

## Where things are

| Path | What |
|---|---|
| `west.yml` | west manifest: sdk-nrf v3.4.2, BabbleSim group on, Matter left out |
| `app/` | the application: devices, control, iPhone part, relay, screens and (step 6) the recorder; starts the core in `BOOT` |
| `modules/ring_core/` | the core logic module; added to the app only when its `zephyr/module.yml` exists |
| `modules/ring_devices/`, `ring_control/`, `ring_glue/` | step 2: pairing and the active device, keys, the glue between joystick, core, control and the iPhone part |
| `modules/ring_inbox/` | step 3: the store of the last 16 notifications (pure logic) |
| `modules/ring_time/` | step 3: the clock (UTC ms and a time-is-set flag; pure record plus a kernel wrapper) |
| `modules/ring_iphone/` | step 3: Apple's Notification Center, Media and Current Time services as a client, and Service Changed; the pure parts are in `ripl.c` |
| `modules/ring_screens/` | step 4: the screens. `rscr_logic.c` (pure: which screen for which state and input), `rscr_draw.c` (LVGL, 240 x 120 frame turned for the 120 x 240 panel), `rscr.c` (the screens thread), `rscr_real.c` (calls the real other modules), `memdisplay.c` (the memory display driver that stands in for the panel), `rscr_capture.c` (test hook: PNG from the frame the driver received) |
| `modules/ring_relay/` | step 5: the relay service (design/firmware.md 7.7). `rrl.c` (pure: frames, record parser, refusal decisions), `rrl_bt.c` (the GATT service, one session per link, the queue for Out); the one store is the iPhone part's (`rip_relay_*` in `ring_iphone/rip.h`) |
| `modules/ring_rhw/` | step 6: the driver interfaces (`rhw.h`), the numbers of the specification (`rrec_spec.h`), the simulated drivers (`CONFIG_RING_RHW_SIM`, on for the simulated chip, off for the development kit) |
| `modules/ring_store/`, `ring_audio/`, `ring_xfer/`, `ring_power/`, `ring_motor/`, `ring_sys/`, `ring_factory/` | step 6: storage, microphones, USB transfer, power, motor, system (update, crash, watchdog, saved time), factory tests; each has a pure part and a thin part; the real driver files (`*_hw_real.c`) build for the development kit (what they contain there was not measured in step 7) and for the ring board (step 7: real code in each, `ring-drivers` stage of `tools/build_all.sh`), and are not proven |
| `modules/ring_recorder/` | step 6: the recorder (the join): the core's actions through the parts above, the boot sequence, `rec_mics_on()` (the one path to the microphone supply), the USB backend; the product's glue ops are in `app/src/main.c` |
| `tests/recorder/` | the recorder's suites with the real core, glue, screens and every step 6 part on the simulated drivers (`broken_run.sh`, `short_run.sh`, `stages_run.sh`) |
| `tests/relay/` | the relay's logic suite (`ring_relay`, native_sim and the simulated chip); `broken_run.sh` |
| `tests/bsim/relay/` | the ring with its screens against a stand-in helper (scenario H) and a stand-in iPhone that also writes relay frames (scenario I); `run.sh`, `--broken` |
| `tests/screens/` | the table (suite `screens_table`) and the drawing with pixel checks and the pictures (suite `screens_draw`), native_sim and the simulated chip; `broken_run.sh` |
| `tests/bsim/screens/` | the ring with its screens against the stand-in iPhone (`run.sh`, `--broken`) |
| `tools/pictures_manifest.py` | checks the PNG files the screens test wrote and lists them |
| `tests/inbox`, `tests/time`, `tests/iphone` | logic suites (native_sim and the simulated ring chip), each with a `broken_run.sh` |
| `tests/bsim/iphone/` | the ring against a stand-in iPhone (`run.sh` N, R, P, L, D; `--broken`) |
| `modules/ring_iphone/ring_iphone_link.conf` | the link and stack settings of the iPhone part: one file added by the product and by the test ring; stage `link-settings` of `tools/build_all.sh` compares the built settings |
| `tests/` | ztest suites run by twister (`tests/smoke` checks the workspace itself) |
| `tools/` | `remote.sh` (Mac), `build_all.sh`, `kit_samples.sh`, `bsim_hr_demo.sh` (container), `setup_server.sh` and `Dockerfile` (server) |
| `build-logs/` | logs saved by `remote.sh` |
| `docs/infra-notes.md` | how the workspace was set up and proven |

On the server: source `/root/ring-os/src`, west workspace `/root/ring-os/ws`
(in the container `/ws`, with the source at `/ws/firmware`), build outputs
`/root/ring-os/ws/out/<run>`, run logs `/root/ring-os/logs`. Image
`ring-os-toolchain:v3.4.2`.

## Not done yet

- The ring's board file (step 7) builds but has not run on a ring.
- Screens are built (step 4) but drawn on a memory display: no panel driver, no Mac notification path. The recorder parts
  (step 6) run on simulated drivers only: no real card, microphone, power chip or USB controller has run (`docs/recorder-notes.md`). The relay service
  (step 5) is built and proven against a stand-in helper only: the helper app itself is not built.
- Nothing has run on real hardware or against a real iPhone: the iPhone part is proven against a stand-in
  that serves Apple's three services (`docs/iphone-notes.md`, "Not built and not proven").
