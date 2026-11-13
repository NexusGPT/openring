#!/usr/bin/env python3
"""check_bench.py: a check of the bench plan against the ring's parts list.

Usage: python3 -I check_bench.py [plan.md] [bom.csv]
Defaults: bench-plan.md and ../bom.csv beside this script.
Exit 0 and last line "RESULT PASS" when every rule holds; exit 1 and "RESULT FAIL" otherwise.

Rules (each prints one line OK or FAIL):
  R1 parts map: the plan has a parts map table; every ring part named in it is a maker_part_number
     of design/bom.csv on the ring reference(s) the plan gives; rows exist for the power chip (U2),
     the microphone (U5), the motor (M1) and the screen (DISP1); the status of each order code is
     "confirmed" (then the cited code source file must exist and print that code) or "not confirmed".
  R2 part numbers in the text: every part number of the power chip, microphone, motor or screen
     families written anywhere in the plan is held by bom.csv or is a confirmed order code of the
     parts map (the stated kit).
  R3 recording light: no line of the plan names the recording light (or its parts LED1, R41, Q2,
     LG1, LP1, light guide) as current: such a line must say it is removed.
  R4 tests: the plan has a tests table; every test has a pass line, a source file and section that
     exist, and each quote from the source is found verbatim in the cited file.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # the ai-ring-recorder folder (design/bench -> design -> root)

plan_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "bench-plan.md")
bom_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(HERE), "bom.csv")

fails = []
oks = []


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


plan_text = read(plan_path)
plan_lines = plan_text.split("\n")
bom_text = read(bom_path)
bom_rows = list(csv.DictReader(open(bom_path, encoding="utf-8", newline="")))
bom_parts = {}  # maker_part_number -> set of references
for r in bom_rows:
    pn = (r.get("maker_part_number") or "").strip()
    if not pn:
        continue
    refs = {x.strip() for x in (r.get("reference") or "").split(",") if x.strip()}
    bom_parts.setdefault(pn, set()).update(refs)


def tables(lines):
    """Return a list of (header cells, [(lineno, cells)]) for each markdown table."""
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append((j + 1, cells))
                j += 1
            out.append((header, rows))
            i = j
        else:
            i += 1
    return out


def col(header, name):
    for k, h in enumerate(header):
        if h.lower() == name.lower():
            return k
    return None


def resolve(p):
    return os.path.join(ROOT, p)


all_tables = tables(plan_lines)

# ---------------- R1 parts map ----------------
roles_needed = {"U2": "power chip", "U5": "microphone", "M1": "motor", "DISP1": "screen"}
confirmed_codes = set()
r1 = []
pm = None
for header, rows in all_tables:
    if col(header, "Ring part (bom.csv)") is not None and col(header, "Order code") is not None:
        pm = (header, rows)
        break
if pm is None:
    r1.append("no parts map table (header with 'Ring part (bom.csv)' and 'Order code')")
else:
    header, rows = pm
    c_ref = col(header, "Ring ref")
    c_part = col(header, "Ring part (bom.csv)")
    c_code = col(header, "Order code")
    c_stat = col(header, "Status")
    c_src = col(header, "Code source")
    c_bench = col(header, "Bench item")
    seen_refs = set()
    for ln, cells in rows:
        if len(cells) != len(header):
            r1.append("line %d: row has %d cells, header has %d" % (ln, len(cells), len(header)))
            continue
        refs = [x.strip() for x in cells[c_ref].split(",") if x.strip()]
        part = cells[c_part]
        code = cells[c_code]
        stat = cells[c_stat]
        src = cells[c_src]
        if part.lower() != "none":
            if part not in bom_parts:
                r1.append("line %d: ring part %r is not a maker_part_number in %s" % (ln, part, os.path.basename(bom_path)))
            else:
                for rf in refs:
                    if rf not in bom_parts[part]:
                        r1.append("line %d: ring reference %s is not a reference of %s in bom.csv (holds %s)" % (ln, rf, part, ",".join(sorted(bom_parts[part]))))
            seen_refs.update(refs)
        if stat == "confirmed":
            if not src or src.lower() == "none":
                r1.append("line %d: order code %r is marked confirmed with no code source" % (ln, code))
            else:
                fp = resolve(src)
                if not os.path.isfile(fp):
                    r1.append("line %d: code source %s does not exist" % (ln, src))
                elif code not in read(fp):
                    r1.append("line %d: code %r is not printed in %s" % (ln, code, src))
                else:
                    confirmed_codes.add(code)
        elif stat == "not confirmed":
            pass
        else:
            r1.append("line %d: status %r is neither 'confirmed' nor 'not confirmed'" % (ln, stat))
    for rf, role in roles_needed.items():
        if rf not in seen_refs:
            r1.append("no parts map row for the %s (ring reference %s)" % (role, rf))
if r1:
    fails.append(("R1 parts map", r1))
else:
    oks.append("R1 parts map: every ring part is in bom.csv on its reference; power chip, microphone, motor and screen rows present; order-code statuses valid")

# ---------------- R2 part numbers in the text ----------------
fam = [
    r"nPM13\d\d[-A-Za-z0-9]*",      # power chip
    r"IM6\dD\d+\w*", r"IM7\dD\d+\w*",  # old Infineon microphones
    r"SPK\d{4}\w*(?:-\w+)?",  # Knowles microphones
    r"W0\d{3}\w{2}\d{3}\w",   # Jinlong motors
    r"VC0\d{3}\w+",           # Vybronics motors
    r"VW0\d{3}\w+",
    r"TOH\d{3}\w+(?:-\d+)?",  # screen
    r"BO095\w+", r"TR095\w+",
]
fam_re = re.compile("|".join("(?:%s)" % f for f in fam), re.I)
r2 = []
bom_low = bom_text.lower()
for k, line in enumerate(plan_lines, start=1):
    for m in fam_re.finditer(line):
        tok = m.group(0).rstrip(".,;:)")
        if tok.lower() in bom_low:
            continue
        if tok in confirmed_codes or tok.lower() in {c.lower() for c in confirmed_codes}:
            continue
        r2.append("line %d: part number %r is not in bom.csv and is not a confirmed kit code of the parts map" % (k, tok))
if r2:
    fails.append(("R2 part numbers in the text", r2))
else:
    oks.append("R2 part numbers in the text: every power chip, microphone, motor and screen part number is held by bom.csv or is a confirmed kit code")

# ---------------- R3 recording light ----------------
light_re = re.compile(r"recording light|red led|\bLED1\b|\bR41\b|\bQ2\b(?=.*(?:transistor|gate|LED|light))|(?:transistor|gate|LED|light).*\bQ2\b|light guide|\bLG1\b|\bLP1\b|\bthe light\b|light test", re.I)
ok_re = re.compile(r"removed|no recording light|out of the design|wires no|not wired", re.I)
r3 = []
for k, line in enumerate(plan_lines, start=1):
    if light_re.search(line) and not ok_re.search(line):
        r3.append("line %d: names the recording light as current: %s" % (k, norm(line)[:110]))
if r3:
    fails.append(("R3 recording light", r3))
else:
    oks.append("R3 recording light: no line names the recording light (or its parts) as current")

# ---------------- R4 tests ----------------
r4 = []
tt = None
for header, rows in all_tables:
    if col(header, "Pass line") is not None and col(header, "ID") is not None:
        tt = (header, rows)
        break
n_tests = 0
if tt is None:
    r4.append("no tests table (header with 'ID' and 'Pass line')")
else:
    header, rows = tt
    c_id = col(header, "ID")
    c_pass = col(header, "Pass line")
    c_src = col(header, "Source (file and section)")
    c_quote = col(header, "Quote from source")
    if c_src is None or c_quote is None:
        r4.append("tests table has no 'Source (file and section)' or 'Quote from source' column")
    else:
        ids = set()
        for ln, cells in rows:
            if len(cells) != len(header):
                r4.append("line %d: row has %d cells, header has %d" % (ln, len(cells), len(header)))
                continue
            tid = cells[c_id]
            n_tests += 1
            if tid in ids:
                r4.append("line %d: test id %s repeated" % (ln, tid))
            ids.add(tid)
            if len(norm(cells[c_pass])) < 10:
                r4.append("line %d: test %s has no pass line" % (ln, tid))
            src = cells[c_src]
            texts = []
            pieces = [p for p in re.split(r";", src) if p.strip()]
            if not pieces:
                r4.append("line %d: test %s has no source file and section" % (ln, tid))
            for piece in pieces:
                pm_ = re.search(r"((?:design/[\w./-]+\.(?:md|csv))|(?:requirements\.md))", piece)
                if not pm_:
                    r4.append("line %d: test %s source %r names no file" % (ln, tid, norm(piece)[:60]))
                    continue
                path = pm_.group(1)
                fp = resolve(path)
                if not os.path.isfile(fp):
                    r4.append("line %d: test %s source file %s does not exist" % (ln, tid, path))
                    continue
                ftxt = read(fp)
                texts.append(norm(ftxt))
                flines = ftxt.split("\n")
                secs = []
                sm = re.search(r"sections? ([\d.]+(?:(?:, | and )[\d.]+)*)", piece)
                if sm:
                    secs = re.findall(r"\d+(?:\.\d+)*", sm.group(1))
                lm = re.search(r"lines? (\d+(?:(?:, | and |, line )\d+)*)", piece)
                lns = re.findall(r"\d+", lm.group(0)) if lm else []
                if not secs and not lns:
                    r4.append("line %d: test %s source %s names no section or line" % (ln, tid, path))
                for s in secs:
                    if not any(re.match(r"^#+\s+%s(?:[.\s]|$)" % re.escape(s), fl) for fl in flines):
                        r4.append("line %d: test %s: %s has no heading numbered %s" % (ln, tid, path, s))
                for l_ in lns:
                    if int(l_) > len(flines):
                        r4.append("line %d: test %s: %s has no line %s" % (ln, tid, path, l_))
            quotes = [norm(q) for q in cells[c_quote].split(" ~ ") if norm(q)]
            if not quotes:
                r4.append("line %d: test %s has no quote from its source" % (ln, tid))
            for q in quotes:
                if not any(q in t for t in texts):
                    r4.append("line %d: test %s: quote not found in the cited file(s): %r" % (ln, tid, q[:80]))
        if n_tests == 0:
            r4.append("the tests table has no test")
if r4:
    fails.append(("R4 tests", r4))
else:
    oks.append("R4 tests: %d tests, each with a pass line, an existing source file and section, and verbatim quotes" % n_tests)

# ---------------- report ----------------
print("check_bench.py plan=%s bom=%s" % (plan_path, bom_path))
for o in oks:
    print("OK   " + o)
for name, items in fails:
    for it in items:
        print("FAIL %s: %s" % (name, it))
print("rules passed %d of 4, findings %d" % (len(oks), sum(len(i) for _, i in fails)))
if fails:
    print("RESULT FAIL")
    sys.exit(1)
print("RESULT PASS")
sys.exit(0)
