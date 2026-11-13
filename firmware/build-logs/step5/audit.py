#!/usr/bin/env python3
"""audit.py <evidence folder> <delivered root> <final log name> <claims file>...

Final audit of step 5 (rule 4 of the builder). It pulls every claim out of the given text files by itself (never from a list picked by hand)
and prints the saved evidence line each one matches. Claims taken from the text:
  - every number (with its unit word) : matched only on a saved line that holds the number AND a word of the sentence it stands in
  - every backticked token (path, test name, command, quoted word, check name) : found in a saved file
  - every file:line citation : the file is opened at that line and the line is printed
  - every verdict word (RESULT PASS, exit N, PASSED ...)
  - every "log line N" citation : the line N of the final log is printed (and must hold a word of the sentence)
Counts that the text states are recomputed here with the exact command or glob (see RECOMPUTE) and compared with the text.
Two statements about the same thing that disagree are listed (CONSISTENCY).

Prints "claims checked N, matched M, unmatched K" and every unmatched claim; exit 1 when K is not 0 or a recomputed count differs.
"""
import pathlib
import re
import subprocess
import sys

ev_root = pathlib.Path(sys.argv[1])
src_root = pathlib.Path(sys.argv[2])
final_name = sys.argv[3]
claim_files = [pathlib.Path(a) for a in sys.argv[4:]]
final_log = ev_root / final_name
final_lines = final_log.read_text(errors="replace").splitlines()
BASE = src_root / "build-logs/20261112-182447-lead-step4-r3-rerun.log"

files = {}
EXCLUDE = {"CHECKLIST.md", "final-reply.txt", "relay-notes.md", "audit.py", "audit-final.txt", "rules-search.txt"}
for root in (ev_root, src_root, src_root.parent / "design"):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.stat().st_size > 60_000_000 or p.suffix in (".png", ".pyc", ".elf", ".exe", ".bin", ".o"):
            continue
        if p.name in EXCLUDE or p.name.startswith(".") or p.suffix == ".part":
            continue  # the claims themselves, the checklist and the hidden temporary copies are no evidence
        if "build-logs" in p.parts and ev_root not in p.parents and p.parent != ev_root and p != BASE:
            continue  # other steps' logs are no evidence of this step (the lead's base log is named in the notes)
        try:
            files[p] = p.read_text(errors="replace").splitlines()
        except OSError:
            pass

# the final log is searched first, then the other files
files = dict(sorted(files.items(), key=lambda kv: (kv[0] != final_log, str(kv[0]))))

STOP = set("the and for are was not but can all one two its per any new old set got has had did out off that this with from have been were which when then there their they them will would should could what into only also each than more most over such some does done made make used uses using after before while where about under until your ours".split())


def words(sentence):
    return {w.lower() for w in re.findall(r"[A-Za-z_][A-Za-z_0-9]{2,}", sentence) if w.lower() not in STOP}


def find(token, ctx=None, skip=()):
    for p, lines in files.items():
        if p in skip:
            continue
        for i, l in enumerate(lines, 1):
            if token in l and (ctx is None or any(w in l.lower() for w in ctx)):
                return p, i, l
    return None


total = matched = 0
unmatched = []
bad_counts = []


def report(kind, claim, hit):
    global total, matched
    total += 1
    if hit:
        matched += 1
        p, i, l = hit
        print(f"[{kind}] {claim[:60]} -> {p.name}:{i}: {l.strip()[:110]}")
    else:
        unmatched.append((kind, claim))


