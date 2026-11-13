"""Case rows of joints.csv: each 'step:' citation of board-notes.md lands on the line of that case step; no cited
line is blank; every quoted phrase of P-case_main's check is in board-notes.md word for word."""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
B = open(os.path.join(HERE, "..", "..", "..", "ecad", "case", "pcb", "board-notes.md"), encoding="utf-8").read().split("\n")
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "joints.csv"), newline="", encoding="utf-8")))
bad = n = 0
for r in rows:
    if not r["step"].startswith("case"):
        continue
    k = int(r["step"].split()[1])
    m = re.search(r"step: design/ecad/case/pcb/board-notes\.md:(\d+)", r["source"])
    if m:
        n += 1
        l = B[int(m.group(1)) - 1]
        ok = l.startswith("%d. " % k)
        bad += not ok
        print("OK " if ok else "BAD", r["joint_id"], "case", k, "line", m.group(1), "|", l[:60])
    for ln in re.findall(r"board-notes\.md:(\d+)", r["source"]):
        if not B[int(ln) - 1].strip():
            print("BAD blank line", r["joint_id"], ln)
            bad += 1
pc = [r for r in rows if r["joint_id"] == "P-case_main"][0]
whole = "\n".join(B)
for q in re.findall(r'"([^"]+)"', pc["check"]):
    n += 1
    ok = q in whole
    bad += not ok
    print("QUOTE", "OK " if ok else "BAD", q)
print("MISSING in P-case_main:", [k for k, v in pc.items() if "MISSING" in v], "gap:", repr(pc["gap"]))
print("RESULT case citations and quotes %d problems %d" % (n, bad))
