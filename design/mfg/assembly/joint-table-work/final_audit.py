"""Final audit: pull the claims out of final-reply.md and joint-table-notes.md by pattern (quoted text in
backticks or double quotes, paths, numbers, the RESULT line) and print the saved evidence line each matches.
Also checks fixed facts against the logs and the reply length. Last line: FINAL AUDIT claims <n> matched <m>
unmatched <u> disagreements <d>. Run: design/.venv/bin/python -B final_audit.py"""
import glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ASM = os.path.join(ROOT, "design/mfg/assembly")
DOCS = [os.path.join(HERE, "final-reply.md"), os.path.join(ASM, "joint-table-notes.md")]
EVID = sorted(set(glob.glob(os.path.join(HERE, "logs", "**", "*"), recursive=True) +
                  glob.glob(os.path.join(HERE, "tests", "**", "*"), recursive=True) +
                  [os.path.join(ASM, f) for f in ("joints.csv", "joint-gaps.md", "check_joints.py")] +
                  [os.path.join(HERE, f) for f in ("build_joints.py", "citations.csv", "CHECKLIST.md", "run_all.sh",
                                                    "make_gaps.py", "count_ends.py", "audit_citations.py")] +
                  [os.path.join(ROOT, p) for p in ("design/mfg/assembly/assembly.md", "design/ecad/band/band-interface.md",
                                                   "design/wiring/wiring-review-3.md", "design/case/case-architecture.md",
                                                   "design/ecad/case/pcb/board-notes.md", "design/wiring/lead-decisions.md",
                                                   "design/mfg/assembly/v7-update-notes.md", "design/wiring/product-wiring.csv")]))
EVID = [p for p in EVID if os.path.isfile(p) and not p.endswith(("final-audit.log",))]
text_of = {}
for p in EVID:
    try:
        text_of[p] = open(p, encoding="utf-8", errors="replace").read()
    except Exception as e:
        text_of[p] = ""


def find_ev(s):
    for p, t in text_of.items():
        i = t.find(s)
        if i >= 0:
            ln = t.count("\n", 0, i) + 1
            line = t.split("\n")[ln - 1]
            return "%s:%d: %s" % (os.path.relpath(p, ROOT), ln, line.strip()[:160])
    return None


