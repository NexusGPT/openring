#!/usr/bin/env python3
"""Count differing pixels of two P6 ppm files of the same size. usage: ppmdiff.py a.ppm b.ppm"""
import sys


def load(p):
    d = open(p, "rb").read()
    parts = d.split(b"\n", 3)
    w, h = map(int, parts[1].split())
    return w, h, parts[3]


wa, ha, A = load(sys.argv[1]); wb, hb, B = load(sys.argv[2])
if (wa, ha) != (wb, hb):
    print(f"size differs {wa}x{ha} vs {wb}x{hb}"); sys.exit(1)
n = sum(1 for i in range(0, len(A), 3) if A[i:i + 3] != B[i:i + 3])
print(f"pixels {wa}x{ha}, differing {n}")
sys.exit(0 if n == 0 else 1)
