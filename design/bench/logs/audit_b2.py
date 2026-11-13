#!/usr/bin/env python3
"""Final audit of b2-notes.md and the final reply: pulls claims out by itself and prints the evidence line of each."""
import glob, os, re, sys
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
B = ROOT + "design/bench/"
targets = [B + "b2-notes.md", B + "logs/b2-final-reply.md"]
skip = set(targets)
# corpus: every text file saved by this run, plus the design files the notes cite
corpus_files = []
for pat in ["*.md", "logs/*", "sources/*.txt", "sources/*.dtsi", "sources/*.html"]:
    corpus_files += glob.glob(B + pat)
corpus_files += [ROOT + "design/bom.csv", ROOT + "design/firmware.md", ROOT + "design/architecture.md", ROOT + "requirements.md",
                 ROOT + "design/ecad/motor-drive/motor-drive.md", ROOT + "design/mech/mic-path/mic-path.md",
                 ROOT + "design/datasheets/npm1304_datasheet_v1_0.txt", ROOT + "design/ecad/motor-drive/src_tlv755p.txt",
                 ROOT + "design/review/design-review-3.md", ROOT + "design/ecad/ring/npm1304-balls.csv"]
corpus = {}
for f in corpus_files:
    if f in skip or not os.path.isfile(f) or f.endswith(".png") or f.endswith(".pdf"):
        continue
    try:
        corpus[f] = open(f, encoding="utf-8", errors="replace").read().split("\n")
    except Exception as e:
        print("unreadable", f, e)

def find(token, rx=None):
    r = re.compile(rx if rx else r"(?<![\w.])" + re.escape(token) + r"(?![\w])")
    for f, lines in corpus.items():
        for i, l in enumerate(lines, 1):
            if r.search(l):
                return "%s:%d: %s" % (os.path.relpath(f, ROOT), i, l.strip()[:90])
    return None

total = 0
nomatch = []
def claim(kind, tok, ev):
    global total
    total += 1
    if ev:
        print("MATCH %-7s %-34s -> %s" % (kind, tok[:34], ev))
    else:
        print("NOMATCH %-7s %s" % (kind, tok))
        nomatch.append((kind, tok))

texts = {t: open(t).read() for t in targets}
for t, txt in texts.items():
    print("=== claims of", os.path.relpath(t, ROOT))
    # 1 paths
    paths = set(re.findall(r"(?:/Users/[\w./-]+|design/[\w./*-]+|requirements\.md)", txt))
    for p in sorted(paths):
        p2 = p.rstrip(".,;:)")
        full = p2 if p2.startswith("/") else ROOT + p2
        ok = bool(glob.glob(full)) or os.path.exists(full)
        claim("path", p2, ("exists " + os.path.relpath(glob.glob(full)[0], ROOT)) if ok else None)
    # 2 bare file names in backticks (relative to bench or logs)
    for name in sorted(set(re.findall(r"`([\w.-]+\.(?:md|py|log|txt|csv))`", txt))):
        hits = glob.glob(B + name) + glob.glob(B + "logs/" + name) + glob.glob(B + "sources/" + name) + glob.glob(B + "logs/" + name.replace("*", "*"))
        claim("file", name, ("exists " + os.path.relpath(hits[0], ROOT)) if hits else None)
    for name in sorted(set(re.findall(r"`(check_[\w*]+\.log)`", txt))):
        pass
    # 3 dates and times
    for d in sorted(set(re.findall(r"\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?", txt))):
        ev = find(d) or find(d.replace(" ", "T"), r"" + re.escape(d.replace(" ", "T")))
        claim("date", d, ev)
    # 4 numbers
    t2 = re.sub(r"\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?", " ", txt)
    t2 = re.sub(r"(?:/Users/[\w./-]+|design/[\w./*-]+)", " ", t2)
    t2 = re.sub(r"`[^`]*`", lambda m: m.group(0) if re.search(r"\d", m.group(0)) and not re.search(r"[/.]", m.group(0)) else " ", t2)
    nums = sorted(set(re.findall(r"(?<![\w.-])\d[\d,]*(?:\.\d+)?(?![\w-])", t2)))
    for n in nums:
        claim("number", n, find(n))
    # 5 part numbers and codes (letters+digits, at least one digit, 4+ chars, hyphen or mixed case)
    for c in sorted(set(re.findall(r"\b[A-Za-z][A-Za-z0-9]*\d[A-Za-z0-9-]{2,}\b", txt))):
        if c.startswith("check_") or re.match(r"^R\d$|^T\d$|^S\d+$|^D\d$|^B\d$|^C\d+$|^P\d+$", c):
            continue
        claim("code", c, find(c, r"" + re.escape(c)))
    # 6 RESULT statements
    for m in re.finditer(r"RESULT (PASS|FAIL)", txt):
        pass

# counts and contradictions
print("=== recomputed counts and contradictions")
plan = open(B + "bench-plan.md").read().split("\n")
conf = sum(1 for l in plan if re.match(r"^\| \d+ \|", l) and l.count("|") > 9 and re.search(r"\| confirmed \|", l))
notc = sum(1 for l in plan if re.match(r"^\| \d+ \|", l) and l.count("|") > 9 and re.search(r"\| not confirmed \|", l))
tests = sum(1 for l in plan if re.match(r"^\| T\d \|", l))
wiring = sum(1 for l in plan if re.match(r"^\| \d+ \| [A-Z_(),0-9 ]+ \| [^|]+ \| [^|]+ \| [^|]*\|$", l))
print("plan: confirmed rows", conf, "not confirmed rows", notc, "tests", tests)
notes = texts[targets[0]]; reply = texts[targets[1]]
def stated(txt, rx):
    return [int(x) for x in re.findall(rx, txt)]
