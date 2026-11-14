diff --git a/firmware/README.md b/firmware/README.md
index 44325b30..6cab3612 100644
--- a/firmware/README.md
+++ b/firmware/README.md
@@ -66,18 +66,22 @@ The simulated chip target at SDK v3.4.2 is `nrf54lm20bsim/nrf54lm20a/cpuapp`
 What exists: the Zephyr board `ringrec/nrf54lm20a/cpuapp` (folder `boards/ringrec`: devicetree with every pin of the
 main chip from `design/ecad/ring/netlist.csv`, the power chip nPM1304 with its two load switches and charger, the SD
 card on `spi00`, the microphones on `pdm20`, the screen's bus on `spi21`, USB, watchdog, the 1 KB crash record in
-retained RAM, the flash layout of `design/firmware.md` 9.2; a stand-in cell model for the fuel gauge; a copy of the
-netlist), the application's settings for it (`app/boards/ringrec_nrf54lm20a_cpuapp.conf` and `.overlay`), and
+retained RAM, the flash layout of `design/firmware.md` 9.2; a cell model for the fuel gauge that is NOT THE RING'S
+CELL (Nordic's 20 mAh sample, a stand-in); a copy of the netlist, which `tools/remote.sh` compares with
+`design/ecad/ring/netlist.csv` before every run, refusing to run when they differ), the application's settings for it
+(`app/boards/ringrec_nrf54lm20a_cpuapp.conf` and `.overlay`), the production settings without the debug port
+(`app/ringrec_production.conf`, `boards/ringrec/ringrec_production.overlay` and `_mcuboot.conf`), and
 `tools/check_ring_pins.py`, which compares the built devicetree with the netlist. Notes: `docs/board-notes.md`.
 
 How to build it: `tools/build_all.sh` stage 6 (`ring`, then `ring-drivers`, `ring-ram`, `ring-pins`,
-`ring-pins-broken`). By hand, in the container:
+`ring-pins-broken`, `ring-production`, `ring-production-check`). By hand, in the container:
 `west build -b ringrec/nrf54lm20a/cpuapp --sysbuild -d <out> app -- -DBOARD_ROOT=/ws/firmware`.
 
 What is unproven: everything that needs a ring. It compiles and its pins match the netlist; no ring has run it. The
-power part's real file does not compile with this kit's fuel gauge library and is off on the ring
-(`CONFIG_RING_POWER_REAL=n`, docs/board-notes.md); the screen has no panel driver (the memory display stands in);
-the joystick has no driver; the cell model is Nordic's 20 mAh sample, not the ring's cell.
+power part's real file compiles and is on (`CONFIG_RING_POWER_REAL=y`), with a cell model that is NOT THE RING'S CELL;
+the screen has no panel driver (the memory display stands in); the joystick has no driver. MCUboot is signed with the
+SDK's debug key ("for debug use only and is not secure"): NOT FOR SHIPPING; the production key is made at the factory
+step (no key is changed here).
 
 ## Where things are
 
@@ -93,7 +97,7 @@ the joystick has no driver; the cell model is Nordic's 20 mAh sample, not the ri
 | `modules/ring_screens/` | step 4: the screens. `rscr_logic.c` (pure: which screen for which state and input), `rscr_draw.c` (LVGL, 240 x 120 frame turned for the 120 x 240 panel), `rscr.c` (the screens thread), `rscr_real.c` (calls the real other modules), `memdisplay.c` (the memory display driver that stands in for the panel), `rscr_capture.c` (test hook: PNG from the frame the driver received) |
 | `modules/ring_relay/` | step 5: the relay service (design/firmware.md 7.7). `rrl.c` (pure: frames, record parser, refusal decisions), `rrl_bt.c` (the GATT service, one session per link, the queue for Out); the one store is the iPhone part's (`rip_relay_*` in `ring_iphone/rip.h`) |
 | `modules/ring_rhw/` | step 6: the driver interfaces (`rhw.h`), the numbers of the specification (`rrec_spec.h`), the simulated drivers (`CONFIG_RING_RHW_SIM`, on for the simulated chip, off for the development kit) |
-| `modules/ring_store/`, `ring_audio/`, `ring_xfer/`, `ring_power/`, `ring_motor/`, `ring_sys/`, `ring_factory/` | step 6: storage, microphones, USB transfer, power, motor, system (update, crash, watchdog, saved time), factory tests; each has a pure part and a thin part; the real driver files (`*_hw_real.c`) build only for the development kit and are not proven |
+| `modules/ring_store/`, `ring_audio/`, `ring_xfer/`, `ring_power/`, `ring_motor/`, `ring_sys/`, `ring_factory/` | step 6: storage, microphones, USB transfer, power, motor, system (update, crash, watchdog, saved time), factory tests; each has a pure part and a thin part; the real driver files (`*_hw_real.c`) build for the development kit (most of them empty there: no node) and for the ring board (step 7, real code), and are not proven |
 | `modules/ring_recorder/` | step 6: the recorder (the join): the core's actions through the parts above, the boot sequence, `rec_mics_on()` (the one path to the microphone supply), the USB backend; the product's glue ops are in `app/src/main.c` |
 | `tests/recorder/` | the recorder's suites with the real core, glue, screens and every step 6 part on the simulated drivers (`broken_run.sh`, `short_run.sh`, `stages_run.sh`) |
 | `tests/relay/` | the relay's logic suite (`ring_relay`, native_sim and the simulated chip); `broken_run.sh` |
