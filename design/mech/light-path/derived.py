#!/usr/bin/env python3
"""Every derived number of light-path.md, computed from its sourced inputs (named in each line). Output: logs/derived2.log."""
import csv
from pathlib import Path

THIN = Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mech/thin"))
rows = {r["part"]: r for r in csv.DictReader(open(THIN / "placement.csv"))}


def lo(r, k):
    return float(r[k]) - float(r["size_" + k]) / 2


def hi(r, k):
    return float(r[k]) + float(r["size_" + k]) / 2


b, m1, j1, sc, st = rows["main_board"], rows["mic_1"], rows["screen_connector"], rows["screen"], rows["storage"]
print(f"board X {lo(b, 'x'):.3f}..{hi(b, 'x'):.3f}, Y {lo(b, 'y'):.3f}..{hi(b, 'y'):.3f}, Z {lo(b, 'z'):.3f}..{hi(b, 'z'):.3f} (placement.csv main_board)")
print(f"v4 mic_1 X {lo(m1, 'x'):.3f}..{hi(m1, 'x'):.3f}, Y {lo(m1, 'y'):.3f}..{hi(m1, 'y'):.3f}; J1 X {lo(j1, 'x'):.3f}..{hi(j1, 'x'):.3f}, Y {lo(j1, 'y'):.3f}..{hi(j1, 'y'):.3f}; storage X {lo(st, 'x'):.3f}..{hi(st, 'x'):.3f}, Y {lo(st, 'y'):.3f}..{hi(st, 'y'):.3f}")
U5 = (-12.8, -8.8, -6.3, -3.3)                      # mic-path.md line 58 (architecture.md 17.19)
print(f"v4: free width at the hand end, board edge to mic_1: {lo(m1, 'x') - lo(b, 'x'):.3f}; strip mic_1 to J1: {lo(j1, 'y') - hi(m1, 'y'):.3f} (Y {hi(m1, 'y'):.3f}..{lo(j1, 'y'):.3f})")
print(f"17.19: free width at the hand end: {U5[0] - lo(b, 'x'):.3f}; strip U5 to J1: {lo(j1, 'y') - U5[3]:.3f} (Y {U5[3]:.3f}..{lo(j1, 'y'):.3f}); column J1 to storage: {lo(st, 'x') - hi(j1, 'x'):.3f} (X {hi(j1, 'x'):.3f}..{lo(st, 'x'):.3f})")
pocket_x, pocket_y = (27.35 + 0.1) / 2, (12.8 + 0.1) / 2          # thin.py line 366
print(f"pocket +-{pocket_x:.3f} x +-{pocket_y:.3f}; board edge to pocket: hand end {pocket_x - hi(b, 'x'):.3f}, long side {pocket_y - hi(b, 'y'):.3f}")
print(f"board top to screen bottom: {lo(sc, 'z') - hi(b, 'z'):.3f}; ledge top {lo(sc, 'z') + 0.4:.3f} to adhesive {hi(sc, 'z'):.3f}: {hi(sc, 'z') - lo(sc, 'z') - 0.4:.3f}")
lens_top = lo(b, "z") - 0.25 + 1.05                  # APTR3216SURCK p1: total 1.05, base 0.25
print(f"APTR3216 on the under face: lens top Z {lens_top:.3f}; into the screen {lens_top - lo(sc, 'z'):.3f}; above the board top {lens_top - hi(b, 'z'):.3f}; board needed {1.05 - 0.25:.3f} thick, +{1.05 - 0.25 - 0.3:.3f}")
print(f"side-view 1.2 needs {1.2 + 2 * 0.20:.3f} with the 0.2 keep-out each side, {1.2 + 2 * 0.10:.3f} with 0.10")
print(f"0402 LED pads 0.5 wide in the 17.19 strip: {(lo(j1, 'y') - U5[3] - 0.5) / 2:.3f} each side (keep-out 0.2)")
LX, LY, WX, WY = -9.70, -2.10, -12.425, -2.95
led_top = lo(b, "z") - 0.02
led_bot = led_top - 0.2
bar_top, bar_bot = led_bot - 0.10, 0.40 + 0.05
h = bar_top - bar_bot
print(f"LED1 centre X {LX:.3f} Y {LY:.3f} Z {(led_top + led_bot) / 2:.3f}; body X {LX - 0.25:.3f}..{LX + 0.25:.3f} Y {LY - 0.5:.3f}..{LY + 0.5:.3f}; pads Y {LY - 0.9:.3f}..{LY + 0.9:.3f}")
print(f"guide height {h:.3f} (Z {bar_bot:.3f}..{bar_top:.3f}, centre {(bar_bot + bar_top) / 2:.3f}); leg 1 length {(LY + h / 2) - (WY - 0.2):.3f}; leg 2 length {(LX + 0.2) - (WX - h / 2):.3f}")
print(f"mirror A: 45 deg face under the LED from (Y {LY - h / 2:.3f}, Z {bar_bot:.3f}) to (Y {LY + h / 2:.3f}, Z {bar_top:.3f}); mirror B at the corner X {LX:.3f} Y {WY:.3f}; "
      f"mirror C from (X {WX + h / 2:.3f}, Z {bar_bot:.3f}) to (X {WX - h / 2:.3f}, Z {bar_top:.3f})")
print(f"light travel: A to B {LY - WY:.3f} along -Y, B to C {LX - WX:.3f} along -X, total {LY - WY + LX - WX:.3f}")
print(f"window move from v4: {WX - (-13.25):.3f} in X, {WY - (-4.7):.3f} in Y")
print(f"APHHS1005SURCK (0.5 tall) guide height {(led_top - 0.5 - 0.10) - bar_bot:.3f}")
print(f"active area start from the drawing {-13.675 + 4.751:.3f} against the lit area edge -9.320: {(-13.675 + 4.751) - (-9.320):.3f}")
print(f"new placement rows: recording_led {LX:.3f},{LY:.3f},{(led_top + led_bot) / 2:.3f},0.500,1.000,0.200; light_pipe {WX:.3f},{WY:.3f},2.450,0.400,0.400,0.400; "
      f"light_guide envelope X {WX - h / 2:.3f}..{LX + 0.2:.3f} Y {WY - 0.2:.3f}..{LY + h / 2:.3f}: centre {((WX - h / 2) + (LX + 0.2)) / 2:.4f},{((WY - 0.2) + (LY + h / 2)) / 2:.3f},{(bar_bot + bar_top) / 2:.3f} size {(LX + 0.2) - (WX - h / 2):.3f} x {(LY + h / 2) - (WY - 0.2):.3f} x {h:.3f}")
