"""Final audit: pull claims out of final-reply.md, the notes and CHECKLIST.md by themselves and print the evidence
line each matches. Claims: quoted RESULT lines, absolute and relative paths, guide line citations with a quote,
checklist 'assembly.md lines' ranges, and every number in the reply. Ends with a count and the unmatched ones."""
import glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
GUIDE = open(os.path.join(HERE, "..", "assembly.md"), encoding="utf-8").read().split("\n")
import sys
REPLY_FILE = sys.argv[1] if len(sys.argv) > 1 else "final-reply.md"
REPLY = open(os.path.join(HERE, REPLY_FILE), encoding="utf-8").read()
NOTES = open(os.path.join(HERE, "..", "guide-joints-notes.md"), encoding="utf-8").read()
CHECK = open(os.path.join(HERE, "CHECKLIST.md"), encoding="utf-8").read()
LOGS = {p: open(p, encoding="utf-8", errors="replace").read() for p in glob.glob(os.path.join(HERE, "logs", "*"))}
corpus = "\n".join(LOGS.values()) + "\n" + NOTES + "\n" + "\n".join(GUIDE)
checked, bad = 0, []


def ok(kind, claim, ev):
    global checked
    checked += 1
    print("OK  %-8s %-50s | %s" % (kind, claim[:50], ev[:110].replace("\n", " ")))


def no(kind, claim, why):
    global checked
    checked += 1
    bad.append((kind, claim, why))
    print("BAD %-8s %-50s | %s" % (kind, claim[:50], why))


def last_line(text):
    ls = [l for l in text.strip().split("\n") if l.strip() and not l.startswith("exit ")]
    return ls[-1] if ls else ""


# 1. quoted RESULT lines must be a last line of a check log (or the check log's own line for FAIL A2)
for src, text in (("reply", REPLY), ("notes", NOTES)):
    for q in sorted(set(re.findall(r"`(RESULT [^`]+)`", text))):
        hits = [os.path.basename(p) for p, t in LOGS.items() if last_line(t) == q]
        (ok if hits else no)("result", "%s: %s" % (src, q), ", ".join(hits) if hits else "no log ends with it")
# 2. paths
for src, text in (("reply", REPLY), ("notes", NOTES)):
    for p in sorted(set(re.findall(r"(/Users/[^\s`)]+)", text))):
        p2 = p.rstrip(".,")
        (ok if os.path.exists(p2) else no)("path", p2, "exists" if os.path.exists(p2) else "missing")
    for p in sorted(set(re.findall(r"`WORK/([^`\s]+)`", text))):
        full = os.path.join(HERE, p)
        (ok if os.path.exists(full) else no)("path", "WORK/" + p, "exists" if os.path.exists(full) else "missing")
# 3. guide line + quote in the notes' bar 3 table and in the reply
for src, text in (("notes", NOTES), ("reply", REPLY)):
    for m in re.finditer(r"(?:line |\| G\d \| |(?<!step )\b)(\d{2,3}) ?(?:\([^)]*\))?: \"([^\"]{12,})\"?", text):
        n, q = int(m.group(1)), m.group(2).strip().rstrip('".;')
        q = q.split("\" and \"")[0][:60]
        line = GUIDE[n - 1] if n <= len(GUIDE) else ""
        (ok if q[:40] in line else no)("quote", "guide %d: %s" % (n, q), line[:110] if q[:40] in line else "not on line %d" % n)
# 4. checklist line claims: each named guide line exists and is not blank
for m in re.finditer(r"assembly\.md lines? ([\d ,to]+)", CHECK):
    nums = [int(x) for x in re.findall(r"\d+", m.group(1))]
    for n in nums:
        line = GUIDE[n - 1] if n <= len(GUIDE) else ""
        (ok if line.strip() else no)("cklist", "guide line %d" % n, line[:110] if line.strip() else "blank or missing")
# 5. every number in the reply is found in the evidence corpus (logs, notes, guide)
for n in sorted(set(re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", REPLY)), key=float):
    pat = re.compile(r"(?<![\w.])%s(?![\w.])" % re.escape(n))
    hit = next((l for l in corpus.split("\n") if pat.search(l)), None)
    (ok if hit else no)("number", n, hit or "not found in logs, notes or guide")
# 6. counts that the reply and the notes both state must agree
pairs = [("RESULT FAIL 114", "RESULT FAIL 114"), ("62 rows", "| 62 |"), ("37 are complete", "37 complete"),
         ("786", "786 citations"), ("129 citations moved", "129 citations moved"), ("117 in design files", "117 in design files"),
         ("21 others", "21 have no new line")]
if REPLY_FILE == "final-reply-4.md":
    pairs = [("RESULT PASS joints 99", "RESULT PASS joints 99"), ("gap lines 0 complete 99 unplaced 0 []", "gap lines 0 complete 99 unplaced 0 []"),
             ("TESTS FAIL 14 of 16 as expected", "TESTS FAIL 14 of 16 as expected"), ("RESULT FAIL 17", "RESULT FAIL 17"),
             ("144 became 150", "(144 to 150)"), ("253 became 262", "(253 to 262)"), ("99 became 103", "(99 to 103)"),
             ("8 more", "8 in these records"), ("85", "85 it could not prove")]
elif REPLY_FILE == "final-reply-3.md":
    pairs = [("RESULT FAIL 33", "RESULT FAIL 33"), ("| 15 | 30 |", "| 15 | 30 |"), ("| 1 | 2 |", "| 1 | 2 |"),
             ("TESTS PASS 16 of 16 as expected", "TESTS PASS 16 of 16 as expected"), ("gap lines 17 complete 82 unplaced 0 []", "gap lines 17 complete 82 unplaced 0 []"),
             ("786", "786 citations"), ("lines 135 and 153", "lines 135 and 153")]
elif REPLY_FILE != "final-reply.md":
    pairs = [("RESULT FAIL 110", "RESULT FAIL 110"), ("| 5 | 8 |", "| 5 | 8 |"), ("| 1 | 1 |", "| 1 | 1 |"),
             ("4 of 4", "4 of 4"), ("3 of 4", "3 of 4"), ("gap lines 57 complete 42 unplaced 0 []", "gap lines 57 complete 42 unplaced 0 []"),
             ("TESTS PASS 13 of 13 as expected", "TESTS PASS 13 of 13 as expected"), ("RESULT FAIL 125", "RESULT FAIL 125"), ("101 lines", "101 failing lines")]
for a, b in pairs:
    (ok if a in REPLY and b in NOTES else no)("agree", "%s / %s" % (a, b), "both present" if a in REPLY and b in NOTES else "reply %s notes %s" % (a in REPLY, b in NOTES))
# 7. the reply's last line and the notes' last line are RESULT lines
for src, text in (("reply", REPLY), ("notes", NOTES)):
    ll = text.strip().split("\n")[-1]
    (ok if ll.startswith("RESULT: ") else no)("last", src, ll[:100])
print("CLAIMS CHECKED %d, UNMATCHED %d" % (checked, len(bad)))
for b in bad:
    print("UNMATCHED", b)
