"""Replace whole steps of assembly.md with the texts in new/. Reads the before copy, writes assembly.md.
Run: design/.venv/bin/python -I <this file>"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.join(HERE, "..", "assembly.md")
BEFORE = os.path.join(HERE, "assembly-before.md")
NEW = os.path.join(HERE, "new")

text = open(BEFORE, encoding="utf-8").read()


def span(t, first, after):
    """Start of '### Step first.' to start of '### Step after.'"""
    a = re.search(r"^### Step %d\. " % first, t, flags=re.M).start()
    b = re.search(r"^### Step %d\. " % after, t, flags=re.M).start()
    return a, b


jobs = [(2, 3, "step02.md"), (4, 5, "step04.md"), (6, 7, "step06.md"), (7, 8, "step07.md"),
        (8, 9, "step08.md"), (9, 10, "step09.md"), (14, 18, "step14-17.md")]
# apply from the end so earlier offsets stay valid
for first, after, fn in sorted(jobs, reverse=True):
    a, b = span(text, first, after)
    new = open(os.path.join(NEW, fn), encoding="utf-8").read().rstrip("\n") + "\n\n"
    print("replace steps %d..%d (chars %d to %d, %d lines) with %s (%d lines)"
          % (first, after - 1, a, b, text[a:b].count("\n"), fn, new.count("\n")))
    text = text[:a] + new + text[b:]
open(GUIDE, "w", encoding="utf-8").write(text)
print("written", os.path.abspath(GUIDE), "lines", text.count("\n"))
