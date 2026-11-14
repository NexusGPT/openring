#!/usr/bin/env python3
"""Final audit of step7-review-2.md: pulls citations, file names, counts and verdicts out of the review by itself and
prints the evidence line each matches, and any disagreement between counts and tables."""
import os
import re
import sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
FW = ROOT + "/firmware"
W = FW + "/build-logs/step7/review2-work"
REV = FW + "/docs/step7-review-2.md"
LOG = FW + "/build-logs/step7/fix1/f1-full1.console"
text = open(REV).read()
parts = text.split("## Last lines of the cited proof files")
body = parts[0] + "\n".join(parts[1].split("\n")[1:]) .split("- `fix1/f1-explore4.console`")[-1]

checked = 0
problems = []

# 1. every file named by base name in the review must exist in review2-work, fix1, step7 or the artifact
names = set(re.findall(r"`([A-Za-z0-9_.\-]+\.(?:txt|console|md|exit|sh|py))`", body))
search = [FW + "/tools", W, FW + "/build-logs/step7/fix1", FW + "/build-logs/step7", FW + "/build-logs/step7/review-work", FW + "/docs", FW]
for n in sorted(names):
    checked += 1
    hit = [d for d in search if os.path.exists(os.path.join(d, n))]
    print("FILE %-40s %s" % (n, hit[0] if hit else "MISSING"))
    if not hit:
        problems.append("missing file " + n)

# 2. every `f1-full1.console` l.N (and lists after it in the same sentence) printed
lines = open(LOG, errors="replace").read().split("\n")
for m in re.finditer(r"f1-full1\.console`? ((?:l\.\d+(?:, \d+)*(?: to \d+)?[ ,;]*)+)", body):
    for num in re.findall(r"\d{4,5}", m.group(1)):
        checked += 1
        print("LOG l.%s: %s" % (num, lines[int(num) - 1][:150]))
for num in re.findall(r"\bl\.(3\d{4}|29\d{3}|28\d{3}|27\d{3})\b", body):
    checked += 1
    print("LOG l.%s: %s" % (num, lines[int(num) - 1][:150]))

# 3. every `path:line` or `path:line` to `:line` citation of a repo file
files = {}
for root, dirs, fs in os.walk(FW):
    if "build-logs" in root or "/docs/review" in root or "/tests/" in root + "/":
        continue
    for f in fs:
        files.setdefault(f, os.path.join(root, f))
files["rst.c"] = FW + "/modules/ring_store/src/rst.c"
files["dts"] = FW + "/boards/ringrec/ringrec_nrf54lm20a_cpuapp.dts"
for m in re.finditer(r"`([A-Za-z0-9_./\-]+):(\d+)`(?: to `:(\d+)`)?", body):
    path, a, b = m.group(1), int(m.group(2)), m.group(3)
    base = os.path.basename(path)
    full = os.path.join(FW, path) if os.path.exists(os.path.join(FW, path)) else files.get(base)
    if path.startswith("prj.conf"):
        full = FW + "/app/prj.conf"
    if full is None or not os.path.exists(full):
        print("CITE %s:%s UNRESOLVED" % (path, a))
        problems.append("unresolved " + path)
        continue
    L = open(full, errors="replace").read().split("\n")
    for k in ([a] + ([int(b)] if b else [])):
        checked += 1
        print("CITE %s:%d: %s" % (path, k, L[k - 1].strip()[:140] if k <= len(L) else "BEYOND END"))
        if k > len(L):
            problems.append("beyond end %s:%d" % (path, k))

# 4. counts against tables
bar = re.findall(r"^\| (R\d) [^|]*\| (PASS|FAIL|NOT PROVEN) \|", body, re.M)
print("BAR verdicts:", bar)
npass = sum(1 for _, v in bar if v == "PASS")
checked += 1
m = re.search(r"Bar: (\d+) of (\d+) PASS", body)
print("BAR count in text:", m.groups(), "from table:", npass, len(bar))
if m and (int(m.group(1)) != npass or int(m.group(2)) != len(bar)):
    problems.append("bar count disagrees")
sev = re.findall(r"^\| S7R-\d+ \| (blocker|major|minor|note) \|", body, re.M)
cnt = {s: sev.count(s) for s in ("blocker", "major", "minor", "note")}
m = re.search(r"Counts: blocker (\d+), major (\d+), minor (\d+), note (\d+)", body)
checked += 1
print("SEVERITY table:", cnt, "text:", m.groups())
if m and tuple(int(x) for x in m.groups()) != (cnt["blocker"], cnt["major"], cnt["minor"], cnt["note"]):
    problems.append("severity count disagrees")

# 5. numbers quoted from saved outputs
for f, pat in [("r7-stage-compare.txt", "stages started: 48 ended: 48"), ("r7-stage-compare.txt", "stages started: 50 ended: 50"),
               ("r1-refusal.console", "network_calls_after=0"), ("r2-mcuboot-spi-count.txt", "297"),
               ("version-compare.txt", "DIFFERS firmware/docs/board-notes.md"), ("r4-ringpins-flags.txt", "SAME FLAGS SD_CS"),
               ("r1-shasum-missing.console", "would PASS (no refusal) although the files differ"),
               ("board-notes-read-time.txt", "017302877ec81862"), ("start-date.txt", "02:24:03")]:
    checked += 1
    s = open(os.path.join(W, f)).read()
    print("NUM %s %r: %s" % (f, pat, "found x%d" % s.count(pat) if pat in s else "NOT FOUND"))
    if pat not in s:
        problems.append("not found %s in %s" % (pat, f))
vc = open(os.path.join(W, "version-compare.txt")).read()
print("NUM version-compare SAME=%d DIFFERS=%d" % (vc.count("SAME "), vc.count("DIFFERS ")))
r1 = open(os.path.join(W, "r1-refusal.console")).read()
print("NUM r1 cases exit=2: %d, REFUSED lines: %d" % (r1.count("exit=2 "), r1.count("REFUSED")))
fl = open(os.path.join(W, "r4-ringpins-flags.txt")).read()
print("NUM SAME FLAGS=%d no source=%d fixed-function=%d" % (fl.count("SAME FLAGS"), fl.count("no source"),
                                                              fl.count("from the chip's fixed function")))
checked += 4
import hashlib
cur = hashlib.sha256(open(FW + "/docs/board-notes.md", "rb").read()).hexdigest()
snap = hashlib.sha256(open(W + "/board-notes-as-read.md", "rb").read()).hexdigest()
checked += 1
print("BOARD-NOTES current sha256 %s snapshot %s %s" % (cur[:16], snap[:16], "SAME" if cur == snap else "CHANGED since read"))
print("AUDIT: %d claims checked, %d problems" % (checked, len(problems)))
for p in problems:
    print("PROBLEM", p)
