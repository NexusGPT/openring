"""Edits for tests/recorder/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_recorder copy folder>
Prints "<named case> <suite file>". One named fault per variant; the edit must match exactly once. The variants are those
of firmware/docs/step6-plan.md, unit J "Broken copies"."""
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
