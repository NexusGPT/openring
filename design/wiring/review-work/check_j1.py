# B5 screen connector J1, by coordinates (own derivation, inputs printed).
# Screen drawing (display_TOH095XVT-01.pdf page 5, read by eye in this review): the front view
# (lit face to the viewer, cable end down) labels the contacts "15 ... 1" left to right, so contact 1
# is on the viewer's RIGHT; the back view labels "1 ... 15".
# Ring frame (ring-board-plan.md line 20): X along the finger (+X fingertip), Y across (-Y joystick),
# Z up toward the screen; KiCad = model + (100, 100), no mirror.
# Layout C (screen-cable-study.md 4.3, lead-decisions row 65): screen turned 180 degrees, so the cable
# leaves the panel toward +X; seen from +Z with the cable end toward +X, the viewer's right is +Y
# (right x up = toward viewer: (+Y) x (-X) = +Z). The two folds turn about the Y axis only, so each
# contact keeps its Y: contact 1 must meet the J1 land at the largest Y, contact 15 the smallest.
# Hirose FH35C land pattern (catalogue p4): odd contacts on the 0.8 long lands, which are on the FPC
# side (p3 detail: lead 0.05 out on the FPC side, 0.15 on the lever side); the opening must face +X.
import csv
import os
W = os.environ.get('WDIR', (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/review-work"))
NETS = {1: 'ELVSS', 2: 'ELVDD', 3: '', 4: 'VDD_3V0', 5: 'VDD_1V8', 6: 'SWIRE', 7: 'LCD_TE', 8: 'LCD_RST', 9: 'LCD_CS',
        10: 'LCD_SCK', 11: 'LCD_DCX', 12: 'LCD_MOSI', 13: 'GND', 14: 'GND', 15: 'GND'}  # ring netlist DISP1 rows
j = {r['pad']: r for r in csv.DictReader(open(f'{W}/pads/ring.csv')) if r['ref'] == 'J1'}
ok = True
ys = []
for k in range(1, 16):
    r = j[str(k)]
    y = float(r['y_mm']) - 100; x = float(r['x_mm']) - 100
    ys.append(y)
    good = r['net'] == NETS[k]
    ok &= good
    print(f"J1 pad {k}: model X {x:+.3f} Y {y:+.3f} layer {r['layers']} size {r['pad_w']}x{r['pad_h']} net {r['net']!r} screen contact {k} net {NETS[k]!r} {'ok' if good else 'MISMATCH'}")
mono = all(ys[i] > ys[i + 1] for i in range(14))
print('Y falls from pad 1 to pad 15 (contact 1 at +Y):', mono)
long_x = sorted({round(float(r['x_mm']) - 100, 3) for k, r in j.items() if k != 'MP' and r['pad_h'] == '0.8'})
short_x = sorted({round(float(r['x_mm']) - 100, 3) for k, r in j.items() if k != 'MP' and r['pad_h'] == '0.65'})
print('long (FPC side) land row X', long_x, 'short (lever side) row X', short_x, '-> opening faces', '+X' if long_x[0] > short_x[0] else '-X')
odd_long = all(j[str(k)]['pad_h'] == '0.8' for k in range(1, 16, 2))
print('odd contacts on the long row:', odd_long)
print('all on B.Cu (screen face):', all(j[str(k)]['layers'] == 'B.Cu' for k in range(1, 16)))
res = ok and mono and long_x[0] > short_x[0] and odd_long
print('RESULT j1', 'PASS' if res else 'FAIL')
