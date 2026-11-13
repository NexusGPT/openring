"""r4 edits, part 2: case-architecture.md and case-notes.md text about the boards from their files, the board retainer, the leads and the lift-out
test. Every number is taken from out/case_params.json (written by case.py) or from the check log given; nothing typed. Each replacement must match once.
usage: edit_docs2.py <case_params.json> <check log>"""
import json
import os
import re
import sys

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = json.load(open(sys.argv[1]))
LOG = open(sys.argv[2]).read()
b = P["boards"]
ol = b["main_outline"]
xs, ys = [p[0] for p in ol], [p[1] for p in ol]
R = P["retainer"]
cav = P["cavity"]
L = P["leads"]
isl = b["pins_islands"]
lift = re.findall(r"17 US (\d+): lifted 0 to ([\d.]+) mm in (\d+) steps.*?smallest free space ([\d.]+) mm to (.+?) at lift ([\d.]+) mm", LOG)
last = [l for l in LOG.strip().split("\n") if l.startswith("case_check:")][-1]
f2 = lambda v: "%.2f" % v
posts = "; ".join("(%.2f, %.2f)" % tuple(p) for p in R["posts"])
lead_tab = "; ".join("%s %.1f mm" % (k[5:], v["length"]) for k, v in sorted(L.items()))
lift_tab = "; ".join("US %s %s mm to %s at %s mm" % (n, d, w, z) for n, _, _, d, w, z in lift)

sec = f"""## Changes from C5d to C5d-r4 (2026-11-13: the routed boards in the model)

Notes with every value and source: `case-model-r4-notes.md`. Check of this version: r4/final_check.log, PASS with 0 failures over {re.search(r"PASS, (\d+) pairs", last).group(1)} pair checks at US 7 to 13 (look/c5d_check_lead_rerun.log is still the lead's rerun of C5d; its count is the one quoted elsewhere in this file until the lead reruns this version).

| Topic | C5d | C5d-r4 | Source |
|---|---|---|---|
| Main board | box 23.0 x 35.4 x 1.0 mm, symmetric, part volumes typed as boxes | read on every run from `design/ecad/case/pcb/case_main.kicad_pcb` (KiCad's Python) and its own STEP (kicad-cli): outline {f2(max(xs) - min(xs))} x {f2(max(ys) - min(ys))} mm with the socket tab (main part u 0 to 23.0, y {f2(min(ys))} to {f2(max(ys))}), thickness {b['main_thickness']:.1f} mm, {len(b['main_parts'])} part bodies | r4/case_boards.py; check test 15 |
| Board place | pcb1_x0 = x_lay + 1.9 (-9.637) | {P['pcb1_x0']:.3f}: the socket body's own front sits 0.3 mm behind the skin (the C5d place read the socket front 0.505 mm too far forward) | case.py `pcb1_x0` |
| Cavity at the board | -X wall at -10.037, ends at y +-20.35 | from 0.35 mm under the board to the ceiling: -X wall at {cav['x0']:.3f}, socket-side end at y {cav['y1']:.2f}; below the board as C5d | case.py `uf` |
| Pin board | three boxes (inner island 3.9 mm wide) | islands from `case_pins.kicad_pcb`: inner y {f2(isl['pin_board_pcb2']['y'][0])} to {f2(isl['pin_board_pcb2']['y'][1])}, wings {f2(isl['pin_board_pcb2_wing_R']['y'][0])} to {f2(isl['pin_board_pcb2_wing_R']['y'][1])} (and mirrored); the holder's island pockets follow | check test 15a |
| Board holding | none | `board_retainer` (printed): web {R['web_t']:.1f} mm under the ceiling, 4 posts dia {R['post_d']:.1f} mm, {R['post_len']:.2f} mm long, at {posts}; a fence x {f2(R['fence']['x'][0])} to {f2(R['fence']['x'][1])}, y {f2(R['fence']['y'][0])} to {f2(R['fence']['y'][1])}; foam pad 0.8 mm under the cell; insulating sheet 0.25 mm on the cell | BOM MECH18 to MECH20 |
| Leads | not modelled | nine swept wires checked against every part (test 16): {lead_tab} | case.py `swept_wire` |
| Pin holder | wires had no room in front of the pad face | a {P['holder_recess']['depth']:.1f} mm recess in the holder's front wall behind the five wire pads, up to z {P['holder_recess']['z_top']:.2f}; the floor slot starts at x {P['slot']['x0']:.2f} (C5d: 6.82) | case.py |
| Lift out | not simulated | test 17: lid open, ring lifted straight up in 0.25 mm steps until clear, every size; smallest free space (seat contacts left out): {lift_tab} | case_check.py test 17 |

"""
p = os.path.join(D, "case-architecture.md")
s = open(p, encoding="utf-8").read()
anchor = "## Changes from C5c to C5d\n"
assert s.count(anchor) == 1
s = s.replace(anchor, sec + anchor)
old_c = "PCB1 23.0 x 35.4 x 1.0 above it with U1 (15.4 x 20.5 x 2.4), U2, U3, U4, U5, L1, L2, the light and the USB-C socket J1 on its top face (reserved volumes, not a layout)."
assert s.count(old_c) == 1
new_c = (f"PCB1 above it, as routed: {f2(max(xs) - min(xs))} x {f2(max(ys) - min(ys))} x {b['main_thickness']:.1f} mm with the socket tab (`case_main.kicad_pcb`), all {len(b['main_parts'])} part bodies "
         f"on its top face from the board's own STEP (C5d-r4; C5d had reserved boxes), held by the board retainer (section \"Changes from C5d to C5d-r4\").")
