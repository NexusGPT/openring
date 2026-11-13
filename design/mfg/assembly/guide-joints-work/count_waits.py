"""Count the failing lines of check_joints.py by the change each row waits for (read from the row's gap text)."""
import csv, re, sys, collections
log, table = sys.argv[1], sys.argv[2]
rows = {r["joint_id"]: r for r in csv.DictReader(open(table, newline="", encoding="utf-8"))}
fails = [l for l in open(log, encoding="utf-8") if l.startswith("R")]
def waits(g):
    w = []
    if "board helper" in g and "J_BAND" in g: w.append("board helper: 15 J_BAND paste openings")
    if "change C3" in g: w.append("board helper: change C3 (J1 openings, test pads)")
    for c in ("C1", "C2", "C13", "C6", "C5", "C4", "C14"):
        if re.search(r"change %s\b" % c, g) or re.search(r"\b%s\b" % c, g) and "change" in g: 
            if re.search(r"\b%s\b" % c, g): w.append("change " + c)
    return tuple(sorted(set(w))) or ("none named",)
lines_by, rows_by = collections.Counter(), collections.defaultdict(set)
other = []
for l in fails:
    m = re.match(r"R\d \S+: (\S+) ", l)
    if not m or m.group(1) not in rows: other.append(l.strip()); continue
    k = waits(rows[m.group(1)]["gap"])
    lines_by[k] += 1; rows_by[k].add(m.group(1))
for k in sorted(lines_by):
    print("WAITS %s | failing lines %d | rows %d | %s" % (" + ".join(k), lines_by[k], len(rows_by[k]), ", ".join(sorted(rows_by[k]))))
print("OTHER", len(other), other[:5])
print("TOTAL failing lines", sum(lines_by.values()) + len(other), "rows", sum(len(v) for v in rows_by.values()))
