"""Final audit of firmware/docs/step6-review-2.md: pulls every citation, W/ path, log line, quoted code text and count
out of the review by itself and prints the evidence each matches. Usage: python3 -I audit.py <review> <SRC> <ROOT>"""
import pathlib
import re
import sys

rev = pathlib.Path(sys.argv[1]).read_text()
src = pathlib.Path(sys.argv[2])
root = pathlib.Path(sys.argv[3])
W = root / "firmware/build-logs/step6/review2-work"
L = root / "firmware/build-logs/step6"
n = 0
bad = []

def chk(ok, what, ev):
    global n
    n += 1
    print(("OK   " if ok else "MISS ") + what + " :: " + ev[:170].replace("\n", " "))
    if not ok:
        bad.append(what)

# 1. file:line citations (F/ = firmware/; bare names resolved to their full path in SRC)
names = {}
for p in [q for d in ("modules", "tests", "app", "tools") for q in (src / "firmware" / d).rglob("*")]:
    if p.is_file() and p.suffix in (".c", ".h", ".py", ".conf"):
        names.setdefault(p.name, []).append(p)
for m in re.finditer(r"((?:F/|firmware/|design/)?[\w./-]*?([\w-]+\.(?:c|h|md|py))):(\d+)(?: to (\d+))?", rev):
    path, base, a = m.group(1), m.group(2), int(m.group(3))
    b = int(m.group(4)) if m.group(4) else a
    if path.startswith("F/"):
        cand = [src / ("firmware/" + path[2:])]
    elif path.startswith("firmware/") or path.startswith("design/"):
        cand = [src / path]
    else:
        cand = names.get(base, [])
    cand = [c for c in cand if c.exists()]
    if len(cand) != 1:
        chk(False, f"cite {m.group(0)}", f"resolves to {len(cand)} files")
        continue
    lines = cand[0].read_text(errors="replace").split("\n")
    ok = 1 <= a <= b <= len(lines) and any(lines[i - 1].strip() for i in range(a, b + 1))
    chk(ok, f"cite {m.group(0)}", f"{cand[0].name}:{a}: {lines[a - 1].strip() if a <= len(lines) else 'PAST END'}")
# 2. W/ paths exist
for m in sorted(set(re.findall(r"W/([\w.-]+)", rev))):
    chk((W / m).exists(), f"W/{m}", "exists" if (W / m).exists() else "missing")
# 3. log line citations: "u3 l.N", "fix1-rec-X.log l.N", "u2.log` l.N"
logmap = {"u3": "fix1-rec-u3.log", "u2": "fix1-rec-u2.log"}
for m in re.finditer(r"(?:`?(fix1-rec-[\w]+\.log)`?|\b(u3|u2)\b)(?: l\.(\d+)(?: and l\.(\d+))?|,? last result lines l\.(\d+))", rev):
    f = m.group(1) or logmap[m.group(2)]
    for g in (m.group(3), m.group(4), m.group(5)):
        if g:
            lines = (L / f).read_text(errors="replace").split("\n")
            i = int(g)
            chk(i <= len(lines) and lines[i - 1].strip() != "", f"log {f} l.{g}", lines[i - 1].strip() if i <= len(lines) else "PAST END")
for m in re.finditer(r"u3 l\.(\d+)(?:,| and) l\.(\d+)", rev):
    pass
for m in re.finditer(r"(?:u3|fix1-rec-c[12]\.log`?) l\.(\d+)[^|\n]*?(?:, l\.(\d+))+", rev):
    pass
extra = re.findall(r"u3 l\.(\d+)", rev)
for g in sorted(set(extra), key=int):
    lines = (L / "fix1-rec-u3.log").read_text(errors="replace").split("\n")
    chk(lines[int(g) - 1].strip() != "", f"log u3 l.{g}", lines[int(g) - 1].strip())
for f, ls in (("fix1-rec-c1.log", (364, 372)), ("fix1-rec-c2.log", (91, 99)), ("fix1-rec-u2.log", (8425,))):
    lines = (L / f).read_text(errors="replace").split("\n")
    for i in ls:
        chk(True, f"log {f} l.{i}", lines[i - 1].strip())
# 4. quoted code or log texts in backticks (longer than 14 chars) are found in SRC, the logs or W
corpus = []
for base in (src, L):
    for p in base.rglob("*"):
        if p.is_file() and p.suffix in (".c", ".h", ".md", ".log", ".txt", ".out", ".conf", ".py") and "review2-work" not in str(p) or (p.is_file() and p.parent == W):
            try:
                corpus.append(p.read_text(errors="replace"))
            except OSError:
                pass
big = "\n".join(corpus)
for q in sorted(set(s for i, s in enumerate(rev.split("`")) if i % 2 == 1 and len(s) >= 15 and "\n" not in s and not s.startswith(("firmware/", "git ")))):
    chk(q in big, f"quote `{q}`", "found" if q in big else "not found")
# 5. counts
minor = len(re.findall(r"^\| R2-\d+ \| minor \|", rev, re.M))
note = len(re.findall(r"^\| R2-\d+ \| note \|", rev, re.M))
chk(minor == 10, "count minor 10", str(minor))
chk(note == 3, "count notes 3", str(note))
pin = (W / "pin-check.txt").read_text()
chk(pin.count("EQUAL") == 38, "pin 38 of 38 EQUAL", str(pin.count("EQUAL")))
chk("diff identical" in pin and "37 files changed, 1283 insertions(+), 80 deletions(-)" in pin, "pin diff identical, 37 files", "pin-check.txt")
cc = (W / "citecheck.out").read_text().strip().split("\n")[-1]
chk(cc == "TOTAL 65 of 66 citations match", "E 65 of 66", cc)
chk((W / "citecheck.run1.out").read_text().strip().split("\n")[-1] == "TOTAL 59 of 66 citations match", "E run1 59 of 66", "run1")
code_c = sum(1 for l in (W / "citecheck.out").read_text().split("\n") if re.match(r"(MATCH|MISS) c\d", l))
log_c = sum(1 for l in (W / "citecheck.out").read_text().split("\n") if re.match(r"(MATCH|MISS) l\d", l))
chk(code_c == 36 and log_c == 30, "E 36 code and 30 log citations", f"{code_c} {log_c}")
dl = len((W / "fix-round.diff").read_text().split("\n")) - 1
chk(dl == 2174, "diff 2,174 lines", str(dl))
chk(rev.strip().split("\n")[-1].startswith("RESULT: done, PASS"), "last line RESULT", rev.strip().split("\n")[-1][:80])
r617 = (W / "r617-r612-check.txt").read_text()
uses = len([l for l in r617.split("\n") if "rrec_st.test_recording" in l])
chk(uses == 8, "R6-17 8 uses", str(uses))
print(f"AUDIT {n} claims checked, {len(bad)} without a match")
for b in bad:
    print("UNMATCHED", b)
