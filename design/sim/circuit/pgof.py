"""Prints the PDF page number (from the =====PAGE n===== markers of src/*.txt) for given line numbers.  Usage: pgof.py file line..."""
import sys, re
f = sys.argv[1]
marks = []
for i, l in enumerate(open(f, errors="replace"), 1):
    m = re.match(r"=====PAGE (\d+)=====", l)
    if m:
        marks.append((i, int(m.group(1))))
for ln in map(int, sys.argv[2:]):
    pg = [p for i, p in marks if i <= ln]
    print("line %d -> page %s" % (ln, pg[-1] if pg else "?"))
