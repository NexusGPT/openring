"""List every case where geom_check.log differs from the expectation written before the run (logs/expected-geom.txt)."""
import re, sys
log = open(sys.argv[1]).read()
diffs = []
tails = re.findall(r"FLEX(\d) US (\d+): flat length ([\d.]+).*?free length ([-+][\d.]+); foot width ([\d.]+), neck width ([\d.]+).*?VERDICT (.*)", log)
if len(tails) != 14: diffs.append(f"tails {len(tails)} expected 14")
for k, us, flat, free, fw, nw, v in tails:
    if abs(float(free)) > 0.05: diffs.append(f"FLEX{k} US {us} free {free} expected within 0.05")
    if abs(float(fw) - 2.5) > 1e-3: diffs.append(f"FLEX{k} US {us} foot {fw} expected 2.500")
    if abs(float(nw) - 1.8) > 1e-3: diffs.append(f"FLEX{k} US {us} neck {nw} expected 1.800")
    if "FOOT DOES NOT PASS" not in v or "NO LIFT" not in v: diffs.append(f"FLEX{k} US {us} verdict {v} expected no pass, no lift")
for key, val in (("land face to floor", "1.030"), ("foot back (stiffener) to floor", "0.790"), ("needs", "1.620")):
    if f"{key} {val}" not in log: diffs.append(f"'{key} {val}' not found")
near = re.findall(r"NEAR (\w+),", log)
exp = {"U3", "U11", "C83", "C84", "J1"}
for r in sorted(exp - set(near)): diffs.append(f"expected near part {r} missing")
for r in near:
    if r not in exp: diffs.append(f"unexpected near part {r} (not in the expectation)")
print("\n".join(diffs) if diffs else "no differences")
print(f"DIFF cases differing: {len(diffs)}")
