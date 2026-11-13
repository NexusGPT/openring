"""Edits for tests/recorder/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_recorder copy folder>
Prints "<named case> <suite file>". One named fault per variant; the edit must match exactly once. The variants are those
of firmware/docs/step6-plan.md, unit J "Broken copies", and the six of fix round 1 (review findings R6-01 to R6-06)."""
import pathlib
import sys

MICS = "src/rrec_mics.c"
REC = "src/rrec.c"
BOOT = "src/rrec_boot.c"
BRIDGE = "src/rrec_bridge.c"
BACKEND = "src/rrec_backend.c"
V = {
    # rec_mics_on switches VDD_MIC on before the sign is drawn
    "mic_before_sign": (MICS, "recorder_sign.test_start_draws_sign_before_mic", "test_sign",
        "\tint r = sign_draw(t);\n\n\tif (r != 0) {\n\t\treturn r;   /* the sign is not drawn: VDD_MIC stays off (FW l.342) */\n"
        "\t}\n\treturn rhw_pmic()->rail_set(RHW_RAIL_MIC, true, \"rec_mics_on\");\n",
        "\tint r = rhw_pmic()->rail_set(RHW_RAIL_MIC, true, \"rec_mics_on\");\n\n\tif (r != 0) {\n\t\treturn r;\n"
        "\t}\n\treturn sign_draw(t);\n"),
    # the screens' refusal is ignored: the sign counts as drawn, VDD_MIC goes on
    "mic_on_refused_sign": (MICS, "recorder_sign.test_sign_refused_no_mic_m3_log", "test_sign",
        "\treturn answer; /* the sign's answer */\n",
        "\t(void)answer;\n\treturn 0; /* the sign's answer ignored */\n"),
    # the close tells the screens the recording ended before VDD_MIC is off
    "screen_leaves_before_mic_off": (REC, "recorder_sign.test_close_mic_off_before_screen_leaves", "test_sign",
        "\t(void)rec_mics_off();                    /* VDD_MIC off */\n",
        "\t{\n\t\tstruct rc_actions none = { 0 };\n\n\t\tnone.last_row = -1;\n"
        "\t\t(void)rscr_glue_after(&none, RC_EV_COUNT, RC_ST_STANDBY, mark);\n\t}\n"
        "\t(void)rec_mics_off();                    /* VDD_MIC off */\n"),
    # the join blanks the display while a recording runs (the dimmed sign goes dark)
    "dim_dark": (BRIDGE, "recorder_sign1.test_sign1_every_row", "test_sign1",
        "\trscr_set_battery((uint8_t)(v.soc_x10 / 10u), v.charging, v.full, v.to_full_min);\n",
        "\trscr_set_battery((uint8_t)(v.soc_x10 / 10u), v.charging, v.full, v.to_full_min);\n"
        "\tif (rrec_core_state() == RC_ST_RECORDING) {\n\t\t(void)rscr_panel(false, 0);\n\t}\n"),
    # M2 plays before the close (VDD_MIC still on)
    "m2_before_mic_off": (REC, "recorder_actions.test_stop_m2_after_mic_off", "test_actions",
        "\tcase RC_ACT_CLOSE:\n\t\t(void)rrec_close(t);\n",
        "\tcase RC_ACT_CLOSE:\n\t\tplay(RREC_PAT_M2);\n\t\t(void)rrec_close(t);\n"),
    # VDD_SD off before VDD_MIC off in the close
    "sd_off_before_mic_off": (REC, "recorder_actions.test_close_order", "test_actions",
        "\t(void)rec_mics_off();                    /* VDD_MIC off */\n"
        "\t(void)rau_release();                     /* HFXO after VDD_MIC (FW l.463) */\n"
        "\t(void)rst_unmount();                     /* VDD_SD off */\n",
        "\t(void)rst_unmount();                     /* VDD_SD off */\n"
        "\t(void)rec_mics_off();                    /* VDD_MIC off */\n"
        "\t(void)rau_release();                     /* HFXO after VDD_MIC (FW l.463) */\n"),
    # the storage is mounted before the charger is turned on
    "charge_after_mount": (BOOT, "recorder_boot.test_vbus_boot_charges_before_mount", "test_boot",
        "\tpr = rpw_start(rrec_power_cb());\n\tmr = rst_mount(true, &mi);\n",
        "\tmr = rst_mount(true, &mi);\n\tpr = rpw_start(rrec_power_cb());\n"),
    # the 60 s storage retry runs but its result never reaches the core
    "retry_not_reported": (BRIDGE, "recorder_actions.test_retry_storage_reports_result", "test_actions",
        "\trglue_event(r == 0 ? RC_EV_STORAGE_RETRY_OK : RC_EV_STORAGE_RETRY_FAILED);\n",
        "\t(void)r;   /* the result is not reported */\n"),
    # a factory test recording leaves VDD_MIC on afterwards (FACTORY_TEST idle)
    "mic_in_factory_idle": (REC, "recorder_rows.test_mic_rail_only_in_recording", "test_rows",
        "\t(void)rau_halt();\n\t(void)rec_mics_off();\n\tif (mic_off_ms != NULL) {\n",
        "\t(void)rau_halt();\n\tif (mic_off_ms != NULL) {\n"),
    # a USB request reaches the glue as a long press of the centre
    "usb_long_press": (BACKEND, "recorder_rules.test_no_command_starts_or_stops", "test_rules",
        "\t/* FW l.1062: each transfer command becomes a record (code 0x0100 | opcode) */\n",
        "\trglue_input(RC_SW_CENTRE, true);\n\tk_sleep(K_MSEC(RREC_LONG_PRESS_MS + 100));\n"
        "\trglue_input(RC_SW_CENTRE, false);\n"
        "\t/* FW l.1062: each transfer command becomes a record (code 0x0100 | opcode) */\n"),
    # a state change writes no event log record
    "no_log_on_state_change": (REC, "recorder_log.test_each_kind_logged", "test_log",
        "\t\trrec_log(RREC_LOG_STATE_CHANGE, sc, sizeof(sc));\n",
        "\t\t(void)sc;\n"),
    # VDD_SD wanted (mounted) in STANDBY
    "sd_on_in_standby": (REC, "recorder_rails.test_rails_per_state", "test_rails",
        "\treturn s == RC_ST_RECOVERY || s == RC_ST_RECORDING || s == RC_ST_TRANSFER;\n",
        "\treturn s == RC_ST_RECOVERY || s == RC_ST_RECORDING || s == RC_ST_TRANSFER || s == RC_ST_STANDBY;\n"),
    # ----- step 6 fix round 1 (review findings R6-01 to R6-06), one copy each
    # R6-01: ship mode stops the motor at once (M2 cut)
    "ship_cuts_m2": (REC, "recorder_ship.test_ship_feels_whole_m2", "test_ship",
        "\twhile (rmo_playing() && rhw_clock()->now_ms() < end) {\n",
        "\twhile (false && rmo_playing() && rhw_clock()->now_ms() < end) {\n"),
    # R6-02: ship mode runs before the screens learn the step (the reviewed order: the screen keeps its picture)
    "ship_screen_on": (REC, "recorder_ship.test_ship_closes_each_part_first", "test_ship",
        "\ton = rscr_glue_after(a, last_event, state, t);\n",
        "\tif (rrec_st.ship_pending) {\n\t\trrec_ship_now();   /* broken: ship mode before the screens are told */\n\t}\n"
        "\ton = rscr_glue_after(a, last_event, state, t);\n"),
    # R6-03: the unmount does not wait for the running store call and its result is dropped
    "unmount_result_dropped": (REC, "recorder_unmount.test_unconfigured_finish_times_out", "test_unmount",
        "\tr = rst_unmount_wait(FINISH_WAIT_MS);\n",
        "\t(void)rst_unmount();\n\tr = 0;\n"),
    # R6-04: no HFXO in BOOT and RECOVERY
    "no_hfxo_in_boot": (REC, "recorder_rails.test_hfxo_in_boot_and_recovery", "test_rails",
        "\treturn s == RC_ST_BOOT || s == RC_ST_RECOVERY || s == RC_ST_CHARGING || s == RC_ST_TRANSFER || s == RC_ST_FACTORY_TEST;\n",
        "\treturn s == RC_ST_CHARGING || s == RC_ST_TRANSFER || s == RC_ST_FACTORY_TEST;\n"),
    # R6-05: the close drops the partial chunk
    "close_drops_partial": (REC, "recorder_actions.test_close_order", "test_actions",
        "\t(void)rst_close(cr.last, &cr.close);     /* partial chunk, CLOSE record, superblock with the flag clear */\n",
        "\t(void)rst_close(NULL, &cr.close);        /* the partial chunk dropped */\n"),
    # R6-06: the factory's test recording is opened as type 1
    "test_recording_wrong_type": (REC, "recorder_factory.test_tmic_records_type_2_for_2s", "test_factory",
        "\t\tr = rst_open(RREC_REC_TYPE_FACTORY, 0, &id);   /* type 2 (FW l.548, l.1024) */\n",
        "\t\tr = rst_open(RREC_REC_TYPE_RECORDING, 0, &id);   /* type 1: wrong */\n"),
    # ----- step 6 fix round 2 (review 2, findings R2-01 to R2-08), one copy each
    # R2-01: the retry decides from the state, then unmounts outside the glue's lock (the code of round 1)
    "retry_outside_lock": (REC, "recorder_unmount.test_retry_never_takes_the_card", "test_unmount",
        "\tif (retry_hook != NULL) {\n\t\tretry_hook();\n\t}\n#endif\n"
        "\trglue_event(RC_EV_COUNT);   /* the decision and the unmount in rails_follow_state, under the glue's lock */\n",
        "\t{\n\t\tenum rc_state s = rrec_core_state();\n\n"
        "\t\tif (s == RC_ST_RECOVERY || s == RC_ST_RECORDING || s == RC_ST_TRANSFER || s == RC_ST_BOOT ||\n"
        "\t\t    s == RC_ST_FACTORY_TEST) {\n\t\t\treturn;\n\t\t}\n"
        "\t\tif (retry_hook != NULL) {\n\t\t\tretry_hook();\n\t\t}\n\t\t(void)unmount_now();\n\t}\n#endif\n"),
    # R2-02: the episode's errno is not kept: the end record carries a 0 left from before
    "end_errno_stale": (REC, "recorder_unmount.test_episode_end_keeps_its_errno", "test_unmount",
        "\t\tunmount_ep_err = r;   /* this episode's last errno */\n",
        ""),
    # R2-03: the rails' pass of the same step waits again for the unmount
    "rails_tries_again": (REC, "recorder_unmount.test_one_wait_each_per_step", "test_unmount",
        "\t\t} else if (!step_unmount_tried) {\n",
        "\t\t} else if (true) {\n"),
    # R2-04: ship mode closes the storage before USB and does not try again (the code of round 1)
    "ship_storage_before_usb": (REC, "recorder_ship.test_ship_closes_usb_before_second_unmount", "test_ship",
        "\t\tunmount_record(r, 1);\n\t\t(void)rxf_stop(FINISH_WAIT_MS);  /* USB first: the command that holds the store is aborted */\n"
        "\t\t*usb_closed = true;\n\t\tr = rst_unmount_wait(FINISH_WAIT_MS);   /* ship: the second try, USB closed */\n\t\tunmount_record(r, 2);\n",
        "\t\tunmount_record(r, 1);\n"),
    # R2-05: the screen is waited for without a bound
    "screen_wait_forever": (REC, "recorder_ship.test_ship_with_stuck_screens_goes_on", "test_ship",
        "\treturn k_sem_take(&sync_done, K_MSEC(RREC_SHIP_SCREEN_WAIT_MS));\n",
        "\treturn k_sem_take(&sync_done, K_FOREVER);\n"),
    # R2-06: a latched VBUS job keeps the event it was latched with
    "latched_vbus_stale": (BRIDGE, "recorder_actions.test_latched_vbus_follows_the_level", "test_actions",
        "\t\t\tj.arg = rhw_pmic()->vbus_present() ? RC_EV_VBUS_IN : RC_EV_VBUS_OUT;\n",
        "\t\t\t(void)j;\n"),
    # R2-07: the factory's test recordings last twice as long (T-SIGN asks for 1 s)
    "tsign_2s": (REC, "recorder_factory.test_tsign_reports_mic_times", "test_factory",
        "\tk_sleep(K_MSEC(ms + RREC_DISCARD_MS));\n",
        "\tk_sleep(K_MSEC(2 * ms + RREC_DISCARD_MS));\n"),
    # R2-08: after "abort the command" the join does not wait for the command to end (FW l.179)
    "abort_no_wait": (REC, "recorder_unmount.test_vbus_out_during_read_command", "test_unmount",
        "\t\trxf_abort();\n\t\tif (!step_finish_waited) {       /* once per step (R2-03) */\n",
        "\t\trxf_abort();\n\t\tif (false) {\n"),
}
if len(sys.argv) == 2 and sys.argv[1] == "--list":
    print(" ".join(V))
    sys.exit(0)
v, root = sys.argv[1], pathlib.Path(sys.argv[2])
rel, case, suite, old, new = V[v]
f = root / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print(case, suite)