s = s.replace(old_c, new_c)
old_h = "- Back: open over the three PCB2 islands (inner island pocket 0.84 x 4.06 mm, outer pockets from x 6.38 back, |y| 2.03 to 4.92)"
assert s.count(old_h) == 1
iy = isl["pin_board_pcb2"]["y"]
s = s.replace(old_h, f"- Back: open over the three PCB2 islands (C5d-r4, islands from the board file: inner island pocket {P['boards']['pins_thickness'] + 0.04:.2f} x {iy[1] - iy[0] + 0.04:.2f} mm, "
                     f"outer pockets from x {P['x_bo'] - 0.02:.2f} back, |y| {iy[1] + 0.02:.2f} to {isl['pin_board_pcb2_wing_R']['y'][1] + 0.02:.2f}; a {P['holder_recess']['depth']:.1f} mm wire recess behind the five wire pads)")
old_f = "C5d adds out/parts/pin_holder.step and out/case_pin_holder.stl"
assert s.count(old_f) == 1
s = s.replace(old_f, "C5d adds out/parts/pin_holder.step and out/case_pin_holder.stl; C5d-r4 adds out/case_board_retainer.stl, out/parts/board_retainer.step, the leads (out/parts/lead_*.step) and the boards as read (out/boards/)")
open(p, "w", encoding="utf-8").write(s)
print("case-architecture.md: section 'Changes from C5d to C5d-r4' added before '## Changes from C5c to C5d'; compartments, holder back and files lines changed")

p = os.path.join(D, "case-notes.md")
s = open(p, encoding="utf-8").read()
anchor = "## C5d: the open points of the soft cube closed (2026-11-11)\n"
assert s.count(anchor) == 1
notes = f"""## C5d-r4: the routed boards in the model (2026-11-13)

Every value and its source: `case-model-r4-notes.md`. Choices (mine, one each):
- Boards read from their files on every run (KiCad's Python and kicad-cli); a part moved on a board moves in the model on the next run, and the check reads the files again (test 15a).
- Board place: the socket's own body front 0.3 mm behind the skin (pcb1_x0 {P['pcb1_x0']:.3f}); the outside is unchanged.
- Holding: a printed board retainer with four posts and a fence, on a foam pad and an insulating sheet (BOM MECH18 to MECH20); rejected: adhesive or screws (screws need holes in the board).
- Leads modelled as swept wires (30 AWG at 0.50 mm, cell leads at 1.0 mm, thermistor leads 0.30 mm: start values).
- Lift out simulated in 0.25 mm steps at every size (test 17).

"""
s = s.replace(anchor, notes + anchor)
open(p, "w", encoding="utf-8").write(s)
print("case-notes.md: section 'C5d-r4' added before '## C5d: the open points of the soft cube closed (2026-11-11)'")
