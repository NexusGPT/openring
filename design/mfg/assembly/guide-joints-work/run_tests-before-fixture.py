"""Proof that check_joints.py can fail, rule by rule, and passes a complete table.
Writes kept copies in tests/broken/ and tests/mini/, runs the real checker by its real path on each,
and prints one line per case with expected and seen results. Last line: TESTS PASS n or TESTS FAIL n.
Run: design/.venv/bin/python -B tests/run_tests.py"""
import csv, os, subprocess, sys

T = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(T)
ROOT = os.path.abspath(os.path.join(WORK, "..", "..", "..", ".."))
PY = os.path.join(ROOT, "design/.venv/bin/python")
CHECK = os.path.join(ROOT, "design/mfg/assembly/check_joints.py")
REAL = os.path.join(ROOT, "design/mfg/assembly/joints.csv")
BROKEN = os.path.join(T, "broken")
MINI = os.path.join(T, "mini")
os.makedirs(BROKEN, exist_ok=True)
os.makedirs(MINI, exist_ok=True)


def run(args, log):
    p = subprocess.run([PY, "-B", CHECK] + args, capture_output=True, text=True)
    with open(log, "w") as f:
        f.write(p.stdout)
        f.write(p.stderr)
        f.write("exit %d\n" % p.returncode)
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    return p.returncode, lines


def read(path):
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        return rd.fieldnames, list(rd)


