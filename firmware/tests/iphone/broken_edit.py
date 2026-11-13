"""Edits for tests/iphone/broken_run.sh. Usage: python3 broken_edit.py <variant> <file> ; prints the named case.
One named fault per variant; the edit must match exactly once."""
import pathlib
import sys

V = {
    "media_state": ("src/ripl.c", "test_media_playback_state",
        "\t\tif (st == 0) {\n\t\t\tm->state = RIPL_PLAYER_PAUSED;\n\t\t} else if (st == 1) {\n\t\t\tm->state = RIPL_PLAYER_PLAYING;",
        "\t\tif (st == 0) {\n\t\t\tm->state = RIPL_PLAYER_PLAYING;\n\t\t} else if (st == 1) {\n\t\t\tm->state = RIPL_PLAYER_PAUSED;"),
    # a zone read that comes back re-applies the time at the uptime of now (the round 2 fault)
    "clock_drift": ("src/ripl.c", "test_clock_no_drift_with_delayed_zone_read",
        "\t(void)up_now_ms;\n",
        "\tc->up_ms = up_now_ms;\n"),
    # a failed zone read is taken as "no zone"
    "clock_failed_read": ("src/ripl.c", "test_clock_failed_zone_read_keeps_the_last_zone",
        "\tif (!read_ok) {\n\t\tc->zone_errors++;\n\t\treturn;\n\t}\n",
        "\tif (!read_ok) {\n\t\tc->zone_errors++;\n\t\tknown = false;\n\t}\n"),
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
