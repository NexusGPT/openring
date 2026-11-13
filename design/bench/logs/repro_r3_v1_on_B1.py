# Reproduction (not the original raw log): rule R3 as it was in check version 1, applied to bench-plan-B1.md.
import re
B=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/bench/")
light_re = re.compile(r"recording light|red led|\bLED1\b|\bR41\b|\bQ2\b|light guide|\bLG1\b|\bLP1\b|\bthe light\b|light test", re.I)
ok_re = re.compile(r"removed|no recording light|out of the design|wires no|not wired", re.I)
for k, line in enumerate(open(B+"bench-plan-B1.md").read().split("\n"), start=1):
    if light_re.search(line) and not ok_re.search(line):
        print("v1 R3 hit line %d: %s" % (k, line.strip()[:90]))
