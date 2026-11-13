"""Final audit: pull every number and path out of the final reply (look/final-reply.txt) and look-notes.md, print the saved evidence line each
matches (first hit in the evidence files), and list the ones with no match. Usage: python3 look/audit.py > look/audit.log"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)
EVID = [os.path.join(CASE, "out", "case_size.txt"), os.path.join(CASE, "out", "case_params.json")] + sorted(
    glob.glob(os.path.join(HERE, "*.log")) + glob.glob(os.path.join(HERE, "*.json")) + glob.glob(os.path.join(HERE, "*.txt")) + glob.glob(os.path.join(HERE, "*.time")))
EVID = [e for e in EVID if os.path.basename(e) not in ("final-reply.txt", "audit.log")]
SRC = [os.path.join(HERE, "final-reply.txt"), os.path.join(HERE, "look-notes.md")]


def lines_of(path):
    try:
        return open(path, errors="replace").read().split("\n")
    except OSError:
        return []


EV = {p: lines_of(p) for p in EVID}
total = miss = 0
for src in SRC:
    print(f"== {os.path.basename(src)}")
    for ln_no, ln in enumerate(lines_of(src), 1):
        claims = set(re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w])", ln)) | set(re.findall(r"/Users/[^\s`,;)]+", ln))
        for c in sorted(claims):
            if c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"):
                continue
            total += 1
            hit = None
            if c.startswith("/Users/"):
                hit = f"exists={os.path.exists(c.rstrip('.'))}"
            else:
                for p, ls in EV.items():
                    for i, e in enumerate(ls):
                        if c in e:
                            hit = f"{os.path.basename(p)}:{i + 1}: {e.strip()[:110]}"
                            break
                    if hit:
                        break
            if hit is None:
                miss += 1
            print(f"  {os.path.basename(src)}:{ln_no} [{c}] -> {hit or 'NO MATCH'}")
print(f"claims checked {total}; no match {miss}")
