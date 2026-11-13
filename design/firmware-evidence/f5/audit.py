"""Final audit: pull every number, path, quote and count claim out of the final reply and the notes by
pattern (not from a hand list), and print the first saved line that holds each; list the unmatched."""
import glob
import os
import re
import sys

repo = sys.argv[1]
d = os.path.join(repo, "design")
ev = os.path.join(d, "firmware-evidence", "f5")
targets = [os.path.join(ev, sys.argv[2] if len(sys.argv) > 2 else "final_reply.md"), os.path.join(d, "firmware-f5-notes.md")]
RB = sys.argv[3] if len(sys.argv) > 3 else "run_broken_final.log"
corpus_files = sorted(set(
    glob.glob(os.path.join(ev, "*.log")) + glob.glob(os.path.join(ev, "*.txt")) + glob.glob(os.path.join(ev, "*.py"))
    + glob.glob(os.path.join(ev, "broken_final", "*.log")) + glob.glob(os.path.join(ev, "broken_gain0", "*.log"))
    + [os.path.join(d, "firmware.md"), os.path.join(d, "firmware-check.py"), os.path.join(d, "architecture.md"),
       os.path.join(d, "parts", "research-npm1304.md"), os.path.join(d, "ecad", "motor-drive", "motor-drive.md"),
       os.path.join(d, "mfg", "assembly", "assembly.md"), os.path.join(d, "ecad", "ring", "sch-notes.md"),
       os.path.join(d, "ecad", "ring", "netlist.csv"), os.path.join(d, "ecad", "ring", "parts.csv"),
       os.path.join(d, "datasheets", "npm1304_datasheet_v1_0.txt"),
       os.path.join(d, "mech", "mic-path", "datasheets", "knowles-spk0641ht4h-1_chipsmall.txt"),
       os.path.join(d, "datasheets", "mic-research", "im68d128b-brief.txt"),
       os.path.join(ev, "before", "firmware-F4.md")]))
corpus = []
for f in corpus_files:
    for i, ln in enumerate(open(f, encoding="utf-8", errors="replace").read().splitlines(), 1):
        corpus.append((f, i, ln))

def find(tok):
    for f, i, ln in corpus:
        if tok in ln:
            return f"{os.path.relpath(f, repo)}:{i}"
    return None

checked = 0
unmatched = []
for t in targets:
    text = open(t, encoding="utf-8").read()
    if t.endswith("firmware-f5-notes.md"):
        # the notes are themselves a target; do not let them prove their own claims
        pass
    print(f"\n=== {os.path.relpath(t, repo)}")
    nums = sorted(set(re.findall(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?![\w])", text)), key=lambda x: (len(x), x))
    for n in nums:
        checked += 1
        hit = find(n)
        if hit is None and "," in n:
            hit = find(n.replace(",", ""))
        print(f"number {n}: {hit}")
        if hit is None:
            unmatched.append((t, "number", n))
    for p in sorted(set(re.findall(r"`(design/[^`\s]+|/Users/[^`\s]+)`", text) + re.findall(r"(<home>/[^\s,]+)", text))):
        checked += 1
        full = p if p.startswith("/") else os.path.join(repo, p)
        full = full.rstrip(".")
        ok = bool(glob.glob(full)) or os.path.exists(full)
        print(f"path {p}: {'exists' if ok else 'MISSING'}")
        if not ok:
            unmatched.append((t, "path", p))
    for q in sorted(set(re.findall(r"\"([^\"]{6,})\"", text))):
        checked += 1
        hit = find(q)
        print(f"quote \"{q[:60]}\": {hit}")
        if hit is None:
            unmatched.append((t, "quote", q))
    for lg in sorted(set(re.findall(r"\b([a-z_0-9]+\.log)\b", text))):
        checked += 1
        ok = os.path.exists(os.path.join(ev, lg)) or os.path.exists(os.path.join(ev, "broken", lg))
        print(f"log {lg}: {'exists' if ok else 'MISSING'}")
        if not ok:
            unmatched.append((t, "log", lg))

print("\n=== counts re-run")
nf = len([l for l in open(os.path.join(ev, "newcheck_on_F4.log"), encoding="utf-8") if l.startswith("FAIL")])
print(f"FAIL lines in newcheck_on_F4.log: {nf}")
rb = open(os.path.join(ev, RB), encoding="utf-8").read()
print(f"broken copies with exit 1 as expected: {len(re.findall(r'^b\d+_\w+: exit 1 \(expected 1\).*as expected$', rb, re.M))}; control: {'control_unchanged: exit 0' in rb}")
cf = open(os.path.join(ev, "check_final.log"), encoding="utf-8").read()
print(f"check_final: {re.findall(r'^exit \d+$', cf, re.M)}, {re.findall(r'^\d+ failures$', cf, re.M)}, {re.findall(r'\d+ transitions', cf)}, {re.findall(r'\d+ named nets', cf)}")
notes = open(os.path.join(d, "firmware-f5-notes.md"), encoding="utf-8").read()
s3 = notes[notes.index("## 3."):notes.index("## 4.")]
print(f"items in notes section 3: {len(re.findall(r'^\d+\. ', s3, re.M))}")
print(f"conflicts in notes section 4: {len(re.findall(r'^\d+\. ', notes[notes.index('## 4.'):notes.index('## 5.')], re.M))}")
print(f"last line of notes: {notes.rstrip().splitlines()[-1][:80]}")
reply = open(targets[0], encoding="utf-8").read()
print(f"reply length: {len(reply)} characters")
for f in [os.path.join(d, "firmware.md"), os.path.join(d, "firmware-check.py"), os.path.join(d, "firmware-f5-notes.md"), targets[0]]:
    s = open(f, encoding="utf-8").read()
    print(f"em or en dashes in {os.path.basename(f)}: {s.count(chr(0x2014)) + s.count(chr(0x2013))}")
print(f"\nclaims checked: {checked}; unmatched: {len(unmatched)}")
for u in unmatched:
    print("UNMATCHED", os.path.basename(u[0]), u[1], u[2])
