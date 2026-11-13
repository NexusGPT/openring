"""Bar 4: every citation of the guide by line number across ROOT/design, with the line it now has.
A citation is 'assembly.md:N', 'assembly.md line N', 'assembly.md` line N' or 'assembly.md lines N, M to K'.
The old line is read in the guide as it was before this rewrite (assembly-before.md); the new line comes from
linemap.py. Writes logs/cites-moved.tsv and prints a summary. My own work folder is skipped.
Run: design/.venv/bin/python -I <this file>"""
import os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import linemap  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DESIGN = os.path.join(ROOT, "design")
SKIP = os.path.abspath(HERE)
EXT = (".md", ".csv", ".txt", ".py", ".json", ".log", ".tsv")
PAT = re.compile(r"assembly\.md`?(?::(\d+)(?:`? to `?(?:design/mfg/assembly/)?assembly\.md:(\d+))?|,? lines? ((?:\d+(?:, | to | and |-)?)+))")
OWN = {os.path.join(DESIGN, "mfg/assembly/joints.csv"), os.path.join(DESIGN, "mfg/assembly/joint-gaps.md"),
       os.path.join(DESIGN, "mfg/assembly/assembly.md")}
lmap = linemap.build()
out, kinds = [], collections.Counter()
for dp, dn, fn in os.walk(DESIGN):
    if os.path.abspath(dp).startswith(SKIP) or "/.venv" in dp or "/node_modules" in dp or "/.git" in dp:
        continue
    for f in fn:
        p = os.path.join(dp, f)
        if not f.endswith(EXT):
            continue
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "assembly.md" not in text:
            continue
        rel = os.path.relpath(p, ROOT)
        if p in OWN:
            continue  # joints.csv is rewritten to the new lines by fill_joints.py and checked by verify_joint_cites.py
        # another file named assembly.md (an old copy elsewhere) is cited by its own path: skip those
        for ln, line in enumerate(text.split("\n"), 1):
            for m in PAT.finditer(line):
                pre = line[max(0, m.start() - 60):m.start()]
                if re.search(r"(docs/|before/|review3-work/|guide-fix-2-work/|guide-fix-work/|fakes/|A\d_)$", pre):
                    continue
                nums = []
                if m.group(1):
                    nums.append(int(m.group(1)))
                    if m.group(2):
                        nums.append(int(m.group(2)))
                else:
                    nums = [int(x) for x in re.findall(r"\d+", m.group(3))]
                for n in nums:
                    to, how, oldtext = lmap.get(n, (None, "beyond the old file", ""))
                    moved = "moved" if to != n else "same"
                    if to is None:
                        moved = "no new line"
                    cat = "mine" if p in OWN else ("work log" if re.search(r"(-work|/logs|/evidence|/out)/", rel) else "other")
                    kinds[(cat, moved)] += 1
                    out.append("\t".join([cat, moved, "%s:%d" % (rel, ln), str(n), str(to), how or "", oldtext[:60].replace("\t", " ")]))
with open(os.path.join(HERE, "logs", "cites-moved.tsv"), "w", encoding="utf-8") as f:
    f.write("category\tstate\tciting place\told line\tnew line\thow\told text\n")
    f.write("\n".join(sorted(out)) + "\n")
for k in sorted(kinds):
    print("COUNT", k[0], k[1], kinds[k])
print("TOTAL", len(out))
