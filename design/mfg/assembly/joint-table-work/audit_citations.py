"""Bar 3 audit: every filled field of joints.csv cites a file line, and `grep -n -F` finds the quoted text on
that line. Reads joints.csv (source column) and citations.csv (the quote of each citation).
Run: design/.venv/bin/python -B audit_citations.py   Last line: AUDIT cited lines found <f> of <t> ..."""
import csv, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
JOINTS = os.path.join(ROOT, "design/mfg/assembly/joints.csv")
FIELDS = ["joint_id", "wiring_line", "end", "what_meets_what", "step", "solder_source", "flux", "tool", "heat",
          "orientation", "alignment", "check", "check_possible_at_this_step"]
with open(JOINTS, newline="") as f:
    rows = list(csv.DictReader(f))
with open(os.path.join(HERE, "citations.csv"), newline="") as f:
    cites = list(csv.DictReader(f))
quote_of = {}
for c in cites:
    quote_of.setdefault((c["joint_id"], c["field"], c["path"], int(c["line"])), c["quote"])
problems, total, found, fields_checked = [], 0, 0, 0
grep_cache = {}
for r in rows:
    per = {}
    for part in r["source"].split(" | "):
        fld, _, refs = part.partition(": ")
        per[fld] = [x.strip() for x in refs.split(";") if x.strip()]
    for fld in FIELDS:
        fields_checked += 1
        refs = per.get(fld, [])
        if not refs:
            problems.append("NO CITATION %s %s" % (r["joint_id"], fld))
            continue
        for ref in refs:
            m = re.fullmatch(r"(.+):(\d+)", ref)
            total += 1
            if not m:
                problems.append("BAD REF %s %s %s" % (r["joint_id"], fld, ref))
                continue
            path, line = m.group(1), int(m.group(2))
            q = quote_of.get((r["joint_id"], fld, path, line))
            if q is None:
                problems.append("NO QUOTE %s %s %s" % (r["joint_id"], fld, ref))
                continue
            key = (path, q)
            if key not in grep_cache:
                p = subprocess.run(["grep", "-n", "-F", "--", q, os.path.join(ROOT, path)], capture_output=True, text=True)
                grep_cache[key] = {int(l.split(":", 1)[0]) for l in p.stdout.splitlines() if l.split(":", 1)[0].isdigit()}
            if line in grep_cache[key]:
                found += 1
            else:
                problems.append("NOT ON LINE %s %s %s:%d %r (grep lines %s)" % (r["joint_id"], fld, path, line, q, sorted(grep_cache[key])[:5]))
for p in problems:
    print(p)
paths = sorted({c["path"] for c in cites})
print("files cited: %d (%s)" % (len(paths), ", ".join(paths)))
print("AUDIT cited lines found %d of %d total, fields with a citation %d of %d, rows %d, problems %d" % (
    found, total, fields_checked - sum(1 for p in problems if p.startswith("NO CITATION")), fields_checked, len(rows), len(problems)))
