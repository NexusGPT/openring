"""Read-only check of citations in recorder-notes.md section "Fix round 1".
Each entry: (id, file, first line, last line, text the notes say is there). A citation matches when the text occurs in
the cited line range of the pinned export (code) or of the log on disk. Usage:
python3 -I citecheck.py <SRC/firmware> <build-logs/step6>"""
import pathlib
import sys

fw = pathlib.Path(sys.argv[1])
logs = pathlib.Path(sys.argv[2])
M = "modules/ring_recorder/src/"
C = [
    # code citations (notes FR1.1, FR1.2)
    ("c01 rrec.c:462 ship_pending", fw / (M + "rrec.c"), 462, 462, "rrec_st.ship_pending = true"),
    ("c02 rrec.c:668 RREC_JOB_SHIP posted", fw / (M + "rrec.c"), 668, 668, "rrec_post(RREC_JOB_SHIP"),
    ("c03 rrec.c:350 rrec_ship_now", fw / (M + "rrec.c"), 350, 350, "void rrec_ship_now(void)"),
    ("c04 rrec.c:352 wait bound", fw / (M + "rrec.c"), 352, 352, "RREC_PAT_M2_MS + SHIP_M2_MARGIN_MS"),
    ("c05 rrec.c:44 SHIP_M2_MARGIN_MS 100", fw / (M + "rrec.c"), 44, 44, "SHIP_M2_MARGIN_MS 100"),
    ("c06 rrec_spec.h:329 RREC_PAT_M2_MS", fw / "modules/ring_rhw/include/ring_rhw/rrec_spec.h", 329, 329, "RREC_PAT_M2_MS                280u"),
    ("c07 rrec_spec.h:448 0x0290", fw / "modules/ring_rhw/include/ring_rhw/rrec_spec.h", 448, 448, "RREC_LOG_UNMOUNT_FAILED = 0x0290"),
    ("c08 rrec.c:273-324 unmount_now", fw / (M + "rrec.c"), 273, 324, "static int unmount_now(void)"),
    ("c09 rrec.c:395 rrec_unmount_retry", fw / (M + "rrec.c"), 395, 395, "void rrec_unmount_retry(void)"),
    ("c10 rrec.c:454 SD_OFF unmount_now", fw / (M + "rrec.c"), 454, 454, "(void)unmount_now();"),
    ("c11 rrec.c:533 ABORT waits rxf_finish", fw / (M + "rrec.c"), 533, 533, "rxf_finish(FINISH_WAIT_MS)"),
    ("c12 rrec.c:503 FINISH rxf_finish", fw / (M + "rrec.c"), 503, 503, "rxf_finish(FINISH_WAIT_MS)"),
    ("c13 rrec.c:533 hfxo_wanted", fw / (M + "rrec.c"), 533, 533, "static bool hfxo_wanted"),
    ("c14 rrec.c:538 rrec_hfxo_follow_state", fw / (M + "rrec.c"), 538, 538, "void rrec_hfxo_follow_state"),
    ("c15 rrec_boot.c:52 HFXO at boot start", fw / (M + "rrec_boot.c"), 52, 52, "rrec_hfxo_follow_state(RC_ST_BOOT)"),
    ("c16 rrec_bridge.c:40-87 latch", fw / (M + "rrec_bridge.c"), 40, 87, "atomic_or(&latched"),
    ("c17 rrec_bridge.c:89-103 latch_flush", fw / (M + "rrec_bridge.c"), 89, 103, "static void latch_flush(void)"),
    ("c18 rrec_bridge.c:108 rrec_idle waits latch", fw / (M + "rrec_bridge.c"), 108, 108, "atomic_get(&latched) == 0"),
    ("c19 rrec_bridge.c:158-166 run_retry", fw / (M + "rrec_bridge.c"), 158, 166, "already mounted"),
    ("c20 rrec_bridge.c:180-183 100 ms latch look", fw / (M + "rrec_bridge.c"), 180, 183, "K_MSEC(100)"),
    ("c21 rrec_int.h:80 atomic_t test_recording", fw / (M + "rrec_int.h"), 80, 80, "atomic_t test_recording"),
    ("c22 rrec_int.h:147-150 test read-outs", fw / (M + "rrec_int.h"), 147, 150, "rrec_test_set_ship_hook"),
    ("c23 rscr.c:544-551 sync before start", fw / "modules/ring_screens/src/rscr.c", 544, 551, "if (!started)"),
    ("c24 rscr.c:534 power_off", fw / "modules/ring_screens/src/rscr.c", 534, 534, "ops->power_off()"),
    ("c25 rst.h:143-147 rst_unmount_wait", fw / "modules/ring_store/include/ring_store/rst.h", 143, 147, "int rst_unmount_wait(int32_t timeout_ms);"),
    ("c26 rst.c:467-512 unmount_locked", fw / "modules/ring_store/src/rst.c", 467, 512, "static int unmount_locked(void)"),
    ("c27 rxf.h:91-95 rxf_stop", fw / "modules/ring_xfer/include/ring_xfer/rxf.h", 91, 95, "int rxf_stop(int32_t timeout_ms);"),
    ("c28 rxf_class.c:353-371 rxf_stop body", fw / "modules/ring_xfer/src/rxf_class.c", 353, 371, "int rxf_stop(int32_t timeout_ms)"),
    ("c29 rdev.h:85-89 rdev_stop", fw / "modules/ring_devices/include/ring_devices/rdev.h", 85, 89, "int rdev_stop(void);"),
    ("c30 rdev.c:498-514 rdev_stop body", fw / "modules/ring_devices/src/rdev.c", 498, 514, "int rdev_stop(void)"),
    ("c31 rau.c:324 clear_state waits", fw / "modules/ring_audio/src/rau.c", 324, 324, "k_sem_take(&halt_sem"),
    ("c32 rmo.c:95-112 F2 guard", fw / "modules/ring_motor/src/rmo.c", 95, 112, "#ifdef CONFIG_RING_RHW_SIM"),
    ("c33 factory common.c:134 ticks", fw / "tests/factory/src/common.c", 134, 134, "k_uptime_ticks()"),
    ("c34 factory common.h:56 ticks", fw / "tests/factory/src/common.h", 56, 56, "fx_frame_ticks"),
    ("c35 test_screen.c:205-216 spacing in us", fw / "tests/factory/src/test_screen.c", 205, 216, "us >= 1000000 && us < 1001000"),
    ("c36 test_rails.c:6-10 header", fw / "tests/recorder/src/test_rails.c", 6, 10, "HFXO on in BOOT and RECOVERY (l.915)"),
    # log citations (notes FR1.3, FR1.4, FR1.6)
    ("l01 u2 l.7535 UNIT PASS", logs / "fix1-rec-u2.log", 7535, 7535, "UNIT PASS tests/recorder tests/store tests/xfer tests/audio tests/motor tests/devices tests/factory tests/screens"),
    ("l02 u2 l.7678 ship_feels_whole_m2", logs / "fix1-rec-u2.log", 7678, 7678, "recorder_ship.ship_feels_whole_m2 passed"),
    ("l03 u2 l.7999 ship_feels_whole_m2 chip", logs / "fix1-rec-u2.log", 7999, 7999, "recorder_ship.ship_feels_whole_m2 passed"),
    ("l04 u2 l.607 copy ship_cuts_m2", logs / "fix1-rec-u2.log", 607, 607, "ship_cuts_m2"),
    ("l05 u2 l.684 copy unmount_result_dropped", logs / "fix1-rec-u2.log", 684, 684, "unmount_result_dropped"),
    ("l06 u2 l.725 copy no_hfxo_in_boot", logs / "fix1-rec-u2.log", 725, 725, "no_hfxo_in_boot"),
    ("l07 u2 l.768 copy close_drops_partial", logs / "fix1-rec-u2.log", 768, 768, "close_drops_partial"),
    ("l08 u2 l.810 copy test_recording_wrong_type", logs / "fix1-rec-u2.log", 810, 810, "test_recording_wrong_type"),
    ("l09 u2 l.642 copy ship_screen_on", logs / "fix1-rec-u2.log", 642, 642, "ship_screen_on"),
    ("l10 u2 l.7669 hfxo case", logs / "fix1-rec-u2.log", 7669, 7669, "recorder_rails.hfxo_in_boot_and_recovery passed"),
    ("l11 u2 l.7654 close_order", logs / "fix1-rec-u2.log", 7654, 7654, "recorder_actions.close_order passed"),
    ("l12 u2 l.7683 tmic", logs / "fix1-rec-u2.log", 7683, 7683, "recorder_factory.tmic_records_type_2_for_2s passed"),
    ("l13 u2 l.7676 battery screens", logs / "fix1-rec-u2.log", 7676, 7676, "recorder_screens.battery_reaches_screens passed"),
    ("l14 u2 l.8423 dk build exit 0", logs / "fix1-rec-u2.log", 8423, 8423, "dk build exit 0"),
    ("l15 u2 l.8425 F2 warnings 0", logs / "fix1-rec-u2.log", 8425, 8425, "F2 warnings: 0"),
    ("l16 u2 l.7579 11 tries", logs / "fix1-rec-u2.log", 7579, 7579, "11"),
    ("l17 u2 l.6301 factory copy failed cases", logs / "fix1-rec-u2.log", 6301, 6301, "factory_motor.test_reads_and_timing"),
    ("l18 u3 l.804 UNIT PASS tests/recorder", logs / "fix1-rec-u3.log", 804, 804, "UNIT PASS tests/recorder"),
    ("l19 u3 l.802 RESULT PASS", logs / "fix1-rec-u3.log", 802, 802, "RESULT PASS"),
    ("l20 u3 l.806 record 1", logs / "fix1-rec-u3.log", 806, 806, "unmount: record 1: errno -16, state TRANSFER, try 1"),
    ("l21 u3 l.807 record 2", logs / "fix1-rec-u3.log", 807, 807, "unmount: record 2: errno 0, state CHARGING, try 6"),
    ("l22 u3 l.808 2 records", logs / "fix1-rec-u3.log", 808, 808, "unmount: 2 records 0x0290"),
    ("l23 u3 l.665 copy unmount_result_dropped", logs / "fix1-rec-u3.log", 665, 665, "unmount_result_dropped"),
    ("l24 u3 l.22 53 of 53", logs / "fix1-rec-u3.log", 22, 22, "53 of 53 executed test cases passed"),
    ("l25 c1 l.936 RESULT PASS", logs / "fix1-rec-c1.log", 936, 936, "RESULT PASS"),
    ("l26 c1 l.372 TEST C", logs / "fix1-rec-c1.log", 372, 372, "TEST C RESULT PASS (31 checks passed)"),
    ("l27 c1 l.365 no advertising", logs / "fix1-rec-c1.log", 365, 365, "HOST H1 CHECK C: no advertising after ship close PASS"),
    ("l28 c2 l.92 copy fails", logs / "fix1-rec-c2.log", 92, 92, "HOST H1 CHECK C: no advertising after ship close FAIL"),
    ("l29 c2 l.101 RESULT PASS", logs / "fix1-rec-c2.log", 101, 101, "RESULT PASS"),
    ("l30 r613a l.83 frame_sequence failed", logs / "fix1-rec-r613a.log", 83, 83, "factory_screen.test_frame_sequence"),
]
ok = 0
for cid, path, a, b, want in C:
    try:
        lines = path.read_text(errors="replace").split("\n")
    except OSError as e:
        print(f"MISS {cid}: cannot read {path.name}: {e}")
        continue
    seg = "\n".join(lines[a - 1:b])
    if want in seg:
        ok += 1
        print(f"MATCH {cid}: {path.name}:{a}-{b}: {lines[a - 1].strip()[:160]}")
    else:
        hit = [i + 1 for i, l in enumerate(lines) if want.split(chr(10))[0] in l]
        print(f"MISS {cid}: {path.name}:{a}-{b} holds {seg.strip()[:160]!r}; the text is at lines {hit[:5]}")
print(f"TOTAL {ok} of {len(C)} citations match")