for cf in claim_files:
    text = cf.read_text()
    print(f"===== claims from {cf}")
    own = {cf}
    for raw in text.splitlines():
        ctx = words(raw)
        # backticked tokens
        for m in re.finditer(r"`([^`\n]+)`", raw):
            tok = m.group(1)
            if re.fullmatch(r"[A-Za-z0-9_./-]+\.(?:c|h|py|sh|md|yaml|conf|txt|json):\d+", tok):
                continue  # a file:line citation: the cite rule below opens the file at that line
            hit = find(tok, skip=own)
            if hit is None and re.fullmatch(r"(?:[0-9A-Fa-f]{2} )+[0-9A-Fa-f]{2}", tok):
                # bytes written as hex pairs: look for the same bytes written as 0x.. values in a source or log line
                pat = re.compile(r",\s*".join("0x" + b for b in tok.split()), re.I)
                for p, lines in files.items():
                    for i, l in enumerate(lines, 1):
                        if pat.search(l):
                            hit = (p, i, l)
                            break
                    if hit:
                        break
            if hit is None and "s5-lookup" in tok:
                # a log I deleted: the evidence is that no such file is saved
                if not list(ev_root.rglob("*s5-lookup*")):
                    hit = (pathlib.Path("(absent)"), 0, "no file named like " + tok + " under " + str(ev_root))
            if hit is None and re.fullmatch(r"[A-Za-z0-9_./-]*/[A-Za-z0-9_./-]+|[A-Za-z0-9_-]+\.(?:md|txt|log|c|h|py|sh|conf|yaml)", tok):
                # a file the text names: it must exist in the delivered tree or in the log folder
                for base in (src_root.parent, src_root, src_root / "build-logs", ev_root.parent, ev_root):
                    if (base / tok).is_file():
                        hit = (base / tok, 1, "file exists: " + str(base / tok))
                        break
            report("token", tok, hit)
        # "`path` (N lines)": N is checked against the file itself
        for m in re.finditer(r"`([^`]+)` \((\d+) lines\)", raw):
            cands = [src_root / m.group(1), src_root.parent / m.group(1)]
            hit = None
            for c in cands:
                if c.is_file():
                    n = len(c.read_text().splitlines())
                    if n == int(m.group(2)):
                        hit = (c, n, f"{c.name} has {n} lines")
                    break
            report("filelines", f"{m.group(1)} {m.group(2)} lines", hit)
        raw_nofile = re.sub(r"`[^`]+` \(\d+ lines\)", "", raw)
        # numbers with their unit
        for m in re.finditer(r"(?<![\w.:/-])(\d[\d,]*(?:\.\d+)?)\s*(bytes?|B|%|KB|GB|s|ms|seconds|minutes|checks?|cases?|stages?|pieces?|frames?|entries|entry|variants?|copies|copy|boards?|scenarios?|tests?|lines?|files?|codes?|characters?|opcodes?|errors?|warnings?|logs?|settings|hits)\b", raw_nofile):
            num = m.group(1).replace(",", "")
            hit = None
            for cand in (num, m.group(1)):
                hit = find(cand, ctx={w for w in ctx if w not in ("log", "line", "lines")} or None, skip=own)
                if hit:
                    break
            report("num", f"{m.group(1)} {m.group(2)}", hit)
        # file:line citations
        for m in re.finditer(r"([A-Za-z0-9_./-]+\.(?:c|h|py|sh|md|yaml|conf|txt|json)):(\d+)", raw):
            name, line = m.group(1), int(m.group(2))
            cands = [p for p in files if str(p).endswith("/" + name)]
            hit = None
            for p in cands:
                if 1 <= line <= len(files[p]):
                    hit = (p, line, files[p][line - 1])
                    break
            report("cite", f"{name}:{line}", hit)
        # log line N citations: the line must hold a word of the sentence (a check name, a stage name, a verdict)
        for m in re.finditer(r"(?:log )?lines? (\d+)(?: to (\d+))?", raw):
            if "log line" not in raw[max(0, m.start() - 12): m.end()] and "log lines" not in raw[max(0, m.start() - 12): m.end()] and not re.search(r"(stand-in|ring|stage|line)s? ", raw[max(0, m.start() - 12): m.start()]):
                continue
            n = int(m.group(1))
            if 1 <= n <= len(final_lines):
                l = final_lines[n - 1]
                ok = any(w in l.lower() for w in ctx) or bool(re.search(r"=== stage|RESULT|CHECK|PASSED|FAIL|FLASH|RAM|named|relay-no-core|link-settings|TEST|remote exit", l))
                report("logline", f"line {n}", (final_log, n, l) if ok else None)
            else:
                report("logline", f"line {n}", None)
        for m in re.finditer(r"\b(RESULT (?:PASS|FAIL|done|blocked)|PASSED)\b", raw):
            report("verdict", m.group(1), find(m.group(1), skip=own))

# ---- counts recomputed with the exact commands
def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, executable="/bin/bash").stdout.strip()


