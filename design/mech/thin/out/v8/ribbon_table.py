#!/usr/bin/env python3
"""Reads the final fit-check log of each size (out/v8) and prints, per size, the RESULT line and the least RIBBON-CLEARANCE per partner group, the slot-wall
clearance and the land-to-foot gap. Every number is copied from a log line (RIBBON-CLEARANCE, 'band circuit ... slot X', 'least land to foot', RESULT); none is typed by hand.
Usage: ribbon_table.py > ribbon_table.md"""
import re
from pathlib import Path

D = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin/out/v8"))
LOGS = {7: "v8b_us7.log", 8: "v8_us8.log", 9: "v8_us9_default.log", 10: "v8_us10.log", 11: "v8_us11.log", 12: "v8b_us12.log", 13: "v8_us13.log"}
SWITCHES = {"joy_sw_fingertip", "joy_sw_hand", "joy_sw_up", "joy_sw_down", "joy_sw_centre"}
pat = re.compile(r"RIBBON-CLEARANCE (\S+) (\S+) to (\S+): ([0-9.]+) mm")
slot_pat = re.compile(r"band circuit (\S+) slot X \S+ to \S+ \(centre \S+\); neck centre \S+: off-centre \S+, free to the ends ([0-9.]+) / ([0-9.]+)")
land_pat = re.compile(r"band circuit (\S+): 8 board lands .* least land to foot ([0-9.]+) mm")
rows = []
print("| size | result | motor | cell | protection circuit | body (channel and slot walls) | slot wall, neck ends | joystick parts (not seated head) | head on switch bases | main board | lands to foot | U3 | U11, C83, C84 |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for us, name in LOGS.items():
    p = D / name
    if not p.exists():
        print(f"| US {us} | no log {name} |" + " |" * 11)
        continue
    txt = p.read_text().splitlines()
    res = [l for l in txt if l.startswith("RESULT")]
    best = {}
    def put(key, d, tag):
        if key not in best or d < best[key][0]:
            best[key] = (d, tag)
    slot = []
    land = []
    for l in txt:
        m = pat.search(l)
        if m:
            rib, grp, pn, d = m.group(1), m.group(2), m.group(3), float(m.group(4))
            tag = f"{rib.replace('band_flex_', '')} {grp}"
            if pn == "vibration_motor": put("motor", d, tag)
            elif pn == "cell": put("cell", d, tag)
            elif pn == "cell_protection": put("prot", d, tag)
            elif pn == "outer_body": put("body", d, tag)
            elif pn == "main_board": put("main", d, tag)
            elif pn == "storage": put("u3", d, tag)
            elif pn in ("motor_regulator", "motor_cap_in", "motor_cap_out"): put("u11", d, tag + " / " + pn)
            elif pn in SWITCHES and grp == "head": put("seat", d, tag + " / " + pn)
            elif pn in ("joystick_dam",) and grp == "head": pass
            elif pn in ("joystick_frame", "joystick_cap", "joystick_dam") or pn in SWITCHES: put("joy", d, tag + " / " + pn)
        m = slot_pat.search(l)
        if m:
            slot.append((float(m.group(2)), float(m.group(3))))
        m = land_pat.search(l)
        if m:
            land.append(float(m.group(2)))
    def c(k):
        return "n/a" if k not in best else f"{best[k][0]:.4f} ({best[k][1]})"
    sl = "n/a" if not slot else f"{min(min(a) for a in slot):.3f}"
    ld = "n/a" if not land else f"{min(land):.4f}"
    print(f"| US {us} | {res[-1] if res else 'no RESULT line'} | {c('motor')} | {c('cell')} | {c('prot')} | {c('body')} | {sl} | {c('joy')} | {c('seat')} | {c('main')} | {ld} | {c('u3')} | {c('u11')} |")
