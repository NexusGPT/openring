import sys, re
f, phrases = sys.argv[1], sys.argv[2:]
page, lines = None, open(f, encoding="utf-8", errors="replace").read().split("\n")
for i, l in enumerate(lines, 1):
    m = re.match(r"--- page (\d+)", l)
    if m:
        page = int(m.group(1))
    for p in phrases:
        if p.lower() in l.lower():
            print(f"{f.split('/')[-1]} line {i} page {page}: {l.strip()[:220]}")
