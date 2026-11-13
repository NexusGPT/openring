#!/usr/bin/env python3
"""Lists each line of the live files (input: the hit list logs/grep_c84_10uF_live.txt) where C84 and a 10 uF value stand
within 80 characters of each other, and no 4.7 uF value is in that window. Output: file:line: window."""
import re, sys
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
seen = set()
for l in open(sys.argv[1]):
    f, n = l.split(':', 2)[:2]
    if (f, n) in seen:
        continue
    seen.add((f, n))
    text = open(R + f, errors='replace').read().split('\n')[int(n) - 1]
    for m in re.finditer(r'C84', text):
        w = text[max(0, m.start() - 80): m.end() + 80]
        if re.search(r'10 ?uF', w) and not re.search(r'4\.7 ?uF', w):
            print('%s:%s: %s' % (f, n, w.replace('\n', ' ')))
            break
