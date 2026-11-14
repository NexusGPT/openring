diff --git a/firmware/README.md b/firmware/README.md
index 6cab3612..d75338d3 100644
--- a/firmware/README.md
+++ b/firmware/README.md
@@ -68,7 +68,8 @@ main chip from `design/ecad/ring/netlist.csv`, the power chip nPM1304 with its t
 card on `spi00`, the microphones on `pdm20`, the screen's bus on `spi21`, USB, watchdog, the 1 KB crash record in
 retained RAM, the flash layout of `design/firmware.md` 9.2; a cell model for the fuel gauge that is NOT THE RING'S
 CELL (Nordic's 20 mAh sample, a stand-in); a copy of the netlist, which `tools/remote.sh` compares with
-`design/ecad/ring/netlist.csv` before every run, refusing to run when they differ), the application's settings for it
+`design/ecad/ring/netlist.csv` before every run where that file exists two folders above `firmware/`, refusing to run
+when they differ or when no sha256 can be made; in an export of `firmware/` alone it says the comparison was skipped), the application's settings for it
 (`app/boards/ringrec_nrf54lm20a_cpuapp.conf` and `.overlay`), the production settings without the debug port
 (`app/ringrec_production.conf`, `boards/ringrec/ringrec_production.overlay` and `_mcuboot.conf`), and
 `tools/check_ring_pins.py`, which compares the built devicetree with the netlist. Notes: `docs/board-notes.md`.
@@ -97,7 +98,7 @@ step (no key is changed here).
 | `modules/ring_screens/` | step 4: the screens. `rscr_logic.c` (pure: which screen for which state and input), `rscr_draw.c` (LVGL, 240 x 120 frame turned for the 120 x 240 panel), `rscr.c` (the screens thread), `rscr_real.c` (calls the real other modules), `memdisplay.c` (the memory display driver that stands in for the panel), `rscr_capture.c` (test hook: PNG from the frame the driver received) |
 | `modules/ring_relay/` | step 5: the relay service (design/firmware.md 7.7). `rrl.c` (pure: frames, record parser, refusal decisions), `rrl_bt.c` (the GATT service, one session per link, the queue for Out); the one store is the iPhone part's (`rip_relay_*` in `ring_iphone/rip.h`) |
 | `modules/ring_rhw/` | step 6: the driver interfaces (`rhw.h`), the numbers of the specification (`rrec_spec.h`), the simulated drivers (`CONFIG_RING_RHW_SIM`, on for the simulated chip, off for the development kit) |
-| `modules/ring_store/`, `ring_audio/`, `ring_xfer/`, `ring_power/`, `ring_motor/`, `ring_sys/`, `ring_factory/` | step 6: storage, microphones, USB transfer, power, motor, system (update, crash, watchdog, saved time), factory tests; each has a pure part and a thin part; the real driver files (`*_hw_real.c`) build for the development kit (most of them empty there: no node) and for the ring board (step 7, real code), and are not proven |
+| `modules/ring_store/`, `ring_audio/`, `ring_xfer/`, `ring_power/`, `ring_motor/`, `ring_sys/`, `ring_factory/` | step 6: storage, microphones, USB transfer, power, motor, system (update, crash, watchdog, saved time), factory tests; each has a pure part and a thin part; the real driver files (`*_hw_real.c`) build for the development kit (what they contain there was not measured in step 7) and for the ring board (step 7: real code in each, `ring-drivers` stage of `tools/build_all.sh`), and are not proven |
 | `modules/ring_recorder/` | step 6: the recorder (the join): the core's actions through the parts above, the boot sequence, `rec_mics_on()` (the one path to the microphone supply), the USB backend; the product's glue ops are in `app/src/main.c` |
 | `tests/recorder/` | the recorder's suites with the real core, glue, screens and every step 6 part on the simulated drivers (`broken_run.sh`, `short_run.sh`, `stages_run.sh`) |
 | `tests/relay/` | the relay's logic suite (`ring_relay`, native_sim and the simulated chip); `broken_run.sh` |
