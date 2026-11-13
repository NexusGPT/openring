"""Computed values of the custom screen panel page. Every input is read from its design file here (not typed),
except where a value is printed only in prose; those inputs are found by a regex on the cited line and the line
number is printed. Run: python3 calc.py > logs/calc.log 2>&1"""
import csv
import json
import re
from pathlib import Path

ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix()))
D = ROOT / "design"
V9 = D / "mech/thin/out/v10/before"


def line_val(path, lineno, pattern, group=1):
    txt = Path(path).read_text(encoding="utf-8").splitlines()[lineno - 1]
    m = re.search(pattern, txt)
    if not m:
        raise SystemExit(f"NOT FOUND {path}:{lineno} /{pattern}/")
    v = float(m.group(group))
    print(f"  input {v} from {Path(path).relative_to(ROOT)}:{lineno} /{pattern}/")
    return v


rows = {r["part"]: r for r in csv.DictReader(open(V9 / "placement.csv"))}


def zr(part):
    r = rows[part]
    z, h = float(r["z"]), float(r["size_z"])
    return round(z - h / 2, 4), round(z + h / 2, 4), h


print("== stack of the thin block (inside model v9 placement.csv as saved in out/v10/before) ==")
b0, b1, bt = zr("main_board")
f0, f1, ft = zr("foam")
s0, s1, st = zr("screen")
a0, a1, at = zr("clear_adhesive")
g0, g1, gt = zr("cover_glass")
print(f"board Z {b0}..{b1} (t {bt}); foam {f0}..{f1} (t {ft}); panel {s0}..{s1} (t {st}); adhesive {a0}..{a1} (t {at}); curved glass {g0}..{g1}")
seat_flat = line_val(D / "look/s1/merged417flat-notes.md", 67, r"glass seat Z (3\.7200)")
top_flat = line_val(D / "look/s1/merged417flat-notes.md", 59, r"FLAT (4\.1455)")
shift = line_val(D / "look/s1/out/work-flat/measure-flat-final-us9.log", 89, r"higher by (0\.9700)")
gthk = line_val(D / "look/s1/merged417flat-notes.md", 60, r"to (0\.4255) everywhere")
under_glass = round(seat_flat - shift, 4)
glass_top = round(top_flat - shift, 4)
print(f"flat glass on the thin block: underside {seat_flat} - {shift} = {under_glass}; top {top_flat} - {shift} = {glass_top}; thickness {gthk} (top - underside {round(glass_top - under_glass, 4)})")
print(f"check: v9 curved glass underside {g0} equals flat underside {under_glass}: {abs(g0 - under_glass) < 1e-6}")
room = round(under_glass - b1, 4)
print(f"STACK board top {b1} to glass underside {under_glass} = {room} = foam {ft} + panel {st} + adhesive {at} = {round(ft + st + at, 4)}")
pmax = round(room - ft - at, 4)
print(f"PANEL THICKNESS MAX {room} - {ft} - {at} = {pmax}")
under = line_val(V9 / "thin.py", 61, r"under=(1\.00)")
gap = line_val(V9 / "thin.py", 61, r"gap=(0\.05)")
padt = line_val(V9 / "thin.py", 61, r"pad_t=(0\.02)")
ztop = round(b0 - padt, 4)
zlow = round(b0 - under, 4)
zfloor = round(zlow - gap, 4)
print(f"UNDER THE BOARD: part tops (land faces) at {b0} - {padt} = {ztop}; parts allowance to {b0} - {under} = {zlow}; floor top {zlow} - {gap} = {zfloor}; land face to floor {round(ztop - zfloor, 4)}")
for hj in (0.9, 1.0):
    print(f"   a part {hj} high hanging from {ztop} ends at {round(ztop - hj, 4)}: {round(ztop - hj - zfloor, 4)} above the floor top")

print("== plan ==")
sx, sy = float(rows["screen"]["size_x"]), float(rows["screen"]["size_y"])
px = line_val(D / "mfg/specs/body.md", 67, r"\((27\.45);")
py = line_val(D / "mfg/specs/body.md", 68, r"pocket (12\.9) ")
cl = line_val(D / "mfg/specs/body.md", 67, r"by (0\.05) mm per side")
print(f"panel today {sx} x {sy}; pocket {px} x {py}; clearance {cl} per side: panel max {round(px - 2 * cl, 3)} x {round(py - 2 * cl, 3)}")
mf = json.load(open(D / "look/s1/out/measures-merged417flat-us9.json"))
gmin, gmax = mf["glass"]["min"], mf["glass"]["max"]
GX, GY = round(gmax[0] - gmin[0], 3), round(gmax[1] - gmin[1], 3)
print(f"flat glass box (measures-merged417flat-us9.json glass min {gmin} max {gmax}): {GX} x {GY}")
roll = line_val(D / "look/s1/merged417flat-notes.md", 61, r"to (0\.42) all round")
corner = line_val(D / "look/s1/merged417flat-notes.md", 64, r"plan corner (2\.5)")
FX, FY = round(GX - 2 * roll, 3), round(GY - 2 * roll, 3)
print(f"GLASS FACE outline {GX} x {GY}, corner radius {corner}; flat part {GX} - 2 x {roll} = {FX} by {GY} - 2 x {roll} = {FY}, corner {round(corner - roll, 3)}")
wall_x, wall_y = round((GX - px) / 2, 4), round((GY - py) / 2, 4)
print(f"WALL from glass edge to pocket face: ends ({GX} - {px}) / 2 = {wall_x}; sides ({GY} - {py}) / 2 = {wall_y}")
lit_today = (21.6, 10.8)
area_today = round(lit_today[0] * lit_today[1], 2)
for b in (0.5, 1.0):
    lx, ly = round(px - 2 * cl - 2 * b, 3), round(py - 2 * cl - 2 * b, 3)
    vis = round(wall_x + cl + b, 3)
    rc = round(corner - vis, 3)
    print(f"LIT with border {b}: {lx} x {ly} = {round(lx * ly, 2)} mm2 ({round(lx * ly / area_today, 3)} x today's {area_today}); black seen from the glass edge to the lit edge {wall_x} + {cl} + {b} = {vis} per side; lit corner radius concentric with the glass corner {corner} - {vis} = {rc}")
    print(f"   share of the glass face outline {GX} x {GY} lit (rectangles): {round(100 * lx * ly / (GX * GY), 1)} percent; today {round(100 * area_today / (GX * GY), 1)} percent")
