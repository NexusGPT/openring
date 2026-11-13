"""Map each line of the guide before the rewrite to its line after it.
Exact text first (unique match); else the same field of the same step (old steps 14, 15, 16 are now 15, 16, 14);
else a table row by its first cell; else None. Used by fill_joints.py and cites_moved.py."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "assembly-before.md")
NEW = os.path.join(HERE, "..", "assembly.md")
RENUM = {14: 15, 15: 16, 16: 14}


def load(p):
    return open(p, encoding="utf-8").read().split("\n")


def index(lines):
    """line number -> (step, field) for section 2 lines; heading -> (step, 'head')."""
    out, step = {}, None
    for i, l in enumerate(lines, 1):
        m = re.match(r"### Step (\d+)\. ", l)
        if m:
            step = int(m.group(1))
            out[i] = (step, "head")
            continue
        if l.startswith("## "):
            step = None
        m = re.match(r"- \*\*([A-Za-z ]+?):\*\* ", l)
        if m and step is not None:
            out[i] = (step, m.group(1))
    return out


def first_cell(l):
    if l.startswith("| "):
        return l.split("|")[1].strip()
    return None


def build():
    old, new = load(OLD), load(NEW)
    oi, ni = index(old), index(new)
    rev = {v: k for k, v in ni.items()}
    newpos = {}
    for i, l in enumerate(new, 1):
        newpos.setdefault(l, []).append(i)
    cells = {}
    for i, l in enumerate(new, 1):
        c = first_cell(l)
        if c:
            cells.setdefault(c, []).append(i)
    m = {}
    for i, l in enumerate(old, 1):
        how, to = None, None
        if l.strip() and len(newpos.get(l, [])) == 1:
            how, to = "same text", newpos[l][0]
        elif i in oi:
            st, f = oi[i]
            st2 = RENUM.get(st, st)
            if (st2, f) in rev:
                how, to = "same field of step %d (was step %d)" % (st2, st), rev[(st2, f)]
            elif (st2, "head") in rev and f == "head":
                how, to = "heading", rev[(st2, "head")]
        elif first_cell(l) and len(cells.get(first_cell(l), [])) == 1:
            how, to = "table row by first cell, text changed", cells[first_cell(l)][0]
        elif len(l.strip()) > 25 and not l.startswith("|---"):
            hits = [j for j, nl in enumerate(new, 1) if nl[:25] == l[:25]]
            if len(hits) == 1:
                how, to = "same first 25 characters, text changed", hits[0]
        if to is None and l.startswith("| Charging pads: plated land or soldered disc"):
            hits = [j for j, nl in enumerate(new, 1) if nl.startswith("| Charging pads: fixed")]
            if len(hits) == 1:
                how, to = "row rewritten (review 3 G4), found by its new start", hits[0]
        m[i] = (to, how, l)
    return m


if __name__ == "__main__":
    for k, (to, how, l) in sorted(build().items()):
        print("%d -> %s | %s | %s" % (k, to, how, l[:80]))
