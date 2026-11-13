# Broken copies of the guide for check_assembly.py (review 4 fault I3) from a snapshot of the live guide (copies/ca/live-snapshot.md); each one
# changes one thing. The tests pass the snapshot of joints.csv and of product-wiring.csv (copies/*-snapshot-2.csv) by --joints and --wiring.
import csv, json, os, re
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work")
OUT = W + "/copies/ca"
txt = open(OUT + "/live-snapshot.md", encoding="utf-8").read()
J = W + "/copies/joints-snapshot-2.csv"; WR = W + "/copies/product-wiring-snapshot-2.csv"
C = []
def add(name, text, want_exit, want_tag, want_id=None, joints=J, wiring=WR):
    p = OUT + "/" + name + ".md"; open(p, "w", encoding="utf-8").write(text)
    C.append({"name": name, "md": p, "joints": joints, "wiring": wiring, "want_exit": want_exit, "want_tag": want_tag, "want_id": want_id})
def rep(old, new, t=txt, n=1):
    assert t.count(old) >= 1, old
    return t.replace(old, new, n)
add("honest_snapshot", txt, None, None)
# (a) G1 reintroduced: ribbon lands get no paste, step 14 solders on the bare lands
g1 = rep("get paste in PASS 2", "get no paste")
g1 = rep("on the solder layer that step 2 put on the 15 lands", "on the bare lands", g1)
add("G1_reintroduced_both_steps", g1, 1, "P1 FAIL")
add("G1_step2_only_no_paste", rep("get paste in PASS 2", "get no paste"), 1, "P1 FAIL")
add("G1_step14_only_bare_lands", rep("on the solder layer that step 2 put on the 15 lands", "on the bare lands"), 1, "P1 FAIL")
add("ribbon_land_count_wrong_step2", rep("J_BAND_A (8 lands) and J_BAND_B (7 lands) on the parts face get paste", "J_BAND_A (7 lands) and J_BAND_B (8 lands) on the parts face get paste"), 1, "P1 FAIL")
add("ribbon_land_total_wrong_step14", rep("step 2 put on the 15 lands", "step 2 put on the 14 lands"), 1, "P1 FAIL")
add("ribbon_paste_pass_wrong", rep("lands (8 lands) and", "lands (8 lands) and") if False else rep("get paste in PASS 2", "get paste in PASS 1"), 1, "P1 FAIL")
# (b) the cell tabs on swapped lands
tabs = rep("Tab P+ goes on land 1 (VBAT), tab NTC on land 3 (NTC), tab P- on land 2 (GND).", "Tab P+ goes on land 2 (GND), tab NTC on land 3 (NTC), tab P- on land 1 (VBAT).")
add("cell_tabs_swapped", tabs, 1, "L1 FAIL")
add("cell_tabs_NTC_and_Pminus_swapped", rep("tab NTC on land 3 (NTC), tab P- on land 2 (GND)", "tab NTC on land 2 (GND), tab P- on land 3 (NTC)"), 1, "L1 FAIL")
add("cell_tab_order_wrong", rep("which is lands 1, 3, 2", "which is lands 1, 2, 3"), 1, "L1 FAIL")
add("motor_lead_land_swapped", rep("land 1 of the motor lands, net VMOT, joined to land 7", "land 1 of the motor lands, net VMOT, joined to land 6"), 1, "L1 FAIL")
add("motor_check_lands_swapped", rep("+ on land 7 (VMOT) and - on land 6 (GND)", "+ on land 6 (VMOT) and - on land 7 (GND)"), 1, "L1 FAIL")
add("motor_red_lead_on_minus", rep("the red lead to the + land", "the blue lead to the + land"), 1, "L1 FAIL")
add("disc_lands_swapped", rep("VBUS to land 4, D- to land 5, D+ to land 6, GND to land 7", "VBUS to land 5, D- to land 4, D+ to land 6, GND to land 7"), 1, "L1 FAIL")
# the guide against the tables: the table is changed, the guide is not
rows = list(csv.DictReader(open(J, newline=""))); hdr = list(rows[0].keys())
def wj(name, rs):
    p = OUT + "/" + name + ".csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(rs)
    return p
rj = [dict(r, orientation=r["orientation"].replace("tab P+ on land 1 (VBAT)", "tab P+ on land 2 (GND)")) if r["joint_id"] == "J-W025-B" else r for r in rows]
add("joints_table_tab_land_differs_from_wiring", txt, 1, "L1 FAIL", joints=wj("joints-tab-land-changed", rj))
rj2 = [dict(r, solder_source=r["solder_source"].replace("paste printed through", "wire fed through")) if r["wiring_line"] == "W001" else r for r in rows]
add("joints_table_says_no_paste_for_a_ribbon_land", txt, 1, "P1 FAIL", joints=wj("joints-no-paste-W001", rj2))
wrows = list(csv.DictReader(open(WR, newline=""))); whdr = list(wrows[0].keys())
def ww(name, rs):
    p = OUT + "/" + name + ".csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=whdr, lineterminator="\n"); w.writeheader(); w.writerows(rs)
    return p
rw = [dict(r, end_B_pin="2 (land of footprint PRT1_Tabs)") if r["id"] == "W033" else r for r in wrows]
add("wiring_list_tab_land_differs_from_guide", txt, 1, "L1 FAIL", wiring=ww("wiring-tab-land-changed", rw))
# (c) citations that hold other text
add("citation_prose_wrong_line", rep("joined to land 6 (MOT-) of J_BAND_A (`design/ecad/band/band-interface.md:123`)", "joined to land 6 (MOT-) of J_BAND_A (`design/ecad/band/band-interface.md:3`)"), 1, "TOKEN")
add("citation_bom_other_row", rep("RT1 inside it as one part, `design/bom.csv:50`", "RT1 inside it as one part, `design/bom.csv:48`"), 1, "TOKEN")
add("citation_placement_final_other_row", rep("J1: `design/ecad/ring/pcb/placement-final.csv:80`", "J1: `design/ecad/ring/pcb/placement-final.csv:78`"), 1, "TOKEN")
add("citation_netlist_other_row", rep("`design/ecad/ring/netlist.csv:387` for J1", "`design/ecad/ring/netlist.csv:381` for J1") if "netlist.csv:387` for J1" in txt else rep("netlist.csv:253", "netlist.csv:250"), 1, "TOKEN")
add("citation_past_end", rep("band-interface.md:123`)", "band-interface.md:9999`)"), 1, "E1 FAIL")
# the reviewer's other fakes, from the snapshot
add("step_without_check_field", rep("- **Check:** the three joints pass the accept rules of step 2.", "- the three joints pass the accept rules of step 2."), 1, "C1 FAIL")
add("no_result_line", txt.rsplit("\nRESULT:", 1)[0] + "\n", 1, "G1 FAIL")
i = txt.index("### Step 1."); j = txt.index("## 3. ")
add("steps_twice", txt[:j] + txt[i:j] + txt[j:], 1, "B1 FAIL")
add("empty_file", "", 1, None)
json.dump(C, open(OUT + "/manifest.json", "w"), indent=1); print(len(C), "cases")
