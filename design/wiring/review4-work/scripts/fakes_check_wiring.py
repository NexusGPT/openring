# Fakes for design/wiring/check_wiring.py --require-complete, each through its --csv entry point. Copies only in W.
import csv, os, subprocess
W = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work")
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
PY = ROOT + "/design/.venv/bin/python"
CHK = ROOT + "/design/wiring/check_wiring.py"
CSV = ROOT + "/design/wiring/product-wiring.csv"
FK = W + "/fakes-cw"; os.makedirs(FK, exist_ok=True)
rows = list(csv.DictReader(open(CSV))); hdr = list(rows[0].keys())
def write(name, rs):
    p = os.path.join(FK, name + ".csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); [w.writerow(r) for r in rs]
    return p
def mod(changes):
    out = []
    for r in rows:
        r = dict(r)
        if r["id"] in changes: r.update(changes[r["id"]])
        out.append(r)
    return out
cases = [("honest_copy", write("honest", rows), 0)]
cases.append(("empty", write("empty", []), 1))
flood = [dict(r) for r in rows]
for k in range(3):
    for r in rows: r2 = dict(r); r2["id"] = r["id"] + "x%d" % k; flood.append(r2)
cases.append(("flood_duplicates", write("flood", flood), 1))
cases.append(("one_line_covers_all", write("oneline", [dict(rows[0], end_B_ref="SW1 SW2 SW3 SW4 SW5 J_BAND_A J_BAND_B J1 CP1 CP2 CP3 CP4 P1 P2 P3 P4")]), 1))
cases.append(("no_marking_lead", write("nomark", mod({"W023": {"carrier_marking": ""}})), 1))
cases.append(("no_cut_lead", write("nocut", mod({"W023": {"cut_mm_us9": ""}})), 1))
cases.append(("wrong_net_both", write("wrongnet", mod({"W001": {"carrier_net": "JOY_DOWN", "signal_A": "JOY_DOWN", "signal_B": "JOY_DOWN"}})), 1))
cases.append(("swap_B_ends", write("swapB", mod({"W001": {"end_B_ref": "SW3"}, "W002": {"end_B_ref": "SW1"}})), 1))
cases.append(("wrong_tail_land", write("wrongtail", mod({"W001": {"join_A": "hot bar (main board land to FLEX1 tail land 2)"}})), 1))
cases.append(("wrong_face", write("wrongface", mod({"W040": {"end_B_face": "F.Cu"}, "W029": {"end_B_face": "F.Cu"}})), 1))
cases.append(("spring_pin_swap", write("springswap", mod({"W054": {"end_B_ref": "P4"}, "W057": {"end_B_ref": "P1"}})), 1))
cases.append(("case_wire_swap", write("wireswap", mod({"W063": {"end_B_ref": "W4"}, "W066": {"end_B_ref": "W1"}})), 1))
cases.append(("motor_colour_swap", write("colourswap", mod({"W023": {"carrier_marking": "blue insulation"}, "W024": {"carrier_marking": "red insulation"}})), 1))
cases.append(("cut_wrong_value", write("cutwrong", mod({"W023": {"cut_mm_us9": "9.99"}})), 1))
cases.append(("proof_text_fake", write("prooffake", mod({"W023": {"proof_carrier": "design/ecad/band/band-interface.md:123|this sentence is not in the file"}})), 1))
cases.append(("row_dropped", write("dropped", [r for r in rows if r["id"] != "W030"]), 1))
cases.append(("crash_missing", FK + "/nope.csv", 1))
differs = 0
for name, p, want in cases:
    r = subprocess.run([PY, CHK, "--require-complete", "--csv", p], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    last = out[-1] if out else ""
    open(os.path.join(FK, name + ".log"), "w").write(r.stdout + r.stderr)
    got = 0 if r.returncode == 0 else 1
    ok = got == want
    differs += 0 if ok else 1
    print("CASE %-22s want_exit=%d got_exit=%d %s | %s" % (name, want, r.returncode, "as expected" if ok else "DIFFERS", last[:220]))
print("RESULT fakes=%d differs=%d" % (len(cases), differs))
