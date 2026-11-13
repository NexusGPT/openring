"""Checks that the case text files agree with their sources (review 3: H03, H04, H16 case part).
Usage: python3 -I check_case_docs.py [ROOT [ARCH_MD]]
ROOT holds case-bom.csv, case-architecture.md, case-notes.md, out/case_size.txt, out/case_params.json, look/c5d_check_lead_rerun.log
(default: the folder of this script). ARCH_MD is design/architecture.md (default: ROOT/../architecture.md).
Prints one line per check and RESULT PASS or RESULT FAIL; exit 0 on PASS, 1 on FAIL."""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
ARCH = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(ROOT, "..", "architecture.md")
HIST = re.compile(r"history|before C5d|before C5e|at that time|\bthen\b|at C5b|at most|owner's limit|rejected|instead of|not fitted|does not fit", re.I)
fails = []


def fail(msg):
    fails.append(msg)
    print("FAIL", msg)


def ok(msg):
    print("ok  ", msg)


def read(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


bom = list(csv.DictReader(open(os.path.join(ROOT, "case-bom.csv"), newline="", encoding="utf-8")))
arch = read("case-architecture.md").split("\n")
notes = read("case-notes.md").split("\n")
size_txt = read("out/case_size.txt")
params = json.load(open(os.path.join(ROOT, "out", "case_params.json")))
log = read("look/c5d_check_lead_rerun.log")
docs = [("case-architecture.md", arch), ("case-notes.md", notes)]

# ---- sources
m = re.search(r"X ([\d.]+) mm x Y ([\d.]+) mm x Z ([\d.]+) mm", size_txt)
size = tuple(m.groups()) if m else None
if not size:
    fail("out/case_size.txt: no size line")
else:
    box = tuple("%.1f" % v for v in params["size_box"])
    if box != size:
        fail("out/case_params.json size_box %s differs from out/case_size.txt %s" % (box, size))
    else:
        ok("size %s x %s x %s mm: case_size.txt and case_params.json agree" % size)
pm = re.findall(r"pairs checked (\d+); failures (\d+)", log)
pairs = pm[-1][0] if pm else None
if not pairs:
    fail("lead log: no 'pairs checked N; failures M' line")
else:
    ok("lead log pairs checked %s, failures %s" % pm[-1])
roll = re.findall(r"roll play .*?pad row moves at most ([\d.]+) mm .*?up to ([\d.]+) mm\): (\w+)", log)
if len(roll) != 7 or any(r[2] != "OK" for r in roll):
    fail("lead log: expected 7 roll lines all OK, found %d" % len(roll))
    rollmax = rolllim = None
else:
    rollmax = max(float(r[0]) for r in roll)
    rolllim = roll[0][1]
    ok("lead log roll: 7 lines OK, largest %.3f mm, limit %s mm" % (rollmax, rolllim))

# ---- 1 pin: one fitted part in every file
bore, barrel = params["pin_holder"]["bore"], params["pin"]["barrel_d"]
fitted = [r for r in bom if r["reference"] == "P1-P4"]
if len(fitted) != 1:
    fail("case-bom.csv: %d rows with reference P1-P4" % len(fitted))
    pin = None
else:
    pin = fitted[0]["maker_part_number"]
    ok("case-bom.csv P1-P4 fitted pin %s %s (holder bore %.2f for barrel %.2f in out/case_params.json)" % (fitted[0]["maker"], pin, bore, barrel))
for r in bom:
    s = " ".join(r.values())
    if ("Mill-Max" in s or "0981" in s) and r["reference"] != "P1-P4":
        if r["quantity"] != "0" or "does not fit" not in s:
            fail("case-bom.csv item %s: Mill-Max line must be quantity 0 and say it does not fit" % r["item"])
        else:
            ok("case-bom.csv item %s: Mill-Max kept as history, quantity 0, says it does not fit" % r["item"])
    if r["maker"] == "Mill-Max" and r["reference"] == "P1-P4":
        fail("case-bom.csv: Mill-Max is the fitted P1-P4")
if pin:
    rows = [l for l in arch if l.startswith("| P1-P4 |")]
    if len(rows) != 1 or not rows[0].split("|")[3].strip().startswith(fitted[0]["maker"] + " " + pin):
        fail("case-architecture.md: the P1-P4 parts row does not name %s" % pin)
    else:
        ok("case-architecture.md P1-P4 parts row names %s" % pin)
    for name, lines in docs:
        for i, l in enumerate(lines, 1):
            if re.search(r"Mill-Max|0981", l) and not HIST.search(l):
                fail("%s:%d names the Mill-Max pin with no history marker: %s" % (name, i, l[:90]))
            for p in set(re.findall(r"P70-\w+", l)):
                if p != pin and p != "P70-6000045R":
                    fail("%s:%d names a different P70 part %s" % (name, i, p))
    for name, lines in docs:
        if not any("not confirmed" in l.lower() and pin in l for l in lines):
            fail("%s: no 'not confirmed' statement for %s" % (name, pin))

# ---- 2 outer size and pair count
trip = re.compile(r"(\d+\.\d) x (\d+\.\d) x (\d+\.\d) mm")
for name, lines in [("case-bom.csv", [",".join(r.values()) for r in bom])] + docs:
    for i, l in enumerate(lines, 1):
        for mt in trip.finditer(l):
            t = mt.groups()
            if size and t != size and all(abs(float(a) - float(b)) < 1.0 for a, b in zip(t, size)) and not HIST.search(l[max(0, mt.start() - 70):mt.start()] + " " + l[mt.end():mt.end() + 20]):
                fail("%s:%d states the size %s x %s x %s mm; out/case_size.txt says %s x %s x %s" % ((name, i) + t + size))
        for mp in re.finditer(r"(\d+) pairs checked", l):
            n = mp.group(1)
            if pairs and n != pairs and not HIST.search(l[max(0, mp.start() - 120):mp.start()]):
                fail("%s:%d states %s pairs checked; the lead log says %s" % (name, i, n, pairs))
for name, lines in docs:
    if size and not any(" x ".join(size) + " mm" in l for l in lines):
        fail("%s never states the current size %s mm" % (name, " x ".join(size)))
    if pairs and not any(pairs + " pairs checked" in l for l in lines):
        fail("%s never states %s pairs checked" % (name, pairs))
if not fails:
    ok("size and pair count statements agree with the source files")

# ---- 3 roll
for name, lines in docs:
    for i, l in enumerate(lines, 1):
        if not re.search(r"roll|pad row", l, re.I):
            continue
        for sent in re.split(r"(?<=\.)\s+", l):
            if re.search(r"not held|0\.680", sent, re.I) and not HIST.search(sent):
                fail("%s:%d states as current that the roll is not held / 0.680 mm: %s" % (name, i, sent[:100]))
    if rollmax is not None and "%.3f" % rollmax not in "\n".join(lines):
        fail("%s never states the current largest roll figure %.3f mm of the lead log" % (name, rollmax))
    if rolllim is not None and not any(("limit " + rolllim) in l or ("against " + rolllim) in l for l in lines):
        fail("%s never states the roll limit %s mm" % (name, rolllim))

# ---- 4 charge current (H16)
am = re.search(r"`CHARGE_CURRENT` = (\d+) mA", open(ARCH, encoding="utf-8").read())
if not am:
    fail("architecture.md: no CHARGE_CURRENT line")
else:
    for i, l in enumerate(arch, 1):
        if "32 mA minimum" in l and "no longer applies" not in l:
            fail("case-architecture.md:%d states the 32 mA minimum as current" % i)
        if "Ring charge:" in l and ("CHARGE_CURRENT = %s mA" % am.group(1)) not in l:
            fail("case-architecture.md:%d does not state CHARGE_CURRENT = %s mA" % (i, am.group(1)))
    ok("charge current checked against architecture.md (%s mA)" % am.group(1))

print("RESULT %s (%d findings)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
