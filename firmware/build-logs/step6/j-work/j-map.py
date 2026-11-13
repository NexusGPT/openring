"""j-map.py <case list log (board case status per line, j-cases1.log)>: the rows of the plan that name J, each with its cases and the log lines that show each case
passing on native_sim and on the simulated chip (the twister parts of tools/unit_run.sh). Prints a markdown table and a
count of cases not found. Every line number is read from the log, never typed."""
import re
import sys

ROWS = [
    ("C1", ["recorder_rows.test_mic_rail_only_in_recording"]),
    ("C4", ["recorder_actions.test_close_order"]),
    ("C5", ["recorder_actions.test_open_order"]),
    ("C6", ["recorder_rows.test_charge_on_every_vbus_row", "recorder_boot.test_vbus_boot_charges_before_mount"]),
    ("C7", ["recorder_boot.test_vbus_boot_charges_before_mount"]),
    ("C8", ["recorder_boot.test_init_done_each_row"]),
    ("C9", ["recorder_boot.test_recovery_rows"]),
    ("C10", ["recorder_sign.test_start_draws_sign_before_mic"]),
    ("C11", ["recorder_sign.test_sign_refused_no_mic_m3_log"]),
    ("C12", ["recorder_actions.test_stop_m2_after_mic_off"]),
    ("C13", ["recorder_actions.test_ble_highlight_marks"]),
    ("C14", ["recorder_rows.test_vbus_in_recording"]),
    ("C15", ["recorder_rows.test_recording_exits"]),
    ("C16", ["recorder_boot.test_restart_after_cut_recovers"]),
    ("C17", ["recorder_rows.test_usb_configured"]),
    ("C18", ["recorder_rows.test_transfer_rows", "recorder_rows.test_fw_end_row"]),
    ("C19", ["recorder_actions.test_retry_storage_reports_result"]),
    ("C20", ["recorder_rows.test_factory_rows"]),
    ("C21", ["recorder_rules.test_no_command_starts_or_stops"]),
    ("C22", ["recorder_rows.test_charge_on_every_vbus_row"]),
    ("C23", ["recorder_actions.test_watchdog_fed_while_recording"]),
    ("C24", []),
    ("C25", ["recorder_actions.test_refusal_plays_m3"]),
    ("C26", ["recorder_actions.test_mw_in_recording_marked"]),
    ("C27", ["recorder_sign.test_start_draws_sign_before_mic", "recorder_actions.test_m1_at_start"]),
    ("C33", ["recorder_log.test_pattern_start_logged", "recorder_actions.test_mw_in_recording_marked"]),
    ("C36", ["recorder_sign1.test_sign1_every_row"]),
    ("C37", ["recorder_sign.test_only_rec_mics_on_enables_mic", "recorder_sign.test_close_mic_off_before_screen_leaves"]),
    ("C38", ["recorder_sign1.test_sign1_every_row", "recorder_sign1.test_forced_draw_failure"]),
    ("C39", ["recorder_screens.test_battery_reaches_screens"]),
    ("A6", ["recorder_sequence.test_start_order_and_times", "recorder_sequence.test_stop_order"]),
    ("A10", ["recorder_log.test_stop_press_time_logged"]),
    ("A12", ["recorder_sequence.test_start_order_and_times"]),
    ("A13", ["recorder_sequence.test_stop_order"]),
    ("P4", ["recorder_boot.test_vbus_boot_charges_before_mount"]),
    ("P6", ["recorder_rails.test_rails_per_state", "recorder_rails.test_sd_rail_per_state"]),
    ("P11", ["recorder_rows.test_vbus_out_at_b2_goes_off"]),
    ("P12", ["recorder_actions.test_ship_closes_everything_first"]),
    ("P18 (J part)", ["recorder_screens.test_ilim_dims_in_recording", "recorder_screens.test_start_during_ilim_hold_is_dim"]),
    ("T8", ["recorder_rows.test_fw_end_row"]),
    ("T9", ["recorder_boot.test_selftest_items"]),
    ("T24", ["recorder_boot.test_boot_count_only_at_boot"]),
    ("T27", ["recorder_log.test_each_kind_logged"]),
]

lines = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
found = {}
for i, ln in enumerate(lines, 1):
    w = ln.split()
    if len(w) == 3 and w[2] in ("passed", "failed", "skipped", "error", "blocked"):
        ident = w[1]
        if ident.startswith("ring_recorder.sim."):
            suite, name = ident[len("ring_recorder.sim."):].split(".", 1)
            ident = "%s.test_%s" % (suite, name)   # twister drops the "test_" of the ZTEST name
        found.setdefault((w[0], ident), (i, w[2]))
parts = sorted({p for (p, _c) in found})
missing = 0
print("| Row | Case | " + " | ".join(parts) + " |")
print("|---|---|" + "---|" * len(parts))
for row, cases in ROWS:
    if not cases:
        print("| %s | (none of J's) | %s |" % (row, " | ".join("-" for _ in parts)))
        continue
    for c in cases:
        cells = []
        for p in parts:
            v = found.get((p, c))
            if v is None:
                cells.append("NOT FOUND")
                missing += 1
            else:
                cells.append("l.%d %s" % v)
        print("| %s | `%s` | %s |" % (row, c, " | ".join(cells)))
print()
print("cases not found in a part: %d; parts: %s" % (missing, ", ".join(parts)))
