# review 3: faked inputs for check_all.py, each through the same entry point; expected: every fake exits with fails > 0 of the named kind,
# the honest control exits with fails = 0.
import csv, os, shutil, subprocess, io
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
W = R + "/design/wiring/review3-work"
F = W + "/fakes"
os.makedirs(F, exist_ok=True)
SRC = R + "/design/wiring/product-wiring.csv"
PADS = W + "/pads"
rows = list(csv.DictReader(open(SRC))); hdr = list(rows[0].keys())
def write(name, rs):
    p = F + "/" + name + ".csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); [w.writerow(r) for r in rs]
    return p
def copy_rows(): return [dict(r) for r in rows]
def byid(rs, i): return [r for r in rs if r["id"] == i][0]
def run(name, csvp, pads=PADS, contact=None, expect="fail", kind=None):
    args = ["/usr/bin/python3", "-I", W + "/scripts/check_all.py", csvp, pads] + ([contact] if contact else [])
    out = subprocess.run(args, capture_output=True, text=True)
    log = F + "/" + name + ".log"
    open(log, "w").write(out.stdout + out.stderr)
    last = (out.stdout.strip().splitlines() or ["(no output)"])[-1]
    nf = int(last.split("fails=")[1]) if "fails=" in last else -1
    kinds = sorted(set(l.split()[1] for l in out.stdout.splitlines() if l.startswith("FAIL")))
    ok = (nf == 0) if expect == "pass" else (nf > 0 and (kind is None or kind in kinds))
    print("%-22s expect %-4s got fails=%s kinds=%s -> %s" % (name, expect, nf, ",".join(kinds), "AS EXPECTED" if ok else "DIFFERS"))
    return ok
res = []
res.append(run("control", write("control", copy_rows()), expect="pass"))
rs = copy_rows(); byid(rs, "W033")["end_B_pin"] = "2 (land of footprint PRT1_Tabs)"; res.append(run("wrong-pin", write("wrong-pin", rs), kind="net"))
rs = copy_rows(); r = byid(rs, "W029"); r["signal_A"] = r["signal_B"] = "USB_DN"; res.append(run("wrong-signal", write("wrong-signal", rs), kind="net"))
rs = copy_rows(); rs.append(dict(byid(rs, "W063"))); res.append(run("duplicate", write("duplicate", rs), kind="dup"))
rs = [r for r in copy_rows() if r["id"] != "W031"]; res.append(run("missing-line", write("missing-line", rs), kind="uncovered"))
rs = copy_rows(); byid(rs, "W024")["cut_mm_us11"] = ""; res.append(run("missing-cut", write("missing-cut", rs), kind="cut"))
rs = copy_rows(); byid(rs, "W059")["carrier_marking"] = ""; res.append(run("missing-mark", write("missing-mark", rs), kind="mark"))
rs = copy_rows(); byid(rs, "W030")["end_B_face"] = "F.Cu"; res.append(run("wrong-face", write("wrong-face", rs), kind="face"))
rs = copy_rows(); byid(rs, "W025")["join_A"] = "hot bar (main board land to FLEX2 tail land 2)"; res.append(run("wrong-tail-land", write("wrong-tail-land", rs), kind="tail"))
rs = copy_rows()
for k in range(200):
    r = dict(byid(rs, "W064")); r["id"] = "X%03d" % k; r["end_A_ref"] = "WP%d" % (k + 10); rs.append(r)
res.append(run("flood-200", write("flood-200", rs), kind="end"))
rs = copy_rows(); r = byid(rs, "W066"); r["end_B_ref"] = "W1"; r["signal_A"] = r["signal_B"] = "VRING"; res.append(run("case-wire-swap", write("case-wire-swap", rs), kind="net"))
rs = []; res.append(run("empty-csv", write("empty-csv", rs)))
# pad dumps faked: a wrong net on a band board, two tail lands swapped, a missing ring land
def fake_pads(name, board, edit):
    d = F + "/pads-" + name; os.makedirs(d, exist_ok=True)
    for f in os.listdir(PADS):
        if f.endswith(".csv"): shutil.copy(PADS + "/" + f, d + "/" + f)
    p = d + "/" + board + "-pads.csv"; lines = open(p).read().splitlines(); lines = edit(lines); open(p, "w").write("\n".join(lines) + "\n")
    return d
def swap_xy(lines, a, b):
    ia = [i for i, l in enumerate(lines) if l.startswith(a)][0]; ib = [i for i, l in enumerate(lines) if l.startswith(b)][0]
    A = lines[ia].split(","); Bv = lines[ib].split(","); A[4], Bv[4] = Bv[4], A[4]; A[5], Bv[5] = Bv[5], A[5]
    lines[ia] = ",".join(A); lines[ib] = ",".join(Bv); return lines
res.append(run("pads-wrong-net", SRC, pads=fake_pads("wrong-net", "flex2-us11", lambda L: [l.replace("CP1,1,VBUS", "CP1,1,USB_DN") for l in L]), kind="net"))
res.append(run("pads-tail-swap", SRC, pads=fake_pads("tail-swap", "flex1-us9", lambda L: swap_xy(L, "J_BAND_A,1,", "J_BAND_A,4,")), kind="mate"))
res.append(run("pads-ring-land-gone", SRC, pads=fake_pads("ring-land-gone", "ring", lambda L: [l for l in L if not l.startswith("J_BAND_B,4,")]), kind="end"))
# contact csv faked: a height above the maker range, and P1/P4 swapped
cr = open(R + "/design/wiring/ring-case-contact.csv").read().splitlines()
p = F + "/contact-high.csv"; open(p, "w").write("\n".join([cr[0]] + [cr[1].replace("2.139", "2.215")] + cr[2:]) + "\n")
res.append(run("contact-high", SRC, contact=p, kind="pair-height"))
p = F + "/contact-swap.csv"; open(p, "w").write("\n".join([cr[0]] + [l.replace("P1,VRING", "P4,GND") for l in cr[1:]]) + "\n")
res.append(run("contact-swap", SRC, contact=p, kind="pair"))
print("RESULT fakes=%d as_expected=%d differs=%d" % (len(res), sum(res), len(res) - sum(res)))
