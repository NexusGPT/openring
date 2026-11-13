#!/usr/bin/env python3
"""Audit design-review-2.md: for every `path:line` followed by a "quote", check the quote (with \\| read as |)
stands on that line of that file. Also lists `path:line` citations with no quote (line exists check only),
counts severities in the findings table, and prints mismatches. Prints how many claims it checked."""
import re, sys, os

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
CASE = "<scratch>/case-at-c64c4e6/design/case/"
REV = ROOT + "design/review/design-review-2.md"
text = open(REV, encoding="utf-8").read()


def resolve(p):
    if p.startswith("CASE/"):
        return CASE + p[5:]
    if p.startswith("review-2/"):
        return ROOT + "design/review/" + p
    return ROOT + p


pat = re.compile(r'`([A-Za-z0-9_./\-]+\.(?:md|csv|py|log|html|txt)):(\d+)`(?:\s*(?:row [^"]*?|x|as above|\(column[^)]*\)|line[^"]*?)?)?\s*"((?:[^"\\]|\\.)*)"')
checked = bad = 0
seen = set()
for m in pat.finditer(text):
    path, ln, quote = m.group(1), int(m.group(2)), m.group(3)
    q = quote.replace("\\|", "|").replace('\\"', '"')
    f = resolve(path)
    key = (path, ln, q)
    if key in seen:
        continue
    seen.add(key)
    checked += 1
    try:
        lines = open(f, encoding="utf-8").read().split("\n")
    except OSError as e:
        print(f"MISSING FILE {path}: {e}"); bad += 1; continue
    if ln > len(lines):
        print(f"NO LINE {path}:{ln} (file has {len(lines)})"); bad += 1; continue
    L = lines[ln - 1]
    # a quote may hold two parts joined by "..." in my text; check each part
    parts = [p.strip() for p in q.split(" ... ")] if " ... " in q else [q]
    ok = all(p in L for p in parts)
    if not ok:
        bad += 1
        print(f"MISMATCH {path}:{ln} quote={q[:90]!r}\n    line={L[:200]!r}")
# bare citations without quote: line must exist
bare = re.compile(r'`([A-Za-z0-9_./\-]+\.(?:md|csv|py|log|html|txt)):(\d+)`')
nb = 0
for m in bare.finditer(text):
    f = resolve(m.group(1)); ln = int(m.group(2))
    try:
        n = len(open(f, encoding="utf-8").read().split("\n"))
    except OSError:
        print(f"MISSING FILE (bare) {m.group(1)}"); bad += 1; continue
    nb += 1
    if ln > n:
        print(f"NO LINE (bare) {m.group(1)}:{ln}"); bad += 1
# severity counts from the findings table
rows = re.findall(r"^\| (G\d\d) \| (S\d) \|", text, re.M)
from collections import Counter
c = Counter(s for _, s in rows)
print("findings rows", len(rows), dict(c))
fstat = re.findall(r"^\| (F\d\d) \| (closed|partly closed|open)", text, re.M)
print("F rows", len(fstat), Counter(s for _, s in fstat))
print("D rows", len(re.findall(r"^\| D\d+ \|", text, re.M)), "K rows", len(re.findall(r"^\| K\d+ \|", text, re.M)))
print(f"quoted citations checked {checked}, bare citations checked {nb}, problems {bad}")
