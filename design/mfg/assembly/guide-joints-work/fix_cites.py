"""Correct moved citations of the guide in other design files, only where the citation is proven to point at the
guide as it was before my rewrite: the citing line quotes text (in double quotes, 12 characters or more) that is on
the old line, and the same text is on the new line. Every other moved citation is listed, not changed.
Only the forms 'assembly.md:N' and 'assembly.md` line N' / 'assembly.md line N' (one number) are rewritten.
Work folders, logs and my own files are skipped. A copy of each changed file goes to fixed-before/.
Run: design/.venv/bin/python -I <this file> [--apply]"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import linemap  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
APPLY = "--apply" in sys.argv
# live specs only: reviews, triage tables and state records cite the guide at their own pinned version
APPLY_ONLY = {"design/mfg/assembly/process.md", "design/ecad/case/pcb/board-notes.md"} if "--live" in sys.argv else None
lmap = linemap.build()
OLD = open(os.path.join(HERE, "assembly-before.md"), encoding="utf-8").read().split("\n")
NEW = open(os.path.join(HERE, "..", "assembly.md"), encoding="utf-8").read().split("\n")
SKIP_DIR = re.compile(r"(-work|/logs|/evidence|/out|/before|/fakes|/broken|/\.venv|/node_modules)(/|$)")
OWN = {os.path.join(ROOT, "design/mfg/assembly", f) for f in ("joints.csv", "joint-gaps.md", "assembly.md", "guide-joints-notes.md")}
PAT = re.compile(r"((?:design/mfg/assembly/)?assembly\.md)(`?)(:| line )(\d+)(?![\d])")
fixed, listed = [], []
for dp, dn, fn in os.walk(os.path.join(ROOT, "design")):
    if SKIP_DIR.search(dp.replace(ROOT, "")):
        continue
    for f in fn:
        p = os.path.join(dp, f)
        if APPLY_ONLY and os.path.relpath(p, ROOT) not in APPLY_ONLY:
            continue
        if p in OWN or not f.endswith((".md", ".csv", ".txt", ".py")) or f.endswith(".log"):
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        if "assembly.md" not in text:
            continue
        lines = text.split("\n")
        changed = False
        for i, line in enumerate(lines):
            def sub(m):
                global_rel = os.path.relpath(p, ROOT)
                pre = line[max(0, m.start() - 40):m.start()]
                if re.search(r"(docs/|before/|-work/|fakes/)$", pre):
                    return m.group(0)
                n = int(m.group(4))
                to, how, oldtext = lmap.get(n, (None, None, ""))
                if to is None or to == n:
                    if to is None:
                        listed.append((global_rel, i + 1, n, "no new line"))
                    return m.group(0)
                quotes = [q for q in re.findall(r"\"([^\"]{12,})\"", line)]
                good = [q for q in quotes if q in OLD[n - 1] and q in NEW[to - 1]]
                if good:
                    fixed.append((global_rel, i + 1, n, to, good[0][:50]))
                    return "%s%s%s%d" % (m.group(1), m.group(2), m.group(3), to)
                why = "quote not on the old line" if quotes and not any(q in OLD[n - 1] for q in quotes) else ("quote changed in the new guide" if quotes else "no quote to prove which version it cites")
                listed.append((global_rel, i + 1, n, "new line %d, not changed: %s" % (to, why)))
                return m.group(0)
            new_line = PAT.sub(sub, line)
            if new_line != line:
                lines[i] = new_line
                changed = True
        if changed and APPLY:
            d = os.path.join(HERE, "fixed-before", os.path.relpath(dp, ROOT))
            os.makedirs(d, exist_ok=True)
            shutil.copy2(p, os.path.join(d, f))
            open(p, "w", encoding="utf-8").write("\n".join(lines))
for x in fixed:
    print("FIXED %s:%d  assembly.md:%d -> %d  (quote: %s)" % x)
for x in listed:
    print("LISTED %s:%d  assembly.md:%d  %s" % x)
print("RESULT fixed %d listed %d applied %s" % (len(fixed), len(listed), APPLY))
