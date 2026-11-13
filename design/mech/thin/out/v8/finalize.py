#!/usr/bin/env python3
"""After the exports: specs Files/Open points, measure_step_v8, check_band final, the RESULT line, band-fit-notes.md. Every step logs into out/v8."""
import re, subprocess, sys
from pathlib import Path
V = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin/out/v8"))
D = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design"))
PY = str(D / ".venv/bin/python")
def run(cmd, log, cwd=None):
    with open(V / log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=cwd)
    print(log, "exit", r.returncode, flush=True)
    return r.returncode
run([sys.executable, str(V / "finish_specs.py")], "finish_specs.log")
run(["nice", "-n", "19", PY, "-I", str(V / "measure_step_v8.py")], "measure_step_v8.log")
rc_cb = run(["nice", "-n", "19", str(D / "ecad/ring/pcb/run_kipy.sh"), str(D / "ecad/band/check_band.py")], "check_band_final.log_raw", cwd=str(D / "ecad/ring/pcb"))
raw = (V / "check_band_final.log_raw").read_text().splitlines()
(V / "check_band_final.log").write_text("\n".join(raw) + "\nexit %d\n" % rc_cb)
LOGS = {7: "v8b_us7.log", 8: "v8_us8.log", 9: "v8_us9_default.log", 10: "v8_us10.log", 11: "v8_us11.log", 12: "v8b_us12.log", 13: "v8_us13.log"}
ok = []
for us, n in LOGS.items():
    t = (V / n).read_text() if (V / n).exists() else ""
    if re.search(r"^RESULT PASS", t, re.M) and "\nexit 0" in t:
        ok.append(us)
bad = [u for u in LOGS if u not in ok]
line = ("RESULT: done, the fit check ends RESULT PASS at US " + ", ".join(map(str, ok)) + " with the drawn ribbons (" + str(len(ok)) + " of 7 sizes), 4 model changes and 2 conflicts for the lead"
        if not bad else "RESULT: blocked, the fit check ends RESULT PASS at " + str(len(ok)) + " of 7 sizes (not at US " + ", ".join(map(str, bad)) + "), 4 model changes and 2 conflicts for the lead")
(V / "notes_result.md").write_text(line + "\n")
run([sys.executable, str(V / "notes_build.py")], "notes_build.log")
print(line)