def write(path, fields, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


results = []

# ---------- the complete miniature (fake but complete) ----------
FIELDS = ["joint_id", "wiring_line", "end", "what_meets_what", "step", "solder_source", "flux", "tool", "heat",
          "orientation", "alignment", "check", "check_possible_at_this_step", "source", "gap"]
WFIELDS = ["id", "join_A", "join_B"]
mini_wiring = os.path.join(MINI, "mini-wiring.csv")
write(mini_wiring, WFIELDS, [dict(id="X001", join_A="hand solder (fake)", join_B="copper (same board)"),
                             dict(id="X002", join_A="made by the maker (fake)", join_B="hand solder (fake)")])
mini_passes = os.path.join(MINI, "mini-passes.txt")
with open(mini_passes, "w") as f:
    f.write("fake board F.Cu\n")
base = dict(what_meets_what="fake land on fake lead", solder_source="fake wire solder", flux="fake flux",
            tool="fake iron", heat="fake 300 C 2 s", orientation="fake face up", alignment="fake mark",
            check="fake ohmmeter reads below 1 ohm", source="fake.md:1", gap="")
mini_rows = [dict(base, joint_id="M-X001-A", wiring_line="X001", end="A", step="7", check_possible_at_this_step="yes"),
             dict(base, joint_id="M-X002-B", wiring_line="X002", end="B", step="case 6",
                  check="fake continuity [needs case 8]", check_possible_at_this_step="no, case 8"),
             dict(base, joint_id="M-PASS", wiring_line="board pass", end="fake board F.Cu", step="2",
                  solder_source="paste layer design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr for ANT1:1 ANT1:2",
                  check_possible_at_this_step="yes")]
mini = os.path.join(MINI, "mini-joints.csv")
write(mini, FIELDS, mini_rows)
rc, out = run(["--joints", mini, "--wiring", mini_wiring, "--passes", mini_passes], os.path.join(MINI, "mini.log"))
ok = rc == 0 and out and out[-1] == "RESULT PASS joints 3"
results.append(("mini complete table", "exit 0, RESULT PASS joints 3", "exit %d, %s" % (rc, out[-1] if out else ""), ok))


# ---------- broken copies: from the miniature (alone) and from the real table (new lines only) ----------
def breaks(rows):
    """name -> (rule, function making the broken rows)"""
    return {
        "row_removed": ("R1", lambda rs: rs[1:]),
        "field_emptied": ("R2", lambda rs: [dict(rs[0], tool="")] + rs[1:]),
        "step_not_exist": ("R3", lambda rs: [dict(rs[0], step="29")] + rs[1:]),
        "paste_no_opening": ("R4", None),
        "paste_file_missing": ("R4", None),
        "check_before_step": ("R5", lambda rs: [dict(rs[0], check_possible_at_this_step="no, 5")] + rs[1:]),
    }


def paste_break(rows, idx, text):
    rs = list(rows)
    rs[idx] = dict(rs[idx], solder_source=text)
    return rs


NO_OPEN = "paste layer design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr for J_BAND_A:1"
NO_FILE = "paste layer design/ecad/ring/pcb/fab/gerber/ring-X_Paste.gbr for ANT1:1"

# miniature copies: must fail with lines of their rule only
for name, (rule, fn) in breaks(mini_rows).items():
    if name == "paste_no_opening":
        rs = paste_break(mini_rows, 2, NO_OPEN)
    elif name == "paste_file_missing":
        rs = paste_break(mini_rows, 2, NO_FILE)
    else:
        rs = fn(mini_rows)
    path = os.path.join(BROKEN, "mini-%s.csv" % name)
    write(path, FIELDS, rs)
    rc, out = run(["--joints", path, "--wiring", mini_wiring, "--passes", mini_passes], path[:-4] + ".log")
    probs = [l for l in out if not l.startswith("RESULT")]
    rules = sorted({l.split()[0] for l in probs})
    ok = rc == 1 and rules == [rule] and out[-1] == "RESULT FAIL %d" % len(probs)
    results.append(("mini " + name, "exit 1, only %s lines" % rule, "exit %d, rules %s, %d lines" % (rc, rules, len(probs)), ok))

# real-table copies: compared with the real table's own run, the new lines are all of the rule
fields, real_rows = read(REAL)
rc0, base_out = run([], os.path.join(BROKEN, "real-base.log"))
base_set = set(base_out)
idx = {r["joint_id"]: i for i, r in enumerate(real_rows)}
target = idx["J-W054-A"]  # a complete row
for name, (rule, fn) in breaks(real_rows).items():
    rs = list(real_rows)
    if name == "row_removed":
        rs = [r for r in real_rows if r["joint_id"] != "J-W001-A"]
    elif name == "field_emptied":
        rs[target] = dict(rs[target], tool="")
    elif name == "step_not_exist":
        rs[target] = dict(rs[target], step="29")
    elif name == "paste_no_opening":
        rs = paste_break(real_rows, idx["J-W036-A"], NO_OPEN)
    elif name == "paste_file_missing":
        rs = paste_break(real_rows, idx["J-W036-A"], NO_FILE)
    elif name == "check_before_step":
        rs[target] = dict(rs[target], check_possible_at_this_step="no, 27")
    path = os.path.join(BROKEN, "real-%s.csv" % name)
    write(path, fields, rs)
    rc, out = run(["--joints", path], path[:-4] + ".log")
    new = [l for l in out if l not in base_set and not l.startswith("RESULT")]
    rules = sorted({l.split()[0] for l in new})
    ok = rc == 1 and rules == [rule] and len(new) >= 1
    results.append(("real " + name, "exit 1, new lines only %s" % rule, "exit %d, new rules %s, %d new lines" % (rc, rules, len(new)), ok))

# ---------- the two opening forms R4 reads since 2026-11-13 (added by the guide helper, granted by the lead) ----------
# A stroked ring: the pin board paste file with the P1 ring moved 2.0 mm off its pad must fail R4.
# A filled region: a 0.40 x 0.40 region on land SW1:3 of flex1-us9 passes; the same region 1.0 mm off it fails R4.
PINS_GBR = os.path.join(ROOT, "design/ecad/case/pcb/fab/case_pins/gerber/case_pins-F_Paste.gbr")


def rel(p):
    return os.path.relpath(p, ROOT)


def mini_paste(name, gbr_path, lands, expect_pass):
    rs = paste_break(mini_rows, 2, "paste layer %s for %s" % (rel(gbr_path), lands))
    path = os.path.join(BROKEN, "mini-%s.csv" % name)
    write(path, FIELDS, rs)
    rc, out = run(["--joints", path, "--wiring", mini_wiring, "--passes", mini_passes], path[:-4] + ".log")
    probs = [l for l in out if not l.startswith("RESULT")]
    rules = sorted({l.split()[0] for l in probs})
    if expect_pass:
        ok = rc == 0 and out and out[-1] == "RESULT PASS joints 3"
        results.append(("mini " + name, "exit 0, RESULT PASS joints 3", "exit %d, %s" % (rc, out[-1] if out else ""), ok))
    else:
        ok = rc == 1 and rules == ["R4"] and out[-1] == "RESULT FAIL %d" % len(probs)
        results.append(("mini " + name, "exit 1, only R4 lines", "exit %d, rules %s, %d lines" % (rc, rules, len(probs)), ok))


ring_dir = os.path.join(BROKEN, "ring-off-pad")
os.makedirs(ring_dir, exist_ok=True)
ring_gbr = os.path.join(ring_dir, "case_pins-F_Paste.gbr")  # same board name, so R4 reads the case_pins pads
with open(PINS_GBR, encoding="utf-8") as f:
    txt = f.read()
moved = txt.replace("X97179000Y-100000000", "X99179000Y-100000000").replace("X95779000Y-100000000", "X97779000Y-100000000")
assert moved != txt
with open(ring_gbr, "w", encoding="utf-8") as f:
    f.write(moved)
mini_paste("ring_off_pad", ring_gbr, "P1:1", False)


def region_gbr(path, cx, cy, half):
    with open(path, "w", encoding="utf-8") as f:
        f.write("%FSLAX46Y46*%\n%MOMM*%\n%LPD*%\nG01*\nG36*\n")
        pts = [(cx - half, cy - half), (cx + half, cy - half), (cx + half, cy + half), (cx - half, cy + half), (cx - half, cy - half)]
        for k, (x, y) in enumerate(pts):
            f.write("X%dY%d%s*\n" % (round(x * 1e6), round(y * 1e6), "D02" if k == 0 else "D01"))
        f.write("G37*\nM02*\n")


sw = [p for p in csv.DictReader(open(os.path.join(WORK, "pads", "flex1-us9-pads.csv"), newline=""))
      if p["ref"] == "SW1" and p["pad"] == "3"][0]
sx, sy = float(sw["x_mm"]), -float(sw["y_mm"])
for name, dx, expect in (("region_on_land", 0.0, True), ("region_off_land", 1.0, False)):
    d = os.path.join(BROKEN, name.replace("_", "-"))
    os.makedirs(d, exist_ok=True)
    g = os.path.join(d, "flex1-us9-F_Paste.gbr")
    region_gbr(g, sx + dx, sy, 0.20)
    mini_paste(name, g, "SW1:3", expect)

fails = 0
for name, exp, seen, ok in results:
    print("%s | expected %s | seen %s | %s" % (name, exp, seen, "as expected" if ok else "DIFFERS"))
    fails += 0 if ok else 1
print("base real table: exit %d, %s" % (rc0, base_out[-1] if base_out else ""))
print("TESTS %s %d of %d as expected" % ("PASS" if fails == 0 else "FAIL", len(results) - fails, len(results)))
