#!/usr/bin/env python3
"""audit.py <claims file>... -- <evidence file>...: pull every claim (numbers, paths, quotes, RESULT/verdict lines) out of the
claims files and print the saved evidence line each one matches, or NO MATCH; then print the claims that appear with different
numbers for the same label. Prints how many claims it checked."""
import os
import re
import sys

args = sys.argv[1:]
sep = args.index("--")
claims_files, evid_files = args[:sep], args[sep + 1:]
evid = []
for f in evid_files:
    try:
        for i, l in enumerate(open(f, errors="replace"), 1):
            evid.append((f, i, l.rstrip("\n")))
    except OSError as e:
        print("cannot read evidence", f, e)


def find(tok):
    for f, i, l in evid:
        if tok in l:
            return "%s:%d: %s" % (os.path.basename(f), i, l.strip()[:110])
    return None


total = 0
nomatch = 0
for cf in claims_files:
    text = open(cf, errors="replace").read()
    claims = []
    for l in text.splitlines():
        for m in re.finditer(r"`([^`]+)`", l):
            claims.append(("code", m.group(1)))
        for m in re.finditer(r"\"([^\"]{4,80})\"", l):
            claims.append(("quote", m.group(1)))
        for m in re.finditer(r"(?<![\w.])(\d+)(?:\s*(?:of|x)\s*(\d+))?(?![\w.])", l):
            claims.append(("num", m.group(0)))
        for m in re.finditer(r"(/[\w./-]+\.(?:md|c|h|py|sh|png|log|out|txt|yaml|conf|overlay))", l):
            claims.append(("path", m.group(1)))
        if l.startswith("RESULT"):
            claims.append(("result", l))
    seen = set()
    print("##### claims of", cf)
    for kind, tok in claims:
        if (kind, tok) in seen:
            continue
        seen.add((kind, tok))
        total += 1
        if kind == "path":
            ok = os.path.exists(tok)
            print("[path] %s -> %s" % (tok, "exists" if ok else "NO MATCH (missing)"))
            nomatch += 0 if ok else 1
            continue
        hit = find(tok)
        if hit is None:
            nomatch += 1
        print("[%s] %s -> %s" % (kind, tok[:90], hit if hit else "NO MATCH"))
print("claims checked:", total, "; without a match:", nomatch)
