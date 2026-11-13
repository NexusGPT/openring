"""cite.py <file> <fixed string>...: prints "<line>: <text>" of the first line of <file> that holds each string
(or "NOT FOUND"). Used to take line numbers for iphone-notes.md from the saved log and from the source files."""
import sys

path = sys.argv[1]
lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
for pat in sys.argv[2:]:
    hit = next((i + 1 for i, l in enumerate(lines) if pat in l), None)
    if hit is None:
        print(f"NOT FOUND: {pat}")
    else:
        t = lines[hit - 1]
        print(f"{hit}: {t[:220]}")
