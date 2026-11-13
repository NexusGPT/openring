"""C5d: add the pin holder and its heat stakes to case-bom.csv and update the post line, with the figures read from out/case_params.json.
Run once from design/case: ../.venv/bin/python look/c5d_bom.py (it replaces rows MECH16 and MECH17 if present, so a re-run does not duplicate)."""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)
BOM = os.path.join(CASE, "case-bom.csv")
prm = json.load(open(os.path.join(CASE, "out", "case_params.json")))
h = prm["pin_holder"]
rows = list(csv.reader(open(BOM, newline="")))
head, body = rows[0], [r for r in rows[1:] if r and r[1] not in ("MECH16", "MECH17")]
col = {k: i for i, k in enumerate(head)}


def row(**kw):
    r = [""] * len(head)
    for k, v in kw.items():
        r[col[k]] = v
    return r


for r in body:
    if r[col["reference"]] == "MECH5":
        r[col["function"]] = ("post with pin lug (C4; C5d: two staking pegs on the lug top): the centre post the ring lies around; the lug carries "
                              "PCB2 and the pin holder (MECH16)")
        r[col["key_figures"]] = ("2 screws M1.2 into the floor; 2 pegs dia 1.0 on the lug top at x %.2f, y +-%.2f mm (case frame), staked flush "
                                 "into the pin holder's counterbores (MECH17)" % (h["stake_x"], h["stake_y"]))
last = max(int(r[0]) for r in body if r[0].isdigit())
body.append(row(item=str(last + 1), reference="MECH16", quantity="1",
                function=("pin holder (own part `pin_holder`, C5d): carries the four pin barrels in front of the PCB2 islands; its front follows the "
                          "band's inner face %.2f mm in front of it along X (the nearest size at each y; smallest true distance 0.270 mm, US 7, "
                          "check test 14); a lip on the lug top; PCB2 is held between it and the lug" % h["front_gap"]),
                maker="Celanese", maker_part_number="Vectra E130i, black",
                package="injection moulded LCP, 30 percent glass fibre, black (the grade is Celanese's; any moulder)",
                size_mm=("X %.2f to %.2f, Y -%.2f to %.2f, Z %.2f to %.2f (case frame)" % (h["front_x_at_y0"], h["lip_x1"], h["half_width"], h["half_width"],
                                                                                     h["z0"], h["lip_top"])),
                key_figures=("4 bores dia %.2f for the 1.50 mm barrels with a 0.2 x 45 degree lead-in; front wall %.2f mm thick at the middle (over the "
                             "touch electrode E1); lip 0.80 thick; 2 holes dia 1.10 with counterbores dia 1.80 x 0.40 for the stakes; open at the back "
                             "and the bottom over the PCB2 islands (the wires leave downward); volume %.1f mm3"
                             % (h["bore"], h["wall_in_front_of_E1"], h["volume"])),
                evidence="CALC", source_file_or_url="design/case/out/parts/pin_holder.step; design/case/out/case_pin_holder.stl"))
body.append(row(item=str(last + 2), reference="MECH17", quantity="2",
                function="heat stakes that fix the pin holder (MECH16) to the post (MECH5)",
                package="feature of the post: pegs moulded on the lug top, formed by a heated tip",
                size_mm="peg dia 1.0 through a dia 1.10 hole in the 0.80 lip; formed head dia 1.70 x 0.35 inside a dia 1.80 x 0.40 counterbore (flush, 0.03 below the lip top)",
                key_figures=("at x %.2f, y +-%.2f mm (case frame); assembly: pins soldered to PCB2, PCB2 pressed into the holder from the back, "
                             "the pair lowered onto the lug (the islands' backs slide on the lug's front faces), stakes formed; the pin force "
                             "(4 x 0.39 N) pushes PCB2 onto the lug, not on the stakes" % (h["stake_x"], h["stake_y"])),
                evidence="CALC", source_file_or_url="design/case/case.py (STAKE); design/case/out/parts/post.step"))
with open(BOM, "w", newline="") as f:
    csv.writer(f).writerows([head] + body)
print("rows", len(body), "; MECH16 and MECH17 written")
