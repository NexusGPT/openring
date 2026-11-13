# check_board.py output folder option (review 4 note N7): on copies of the ring board in W (with its project file and library table)
import os, shutil, subprocess, time
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = ROOT + "/design/wiring/checks-harden-work"
KIPY = ROOT + "/design/ecad/ring/pcb/run_kipy.sh"
CHK = ROOT + "/design/ecad/ring/pcb/check_board.py"
src = ROOT + "/design/ecad/ring/pcb/ring.kicad_pcb"
T = W + "/copies/board-test-" + time.strftime("%H%M%S")   # a new folder for each run, nothing is deleted
os.makedirs(T + "/out"); os.makedirs(T + "/default"); os.makedirs(T + "/out-report")
for d in ("out", "default"):
    for f in ("ring.kicad_pro", "ring.kicad_prl"):
        shutil.copy(ROOT + "/design/ecad/ring/pcb/" + f, T + "/" + d + "/" + f)
    shutil.copy(src, T + "/" + d + "/ring.kicad_pcb")
    shutil.copy(W + "/copies/board/fp-lib-table", T + "/" + d + "/fp-lib-table")
ok = 0; n = 0
def run(name, d, env_out, want_report, absent_report):
    global ok, n
    env = {k: v for k, v in os.environ.items() if k != "CHECK_BOARD_OUT"}
    if env_out: env["CHECK_BOARD_OUT"] = env_out
    r = subprocess.run(["nice", "-n", "19", "bash", KIPY, CHK, T + "/" + d + "/ring.kicad_pcb"], capture_output=True, text=True, env=env)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "Debug: Adding" not in l and "wxApp" not in l)
    open(W + "/logs/board/test-" + name + ".log", "w").write(out + "\nEXIT %d\n" % r.returncode)
    last = [l for l in out.splitlines() if l.startswith("RESULT")][-1:]
    good = r.returncode == 0 and os.path.isfile(want_report) and not os.path.exists(absent_report)
    n += 1; ok += good
    print("CASE check_board/%-34s exit=%d report_in_wanted_place=%s report_in_other_place=%s %s | %s" % (
        name, r.returncode, os.path.isfile(want_report), os.path.exists(absent_report), "as expected" if good else "DIFFERS", last))
run("with_CHECK_BOARD_OUT", "out", T + "/out-report", T + "/out-report/ring-drc.json", T + "/out/ring-drc.json")
run("default_without_the_variable", "default", None, T + "/default/ring-drc.json", T + "/default-report/ring-drc.json")
print("SECTION check_board ok=%d of %d" % (ok, n))