claims, unmatched = 0, []
out = []
for d in DOCS:
    t = open(d, encoding="utf-8").read()
    name = os.path.relpath(d, ROOT)
    # quoted text
    for q in re.findall(r"`([^`]+)`", t) + re.findall(r'"([^"]{6,})"', t):
        claims += 1
        q2 = q.replace("ROOT/", "").replace("WORK/", "")
        hit = find_ev(q2)
        if hit is None and ("/" in q2 or q2.endswith((".csv", ".md", ".py", ".log", ".txt", ".sh"))):
            cands = [os.path.join(ROOT, q2), os.path.join(ASM, q2), os.path.join(HERE, q2), os.path.join(ROOT, "design", q2)]
            ex = [c for c in cands if os.path.exists(c)] + glob.glob(os.path.join(HERE, q2))
            hit = ("path exists: " + os.path.relpath(ex[0], ROOT)) if ex else None
        if hit is None:
            unmatched.append("%s QUOTE %r" % (name, q))
        else:
            out.append("%s QUOTE %r -> %s" % (name, q[:80], hit))
    # numbers with a word after them (counts) and plain numbers
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", t):
        n = m.group(1)
        claims += 1
        ctx = t[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
        hit = None
        for p, tt in text_of.items():
            if re.search(r"(?<![\w.])%s(?![\w.])" % re.escape(n), tt):
                hit = os.path.relpath(p, ROOT)
                break
        if hit is None:
            unmatched.append("%s NUMBER %s in ...%s..." % (name, n, ctx))
        else:
            out.append("%s NUMBER %s (...%s...) -> found in %s" % (name, n, ctx.strip()[:60], hit))

# fixed facts: each statement against its log line
L = os.path.join(HERE, "logs", "final")
facts = [
    ("check last line", "RESULT FAIL 365", os.path.join(L, "check.log")),
    ("check exit", "exit 1", os.path.join(L, "check.log")),
    ("rule counts", "R1 0\nR2 360\nR3 0\nR4 1\nR5 4", os.path.join(L, "check-rule-counts.txt")),
    ("tests", "TESTS PASS 13 of 13 as expected", os.path.join(L, "tests.log")),
    ("mini", "RESULT PASS joints 3", os.path.join(HERE, "tests", "mini", "mini.log")),
    ("audit", "AUDIT cited lines found 1837 of 1837 total, fields with a citation 1287 of 1287, rows 99, problems 0", os.path.join(L, "audit_citations.log")),
    ("arith", "ARITHMETIC 81 ends in joints.csv + 53 ends with no joint = 134 = 2 x 67 lines", os.path.join(L, "count_ends.log")),
    ("gaps", "GAPS 95 of 99 rows", os.path.join(L, "list-gaps.log")),
    ("gap lines", "gap lines 95 complete 4 unplaced 0", os.path.join(L, "make_gaps.log")),
    ("flux 81", "MISSING in flux 81", os.path.join(L, "missing-counts.log")),
    ("paste F", "flashes 302 smd pads on F.Cu 317 with F.Paste in footprint 302 of these with an opening 302", os.path.join(HERE, "logs", "probe_paste.log")),
    ("paste B", "with B.Paste in footprint 45 of these with an opening 45", os.path.join(HERE, "logs", "probe_paste.log")),
    ("paste case", "with F.Paste in footprint 261 of these with an opening 261", os.path.join(HERE, "logs", "probe_paste.log")),
    ("U2:25", "holds no opening for land U2:25 (GND)", os.path.join(L, "check.log")),
    ("size", "5,6M", os.path.join(L, "time.txt")),
    ("passes", "board pass rows: 18; rows total 99", os.path.join(L, "count_ends.log")),
]
dis = []
for name, s, p in facts:
    claims += 1
    t = open(p, encoding="utf-8").read()
    if s in t:
        out.append("FACT %s: %r found in %s" % (name, s[:70], os.path.relpath(p, ROOT)))
    else:
        dis.append("FACT %s: %r NOT in %s" % (name, s, os.path.relpath(p, ROOT)))
hot = open(os.path.join(L, "check-hotbar-solder.txt")).read()
for j in ["J-W001-A", "J-W002-A", "J-W003-A", "J-W004-A", "J-W005-A", "J-W011-A", "J-W021-A", "J-W022-A",
          "J-W025-A", "J-W026-A", "J-W027-A", "J-W029-A", "J-W030-A", "J-W031-A", "J-W032-A"]:
    claims += 1
    (out if ("R2 MISSING: %s field solder_source" % j) in hot else dis).append("HOTBAR %s solder_source MISSING line" % j)
groups = open(os.path.join(ASM, "joint-gaps.md")).read().count("\n## Group ")
claims += 1
(out if groups == 13 else dis).append("GROUPS in joint-gaps.md: %d (claimed 13)" % groups)
reply = open(DOCS[0], encoding="utf-8").read()
claims += 1
(out if len(reply) < 3500 else dis).append("REPLY length %d characters (limit 3500)" % len(reply))
notes_last = open(DOCS[1], encoding="utf-8").read().rstrip("\n").split("\n")[-1]
claims += 1
(out if notes_last.startswith("RESULT: done,") else dis).append("NOTES last line: %s" % notes_last[:120])
for l in out:
    print("OK", l)
for l in unmatched:
    print("UNMATCHED", l)
for l in dis:
    print("DISAGREE", l)
print("FINAL AUDIT claims %d matched %d unmatched %d disagreements %d" % (claims, claims - len(unmatched) - len(dis), len(unmatched), len(dis)))
