"""Run design/firmware-check.py (the delivered script, by its real path) on each broken copy and on an
unmodified copy; compare with expected_broken.txt; list every case whose result differs."""
import os
import shutil
import subprocess
import sys

repo, py = sys.argv[1], sys.argv[2]
ev = os.path.join(repo, "design", "firmware-evidence", "f5")
check = os.path.join(repo, "design", "firmware-check.py")
bdir = os.path.join(ev, sys.argv[3] if len(sys.argv) > 3 else "broken")
shutil.copyfile(os.path.join(repo, "design", "firmware.md"), os.path.join(bdir, "control_unchanged.md"))
exp = {}
for ln in open(os.path.join(ev, sys.argv[4] if len(sys.argv) > 4 else "expected_broken.txt"), encoding="utf-8"):
    if ln.startswith("#") or not ln.strip():
        continue
    name, code, texts = [x.strip() for x in ln.split("|")]
    exp[name] = (int(code), [t.strip() for t in texts.split(";") if t.strip() and t.strip() != "(none)"])
diffs = 0
for name in exp:
    path = os.path.join(bdir, name + ".md")
    r = subprocess.run([py, "-I", check, path], capture_output=True, text=True, cwd=repo)
    out = r.stdout + r.stderr
    open(os.path.join(bdir, name + ".log"), "w", encoding="utf-8").write(out + f"exit {r.returncode}\n")
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    code, texts = exp[name]
    missing = [t for t in texts if not any(t in f for f in fails)]
    extra = [f for f in fails if not any(t in f for t in texts)]
    ok = r.returncode == code and not missing
    print(f"{name}: exit {r.returncode} (expected {code}); FAIL lines {len(fails)}; expected texts missing {missing}; FAIL lines not expected {extra}; {'as expected' if ok else 'DIFFERS'}")
    if not ok or extra:
        diffs += 1
print(f"cases differing from the expectation (missing text, wrong exit or an unexpected FAIL line): {diffs}")
