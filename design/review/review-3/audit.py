"""Final audit of design-review-3.md: every `path:line` citation opens, and every quote that follows it
(before the next citation) is found on that line or within 2 lines. `:N` alone reuses the last path.
Also re-counts the findings table by severity and checks the counts line and the RESULT line."""
import os
import re
import sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
REV = os.path.join(ROOT, "design/review/design-review-3.md")
R3 = os.path.join(ROOT, "design/review/review-3")
text = open(REV, encoding="utf-8").read()
cache = {}


def lines_of(path):
    if path not in cache:
        for base in (ROOT, R3, os.path.join(ROOT, "design")):
            p = os.path.join(base, path.replace("review-3/", "")) if path.startswith("review-3/") else os.path.join(base, path)
            if os.path.isfile(p):
                cache[path] = open(p, encoding="utf-8", errors="replace").read().splitlines()
                break
        else:
            cache[path] = None
    return cache[path]


tok = re.compile(r"`([A-Za-z0-9_./-]*):(\d+)`|`([A-Za-z0-9_./-]+\.(?:log|csv|md|txt|json|py))`|\"((?:[^\"\\]|\\.)+)\"")
checked = ok = 0
bad = []
for ln_no, ln in enumerate(text.splitlines(), 1):
    cur = None
    last_path = None
    for m in tok.finditer(ln):
        if m.group(2):
            path = m.group(1) or last_path
            if not path:
                bad.append(f"review line {ln_no}: bare :{m.group(2)} with no earlier path")
                continue
            last_path = path
            fl = lines_of(path)
            checked += 1
            n = int(m.group(2))
            if fl is None:
                bad.append(f"review line {ln_no}: {path} does not open")
                cur = None
            elif n < 1 or n > len(fl):
                bad.append(f"review line {ln_no}: {path}:{n} beyond {len(fl)} lines")
                cur = None
            else:
                ok += 1
                cur = (path, n, fl)
        elif m.group(3):
            path = m.group(3)
            fl = lines_of(path)
            checked += 1
            if fl is None:
                bad.append(f"review line {ln_no}: {path} does not open")
                cur = None
            else:
                ok += 1
                last_path = path
                cur = (path, 0, fl)
        elif m.group(4) and cur:
            q = m.group(4).replace("\\|", "|").replace('\\"', '"')
            path, n, fl = cur
            window = " ".join(fl) if n == 0 else " ".join(fl[max(0, n - 3):n + 2])
            parts = [x.strip() for x in re.split(r"\.\.\.", q) if x.strip()]
            checked += 1
            if all(x in window for x in parts):
                ok += 1
            else:
                bad.append(f"review line {ln_no}: quote not in {path}{':' + str(n) if n else ''}: {q[:70]}")
# findings table counts
sev = {"S1": 0, "S2": 0, "S3": 0}
for ln in text.splitlines():
    m = re.match(r"^\| H\d\d \| (S[123]) \|", ln)
    if m:
        sev[m.group(1)] += 1
print("findings by severity from the table:", sev)
counts = re.search(r"S1: (\d+) .*?S2: (\d+) .*?S3: (\d+)", text)
print("counts line:", counts and counts.groups())
if counts and tuple(int(x) for x in counts.groups()) != (sev["S1"], sev["S2"], sev["S3"]):
    bad.append("counts line disagrees with the table")
last = text.rstrip("\n").splitlines()[-1]
rm = re.search(r"(\d+) S1, (\d+) S2 and (\d+) S3", last)
print("RESULT line:", last)
if not rm or tuple(int(x) for x in rm.groups()) != (sev["S1"], sev["S2"], sev["S3"]):
    bad.append("RESULT line counts disagree with the table")
nc = len(re.findall(r"^\| C\d+ \|", text, re.M))
print("contradiction rows:", nc)
if "Contradictions: %d" % nc not in text:
    bad.append("contradiction count disagrees")
if "—" in text or "–" in text:
    bad.append("an em or en dash is in the review")
print(f"claims checked {checked}, matched {ok}, problems {len(bad)}")
for b in bad:
    print("PROBLEM", b)
sys.exit(1 if bad else 0)
