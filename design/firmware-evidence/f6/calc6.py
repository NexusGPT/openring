"""F6 figures from the measured cells of architecture 17.26 (read from the file)."""
import re
import sys

arch = open(sys.argv[1], encoding="utf-8").read()
sec = arch[arch.index("### 17.26 "):arch.index("## 18. ")]
rows = re.findall(r"^\| US (\d+) \| [^|]+\| [^|]+\| [\d.]+ mm \| ([\d.]+) to ([\d.]+) mAh \| ([\d.]+) to ([\d.]+) \|$", sec, re.M)
print("17.26 rows read:", len(rows))
I = 4.0 + 2 * (0.63 - 0.58)
lo = min(float(r[1]) for r in rows)
hi = max(float(r[2]) for r in rows)
print(f"smallest {lo} mAh, largest {hi} mAh, recording {I:.2f} mA")
for us, a, b, h1, h2 in rows:
    a, b = float(a), float(b)
    print(f"US {us}: {a} to {b} mAh; record {a / I:.2f} to {b / I:.2f} h (17.26: {h1} to {h2}); charge {a / 15:.2f} to {b / 15:.2f} h")
for name, pct in (("B15", 15), ("B5", 5), ("B2", 2)):
    for c in (lo, hi):
        m = pct / 100 * c
        print(f"{name} on {c}: {pct} % x {c} = {m:.3f} mAh; / {I:.1f} x 60 = {m / I * 60:.1f} min")
print(f"recording {lo} / 4.1 = {lo / I:.2f} h; {hi} / 4.1 = {hi / I:.2f} h")
print(f"standby {lo} / 0.03 = {lo / 0.03:.1f} h = {lo / 0.03 / 24:.1f} days; {hi} / 0.03 = {hi / 0.03:.1f} h = {hi / 0.03 / 24:.1f} days")
print(f"Plaud 13 mA: {lo / 13:.2f} to {hi / 13:.2f} h")
print(f"charge 15 mA: 15 / {lo} = {15 / lo:.2f} C; 15 / {hi} = {15 / hi:.2f} C; 16.5 / {lo} = {16.5 / lo:.2f} C")
print(f"1 C of the smallest cell = {lo} mA = {int(round(lo * 1000))} uA")
print(f"first charge to 50 %: 0.5 x {lo} / 15 = {0.5 * lo / 15:.2f} h; 0.5 x {hi} / 15 = {0.5 * hi / 15:.2f} h")
for i, w in ((80, "motor running"), (175, "motor start")):
    print(f"{w}: {i} / {lo} = {i / lo:.2f} C; {i} / {hi} = {i / hi:.2f} C")
print(f"ship days on the smallest cell with U11 1 uA alone: {lo} / 0.001 / 24 = {lo / 0.001 / 24:.0f} days")
