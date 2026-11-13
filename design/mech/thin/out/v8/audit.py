#!/usr/bin/env python3
"""Final audit: pulls every claim (numbers, RESULT lines, paths, quoted words) out of the final reply and out of band-fit-notes.md by itself (regex, no hand list),
prints the saved evidence line each matches (grep -F over out/v8/*.log, out/v8/*.txt, the check logs and the edited files), and every number with no match.
Usage: audit.py <reply.md> <notes.md> > audit.log ; the last line says how many claims were checked and how many have no match."""
import re, sys, glob, os
from pathlib import Path

T = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin"))
files = [Path(f) for pat in ("out/v8/*.log", "out/v8/*.txt", "out/v8/*.md", "out/v8/broken_trunk/*.log", "out/v8/*.csv", "out/v8/*.json") for f in glob.glob(str(T / pat))]
files += [T / "thin.py", T / "check_thin.py", T / "placement.csv", Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/band/band-notes.md")),
          Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/band/band-interface.md")), Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/band/evidence/final/check_all.log"))]
texts = {}
for f in files:
    try:
        texts[f] = f.read_text(errors="replace").splitlines()
    except Exception:
        pass
src = [Path(a).read_text() for a in sys.argv[1:3]]
claims = []
for k, t in enumerate(src):
    for n, line in enumerate(t.splitlines(), 1):
        for m in re.finditer(r"RESULT[: ][^`|]*", line):
            claims.append(("result", m.group(0).strip(), k, n))
        for m in re.finditer(r"(?<![\w.])-?\d+\.\d+(?![\w.])|(?<![\w.])\d{2,}(?![\w.])", line):
            claims.append(("number", m.group(0), k, n))
        for m in re.finditer(r"(/Users/[\w./_-]+)", line):
            claims.append(("path", m.group(1).rstrip("."), k, n))
        for m in re.finditer(r"`([^`]{4,80})`", line):
            claims.append(("quote", m.group(1), k, n))
seen = set()
nomatch = 0
checked = 0
for kind, val, k, n in claims:
    key = (kind, val)
    if key in seen:
        continue
    seen.add(key)
    checked += 1
    hit = None
    if kind == "path":
        hit = f"exists: {os.path.exists(val)}"
        if not os.path.exists(val):
            nomatch += 1
    else:
        for f, ls in texts.items():
            for i, l in enumerate(ls, 1):
                if val in l:
                    hit = f"{f}:{i}: {l[:160]}"
                    break
            if hit:
                break
        if hit is None:
            nomatch += 1
            hit = "NO MATCH"
    print(f"[{kind}] {val!r} (source {k + 1} line {n}) -> {hit}")
print(f"claims checked {checked}, without a match {nomatch}")
