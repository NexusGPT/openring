"""Check every number and every quote of a page against the file lines the same page line cites.
Run: python3 verify.py <page.md> [...] > verify.log 2>&1
A citation is `path:N` or `path:N` to `path:M` (path from the repository root). Each number on a page line
(outside citations, not a list ordinal at the line start, not part of a name like FH35C-15S or RGB565) must be
found as a number on one of the lines that page line cites (numeric equality, sign ignored, or the same text).
Each quote "..." of 3 words or more must be found verbatim on a cited line. Lines with numbers and no citation
fail every number."""
import re
import sys
from pathlib import Path

ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix()))
CIT = re.compile(r"`((?:design|firmware)/[^`\s:]+):(\d+)`(?:\s+to\s+`(?:design|firmware)/[^`\s:]+:(\d+)`)?")
NUM = re.compile(r"(?<![A-Za-z0-9_.+-])[-+]?\d+(?:\.\d+)?(?![A-Za-z0-9_]|\.\d)")
ANYNUM = re.compile(r"[-+]?\d+(?:\.\d+)?")
QUOTE = re.compile(r'"([^"]{8,}?)"')

checked = missing = qchecked = qmissing = 0
cache = {}


def lines_of(path):
    if path not in cache:
        p = ROOT / path
        cache[path] = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.exists() else None
    return cache[path]


for page in sys.argv[1:]:
    text = Path(page).read_text(encoding="utf-8").splitlines()
    print(f"== page {page}: {len(text)} lines")
    for i, line in enumerate(text, 1):
        cites = []
        bad_cite = []
        for m in CIT.finditer(line):
            path, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            L = lines_of(path)
            if L is None or b > len(L) or a < 1:
                bad_cite.append(m.group(0))
                continue
            cites.extend(L[a - 1:b])
        for bc in bad_cite:
            print(f"L{i}: CITATION NOT OPENABLE {bc}")
            missing += 1
        body = CIT.sub(" ", line)
        body = re.sub(r"`[^`]*`", " ", body)          # code names and bare paths are not values
        body = re.sub(r"^\s*\d+\.\s", " ", body)      # list ordinal
        body = re.sub(r"\b(?:0201|0402|0603)\b", " ", body)   # package size names, not values
        body = re.sub(r"^#+.*", " ", body)            # headings
        # the page's own cross references (not values): "question(s) 2, 7 and 8", "questions 2 to 4", "option 1"
        body = re.sub(r"\b(?:questions?|options?)\s+\d+(?:\s*(?:,|and|to)\s*\d+)*", " ", body)
        nums = [n for n in NUM.findall(body)]
        pool_txt = "\n".join(cites)
        pool = {abs(float(x)) for x in ANYNUM.findall(pool_txt)}
        for n in nums:
            checked += 1
            v = abs(float(n))
            ok = (v in pool) or (n in pool_txt) or any(abs(v - p) < 1e-9 for p in pool)
            if not ok:
                missing += 1
                print(f"L{i}: NOT FOUND {n}  (cites {len(cites)} lines)  | {line[:140]}")
        for q in QUOTE.findall(line):
            if len(q.split()) < 3:
                continue
            qchecked += 1
            if q not in pool_txt and ("## " + q) not in text:   # a quote of a heading of this page is found in the page
                qmissing += 1
                print(f"L{i}: QUOTE NOT FOUND \"{q}\"")
print(f"quotes checked {qchecked}, not found {qmissing}")
print(f"values checked {checked}, not found {missing}")
