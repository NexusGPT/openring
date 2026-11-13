"""First fit check for the slim ring (owner's choice 2026-11-10: about 22 x 15 x 6.5 mm).
Every figure is tagged: DS = read from a maker document already in this project,
EST = estimate to replace when design/parts/slim.md lands. Exit 1 when the stack or
the board area does not fit. Run: design/.venv/bin/python -I design/mech/slim_budget.py"""
import csv, re, collections, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
BLOCK = dict(x=22.0, y=15.0, z=6.5)                       # owner's slim size
WALL, FLOOR = 0.8, 0.6                                    # EST: side wall as today, thinner floor
stack = [  # name, mm, tag
 ("cover glass", 0.50, "DS"), ("clear adhesive", 0.10, "DS"), ("screen module", 0.80, "EST"),
 ("foam pad", 0.15, "EST"), ("board", 0.40, "EST"), ("tallest part under the board", 1.00, "DS coil 1.0, mic IM68D128 0.98"),
 ("gap", 0.10, "EST"), ("floor", FLOOR, "EST")]
fixed = sum(v for _, v, _ in stack)
cell_room = BLOCK["z"] - fixed
swelling = round(cell_room * 0.10, 2)                     # EST: 10 percent of the cell slot
cell_t = round(cell_room - swelling, 2)
cav_x, cav_y = BLOCK["x"] - 2 * WALL, BLOCK["y"] - 2 * WALL
cell_x, cell_y = cav_x - 2.0, cav_y - 1.0                 # EST: room for the tab end and the walls
vol = cell_t * cell_x * cell_y
OLD_DENSITY = 135 / (4.6 * 13.0 * 25.0)                   # mAh per cubic mm of the cell planned before
cap_lo, cap_hi = vol * OLD_DENSITY * 0.70, vol * OLD_DENSITY * 0.90   # EST: small thin cells store less per volume
# board area, one side (the screen rests on the other side)
board_x, board_y = cav_x - 0.6, cav_y - 0.6
board_area = board_x * board_y
c = collections.Counter()
for r in csv.DictReader(open(os.path.join(HERE, "..", "bom.csv"))):
    for ref in re.split(r"[ ,;]+", r["reference"]):
        m = re.match(r"[A-Za-z]+", ref)
        if m: c[m.group(0)] += int(1)
passives = c["R"] + c["C"] + c["FB"]
big = [  # name, area mm2 with 0.2 mm keep-out per side, tag
 ("main chip 3.02 x 2.43", 3.42 * 2.83, "DS"), ("power chip 3.1 x 2.4", 3.5 * 2.8, "DS"),
 ("screen supply chip and coil", 2.4 * 2.4 + 2.9 * 2.4, "DS; drops out when the screen brings its own supply"),
 ("storage", 6.4 * 5.4, "EST 6 x 5 mm package; today's part is 8.0 x 6.2"),
 ("2 microphones 3.5 x 2.65", 2 * 3.9 * 3.05, "DS IM68D128"), ("antenna 3.2 x 1.6 with clear zone", 5.0 * 3.0, "EST"),
 ("screen connector", 5.6 * 3.6, "DS FH35C footprint assumed"), ("2 power coils", 2 * 2.4 * 2.0, "EST"),
 ("2 crystals", 2.0 * 1.6 + 2.0 * 1.6, "EST"), ("5 joystick switches", 5 * 3.0 * 2.0, "EST SKTA class 2.6 x 1.6"),
 ("vibration part", 6.4 * 6.4, "EST coin motor 6 mm, beside the board when it does not fit on it"),
 (f"{passives} small parts in 0201 size", passives * 1.0 * 0.6, "count from bom.csv of the large ring")]
used = sum(a for _, a, _ in big)
fill = used / board_area
print(f"block {BLOCK['x']} x {BLOCK['y']} x {BLOCK['z']} mm; cavity {cav_x:.1f} x {cav_y:.1f}")
for n, v, t in stack: print(f"  stack {n:32s} {v:5.2f}  [{t}]")
print(f"  fixed layers {fixed:.2f}; left for the cell and its swelling {cell_room:.2f}")
print(f"cell {cell_t} x {cell_y:.1f} x {cell_x:.1f} mm, {vol:.0f} cubic mm, about {cap_lo:.0f} to {cap_hi:.0f} mAh (EST)")
print(f"board {board_x:.1f} x {board_y:.1f} = {board_area:.0f} square mm, one side")
for n, a, t in big: print(f"  area {n:38s} {a:6.1f}  [{t}]")
print(f"  parts by type in bom.csv: {dict(c)}")
print(f"parts area {used:.0f} of {board_area:.0f} square mm = {fill:.0%} (limit 60% for a routable one-sided board)")
fails = []
if cell_t < 2.0: fails.append(f"cell thinner than 2.0 mm ({cell_t})")
if fill > 0.60: fails.append(f"board fill {fill:.0%} over 60%")
print("RESULT:", "PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
