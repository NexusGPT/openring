"""Final audit of U0's reply: pulls every claim-bearing token out of the reply file by itself (numbers, paths, quoted
text, case names, verdict words) and prints, for each, the saved evidence line that holds it (first match in the
evidence files), or NO MATCH. Usage: python3 -I u0-audit.py <reply file> <evidence file or folder> ..."""
import pathlib
import re
import sys

reply = pathlib.Path(sys.argv[1]).read_text()
ev_lines = []
for a in sys.argv[2:]:
    p = pathlib.Path(a)
    files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file() and x.suffix in (".log", ".md", ".h", ".c", ".sh", ".py", ".yaml", ".conf", ".txt", ".console", ".exit", ".overlay"))
    for f in files:
        try:
            for i, line in enumerate(f.read_text(errors="replace").split("\n"), 1):
                ev_lines.append((f"{f}:{i}", line))
        except OSError:
            pass

claims = []
for m in re.finditer(r"`([^`]+)`", reply):
    claims.append(("quote", m.group(1)))
for m in re.finditer(r"\b(test_[a-z0-9_]+)\b", reply):
    claims.append(("case", m.group(1)))
for m in re.finditer(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\w])", reply):
    claims.append(("number", m.group(1)))
for m in re.finditer(r"((?:/[\w.,\-]+)+|[\w\-]+/[\w./\-]+)", reply):
    claims.append(("path", m.group(1)))
for w in ("PASS", "FAIL", "exit 0", "exit 1", "RESULT", "UNIT PASS", "not provable", "blocked", "done"):
    if w in reply:
        claims.append(("verdict", w))

seen = set()
n_ok = n_bad = 0
for kind, c in claims:
    if (kind, c) in seen:
        continue
    seen.add((kind, c))
    needle = c
    hit = None
    for loc, line in ev_lines:
        if needle in line or needle.replace(",", "") in line:
            hit = (loc, line.strip()[:160])
            break
    if kind == "path" and hit is None:
        q = pathlib.Path(c)
        if q.exists():
            hit = (str(q), "exists")
    if hit:
        n_ok += 1
        print(f"OK {kind} {c!r} -> {hit[0]}: {hit[1]}")
    else:
        n_bad += 1
        print(f"NO MATCH {kind} {c!r}")
print(f"claims checked: {n_ok + n_bad}; matched {n_ok}; no match {n_bad}")
