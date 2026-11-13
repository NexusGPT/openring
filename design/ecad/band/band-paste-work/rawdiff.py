#!/usr/bin/env python3
"""Text compare of board files, uuid lines removed. usage: rawdiff.py <dirA> <dirB> <ext list comma>"""
import os, re, sys, difflib
a, b, exts = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
names = [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]
nd = 0
for n in names:
    for e in exts:
        A = [l for l in open(os.path.join(a, n + e)).read().splitlines() if "(uuid " not in l and "(tstamp " not in l]
        B = [l for l in open(os.path.join(b, n + e)).read().splitlines() if "(uuid " not in l and "(tstamp " not in l]
        d = [l for l in difflib.unified_diff(A, B, lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
        nd += 1 if d else 0
        print(f"{n}{e}: {'identical (uuid lines removed)' if not d else 'DIFF %d lines' % len(d)}")
        for l in d[:6]:
            print("   ", l)
print(f"RESULT: files compared {len(names) * len(exts)}, differing {nd}")
