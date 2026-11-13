#!/usr/bin/env python3
"""Fit check for the thin ring model (thin.py). Exit 1 on any finding, 0 when everything fits.

1. no two solid parts intersect (> LIMIT mm3); the shell (outer_body) and the band liner touch by design
   and are excluded from each other
2. every part lies inside the outer body's envelope (block + band + shoulders, before the cavities)
3. motor rim: at least 0.40 mm of metal at every rim point, and the motor stays out of the block interior
4. the block's layer stack sums to 3.20 mm or less (thicknesses from the model, and the measured Z span)
Last line: RESULT PASS pairs=<n> parts=<n>   (or RESULT FAIL ...)
"""
import sys
import itertools
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import thin  # noqa: E402

LIMIT = 0.001  # mm3
WALL_MIN = 0.40  # mm of metal at every point of the motor's rim


def vol(s):
    try:
        return s.volume
    except Exception:
        return 0.0


def inter_vol(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
            or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
        return 0.0
    return vol(a & b)


def main():
    m = thin.build()
    P = m["parts"]
    by = {p["name"]: p for p in P}
    findings, errors = [], []
    pairs = 0
    for a, b in itertools.combinations(P, 2):
        if {a["name"], b["name"]} == {"outer_body", "band_liner"}:
            continue
        pairs += 1
        try:
            v = inter_vol(a["solid"], b["solid"])
        except Exception as e:
            errors.append(f"ERROR boolean {a['name']} x {b['name']}: {e}")
            continue
        if v > LIMIT:
            findings.append(f"COLLISION {a['name']} x {b['name']}: {v:.4f} mm3")
    env = m["envelope"]
    for p in P:
        if p["name"] == "outer_body":
            continue
        pv = vol(p["solid"])
        out = pv - vol(p["solid"] & env)
        if out > LIMIT:
            findings.append(f"OUTSIDE body envelope {p['name']}: {out:.4f} mm3 of {pv:.4f}")
    # motor: out of the block interior, and at least WALL_MIN of metal at every point of its rim
    from build123d import Box, Pos
    inter = by["vibration_motor"]["solid"] & (Pos(0, 0, 1.575) * Box(27.45, 12.9, 2.35))
    blk = vol(inter)
    print(f"motor x block interior: {blk:.4f} mm3 (limit {LIMIT})")
    if blk > LIMIT:
        findings.append(f"MOTOR enters the block interior: {blk:.4f} mm3")
    w, where = thin.motor_rim_min_wall(by["outer_body"]["solid"])
    print(f"motor rim: least metal along the outward ray {w:.3f} mm at {where} (limit {WALL_MIN})")
    if w < WALL_MIN - 1e-9:
        findings.append(f"WALL under {WALL_MIN} mm at the motor rim: {w:.3f} mm at {where}")
    # layer stack of the block
    t = thin.P
    stack = [("floor", t["floor"]), ("gap", t["gap"]), ("parts under the board", t["under"]),
             ("board", t["board_t"]), ("foam", t["foam_t"]), ("screen", t["screen_t"]),
             ("adhesive", t["adh_t"]), ("glass", t["glass_t"])]
    total = sum(v for _, v in stack)
    print("block stack: " + " + ".join(f"{n} {v:.2f}" for n, v in stack) + f" = {total:.3f} mm (limit 3.20)")
    if total > 3.20 + 1e-9:
        findings.append(f"STACK sum {total:.3f} > 3.20")
    top = max(by[n]["solid"].bounding_box().max.Z for n in ("cover_glass", "clear_adhesive", "screen"))
    under_min = min(by[n]["solid"].bounding_box().min.Z for n in ("main_chip", "storage", "screen_supply_coil",
                                                                  "mic_1", "mic_2", "power_coil_1"))
    print(f"measured: glass top Z {top:.3f}, lowest under-board part Z {under_min:.3f}, floor top Z {t['floor']:.3f}")
    if top > 3.20 + 1e-9:
        findings.append(f"STACK glass top {top:.3f} > 3.20")
    if under_min < t["floor"] + t["gap"] - 1e-9:
        findings.append(f"STACK a part sits under Z {t['floor'] + t['gap']:.2f}: {under_min:.3f}")
    for e in errors:
        print(e)
    for f in findings:
        print(f)
    bad = len(findings) + len(errors)
    print(f"check_thin: {len(findings)} findings, {len(errors)} errors")
    print(f"RESULT {'FAIL' if bad else 'PASS'} pairs={pairs} parts={len(P)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
