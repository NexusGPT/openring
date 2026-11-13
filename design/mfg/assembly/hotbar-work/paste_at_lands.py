"""Count paste openings of ring-F_Paste.gbr at the 15 J_BAND land centres (read only). usage: python3 -I paste_at_lands.py <gbr> <ring-dump.txt>"""
import re, sys
g = open(sys.argv[1]).read()
m = re.search(r"%FSLAX(\d)(\d)Y", g)
dec = int(m.group(2))
flashes = [(int(x) / 10 ** dec, int(y) / 10 ** dec) for x, y in re.findall(r"X(-?\d+)Y(-?\d+)D03", g)]
lands = []
for line in open(sys.argv[2]):
    if line.startswith("J_BAND_"):
        p = line.split(",")
        if not p[1].isdigit():
            continue
        lands.append((p[0] + " " + p[1], float(p[3]), float(p[4])))
print(f"format decimals {dec}; flashes {len(flashes)}; lands {len(lands)}")
hits = 0
for name, x, y in lands:
    near = [f for f in flashes if abs(f[0] - x) < 0.2 and (abs(f[1] - y) < 0.2 or abs(f[1] + y) < 0.2)]
    hits += bool(near)
    print(f"{name} at ({x:.3f}, {y:.3f}): paste flashes within 0.2 mm: {len(near)}")
ctrl = [f for f in flashes if abs(f[0] - 99.54) < 0.2 and abs(abs(f[1]) - 105.45) < 0.2]
print(f"control: C83 pad 1 at (99.540, 105.450) has {len(ctrl)} paste flash(es) within 0.2 mm")
print(f"RESULT lands with a paste opening: {hits} of {len(lands)}")
