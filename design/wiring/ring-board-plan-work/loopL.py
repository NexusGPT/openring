# Loop inductance of each over-limit capacitor in a capdist log: 0.259 nH/mm for a 0.15 mm track on L1 over the
# L2 ground (h 0.065, Z0 43.4 ohm, eeff 3.20, ring-board-plan.md R3.4), track = 1.2 x the centre distance.
import sys,re
for l in open(sys.argv[1]):
    m=re.match(r"(\S+)\s+(must|should)\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+OVER",l)
    if m:
        d=float(m.group(4))
        print(f"{m.group(1)} {m.group(2)} limit {m.group(3)} distance {d:.2f} track {1.2*d:.2f} mm inductance {1.2*d*0.259:.2f} nH ({m.group(5)})" if d<90 else f"{m.group(1)} not placed")
