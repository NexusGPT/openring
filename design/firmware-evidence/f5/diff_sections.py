"""List every changed line range of firmware.md (F5) against the F4 copy, with the section that holds it,
and the line range of every section heading in F5."""
import difflib
import re
import sys

old = open(sys.argv[1], encoding="utf-8").read().splitlines()
new = open(sys.argv[2], encoding="utf-8").read().splitlines()
heads = [(i + 1, l) for i, l in enumerate(new) if re.match(r"^#{2,3} ", l) or l.startswith("Changes from F4 to F5") or l.startswith("Peripheral instances")]
def sec_of(n):
    cur = "top (title, header, change lists, how to read)"
    for ln, h in heads:
        if ln <= n:
            cur = h
    return cur
print("Section line ranges in F5:")
for k, (ln, h) in enumerate(heads):
    end = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(new)
    print(f"  {ln}-{end}: {h[:90]}")
print("\nChanged hunks (F4 lines -> F5 lines):")
sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
total = 0
per = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    total += 1
    s = sec_of(j1 + 1 if j2 > j1 else j1)
    per.setdefault(s, []).append((j1 + 1, j2))
    print(f"  {tag}: F4 {i1 + 1}-{i2} -> F5 {j1 + 1}-{j2}  [{s[:70]}]")
print(f"\n{total} hunks; F4 {len(old)} lines, F5 {len(new)} lines")
print("\nPer section (F5 line ranges changed):")
for s, rs in per.items():
    print(f"  {s[:80]}: " + ", ".join(f"{a}-{b}" if b >= a else f"deleted before {a}" for a, b in rs))
