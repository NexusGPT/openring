"""Edits for tests/power/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_power copy folder>
Prints "CASE <suite.case>" (the suite runs and that one case must fail) or "BUILD <message>" (the build must fail with
that assertion message). One named fault per variant; each edit must match exactly once.
The variants are those of firmware/docs/step6-plan.md, unit U5 "Broken copies"."""
import pathlib
import sys

CC = "#define CHARGE_CURRENT 15000"
V = {
    # the voltage rule of B5 (3.45 V) is ignored; the state of charge still judges
    "voltage_ignored": ("src/rpw_logic.c", "CASE power_levels.test_voltage_edges",
        "if (soc_x10 <= RREC_B5_SOC_X10 || rpwl_volt_at_or_under(sum_mv, n, RREC_B5_MV)) {",
        "if (soc_x10 <= RREC_B5_SOC_X10) {"),
    # the window holds 5 samples, not 10
    "mean_of_5": ("src/rpw_logic.h", "CASE power_levels.test_mean_of_ten_in_recording",
        "#define RPWL_WINDOW RREC_MEAN_SAMPLES", "#define RPWL_WINDOW 5u"),
    # a level is reported only when it gets worse
    "report_down_only": ("src/rpw_logic.c", "CASE power_levels.test_report_on_change_both_ways",
        "*changed = lvl != j->reported;", "*changed = lvl > j->reported;"),
    # "charge on" writes every time
    "charge_on_rewrites": ("src/rpw_logic.c", "CASE power_charger.test_charge_on_twice_writes_once",
        "return !is_on;", "return true;"),
    # the charger is not disabled before the current is written
    "write_while_enabled": ("src/rpw_logic.c", "CASE power_charger.test_disable_write_enable_order",
        "{ RPWL_CHG_DISABLE, RPWL_CHG_CURRENT, RPWL_CHG_ENABLE }", "{ RPWL_CHG_NONE, RPWL_CHG_CURRENT, RPWL_CHG_ENABLE }"),
    # the motor's charge is subtracted from the current instead of added
    "motor_charge_subtracted": ("src/rpw_logic.c", "CASE power_gauge.test_motor_charge_added",
        "fed = fed + (int64_t)motor_uas * 1000 / dt_ms;", "fed = fed - (int64_t)motor_uas * 1000 / dt_ms;"),
    # SHPHLDCONFIG is written but the strobe is skipped
    "ship_no_strobe": ("src/rpw_logic.c", "CASE power_ship.test_entry_order_without_vbus",
        "\tcase RPWL_SS_CONFIG:\n\t\ts->st = RPWL_SS_STROBE;", "\tcase RPWL_SS_CONFIG:\n\t\ts->st = RPWL_SS_VBUS;"),
    # the task is written without waiting for VBUS removed
    "ship_no_wait": ("src/rpw_logic.c", "CASE power_ship.test_waits_for_vbus_removed",
        "\t\tif (vbus) {\n\t\t\treturn RPWL_SHIP_WAIT_VBUS;", "\t\tif (vbus && false) {\n\t\t\treturn RPWL_SHIP_WAIT_VBUS;"),
    # the first current-limit reading plays the pattern M3 on the motor pin (FW l.995 forbids any motor pattern)
    "ilim_plays_m3": ("src/rpw.c", "CASE power_ilim.test_first_active",
        "\t\t\tcb.ilim(first, mv, count);",
        "\t\t\tif (first) {\n\t\t\t\t(void)rhw_motor()->set(true);\n\t\t\t\t(void)rhw_motor()->set(false);\n\t\t\t}\n\t\t\tcb.ilim(first, mv, count);"),
    # the causes are logged but not cleared
    "causes_not_cleared": ("src/rpw.c", "CASE power_reset.test_causes_logged_then_cleared",
        "\tr = rhw_pmic()->reset_causes_clear();\n\treturn r;", "\tr = 0;\n\treturn r;"),
    # step 6, the join's addition: the read now is made on the caller's thread, not the power thread
    "read_on_caller_thread": ("src/rpw.c", "CASE power_read.test_sample_now_from_power_thread",
        "\tif (k_msgq_put(&ev_q, &e, K_NO_WAIT) != 0) {\n\t\tr = -EBUSY;",
        "\t(void)e;\n\tif (started) {\n\t\tdo_read();\n\t}\n\tif (!started) {\n\t\tr = -ETIMEDOUT;"),
    # CHARGE_CURRENT build assertions (FW l.894): each must fail the build with its own message
    "cc_unset": ("src/rpw_logic.c", "BUILD CHARGE_CURRENT is not set (FW l.894)", CC + "\n", ""),
    "cc_17601": ("src/rpw_logic.c", "BUILD CHARGE_CURRENT is above 17,600 uA (FW l.894)", CC,
        "#define CHARGE_CURRENT 17601"),
    "cc_3999": ("src/rpw_logic.c", "BUILD CHARGE_CURRENT is under 4,000 uA (FW l.894)", CC,
        "#define CHARGE_CURRENT 3999"),
    "cc_100500": ("src/rpw_logic.c", "BUILD CHARGE_CURRENT is over 100,000 uA (FW l.894)", CC,
        "#define CHARGE_CURRENT 100500"),
    "cc_15250": ("src/rpw_logic.c", "BUILD CHARGE_CURRENT is not a multiple of 500 uA (FW l.894)", CC,
        "#define CHARGE_CURRENT 15250"),
}
if len(sys.argv) == 2 and sys.argv[1] == "--list":
    print(" ".join(V))
    sys.exit(0)
v, root = sys.argv[1], pathlib.Path(sys.argv[2])
rel, what, old, new = V[v]
f = root / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print(what)
