"""Edits for tests/motor/broken_run.sh. Usage: python3 broken_edit.py <variant> <ring_motor copy folder>
Prints the named case of the variant. One named fault per variant; the edit must match exactly once. The variants are
those of firmware/docs/step6-plan.md, unit U6 "Broken copies" (the two soft start copies are dropped: ruling D3)."""
import pathlib
import sys

LOGIC = "src/rmo_logic.c"
THIN = "src/rmo.c"
V = {
    # MH and MT also cut M1 (they may not cut M2, M3 and MF)
    "mh_cuts_m1": (LOGIC, "motor_player.test_replace_rules",
        "&& is_never_cut(playing)) {",
        "&& is_never_cut(playing) && playing != RREC_PAT_M1) {"),
    # the setting "Vibration" off also mutes MW
    "vibration_mutes_mw": (LOGIC, "motor_player.test_vibration_off_keeps_the_others",
        "return !(id == RREC_PAT_MH || id == RREC_PAT_MT);",
        "return !(id == RREC_PAT_MH || id == RREC_PAT_MT || id == RREC_PAT_MW);"),
    # the gap of M2 is 100 ms instead of 120
    "m2_gap_100": (LOGIC, "motor_player.test_every_pattern_pin_times",
        "{ 3, { 80, 120, 80 } }",
        "{ 3, { 80, 100, 80 } }"),
    # the edge callback reports the clock 10 ms late
    "edge_late": (THIN, "motor_player.test_edge_times_reported",
        "cb.edge(high, rhw_clock()->cycles());",
        "cb.edge(high, rhw_clock()->cycles() + rhw_clock()->cycles_per_sec() / 100u);"),
    # the start allowance is 5 ms instead of 10
    "allowance_5ms": (LOGIC, "motor_charge.test_charge_per_pattern",
        "return t_on_ms * RREC_MOTOR_RUN_MA + RREC_MOTOR_START_MS * RREC_MOTOR_START_MA;",
        "return t_on_ms * RREC_MOTOR_RUN_MA + 5u * RREC_MOTOR_START_MA;"),
}
v, root = sys.argv[1], pathlib.Path(sys.argv[2])
rel, case, old, new = V[v]
f = root / rel
t = f.read_text()
if t.count(old) != 1:
    print(f"edit {v} did not match exactly once ({t.count(old)})", file=sys.stderr)
    sys.exit(1)
f.write_text(t.replace(old, new))
print(case)
