# Audit: pull every number and quoted string out of final_reply.md and find each in the saved evidence and deliverables.
import glob
import os
import re
import sys

C = sys.argv[1]
reply = open(os.path.join(C, "evidence", "final_reply.md")).read()
srcs = {}
for pat in ("evidence/*.log", "evidence/html/*.log", "*.md", "case-bom.csv", "out/case_size.txt", "case.py", "case_check.py"):
    for f in glob.glob(os.path.join(C, pat)):
        if f.endswith("final_reply.md") or f.endswith("CHECKLIST.md"):
            continue
        srcs[os.path.relpath(f, C)] = open(f, errors="replace").read()
print("characters in reply:", len(reply))
claims = sorted(set(re.findall(r"\d+(?:\.\d+)?", reply)))
quotes = re.findall(r"`([^`]+)`", reply)
checked = 0
nomatch = []
for c in claims:
    checked += 1
    hits = [n for n, t in srcs.items() if re.search(r"(?<![\d.])" + re.escape(c) + r"(?![\d])", t)]
    if hits:
        f = hits[0]
        line = next(l for l in srcs[f].splitlines() if re.search(r"(?<![\d.])" + re.escape(c) + r"(?![\d])", l))
        print(f"NUM {c}: {f}: {line.strip()[:150]}")
    else:
        nomatch.append(c)
        print(f"NUM {c}: NO MATCH")
for q in quotes:
    checked += 1
    hits = [n for n, t in srcs.items() if q in t]
    print(f"QUOTE {q[:70]}: {hits[:3] if hits else 'NO MATCH'}")
    if not hits:
        nomatch.append(q)
# last-line quotes
for f, q in (("evidence/run_done_final.log", "mar. 10 nov. 2026 15:28:29 CET"),
             ("evidence/run_fault_test.log", '52:PINB_TOP = -(PIN["free_h"] - PIN["mid"])  # mid stroke when the block rests on the seat'),
             ("case-notes.md", None)):
    lines = open(os.path.join(C, f)).read().rstrip("\n").splitlines()
    last = lines[-1]
    ok = (q == last) if q else (last in reply)
    checked += 1
    print(f"LASTLINE {f}: {'MATCH' if ok else 'DIFFERS'}: {last[:120]}")
    if not ok:
        nomatch.append(f)
    if f.endswith("run_done_final.log"):
        print(f"  line before last: {lines[-2]}")
# disagreement checks on key figures
for key, pat in (("transfer min per hour", r"6\.32 min"), ("outer size", r"33\.6 x 33\.4 x 55\.2"), ("pairs", r"594 pairs|pairs checked 594")):
    print(f"CONSISTENT {key}: files stating it: {[n for n, t in srcs.items() if re.search(pat, t)]}")
print(f"claims checked {checked}; without match {len(nomatch)}: {nomatch}")
