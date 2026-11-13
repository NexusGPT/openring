"""Read-only: for each fix-round copy, count how often its 'from' text occurs in the pinned export (SRC), and print
the line number of the first hit. Usage: python3 -I copycheck.py <SRC/firmware>"""
import importlib.util
import pathlib
import sys

fw = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("be", fw / "tests/recorder/broken_edit.py")
src = (fw / "tests/recorder/broken_edit.py").read_text()
# load V without running the CLI part: exec only up to the line that starts the CLI
cut = src.index('if len(sys.argv) == 2 and sys.argv[1] == "--list":')
ns = {"__name__": "be"}
exec(compile(src[:cut], "broken_edit.py", "exec"), ns)
V = ns["V"]
fix = ["ship_cuts_m2", "ship_screen_on", "unmount_result_dropped", "no_hfxo_in_boot", "close_drops_partial",
       "test_recording_wrong_type"]
for name in fix:
    f, case, suite, a, b = V[name]
    text = (fw / "modules/ring_recorder" / f).read_text()
    n = text.count(a)
    line = text[: text.find(a)].count("\n") + 1 if n else -1
    print(f"COPY {name}: file modules/ring_recorder/{f}, case {case}, matches {n}, first line {line}")
# bsim copy
b = (fw / "tests/bsim/control/broken_edit.py").read_text()
a = "\tstopped = true;\n\tadv_stop();\n"
t = (fw / "modules/ring_devices/src/rdev.c").read_text()
print(f"COPY radio_not_stopped: matches {t.count(a)}, first line {t[: t.find(a)].count(chr(10)) + 1}")
print("radio_not_stopped in bsim broken_edit.py:", "radio_not_stopped" in b)
print("DONE", len(fix) + 1, "copies checked")
