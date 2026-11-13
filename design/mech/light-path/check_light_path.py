#!/usr/bin/env python3
"""Fit check of the recommended recording light path (design/mech/light-path/light-path.md, section 4).

Reads design/mech/thin/placement.csv and design/mech/thin/layers.json (inside model v4, read only), the screen ledge
numbers measured from the maker drawing (logs/screen_ledge.log), the glass probe (logs/glass_probe2.log) and the LED
forward voltage read from the maker curve (logs/kpg_vf_curve.log). Runs every check twice:
  scenario v4    placement.csv as it is;
  scenario 17.19 the same with mic_1 and mic_2 replaced by the microphones of architecture.md 17.19
                 (design/mech/mic-path/mic-path.md line 58: U5 X -12.800..-8.800, Y -6.300..-3.300, Z 0.430..1.430; U6 mirrored in X).
Prints one line per check; the last line is RESULT PASS or RESULT FAIL <what>. Exit 0 on PASS, 1 on FAIL.

Rules used (quoted):
- Collision: check_thin.py line 25 "LIMIT = 0.001" (mm3 of common volume).
- Clearance 0.10 mm between parts: thin-notes.md line 35 "fills the opening with 0.1 mm clearance" and line 69
  "0.1 to the channel wall, 0.1 to the motor". Used for the light guide, LP1 and the board hole (GAP_MIN).
- Board parts: architecture.md line 381 "Parts with a 0.2 mm keep-out" (also rule R2 of the microphone study).
  Used for LED1 and its pads against every other board part, in plan (KEEP).
- Floor: check_thin.py line 161, no under-board part below the floor top; thin.py line 38 gap=0.05.
- Parts under the board at most 1.00 mm: design/mfg/specs/main-board.md line 39.
- Pocket: thin.py line 366, panel pocket = screen outline + 0.1.
- Copper pad to a non-plated hole edge 0.20 mm: [ESTIMATE] board-maker rule, not a project rule.
Options: --shift-led-y <mm> and --shift-riser-x <mm> move the LED or the light column, for the broken-copy tests.
"""
import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
THIN = HERE.parent / "thin"
LOGS = HERE / "logs"
GAP_MIN = 0.10
KEEP = 0.20
PAD_HOLE_MIN = 0.20
results = []


def check(name, ok, detail):
    results.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")


def info(name, detail):
    print(f"INFO {name}: {detail}")


def open_item(name, detail):
    print(f"NOT CHECKED {name}: {detail}")


def box(x0, x1, y0, y1, z0, z1):
    return (min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))


def row_box(r):
    x, y, z = float(r["x"]), float(r["y"]), float(r["z"])
    sx, sy, sz = float(r["size_x"]), float(r["size_y"]), float(r["size_z"])
    return box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2)


def gap(a, b):
    d = [max(0.0, a[2 * i] - b[2 * i + 1], b[2 * i] - a[2 * i + 1]) for i in range(3)]
    ov = 1.0
    for i in range(3):
        ov *= max(0.0, min(a[2 * i + 1], b[2 * i + 1]) - max(a[2 * i], b[2 * i]))
    return math.sqrt(sum(v * v for v in d)), ov


def gap2d(a, b):
    d = [max(0.0, a[2 * i] - b[2 * i + 1], b[2 * i] - a[2 * i + 1]) for i in range(2)]
    return math.sqrt(sum(v * v for v in d))


def circle_box_gap(cx, cy, r, b):
    dx = max(b[0] - cx, 0.0, cx - b[1])
    dy = max(b[2] - cy, 0.0, cy - b[3])
    return math.hypot(dx, dy) - r


def num(pattern, text, n=1):
    m = re.search(pattern, text)
    if not m:
        raise SystemExit(f"RESULT FAIL could not read '{pattern}'")
    return [float(m.group(i + 1)) for i in range(n)]


