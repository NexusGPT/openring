# Broken copies of joints.csv for check_joints.py rules R6 and R7 (review 4 fault I2). Source: W/copies/joints-snapshot-1.csv, a copy of the
# real table as it stood when I started (joints.csv is owned by another helper and is never edited here). Writes into W/copies/cj only.
import csv, os, json
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work")
SRC = W + "/copies/joints-snapshot-1.csv"
OUT = W + "/copies/cj"; os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(SRC, newline=""))); hdr = list(rows[0].keys())
def write(name, rs):
    p = OUT + "/" + name + ".csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(rs)
    return p
W027 = "land B3, FACTORY ENTER and T-CHARGE pass at the end of the step (T-CHARGE exits 0, 0 violations); an open NTC land reads as cold and T-CHARGE fails with the charger off (hotbar-joint.md section 4)"
def mod(jid, **ch):
    # every fake starts from the real table with J-W027-A's check amended (so the only change is the fake's own); the first case runs the unamended real table
    return [dict(r, **ch) if r["joint_id"] == jid else (dict(r, check=W027) if r["joint_id"] == "J-W027-A" else r) for r in rows]
T = "J-W054-A"
C = []
C.append(("real_snapshot_as_it_stands", rows, 1, "R6 weak-check", "J-W027-A"))
C.append(("real_with_W027_check_amended", mod("J-W027-A", check=W027), 0, None, None))
C.append(("check_ok", mod(T, check="ok"), 1, "R6 weak-check", T))
C.append(("check_looks_fine", mod(T, check="looks fine, checked by the builder"), 1, "R6 weak-check", T))
C.append(("check_measure_without_pass", mod(T, check="ohmmeter at the foot, optical inspection at 20 times"), 1, "R6 weak-check", T))
C.append(("check_pass_without_method", mod(T, check="the result is good enough and less than 5 is fine"), 1, "R6 weak-check", T))
C.append(("check_accept_rule_of_missing_step", mod(T, check="optical inspection; each joint passes the accept rules of step 99"), 1, "R6 weak-check", T))
C.append(("check_file_line_past_end", mod(T, check="optical inspection; accept rule design/mfg/assembly/process.md:99999"), 1, "R6 weak-check", T))
C.append(("check_file_line_real_accepted", mod(T, check="optical inspection; accept rule design/mfg/assembly/process.md:105"), 0, None, None))
C.append(("check_file_line_holds_no_pass_value", mod(T, check="optical inspection; accept rule design/mfg/assembly/process.md:100"), 1, "R6 weak-check", T))
C.append(("check_file_line_other_text", mod(T, check="optical inspection; accept rule design/mfg/assembly/process.md:1"), 1, "R6 weak-check", T))
C.append(("check_accept_rule_step_real_accepted", mod(T, check="optical inspection at 10 times; each joint passes the accept rules of step 2"), 0, None, None))
C.append(("check_number_unit_accepted", mod(T, check="feeler: height 0.53 mm"), 0, None, None))
C.append(("heat_hot", mod(T, heat="hot"), 1, "R7 weak-heat", T))
C.append(("heat_warm_no_value", mod(T, heat="warm enough to melt the solder"), 1, "R7 weak-heat", T))
C.append(("heat_value_without_unit", mod(T, heat="iron 340"), 1, "R7 weak-heat", T))
C.append(("heat_none_without_reason", mod(T, heat="none"), 1, "R7 weak-heat", T))
C.append(("heat_profile_without_file", mod(T, heat="P3 profile"), 1, "R7 weak-heat", T))
C.append(("heat_profile_missing_section", mod(T, heat="P9 profile (process.md P9)"), 1, "R7 weak-heat", T))
C.append(("heat_value_no_tool_anywhere", mod(T, heat="340 C, 7 s", tool="gloves"), 1, "R7 weak-heat", T))
C.append(("heat_value_tool_in_tool_field_accepted", mod(T, heat="340 C, 7 s", tool="50 W soldering iron"), 0, None, None))
C.append(("heat_profile_with_file_accepted", mod(T, heat="P3 profile (process.md P3)"), 0, None, None))
C.append(("heat_none_with_reason_accepted", mod(T, heat="none: pressed contact, no heat"), 0, None, None))
# reviewer's two fakes, rebuilt from the snapshot with the same change as review4-work/scripts/fakes_check_joints.py (check "ok", heat "hot")
rev = []
for n, jid, ch in (("rev_check_ok", "J-W026-A", {"check": "ok"}), ("rev_heat_hot", "J-W061-B", {"heat": "hot"})):
    rev.append((n, mod(jid, **ch), 1, "R6 weak-check" if "check" in ch else "R7 weak-heat", jid))
C += rev
man = [{"name": n, "csv": write(n, rs), "want_exit": we, "want_tag": wt, "want_id": wi} for n, rs, we, wt, wi in C]
json.dump(man, open(OUT + "/manifest.json", "w"), indent=1); print(len(man), "cases")
