"""Edits for tests/factory/broken_run.sh. Usage:
  python3 broken_edit.py --module <variant>            prints the module folder the variant edits (ring_factory or ring_rhw)
  python3 broken_edit.py <variant> <module copy folder>  makes the one edit, prints the named case
One named fault per variant; the edit must match exactly once. The variants are those of firmware/docs/step6-plan.md,
unit U8 "Broken copies" (ten). store_lba_4097 edits a copy of ring_rhw (the number of the factory area's first sector
lives in rrec_spec.h, written once, and ring_store's area test reads it from there)."""
import pathlib
import sys

LOGIC = "src/rfa_logic.c"
THIN = "src/rfa.c"
SPEC = "include/ring_rhw/rrec_spec.h"
V = {
    # the flag is not looked at: a request with the flag clear is answered
    "flag_ignored": ("ring_factory", LOGIC, "factory_cmd.test_flag_rules",
        "\tif (!flag) {\n\t\treturn RREC_ST_NOT_ALLOWED;",
        "\tif (false && !flag) {\n\t\treturn RREC_ST_NOT_ALLOWED;"),
    # the removed sub-command 0x11 is accepted like a plain one
    "x11_accepted": ("ring_factory", LOGIC, "factory_cmd.test_0x11_bad_arg",
        "\tcase RREC_FAC_SCREEN:\n",
        "\tcase RREC_FAC_SKEW_REMOVED:\n\tcase RREC_FAC_SCREEN:\n"),
    # a run of 999 equal samples is already stuck
    "run_999": ("ring_factory", LOGIC, "factory_mic.test_rms_and_runs",
        "return longest_run >= RREC_FAC_MIC_STUCK_RUN;",
        "return longest_run >= 999u;"),
    # the factory part switches VDD_MIC itself before the test recording, with no sign
    "mic_without_sign": ("ring_factory", THIN, "factory_mic.test_no_screen_no_mic",
        "/* mic path: the test recording only (rec_mics_on after the sign, R18) */",
        "(void)rhw_pmic()->rail_set(RHW_RAIL_MIC, true, \"rfa_mic\");"),
    # a long press of the centre in FACTORY_TEST starts a test recording
    "centre_records": ("ring_factory", THIN, "factory_input.test_centre_reported_never_records",
        "/* the events end here: they reach the jig only, never a recording */",
        "{\n\t\tint64_t a = 0, b = 0;\n\n\t\tif (ev == RFA_IN_LONG && ops.test_recording != NULL) {\n"
        "\t\t\t(void)ops.test_recording(RREC_FAC_SIGN_REC_MS, NULL, &a, &b);\n\t\t}\n\t}"),
    # the second VBAT read is made at once, not 250 ms into the pulse
    "vbat_read_at_0": ("ring_factory", LOGIC, "factory_motor.test_reads_and_timing",
        "return RREC_FAC_MOTOR_READ_MS;",
        "return 0u;"),
    # the area of T-STORE starts one sector late
    "store_lba_4097": ("ring_rhw", SPEC, "factory_store.test_area_write_read",
        "RREC_LBA_FACTORY_FIRST        4096u",
        "RREC_LBA_FACTORY_FIRST        4097u"),
    # the test recordings are not deleted
    "type2_left": ("ring_factory", THIN, "factory_store.test_test_recordings_deleted",
        "int rc2 = rst_delete_factory_recordings(deleted);",
        "int rc2 = 0;"),
    # the ship beacon can be connected to
    "beacon_connectable": ("ring_factory", THIN, "factory_ship.test_beacon_name",
        "return beacon_start(false); /* ship */",
        "return beacon_start(true); /* ship */"),
    # the beacon stops after the ship task, not before it
    "beacon_after_ship": ("ring_factory", THIN, "factory_ship.test_beacon_window",
        "void rfa_beacon_stop(void)\n{\n\tbeacon_stop_now();\n}",
        "static void late_fn(struct k_work *w)\n{\n\tARG_UNUSED(w);\n\tbeacon_stop_now();\n}\n\n"
        "static K_WORK_DELAYABLE_DEFINE(late_work, late_fn);\n\n"
        "void rfa_beacon_stop(void)\n{\n\t(void)k_work_schedule(&late_work, K_MSEC(50));\n}"),
}
if sys.argv[1] == "--module":
    print(V[sys.argv[2]][0])
    sys.exit(0)
v, root = sys.argv[1], pathlib.Path(sys.argv[2])
mod, rel, case, old, new = V[v]
f = root / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print(case)
