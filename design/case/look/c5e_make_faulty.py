"""Builds faulty copies of the case files under look/c5e_faulty_<name>/ (one deliberate fault each) and runs check_case_docs.py on each; logs next to them."""
import os, shutil, subprocess, sys
CASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOK = os.path.join(CASE, "look")
FILES = ["case-bom.csv", "case-architecture.md", "case-notes.md", "out/case_size.txt", "out/case_params.json", "look/c5d_check_lead_rerun.log"]
FAULTS = {
 "pin": [("case-architecture.md", "| Harwin P70-6000045R (the fitted pin;", "| Mill-Max 0981-0-15-20-87-14-11-0 (the fitted pin;")],
 "size": [("case-architecture.md", "**Outer size, closed** (out/case_size.txt): 45.4 x 45.9", "**Outer size, closed** (out/case_size.txt): 45.5 x 45.9")],
 "pairs": [("case-architecture.md", "PASS, 3447 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]\"). C5d:", "PASS, 1842 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]\"). C5d:")],
 "roll": [("case-architecture.md", "against 0.50 mm that a 0.6 mm pin tip can take on a 1.6 mm pad before it leaves the pad: OK.", "against 0.2 mm that a 0.6 mm pin tip can take on a 1.0 mm pad before it leaves the pad. So the roll is NOT held to the pad's tolerance.")],
 "charge": [("case-architecture.md", "so the 32 mA minimum of the old nPM1300 no longer applies)", "but the power chip's 32 mA minimum is above 1 C for this cell)")],
}
res = {}
for name, edits in FAULTS.items():
    d = os.path.join(LOOK, "c5e_faulty_" + name)
    for f in FILES:
        os.makedirs(os.path.dirname(os.path.join(d, f)), exist_ok=True)
        shutil.copy(os.path.join(CASE, f), os.path.join(d, f))
    for f, a, b in edits:
        p = os.path.join(d, f); t = open(p, encoding="utf-8", newline="").read()
        assert t.count(a) == 1, (name, f, t.count(a))
        open(p, "w", encoding="utf-8", newline="").write(t.replace(a, b))
    r = subprocess.run([sys.executable, "-I", os.path.join(CASE, "check_case_docs.py"), d, os.path.join(CASE, "..", "architecture.md")], capture_output=True, text=True)
    out = r.stdout + r.stderr
    open(os.path.join(LOOK, "c5e_faulty_%s.log" % name), "w").write(out + "exit %d\n" % r.returncode)
    res[name] = (r.returncode, out.strip().splitlines()[-1])
for k, v in res.items():
    print(k, v)
