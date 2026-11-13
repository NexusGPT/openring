#!/usr/bin/env python3
"""u9-compare.py <run log> <design manifest> <step 5 log>: compare the picture manifests of the U9 short run with the saved manifest of
the screens (design/software/os/screens/manifest.md) and the frame hashes with the SCREENPIC lines of step 5's last full run."""
import re, sys
run, design, step5 = [open(a, encoding="utf-8").read() for a in sys.argv[1:4]]
def rows(text):
    d = {}
    for l in text.splitlines():
        if l.startswith("| ") and not l.startswith("| picture") and not l.startswith("|---"):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            d[c[0]] = c
    return d
secs = re.split(r"^=== manifest (native_sim|bsim)$", run, flags=re.M)
mine = {secs[i]: rows(secs[i + 1].split("=== ")[0]) for i in range(1, len(secs), 2)}
ref = rows(design)
s5 = {}
for m in re.finditer(r"^SCREENPIC (\S+) \| scene: (.*?) \| 240x120 \| hash ([0-9a-f]+) \| lit px (\d+)", step5, re.M):
    s5.setdefault(m.group(1), set()).add((m.group(2), m.group(3), m.group(4)))
bad = 0
print("design manifest rows:", len(ref), "; step 5 pictures:", len(s5), "; step 5 distinct (scene, hash, lit) per picture max:", max(len(v) for v in s5.values()))
for board, r in mine.items():
    ok = 0
    for n, c in r.items():
        same_design = ref.get(n) == c
        same5 = (c[1], c[3], c[4]) in s5.get(n, set())
        if same_design and same5:
            ok += 1
        else:
            bad += 1
            print("DIFF", board, n, "design", same_design, "step5", same5)
    print(board, "pictures", len(r), "equal in every column to the design manifest and to step 5:", ok)
print("RESULT", "EQUAL" if bad == 0 and all(len(r) == 21 for r in mine.values()) and len(mine) == 2 else "DIFFERENT")