def scenario(tag, rows, layer_of, a):
    by = {r["part"]: r for r in rows}
    print(f"---- scenario {tag}")
    b = by["main_board"]
    Z_BD0 = float(b["z"]) - float(b["size_z"]) / 2
    Z_BD1 = float(b["z"]) + float(b["size_z"]) / 2
    bx, by_ = float(b["size_x"]) / 2, float(b["size_y"]) / 2
    f = by["foam"]
    Z_FM1 = float(f["z"]) + float(f["size_z"]) / 2
    s = by["screen"]
    Z_SC0 = float(s["z"]) - float(s["size_z"]) / 2
    sx_half, sy_half = float(s["size_x"]) / 2, float(s["size_y"]) / 2
    ad = by["clear_adhesive"]
    Z_AD0 = float(ad["z"]) - float(ad["size_z"]) / 2
    PAD_T, GAP_FLOOR = 0.02, 0.05                       # thin.py line 38: pad_t=0.02, gap=0.05
    Z_FLOOR = Z_BD0 - 1.00 - GAP_FLOOR                  # thin.py build(): Z_FLOOR = Z_BD0 - under - gap
    Z_LEDGE = Z_SC0 + 0.4                               # thin.py line 322: lower glass 0.4
    print(f"stack: board Z {Z_BD0:.3f}..{Z_BD1:.3f}, foam top {Z_FM1:.3f}, screen bottom {Z_SC0:.3f}, ledge top {Z_LEDGE:.3f}, adhesive bottom {Z_AD0:.3f}, floor top {Z_FLOOR:.3f}")
    m1 = row_box(by["mic_1"])
    print(f"mic_1 box X {m1[0]:.3f}..{m1[1]:.3f} Y {m1[2]:.3f}..{m1[3]:.3f} Z {m1[4]:.3f}..{m1[5]:.3f}")

    sl = (LOGS / "screen_ledge.log").read_text()
    ledge_len = num(r"ledge \(lower glass only\) length from the panel end: ([\d.]+) mm", sl)[0]
    f0, f1 = num(r"bond fingers: \d+ lines, from ([\d.]+) to ([\d.]+) mm from the panel end", sl, 2)
    fy0, fy1 = num(r"across (-?[\d.]+) to (-?[\d.]+) mm from the centre line", sl, 2)
    py0, py1 = num(r"FPC outline: across (-?[\d.]+) to (-?[\d.]+) mm", sl, 2)
    pin = num(r"starts ([\d.]+) mm inside the panel end", sl)[0]
    X_END = -sx_half
    X_UPPER_DRAW = X_END + ledge_len
    X_UPPER_MODEL = X_END + 4.8                         # thin.py line 323
    fpc_bond = box(X_END, X_END + pin, py0, py1, Z_LEDGE, Z_LEDGE + 0.2)       # drawing p5: tail 0.2 thick with stiffener
    fingers = box(X_END + f0, X_END + f1, fy0, fy1, Z_LEDGE - 0.001, Z_LEDGE)
    drv_ic = box(X_END + 2.4 - 0.8, X_END + 2.4 + 0.8, -4.0, 4.0, Z_LEDGE, Z_LEDGE + 0.3)   # thin.py line 324 (ASSUMED in the model)

    # ---------------- the recommended path (light-path.md section 4)
    WX, WY = -12.425 + a.shift_riser_x, -2.95          # light column: riser, board hole, foam notch, LP1, print window
    LX, LY = -9.70, -2.10 + a.shift_led_y              # LED1 centre, long side along Y
    led = box(LX - 0.25, LX + 0.25, LY - 0.5, LY + 0.5, Z_BD0 - PAD_T - 0.2, Z_BD0 - PAD_T)       # KPG-1005SURC-TT 1.0 x 0.5 x 0.2 (p1)
    pads = [box(LX - 0.25, LX + 0.25, LY - 0.9, LY - 0.2, Z_BD0 - PAD_T, Z_BD0),                   # land 0.7 + 0.4 + 0.7 x 0.5 (p4)
            box(LX - 0.25, LX + 0.25, LY + 0.2, LY + 0.9, Z_BD0 - PAD_T, Z_BD0)]
    bar_top = led[4] - GAP_MIN
    bar_bot = Z_FLOOR + GAP_FLOOR
    h = bar_top - bar_bot
    W = 0.40                                            # guide section width
    leg2 = box(WX - h / 2, LX + W / 2, WY - W / 2, WY + W / 2, bar_bot, bar_top)                # along X, mirror C at its -X end, mirror B at its +X end
    leg1 = box(LX - W / 2, LX + W / 2, WY - W / 2, LY + h / 2, bar_bot, bar_top)                # along Y, mirror A under the LED at its +Y end
    riser_r, hole_r = 0.15, 0.25                        # riser dia 0.3, non-plated hole dia 0.5
    riser = box(WX - riser_r, WX + riser_r, WY - riser_r, WY + riser_r, bar_top, Z_BD1)
    foam_win = box(WX - 0.25, WX + 0.25, WY - 0.25, WY + 0.25, Z_BD1, Z_FM1)
    lp1 = box(WX - 0.2, WX + 0.2, WY - 0.2, WY + 0.2, Z_LEDGE, Z_AD0)                           # LP1 0.4 x 0.4 x 0.4
    win_r = 0.2                                         # print window dia 0.4
    print(f"LED1 X {led[0]:.3f}..{led[1]:.3f} Y {led[2]:.3f}..{led[3]:.3f} Z {led[4]:.3f}..{led[5]:.3f}; pads Y {pads[0][2]:.3f}..{pads[1][3]:.3f}")
    print(f"guide leg 1 X {leg1[0]:.3f}..{leg1[1]:.3f} Y {leg1[2]:.3f}..{leg1[3]:.3f}; leg 2 X {leg2[0]:.3f}..{leg2[1]:.3f} Y {leg2[2]:.3f}..{leg2[3]:.3f}; Z {bar_bot:.3f}..{bar_top:.3f} (height {h:.3f})")
    print(f"riser dia {2 * riser_r} at X {WX} Y {WY} Z {riser[4]:.3f}..{riser[5]:.3f}; board hole dia {2 * hole_r}; foam notch {foam_win[1] - foam_win[0]:.2f} square; LP1 {lp1[1] - lp1[0]:.2f} square Z {lp1[4]:.3f}..{lp1[5]:.3f}; print window dia {2 * win_r}")

    others = {r["part"]: r for r in rows if r["part"] not in ("recording_led", "light_pipe")}
    containers = {"main_board", "foam", "screen", "clear_adhesive", "cover_glass", "outer_body", "band_liner"}

    def nearest(solid, plan=False, board_only=False):
        worst = (1e9, None, 0.0)
        for n, r in others.items():
            if n in containers or (board_only and r["layer"] != "board"):
                continue
            if r["angle_deg"]:
                c = (float(r["x"]), float(r["y"]), float(r["z"]))
                rad = 0.5 * math.sqrt(float(r["size_x"]) ** 2 + float(r["size_y"]) ** 2 + float(r["size_z"]) ** 2)
                d = math.sqrt(sum(max(solid[2 * i] - c[i], 0, c[i] - solid[2 * i + 1]) ** 2 for i in range(3))) - rad
                g, ov = max(d, 0.0), (1.0 if d < 0 else 0.0)
            elif plan:
                g, ov = gap2d(solid, row_box(r)), gap(solid, row_box(r))[1]
            else:
                g, ov = gap(solid, row_box(r))
            if g < worst[0]:
                worst = (g, n, ov)
        return worst

    # 1. LED1 and pads: plan keep-out 0.2 to every other board part
    for lab, sb in (("LED1 body", led), ("LED1 pad 1", pads[0]), ("LED1 pad 2", pads[1])):
        g, n, ov = nearest(sb, plan=True, board_only=True)
        check(f"[{tag}] {lab} plan gap to every board part >= {KEEP}", g >= KEEP - 1e-9 and ov <= 0.001, f"nearest {n} at {g:.3f} mm, common volume {ov:.4f} mm3")
    # 2. guide, LP1: 0.10 to every part
    for lab, sb in (("guide leg 1", leg1), ("guide leg 2", leg2), ("guide riser", riser), ("LP1", lp1)):
        g, n, ov = nearest(sb)
        check(f"[{tag}] {lab} gap to every part >= {GAP_MIN}", g >= GAP_MIN - 1e-9 and ov <= 0.001, f"nearest {n} at {g:.3f} mm, common volume {ov:.4f} mm3")
    # 3. LED seated, guide under it, floor, height
    check(f"[{tag}] LED1 seated on the under face", abs(led[5] - (Z_BD0 - PAD_T)) < 1e-9, f"LED top Z {led[5]:.3f} = board under face {Z_BD0:.3f} - pad {PAD_T}")
    g, ov = gap(led, leg1)
    check(f"[{tag}] guide below the LED's emitting face", g >= GAP_MIN - 1e-9 and ov == 0, f"gap {g:.3f} mm")
    check(f"[{tag}] mirror A under the LED's centre", leg1[2] <= LY <= leg1[3] and leg1[0] <= LX <= leg1[1], f"LED centre ({LX}, {LY}) inside leg 1 in plan")
    low = min(led[4], leg1[4], leg2[4])
    check(f"[{tag}] no new part below the floor top", low >= Z_FLOOR - 1e-9, f"lowest Z {low:.3f}, floor top {Z_FLOOR:.3f} (gap {low - Z_FLOOR:.3f})")
    check(f"[{tag}] height under the board <= 1.00", Z_BD0 - low <= 1.00 + 1e-9, f"{Z_BD0 - low:.3f} mm")
    # 4. pocket
    px, py = sx_half + 0.05, sy_half + 0.05
    for lab, sb in (("LED1", led), ("guide leg 1", leg1), ("guide leg 2", leg2), ("riser", riser), ("LP1", lp1)):
        ok = sb[0] >= -px and sb[1] <= px and sb[2] >= -py and sb[3] <= py
        check(f"[{tag}] {lab} inside the panel pocket", ok, f"X {sb[0]:.3f}..{sb[1]:.3f} Y {sb[2]:.3f}..{sb[3]:.3f} in +-{px:.3f} x +-{py:.3f}")
    # 5. board hole
    hole_edge = min(WX - hole_r + bx, bx - (WX + hole_r), WY - hole_r + by_, by_ - (WY + hole_r))
    check(f"[{tag}] board hole inside the board outline", hole_edge >= GAP_MIN, f"least board material to the edge {hole_edge:.3f} mm")
    worst = (1e9, None)
    for n, r in others.items():
        if n in containers or r["angle_deg"] or r["layer"] != "board":
            continue
        g = circle_box_gap(WX, WY, hole_r, row_box(r))
        if g < worst[0]:
            worst = (g, n)
    check(f"[{tag}] board hole to every board part body >= {GAP_MIN}", worst[0] >= GAP_MIN - 1e-9, f"nearest {worst[1]} at {worst[0]:.3f} mm")
    gp = min(circle_box_gap(WX, WY, hole_r, p) for p in pads)
    check(f"[{tag}] board hole to LED1 pads >= {PAD_HOLE_MIN} [ESTIMATE rule]", gp >= PAD_HOLE_MIN - 1e-9, f"{gp:.3f} mm")
    check(f"[{tag}] riser in the board hole with radial gap >= {GAP_MIN}", hole_r - riser_r >= GAP_MIN - 1e-9, f"{hole_r - riser_r:.3f} mm (filled with clear UV glue)")
    ant = row_box(by["antenna"])
    ac = ((ant[0] + ant[1]) / 2, (ant[2] + ant[3]) / 2)
    keep = [box(ac[0] - 2.1, ac[0] + 2.1, ac[1] - 2.35, ac[1] + 2.35, 0, 9), box(ac[0] - 2.35, ac[0] + 2.35, ac[1] - 2.1, ac[1] + 2.1, 0, 9)]
    dk = min(min(gap2d(sb, k) for k in keep) for sb in (led, pads[0], pads[1], leg1, leg2, riser))
    check(f"[{tag}] light parts outside the antenna keep-out 4.2 x 4.7 (main-board.md line 56), either orientation", dk > 0, f"least gap {dk:.3f} mm")
    mir = box(WX - hole_r, WX + hole_r, -WY - hole_r, -WY + hole_r, 0, 9)
    info(f"[{tag}] same column mirrored to the thumb side (Y +{-WY}) inside that antenna keep-out", f"{'yes' if min(gap2d(mir, k) for k in keep) == 0 else 'no'}")
    # 6. foam, riser top
    fr = min(foam_win[0] + bx, foam_win[2] + by_)
    check(f"[{tag}] foam notch leaves foam on the board-edge side", fr >= GAP_MIN, f"{fr:.3f} mm")
    check(f"[{tag}] riser top below the screen's lower glass", Z_SC0 - riser[5] >= GAP_MIN - 1e-9, f"{Z_SC0 - riser[5]:.3f} mm")
    # 7. LP1 on the ledge
    check(f"[{tag}] LP1 stands on the ledge top and meets the adhesive", abs(lp1[4] - Z_LEDGE) < 1e-9 and abs(lp1[5] - Z_AD0) < 1e-9, f"Z {lp1[4]:.3f}..{lp1[5]:.3f}")
    check(f"[{tag}] LP1 before the upper glass (maker drawing)", X_UPPER_DRAW - lp1[1] >= GAP_MIN - 1e-9, f"{X_UPPER_DRAW - lp1[1]:.3f} mm to X {X_UPPER_DRAW:.3f}")
    check(f"[{tag}] LP1 before the upper glass (inside model)", X_UPPER_MODEL - lp1[1] >= GAP_MIN - 1e-9, f"{X_UPPER_MODEL - lp1[1]:.3f} mm to X {X_UPPER_MODEL:.3f}")
    g, ov = gap(lp1, fpc_bond)
    check(f"[{tag}] LP1 clear of the FPC bond (maker drawing)", g >= GAP_MIN - 1e-9 and ov == 0, f"gap {g:.3f} mm")
    g, ov = gap(lp1, drv_ic)
    check(f"[{tag}] LP1 clear of the driver IC (inside model, ASSUMED IC)", g >= GAP_MIN - 1e-9 and ov == 0, f"gap {g:.3f} mm")
    g = gap2d(riser, fingers)
    check(f"[{tag}] light column clear of the bond fingers (maker drawing)", g >= GAP_MIN - 1e-9, f"gap {g:.3f} mm")
    open_item(f"[{tag}] ledge glass clear (no metal, no fan-out, no back film) at the light column", f"X {lp1[0]:.3f}..{lp1[1]:.3f} Y {lp1[2]:.3f}..{lp1[3]:.3f}: the drawing shows none; only the screen maker can confirm")
    open_item(f"[{tag}] drawing tolerance", "TOH095XVT-01 p5 note 9 'UNMARKED TOLERANCE: +-0.2': the bond end and LP1 are 0.15 apart at nominal")
    # 8. print window
    lit_cx = -29.3 / 2 + 5.33 + 21.6 / 2                # thin.py line 325
    lit = box(lit_cx - 10.8, lit_cx + 10.8, -5.4, 5.4, 0, 9)
    dl = circle_box_gap(WX, WY, win_r, lit)
    check(f"[{tag}] print window outside the lit area", dl >= GAP_MIN, f"{dl:.3f} mm to the lit area edge X {lit[0]:.3f}")
    gpl = (LOGS / "glass_probe2.log").read_text()
    gb, gt, gth = num(r"window recommended: X -12.425 Y -2.95: glass bottom Z ([\d.]+) top Z ([\d.]+) thickness ([\d.]+)", gpl, 3)
    check(f"[{tag}] print window on the flat glass bottom (glass_probe2.log)", abs(gb - Z_AD0 - 0.10) < 0.001 and a.shift_riser_x == 0.0, f"glass bottom Z {gb:.3f}, top Z {gt:.3f}, thickness {gth:.3f}")
    check(f"[{tag}] print window not on the glass end roll (starts X -13.45, thin-notes.md line 86)", WX - win_r > -13.45, f"window edge X {WX - win_r:.3f}")
    check(f"[{tag}] print window no larger than LP1", 2 * win_r <= (lp1[1] - lp1[0]) + 1e-9, f"window dia {2 * win_r:.2f}, LP1 side {lp1[1] - lp1[0]:.2f}")
    v4 = (-13.25, -4.7)
    over = fpc_bond[0] <= v4[0] <= fpc_bond[1] and fpc_bond[2] <= v4[1] <= fpc_bond[3]
    info(f"[{tag}] v4 window X -13.25 Y -4.7 over the FPC bond of the maker drawing", f"{'yes' if over else 'no'} (bond X {fpc_bond[0]:.3f}..{fpc_bond[1]:.3f}, Y {fpc_bond[2]:.3f}..{fpc_bond[3]:.3f})")
    # first layout (light-path.md section 4, note): LED at X -10.95 Y -3.2 long side along X; does it fit this scenario?
    old_led = box(-11.85, -10.05, -3.45, -2.95, Z_BD0 - PAD_T - 0.2, Z_BD0)
    g, n, ov = nearest(old_led, plan=True, board_only=True)
    info(f"[{tag}] first layout's LED1 with pads (X -11.85..-10.05, Y -3.45..-2.95) plan gap", f"{g:.3f} mm to {n}, common volume {ov:.4f} mm3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shift-led-y", type=float, default=0.0)
    ap.add_argument("--shift-riser-x", type=float, default=0.0)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(THIN / "placement.csv")))
    layers = json.load(open(THIN / "layers.json"))
    layer_of = {p: L["name"] for L in layers["layers"] for p in L["parts"]}
    print(f"read {THIN / 'placement.csv'}: {len(rows)} rows; {THIN / 'layers.json'}: {len(layer_of)} parts in {len(layers['layers'])} layers")
    scenario("v4", rows, layer_of, a)
    rows_b = [dict(r) for r in rows]
    for r in rows_b:
        if r["part"] in ("mic_1", "mic_2"):
            sgn = -1 if r["part"] == "mic_1" else 1
            r.update(x=f"{sgn * 10.8:.3f}", y="-4.800", z="0.930", size_x="4.000", size_y="3.000", size_z="1.000")   # mic-path.md line 58, architecture.md 17.19
    scenario("17.19", rows_b, layer_of, a)

    print("---- both scenarios")
    vf = num(r"at y 1.5: x ([\d.]+)", (LOGS / "kpg_vf_curve.log").read_text())[0]
    V, I, RQ = 3.0, 0.0015, 0.7                          # architecture.md line 284 (W5: 3.0 V, 1.5 mA); 0.7 ohm max of DMN2450UFB4 (architecture.md line 50)
    r_ideal = (V - vf - I * RQ) / I
    e24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
    r_pick = min((v * 100 for v in e24), key=lambda v: abs(v - r_ideal))
    i_pick = (V - vf) / (r_pick + RQ) * 1000
    i_old = (V - vf) / (680 + RQ) * 1000
    check("R41 gives 1.5 +- 0.1 mA at the curve's Vf", abs(i_pick - 1.5) <= 0.1, f"Vf {vf:.3f} V at 1.5 mA (KPG p3 curve); ideal {r_ideal:.0f} ohm; E24 {r_pick:.0f} ohm gives {i_pick:.3f} mA; the present 680 ohm gives {i_old:.3f} mA")
    for dv in (-0.1, 0.1):
        info(f"R41 {r_pick:.0f} ohm with Vf {dv:+.1f} V (datasheet p2 note 2, +-0.1 V)", f"{(V - vf - dv) / (r_pick + RQ) * 1000:.3f} mA")
    check("layers.json: recording_led in layer board, light_pipe in layer screen", layer_of.get("recording_led") == "board" and layer_of.get("light_pipe") == "screen",
          f"recording_led {layer_of.get('recording_led')}, light_pipe {layer_of.get('light_pipe')}")
    info("layers.json: light_guide", f"listed: {'light_guide' in layer_of} (to add to layer board: change list)")
    by = {r["part"]: r for r in rows}
    for n in ("recording_led", "light_pipe"):
        r = by[n]
        info(f"placement.csv row {n} today", f"X {r['x']} Y {r['y']} Z {r['z']} size {r['size_x']} x {r['size_y']} x {r['size_z']} (moves: change list)")
    bad = [n for n, ok in results if not ok]
    print(f"checks: {len(results)}, failed: {len(bad)}")
    print("RESULT PASS" if not bad else "RESULT FAIL " + "; ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