issues = 0
for label, rx, val in [("confirmed", r"Confirmed \((\d+)\)", conf), ("not confirmed", r"Not confirmed \((\d+)\)", notc)]:
    s = stated(notes, rx)
    ok = s == [val]
    print("notes states %s %s, plan has %d -> %s" % (label, s, val, "OK" if ok else "DISAGREE")); issues += (not ok)
m = re.search(r"(\d+) confirmed with their source file; (\d+) not confirmed", reply)
ok = bool(m) and (int(m.group(1)), int(m.group(2))) == (conf, notc)
print("reply states", m.groups() if m else None, "plan has", (conf, notc), "->", "OK" if ok else "DISAGREE"); issues += (not ok)
m = re.search(r"Tests T0 to T7 \((\d+)\)", reply)
ok = bool(m) and int(m.group(1)) == tests
print("reply states tests", m.group(1) if m else None, "plan has", tests, "->", "OK" if ok else "DISAGREE"); issues += (not ok)
rows = [int(re.match(r"^\| (\d+) \|", l).group(1)) for l in plan if re.match(r"^\| \d+ \| (?:VBAT|GND|VDD|PMIC|MIC|SD_|LCD|OLED|BTN|JOY|MOTOR|PMIC loads|MIC_A_CLK, MOTOR|VBAT, VMOT)", l)]
m = re.search(r"Wiring table: (\d+) rows", reply)
ok = bool(m) and int(m.group(1)) == max(rows)
print("reply states wiring rows", m.group(1) if m else None, "plan table has rows numbered up to", max(rows), "->", "OK" if ok else "DISAGREE"); issues += (not ok)
# check results stated vs logs
for name, rx in [("check_FINAL_bench-plan.log", r"bench-plan\.md: rules passed (\d) of 4, RESULT PASS"),
                 ("check_FINAL_bench-plan-B1.log", r"bench-plan-B1\.md: rules passed (\d) of 4, RESULT FAIL"),
                 ("check_FINAL_bench-plan-faulty.log", r"bench-plan-faulty\.md \(microphone part changed to IM68D128BV01\): rules passed (\d) of 4, RESULT FAIL")]:
    L = open(B + "logs/" + name).read().strip().split("\n")
    m = re.search(r"rules passed (\d) of 4", L[-2]); res = L[-1]
    s = re.search(rx, reply)
    ok = bool(s) and m and s.group(1) == m.group(1) and res == ("RESULT PASS" if "PASS" in rx else "RESULT FAIL")
    print("reply vs", name, "->", "OK" if ok else "DISAGREE", "| log:", L[-2], "|", res); issues += (not ok)
for l in open(B + "logs/check_FINAL_bench-plan-B1.log").read().split("\n"):
    pass
b1 = open(B + "logs/check_run0_b2_first.log").read()
print("first-run log last line:", b1.strip().split("\n")[-1])

# statements about earlier runs, checked in their logs
print("=== statements about earlier runs")
def rd(n): return open(B + "logs/" + n).read()
chk = [
 ("first B2 run failed on R2 file names", "FAIL R2" in rd("check_run0_b2_first.log") and "npm1304_ek" in rd("check_run0_b2_first.log") and rd("check_run0_b2_first.log").strip().endswith("RESULT FAIL")),
 ("B1 v1 rule R3 reproduction: lines 12, 13, 22, 31, 50, 54, 64", all(("hit line %d:" % n) in rd("repro_r3_v1_on_B1.log") for n in (12, 13, 22, 31, 50, 54, 64))),
 ("B1 v2 run: R3 lines 13, 31, 50, 64 and not 12, 22, 54", all(("line %d: names the recording light" % n) in rd("check_v2_bench-plan-B1.log") for n in (13, 31, 50, 64)) and not any(("line %d: names the recording light" % n) in rd("check_v2_bench-plan-B1.log") for n in (12, 22, 54))),
 ("extra light copy fails on R3 only", "FAIL R3" in rd("check_FINAL_bench-plan-faulty-light.log") and "FAIL R1" not in rd("check_FINAL_bench-plan-faulty-light.log") and "FAIL R4" not in rd("check_FINAL_bench-plan-faulty-light.log")),
 ("extra pass line copy fails on R4 only", "FAIL R4" in rd("check_FINAL_bench-plan-faulty-passline.log") and "FAIL R1" not in rd("check_FINAL_bench-plan-faulty-passline.log") and "FAIL R3" not in rd("check_FINAL_bench-plan-faulty-passline.log")),
 ("faulty copy fails on R1 and R2", "FAIL R1" in rd("check_FINAL_bench-plan-faulty.log") and "FAIL R2" in rd("check_FINAL_bench-plan-faulty.log")),
 ("B1 file unchanged against the saved original", open(B + "bench-plan-B1.md").read() == open(B + "logs/bench-plan-B1-original.md").read()),
 ("final hashes match the delivered files now", all(h in rd("final_hashes.log") for h in [__import__("hashlib").sha256(open(B + n, "rb").read()).hexdigest() for n in ("bench-plan.md", "check_bench.py", "bench-plan-B1.md")])),
 ("no request URL names a project, owner or company (urls in the fetch log hold none of the words below)", not re.search(r"(?i)<platform>|<user>|orga|ring-recorder|ai-ring", rd("fetch_all.log"))),
]
for name, ok in chk:
    total += 1
    print(("OK    " if ok else "FAILED ") + name)
    if not ok: issues += 1

print("claims checked", total, "no match", len(nomatch), "disagreements", issues)
for k, t in nomatch:
    print("  unmatched", k, t)
sys.exit(1 if (nomatch or issues) else 0)