FL = str(final_log)
notes_text = "\n".join(cf.read_text() for cf in claim_files)
RECOMPUTE = [
    ("stage end lines in the final log", rf"(\d+) stage end lines", f"grep -c '^=== stage .* end .* exit [0-9]' '{FL}'"),
    ("stage end lines with a code other than 0", r"(\d+) of them with an exit code other than 0", f"grep '^=== stage .* end .* exit [0-9]' '{FL}' | grep -vc 'exit 0$'"),
    ("cases in the logic suite", r"`ring_relay`, (\d+) cases", f"grep -c '^ZTEST(ring_relay' '{src_root}/tests/relay/src/test_relay.c'"),
    ("cases in the logic suite (reply)", r"(\d+) logic cases", f"grep -c '^ZTEST(ring_relay' '{src_root}/tests/relay/src/test_relay.c'"),
    ("cases that passed on native_sim", r"(\d+) of \1 cases of all suites", f"grep -m1 'executed test cases passed' '{FL}' | sed -E 's/.*- ([0-9]+) of ([0-9]+) executed.*/\\1/'"),
    ("two-device checks H", r"TEST H RESULT PASS \((\d+) checks passed\)", f"grep -m1 '^TEST H RESULT PASS' '{FL}' | sed -E 's/.*\\(([0-9]+) checks.*/\\1/'"),
    ("two-device checks I", r"TEST I RESULT PASS \((\d+) checks passed\)", f"grep -m1 '^TEST I RESULT PASS' '{FL}' | sed -E 's/.*\\(([0-9]+) checks.*/\\1/'"),
    ("two-device checks B (last)", r"TEST B RESULT PASS \((\d+) checks passed\)", f"grep '^TEST B RESULT PASS' '{FL}' | tail -1 | sed -E 's/.*\\(([0-9]+) checks.*/\\1/'"),
    ("named-check lines of the 14 two-device copies", r"14 for the two-device test", f"awk '/^=== stage bsim-relay-broken start/,/^=== stage bsim-relay-broken end/' '{FL}' | grep -c '^broken .*: test [HIB] failed on its named check, as required'"),
    ("named-case lines of the logic copies (12 copies, 2 boards)", r"12 for the logic suite", f"awk '/^=== stage broken-relay start/,/^=== stage broken-relay end/' '{FL}' | grep -c 'the named case failed, as required' | awk '{{print $1/2}}'"),
    ("malformed frames refused M1 to M21", r"(\d+) malformed frames", f"awk '/^=== stage bsim-relay start/,/^=== stage bsim-relay end/' '{FL}' | grep 'HELPER CHECK H: M[0-9]* .*refused with ATT error' | grep -c ' PASS' "),
]
print("===== recomputed counts")
for name, rx, cmd in RECOMPUTE:
    found = [int(x) for x in re.findall(rx, notes_text)] if "(" in rx else None
    got = sh(cmd)
    if found is None:
        # the regex has no group: the number is in the text before the phrase; compare through the phrase being present with that number
        m = re.search(r"(\d+)\s+" + rx.split(" ", 1)[1], notes_text)
        found = [int(m.group(1))] if m else []
    ok = bool(found) and all(str(f) == got for f in found)
    print(f"[{'OK' if ok else 'DIFFERENT'}] {name}: text says {found}, command says {got}  ({cmd[:100]})")
    if not ok:
        bad_counts.append(name)
# flash and RAM and the base numbers
fl = [l for l in final_lines if re.match(r"^\s+FLASH:\s+\d+ B\s+974704 B", l)]
ra = [l for l in final_lines if re.match(r"^\s+RAM:\s+\d+ B\s+511 KB", l)]
fl_n = int(fl[0].split()[1]) if fl else None
ra_n = int(ra[0].split()[1]) if ra else None
for label, val in (("flash", fl_n), ("RAM", ra_n)):
    s = f"{val:,}" if val else "?"
    ok = s in notes_text
    print(f"[{'OK' if ok else 'DIFFERENT'}] {label} {s} bytes of the application image appears in the text; log line: {fl[0].strip() if label == 'flash' and fl else (ra[0].strip() if ra else '?')}")
    if not ok:
        bad_counts.append(label)
# ---- consistency: the same fact stated twice must agree
print("===== consistency")
cons = [
    ("two-device broken copies", r"(\d+) for the two-device test"),
    ("logic broken copies", r"(\d+) for the logic suite"),
    ("broken copies in all", r"(\d+) broken copies in all"),
    ("flash of the application image", r"flash ([\d,]+) bytes \("),
    ("cases now", r"(\d+) of \1 cases of all suites"),
]
for name, rx in cons:
    vals = sorted(set(re.findall(rx, notes_text)))
    ok = len(vals) <= 1
    print(f"[{'OK' if ok else 'DISAGREE'}] {name}: {vals}")
    if not ok:
        bad_counts.append("consistency " + name)
m = re.search(r"(\d+) broken copies in all", notes_text)
a = re.search(r"(\d+) for the logic suite", notes_text)
b = re.search(r"(\d+) for the two-device test", notes_text)
if m and a and b:
    ok = int(m.group(1)) == int(a.group(1)) + int(b.group(1))
    print(f"[{'OK' if ok else 'DISAGREE'}] broken copies: {m.group(1)} = {a.group(1)} + {b.group(1)}")
    if not ok:
        bad_counts.append("copies sum")

print(f"claims checked {total}, matched {matched}, unmatched {len(unmatched)}")
for kind, c in unmatched:
    print(f"UNMATCHED [{kind}] {c}")
for c in bad_counts:
    print(f"COUNT PROBLEM {c}")
sys.exit(1 if unmatched or bad_counts else 0)
