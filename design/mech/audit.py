import re, glob, sys
notes = open("mech-notes.md").read()
ev = ""
for f in glob.glob("logs/*.log") + ["dimensions.csv", "placement.csv", "out/mass-estimate.csv", "ring.py", "check_fit.py", "src_text/wikipedia_ring_size_raw.txt", "mass.py", "../parts/ui-pass3.md", "../architecture.md"]:
    ev += open(f, errors="ignore").read() + "\n"
nums = sorted(set(re.findall(r"(?<![\w.])-?\d+\.\d+|(?<![\w.])\d+(?![\w.])", notes)), key=lambda s: float(s))
miss = []
for n in nums:
    v = n.lstrip("-")
    if v in ev:
        continue
    miss.append(n)
print(f"numbers checked: {len(nums)}, not found verbatim in evidence: {len(miss)}")
print("UNMATCHED:", " ".join(miss))
