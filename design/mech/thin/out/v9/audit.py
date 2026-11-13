#!/usr/bin/env python3
"""Audit of model-v9-notes.md: every path it names must exist; every backticked quote of a log line must be found in the evidence files
(out/v9 recursively, design/mfg/tools/logs/draw_v9*.log, the delivered files); every number of the per-size table must be in its size log.
Prints each claim with its match and the counts."""
import re, glob, os
T = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin")
D = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design")
notes = open(f"{T}/model-v9-notes.md").read()
ev = [f for f in glob.glob(f"{T}/out/v9/**/*", recursive=True) if os.path.isfile(f) and os.path.getsize(f) < 5e6 and not f.endswith(".json")]
ev += glob.glob(f"{D}/mfg/tools/logs/draw_v9*.log") + [f"{T}/thin.py", f"{T}/check_thin.py"]
texts = {}
for f in ev:
    try:
        texts[f] = open(f, errors="replace").read()
    except Exception:
        pass
bad = n = 0
for p in sorted(set(re.findall(r"out/v9/[\w./-]+", notes))):
    p = p.rstrip(".,)")
    n += 1
    ok = os.path.exists(f"{T}/{p}")
    bad += not ok
    print(f"path {p}: {'exists' if ok else 'MISSING'}")
for p in sorted(set(re.findall(r"design/[\w./-]+\.(?:md|py|csv|log|step|sh)", notes))):
    n += 1
    ok = os.path.exists(f"{D}/../{p}") or os.path.exists(f"{T}/{p}")
    bad += not ok
    print(f"path {p}: {'exists' if ok else 'MISSING'}")
for q in sorted(set(re.findall(r"(?<![`\w])`([^`\n|]{8,}?)`(?!`)", notes))):
    if "/" in q and " " not in q:
        continue
    n += 1
    parts = [x.strip() for x in q.split("...")]
    hit = next((f for f, t in texts.items() if all(x in t for x in parts if x)), None)
    bad += hit is None
    print(f"quote `{q[:90]}`: {'in ' + os.path.relpath(hit, T) if hit else 'NOT FOUND'}")
for row in re.findall(r"^\| US (\d+) \| out/v9/final_us\d+\.log \|(.*)$", notes, re.M):
    t = open(f"{T}/out/v9/final_us{row[0]}.log").read()
    for num in re.findall(r"\d+\.\d{4}", row[1]):
        n += 1
        ok = num in t
        bad += not ok
        print(f"US {row[0]} number {num}: {'in its log' if ok else 'NOT IN LOG'}")
print(f"claims checked {n}, without evidence {bad}")
