"""For every assembly.md:N in joints.csv: the line exists; a 'step:' citation of a row whose step is an assembly
step lands inside that step (between its heading and the next heading). Prints each problem and a count."""
import csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
G = open(os.path.join(HERE, "..", "assembly.md"), encoding="utf-8").read().split("\n")
heads = [(i, int(m.group(1))) for i, l in enumerate(G, 1) for m in [re.match(r"### Step (\d+)\. ", l)] if m]
def step_of(n):
    s = None
    for i, st in heads:
        if i <= n: s = st
    nxt = [i for i, _ in heads if i > n]
    sec = [i for i, l in enumerate(G, 1) if l.startswith("## ") and i > n]
    if s is not None and sec and (not nxt or sec[0] < nxt[0]) and sec[0] < n: return None
    return s
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "joints.csv"), newline="", encoding="utf-8")))
probs = total = 0
for r in rows:
    for m in re.finditer(r"([a-z_]+): ([^|]*)", r["source"]):
        key, val = m.group(1), m.group(2)
        for n in re.findall(r"design/mfg/assembly/assembly\.md:(\d+)", val):
            n = int(n); total += 1
            if n > len(G) or not G[n-1].strip():
                print("PROBLEM", r["joint_id"], key, n, "empty or missing line"); probs += 1; continue
            if key == "step" and re.fullmatch(r"\d+", r["step"].strip()):
                if step_of(n) != int(r["step"]):
                    print("PROBLEM", r["joint_id"], "step", r["step"], "cites line", n, "in step", step_of(n)); probs += 1
            print("OK", r["joint_id"], key, n, "step", step_of(n), "|", G[n-1][:70])
print("RESULT citations %d problems %d" % (total, probs))
