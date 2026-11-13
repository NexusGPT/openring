# Makes the broken copies of the wiring list for check_wiring.py, all from the REBUILT FIXED list (copies/rebuilt-fixed.csv, written by
# build_wiring.py with the CR fix into W), so a fake fails only for its own fault. Same changes as review4-work/scripts/fakes_check_wiring.py
# for the reviewer's fakes (names kept), plus the new ones. Writes into W/copies/cw only.
import csv, os
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work")
SRC = W + "/copies/rebuilt-fixed.csv"
OUT = W + "/copies/cw"; os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(SRC, newline=""))); hdr = list(rows[0].keys())
def write(name, rs):
    p = OUT + "/" + name + ".csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr, lineterminator="\n"); w.writeheader(); [w.writerow(r) for r in rs]
    return p
def mod(ch):
    out = []
    for r in rows:
        r = dict(r)
        if r["id"] in ch: r.update(ch[r["id"]])
        out.append(r)
    return out
# (name, rows, want_exit, want_tag, want_id)   want_tag None = must pass
C = []
C.append(("honest_fixed_copy", rows, 0, None, None))
# the reviewer's 17
C.append(("empty", [], 1, None, None))
flood = [dict(r) for r in rows]
for k in range(3):
    for r in rows: r2 = dict(r); r2["id"] = r["id"] + "x%d" % k; flood.append(r2)
C.append(("flood_duplicates", flood, 1, "terminal-twice", None))
C.append(("one_line_covers_all", [dict(rows[0], end_B_ref="SW1 SW2 SW3 SW4 SW5 J_BAND_A J_BAND_B J1 CP1 CP2 CP3 CP4 P1 P2 P3 P4")] , 1, None, None))
C.append(("no_marking_lead", mod({"W023": {"carrier_marking": ""}}), 1, "state-kind", "W023"))
C.append(("no_cut_lead", mod({"W023": {"cut_mm_us9": ""}}), 1, "lead-length", "W023"))
C.append(("wrong_net_both", mod({"W001": {"carrier_net": "JOY_DOWN", "signal_A": "JOY_DOWN", "signal_B": "JOY_DOWN"}}), 1, "states-net", "W001"))
C.append(("swap_B_ends", mod({"W001": {"end_B_ref": "SW3"}, "W002": {"end_B_ref": "SW1"}}), 1, None, None))
C.append(("wrong_tail_land", mod({"W001": {"join_A": "hot bar (main board land to FLEX1 tail land 2)"}}), 1, "states-tail", "W001"))
C.append(("wrong_face_W040", mod({"W040": {"end_B_face": "F.Cu"}}), 1, "states-face", "W040"))
C.append(("wrong_face_W029", mod({"W029": {"end_B_face": "F.Cu"}}), 1, "states-face", "W029"))
C.append(("spring_pin_swap", mod({"W054": {"end_B_ref": "P4"}, "W057": {"end_B_ref": "P1"}}), 1, None, None))
C.append(("case_wire_swap", mod({"W063": {"end_B_ref": "W4"}, "W066": {"end_B_ref": "W1"}}), 1, None, None))
C.append(("motor_colour_swap", mod({"W023": {"carrier_marking": "blue insulation"}, "W024": {"carrier_marking": "red insulation"}}), 1, "states-colour", "W023"))
C.append(("cut_wrong_value_9.99", mod({"W023": {"cut_mm_us9": "9.99"}}), 1, "states-cut", "W023"))
C.append(("proof_text_fake", mod({"W023": {"proof_carrier": "design/ecad/band/band-interface.md:123|this sentence is not in the file"}}), 1, "proof-text", "W023"))
C.append(("row_dropped", [r for r in rows if r["id"] != "W030"], 1, None, None))
# new rules
C.append(("net_in_netlist_only", mod({"W040": {"signal_B": "ELVDD", "carrier_net": "ELVSS/ELVDD", "pairing_rule": "contact k of the screen cable on position k of J1"}}), 1, "states-net", "W040"))
C.append(("end_A_main_face_wrong", mod({"W001": {"end_A_face": "B.Cu; tail land on F.Cu"}}), 1, "states-face", "W001"))
C.append(("end_A_tail_face_wrong", mod({"W001": {"end_A_face": "F.Cu; tail land on B.Cu"}}), 1, "states-face", "W001"))
C.append(("tail_land_wrong_flex", mod({"W001": {"join_A": "hot bar (main board land to FLEX2 tail land 1)"}}), 1, "states-tail", "W001"))
C.append(("cut_one_size", mod({"W023": {"cut_mm_us13": "1.40"}}), 1, "states-cut", "W023"))
C.append(("cut_case_wire", mod({"W063": {"cut_mm_us7": "15.7"}}), 1, "states-cut", "W063"))
C.append(("cut_thermistor", mod({"W061": {"cut_mm_us10": "12"}}), 1, "states-cut", "W061"))
C.append(("case_wire_colour", mod({"W064": {"carrier_marking": "green insulation"}, "W065": {"carrier_marking": "white insulation"}}), 1, "states-colour", "W064"))
C.append(("cell_lead_colour", mod({"W059": {"carrier_marking": "black (-)"}}), 1, "states-colour", "W059"))
C.append(("copper_length_changed", mod({"W001": {"copper_mm_us9": "11.000"}}), 1, "states-copper", "W001"))
C.append(("carrier_net_differs", mod({"W001": {"carrier_net": "JOY_UP2"}}), 1, "states-net", "W001"))
C.append(("cr_in_field", mod({"W001": {"state_reason": "both ends\rok"}}), 1, "field-newline", "W001"))
C.append(("newline_in_field", mod({"W001": {"state_reason": "both ends\nok"}}), 1, "field-newline", "W001"))
C.append(("rebuild_state_reason", mod({"W001": {"state_reason": "all fine, trust me"}}), 1, "rebuild", "W001"))
C.append(("rebuild_join_B", mod({"W001": {"join_B": "hand solder"}}), 1, "rebuild", "W001"))
C.append(("rebuild_cut_note", mod({"W040": {"cut_note": "size dependent"}}), 1, "rebuild", "W040"))
C.append(("rebuild_pad_pin_text", mod({"W001": {"end_B_pin": "4"}}), 1, "rebuild", "W001"))
import json
man = []
for name, rs, we, wt, wi in C:
    man.append({"name": name, "csv": write(name, rs), "want_exit": we, "want_tag": wt, "want_id": wi})
json.dump(man, open(OUT + "/manifest.json", "w"), indent=1)
print("wrote", len(man), "cases to", OUT)
