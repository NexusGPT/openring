"""Local check (before any server run): each broken-copy edit of tests/sys/broken_edit.py matches exactly once.
Copies modules/ring_sys into a new folder per variant under build-logs/step6/u7-editcheck/<stamp>/ and runs the edit."""
import pathlib, shutil, subprocess, sys, time, difflib
FW = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
OUT = FW / "build-logs/step6/u7-editcheck" / time.strftime("%Y%m%d-%H%M%S")
V = "size_999425_ok end_off_by_one writes_slot0 selftest_31s allowed_at_30 feed_without_progress crash_copied_twice guess_marked_set".split()
bad = 0
for v in V:
    d = OUT / v
    shutil.copytree(FW / "modules/ring_sys", d)
    r = subprocess.run([sys.executable, "-B", "-I", str(FW / "tests/sys/broken_edit.py"), v, str(d)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{v}: FAILED {r.stderr.strip()}"); bad += 1; continue
    n = 0
    for f in (FW / "modules/ring_sys").rglob("*"):
        if f.is_file():
            a = f.read_text().splitlines(); b = (d / f.relative_to(FW / "modules/ring_sys")).read_text().splitlines()
            if a != b:
                n += sum(1 for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---"))
    print(f"{v}: matches exactly once, named case {r.stdout.strip()}, changed lines {n}")
print("RESULT", "FAIL" if bad else "PASS", len(V), "variants checked")
sys.exit(1 if bad else 0)
