# audit.py <notes>: every backtick quote that follows a cited evidence path on the same line must appear in that file
import re, sys, os
P = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/")
MAP = {"R3/": P + "evidence/r3/", "R2/": P + "evidence/r2/"}
def resolve(t):
    for k, v in MAP.items():
        if t.startswith(k): return v + t[len(k):]
    for base in (P, P + "../", (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/")):
        if os.path.exists(base + t): return base + t
    return None
ok = bad = paths = 0
for n, line in enumerate(open(sys.argv[1]), 1):
    cur = None
    for t in re.findall(r"`([^`]+)`", line):
        f = resolve(t) if ("/" in t or re.search(r"\.(log|txt|py|csv|md|sh)$", t)) else None
        if f is not None or t.startswith("R3/") or t.startswith("R2/"):
            paths += 1
            if f is None or not os.path.exists(f):
                if "<" not in t: bad += 1; print("line %d MISSING FILE %s" % (n, t))
                cur = None
            else:
                cur = f if os.path.isfile(f) else None
            continue
        if cur:
            if t in open(cur, errors="replace").read(): ok += 1; print("line %d ok %r in %s" % (n, t[:70], os.path.basename(cur)))
            else: bad += 1; print("line %d NOT FOUND %r in %s" % (n, t, cur))
print("paths cited %d, quotes matched %d, problems %d" % (paths, ok, bad))