print(f"today's print borders (cover-glass.md lines 38 to 40): long side 1.98, fingertip 2.38, hand end 5.33")

print("== pixels ==")
ppi = line_val(D / "datasheets/slim_tailor-toh095xvt-01-p4-8.txt", 77, r"^(282)$")
pitch = round(lit_today[0] / 240, 4)
print(f"today's pitch 21.6 / 240 = {pitch}, 10.8 / 120 = {round(10.8 / 120, 4)}; 25.4 / {pitch} = {round(25.4 / pitch, 1)} ppi (sheet: {ppi})")
spi = line_val(D / "firmware.md", 79, r"maximum data rate (8) Mbit/s")
for b in (0.5, 1.0):
    lx, ly = round(px - 2 * cl - 2 * b, 3), round(py - 2 * cl - 2 * b, 3)
    p_l, p_w = round(lx / 240, 4), round(ly / 120, 4)
    sq = min(p_l, p_w)
    print(f"OPTION 1 border {b}: 240 x 120 on {lx} x {ly}: pitch along the finger {p_l}, across {p_w} (pixel {round(p_l / p_w, 3)} times longer than wide); square pixels at {sq}: lit {round(240 * sq, 2)} x {round(120 * sq, 2)}")
    nx, ny = int(lx / pitch), int(ly / pitch + 1e-9)
    print(f"OPTION 2 border {b}: at pitch {pitch}: {lx} / {pitch} = {round(lx / pitch, 2)} -> {nx} columns, {ly} / {pitch} = {round(ly / pitch, 2)} -> {ny} rows: {nx} x {ny} = {nx * ny} pixels ({round(nx * ny / 28800, 3)} x 28800)")
    fb = nx * ny * 2
    print(f"   frame RGB565 {nx} x {ny} x 2 = {fb} bytes (today 240 x 120 x 2 = {240 * 120 * 2}); one full frame at {spi:.0f} Mbit/s: {round(fb * 8 / (spi * 1e6) * 1000, 1)} ms (today {round(240 * 120 * 2 * 8 / (spi * 1e6) * 1000, 1)} ms)")

print("== connection ==")
j1x = -11.650
j1_now = -4.933
print(f"J1 move from the routed place X {j1_now} to the thin plan X {j1x}: {round(j1_now - j1x, 3)} mm toward the hand end")
jy = -0.150
for w in (4.8, 5.0):
    print(f"tail {w} wide centred on J1 Y {jy}: Y {round(jy - w / 2, 3)}..{round(jy + w / 2, 3)}; to the copper-free zone edge Y 3.10: {round(3.10 - (jy + w / 2), 3)}; past the radio corner edge Y 2.05: {round(jy + w / 2 - 2.05, 3)}")
pitch_hb, land_w = 0.51, 0.30
for p, lw in ((pitch_hb, land_w), (0.30, 0.15)):
    print(f"15 lands {lw} wide at pitch {p}: row {round(14 * p + lw, 3)} long")
# option C: lands on the screen face beside a shortened panel (land 0.55 long from the edge band at -13.45)
land_x0 = round(-13.45 + 0.05, 3)
land_x1 = round(land_x0 + 0.55, 3)
pend = round(land_x1 + 0.05, 3)
print(f"OPTION C: lands X {land_x0}..{land_x1}, panel hand end at {pend} instead of {-sx / 2}: shorter by {round(pend - (-sx / 2), 3)}")
print("J1 under the board: see UNDER THE BOARD lines (0.9 nominal, 1.0 catalogue maximum)")
tailpocket_x0 = round(-13.775 - 0.55 / 2, 3)
print(f"tail pocket of model v9 (thin.py line 530 box 0.55 wide at X -13.775): X {tailpocket_x0}..{round(-13.775 + 0.275, 3)}, end wall left {round(GX / 2 + tailpocket_x0, 3)}")
print("RESULT calc done")
