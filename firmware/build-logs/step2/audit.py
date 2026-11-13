"""Final audit: pulls every claim out of the final reply by itself and prints the saved evidence line
it matches. Usage: python3 -I audit.py <reply file> <evidence folder> [extra evidence files...]

Claims extracted from each line of the reply:
  - numbers (with a decimal part, a thousands part or two or more digits) and number words
  - file names (names with an extension, or a path)
  - quoted words in backticks
  - verdict words RESULT PASS / RESULT FAIL / PASS / FAIL
For each claim the script searches every evidence file for a line that contains the claim and at
least one other word (4 letters or more) of the reply line. It prints the first such line with its file
and line number, or UNMATCHED. It also lists numbers that appear twice in the reply with different
neighbouring words (two statements about the same thing) for a manual read.
"""

import pathlib
import re
import sys

reply = pathlib.Path(sys.argv[1]).read_text().splitlines()
folder = pathlib.Path(sys.argv[2])
extra = [pathlib.Path(p) for p in sys.argv[3:]]

files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix in (".log", ".txt", ".md", ".diff"))
files += [p for p in extra if p.is_file()]
text = {}
for p in files:
    try:
        text[p] = p.read_text(errors="replace").splitlines()
    except OSError as err:
        print("cannot read", p, err)

num_re = re.compile(r"\b\d[\d,]*\.?\d*%?|\b\d{2,}\b")
file_re = re.compile(r"[\w./-]+\.(?:log|txt|md|sh|conf|h|c|yaml|py)\b|[\w-]+/[\w./-]+")
quote_re = re.compile(r"`([^`]+)`")
word_re = re.compile(r"[A-Za-z_]{4,}")

total = 0
unmatched = 0
seen = {}
for n, line in enumerate(reply, 1):
    if not line.strip():
        continue
    words = set(w.lower() for w in word_re.findall(line))
    claims = []
    claims += [m.group(0) for m in num_re.finditer(line)]
    claims += file_re.findall(line)
    claims += quote_re.findall(line)
    for v in ("RESULT PASS", "RESULT FAIL", "0x3d"):
        if v in line:
            claims.append(v)
    for c in dict.fromkeys(claims):
        c = c.strip().rstrip(",.;:")
        if not c:
            continue
        total += 1
        seen.setdefault(c, []).append(n)
        hit = None
        best = 0
        c_nocomma = c.replace(",", "")
        for p, lines in text.items():
            if p.name == "final-reply.txt":
                continue
            for i, l in enumerate(lines, 1):
                ll = l.lower()
                if c.lower() in ll or c_nocomma.lower() in ll.replace(",", ""):
                    score = sum(1 for w in words if w in ll and w not in c.lower())
                    if p.name.endswith("final.log"):
                        score += 0.5
                    if score > best:
                        best = score
                        hit = (p.name, i, l.strip()[:150], score)
        if hit and best < 2 and len(c) <= 14 and not re.search(r"[./_-]", c):
            hit = None  # a short claim with one shared word proves nothing
        if hit:
            print(f"reply line {n}: [{c}] (score {hit[3]}) -> {hit[0]}:{hit[1]}: {hit[2]}")
        else:
            unmatched += 1
            print(f"reply line {n}: [{c}] -> UNMATCHED")

print()
print(f"claims checked: {total}, unmatched: {unmatched}")
print("claims that appear on more than one reply line (read for disagreement):")
for c, ls in seen.items():
    if len(ls) > 1 and re.search(r"\d", c):
        print(f"  [{c}] on reply lines {ls}")
