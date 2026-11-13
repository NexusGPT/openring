"""Edit helper: python3 -I ed.py <edits.py>  where edits.py defines EDITS = [(file, old, new, follows), ...]
Each old must occur exactly once in the file. Logs file, line found, before, after, decision to edits.log (appended)."""
import sys, json, datetime, runpy
LOG = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/text-pass-work/edits.log")
ns = runpy.run_path(sys.argv[1])
bad = 0
for f, old, new, why in ns["EDITS"]:
    s = open(f, encoding="utf-8").read()
    n = s.count(old)
    if n != 1:
        print("FAIL count", n, f, repr(old[:70])); bad += 1; continue
    i = s.index(old)
    line = s.count("\n", 0, i) + 1
    s = s[:i] + new + s[i+len(old):]
    open(f, "w", encoding="utf-8").write(s)
    with open(LOG, "a", encoding="utf-8") as lg:
        lg.write(json.dumps({"file": f.replace((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/"), ""), "line": line, "before": old, "after": new, "follows": why}, ensure_ascii=False) + "\n")
    print("ok", f.split("/")[-1], line)
print("failures", bad)
