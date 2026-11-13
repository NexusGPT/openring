# Fakes for my own checker check_all.py, each through the same entry point. Expected: honest control exit 0, every fake exit != 0.
import csv, os, shutil, subprocess, sys
W = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work")
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
PY = ROOT + "/design/.venv/bin/python"
CSV = ROOT + "/design/wiring/product-wiring.csv"
FK = W + "/fakes"; os.makedirs(FK, exist_ok=True)
rows = list(csv.DictReader(open(CSV))); hdr = list(rows[0].keys())
def write(name, rs):
    p = os.path.join(FK, name + ".csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); [w.writerow(r) for r in rs]
    return p
def mod(idv, **kw):
    out = []
    for r in rows:
        r = dict(r)
        if r["id"] == idv: r.update(kw)
        out.append(r)
    return out
def padcopy(name, board, fn):
    d = os.path.join(FK, "pads-" + name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(W + "/pads"):
        if f.endswith(".csv"): shutil.copy(os.path.join(W, "pads", f), d)
    p = os.path.join(d, board + "-pads.csv"); lines = open(p).read().splitlines()
    open(p, "w").write("\n".join(fn(lines)) + "\n"); return d
cases = []
cases.append(("honest", CSV, W + "/pads", [], 0))
cases.append(("empty", write("empty", []), W + "/pads", [], 1))
flood = [dict(r) for r in rows]
for k in range(2):
    for r in rows: r2 = dict(r); r2["id"] = r["id"] + "x%d" % k; flood.append(r2)
cases.append(("flood_dup_rows", write("flood", flood), W + "/pads", [], 1))
cases.append(("missing_marking", write("nomark", mod("W023", carrier_marking="")), W + "/pads", [], 1))
cases.append(("missing_cuts", write("nocut", mod("W059", **{"cut_mm_us9": "", "cut_note": ""})), W + "/pads", [], 1))
cases.append(("wrong_net", write("wrongnet", mod("W001", carrier_net="JOY_DOWN")), W + "/pads", [], 1))
cases.append(("wrong_tail_land", write("wrongtail", mod("W001", join_A="hot bar (main board land to FLEX1 tail land 2)")), W + "/pads", [], 1))
cases.append(("wrong_face", write("wrongface", mod("W040", end_B_face="F.Cu")), W + "/pads", [], 1))
cases.append(("row_dropped", write("dropped", [r for r in rows if r["id"] != "W030"]), W + "/pads", [], 1))
cases.append(("spring_swap", write("springswap", mod("W054", end_B_ref="P4")), W + "/pads", [], 1))
cases.append(("missing_column", write("nocol", rows), W + "/pads", [], None))
def shift(lines):
    out = []
    for l in lines:
        if l.startswith("J_BAND_A,1,"):
            f = l.split(","); f[3] = "%.4f" % (float(f[3]) + 0.1); l = ",".join(f)
        out.append(l)
    return out
cases.append(("mating_shift", CSV, padcopy("shift", "flex1-us9", shift), [], 1))
def netchg(lines): return [l.replace("J_BAND_B,4,VBUS,", "J_BAND_B,4,USB_DN,") for l in lines]
cases.append(("ring_pad_net", CSV, padcopy("net", "ring", netchg), [], 1))
cont = list(csv.DictReader(open(ROOT + "/design/wiring/ring-case-contact.csv")))
cont[5]["working_height_mm"] = "2.300"
cp = os.path.join(FK, "contact-high.csv")
with open(cp, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(cont[0].keys())); w.writeheader(); [w.writerow(r) for r in cont]
cases.append(("contact_height", CSV, W + "/pads", [ROOT + "/design/ecad/ring/netlist.csv", ROOT + "/design/ecad/case/netlist.csv", cp], 1))
cases.append(("crash_missing_file", FK + "/does-not-exist.csv", W + "/pads", [], 1))
differs = 0
for name, c, pads, extra, want in cases:
    if name == "missing_column":
        p = os.path.join(FK, "nocol.csv"); h2 = [h for h in hdr if h != "carrier_marking"]
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=h2, extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
        c = p; want = 1
    r = subprocess.run([PY, W + "/scripts/check_all.py", c, pads] + extra, capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    got = 0 if r.returncode == 0 else 1
    crash = "Traceback" in r.stderr
    ok = (got == want)
    if not ok: differs += 1
    print("CASE %-20s want_exit=%s got_exit=%d crash=%s %s | %s" % (name, want, r.returncode, crash, "as expected" if ok else "DIFFERS", last))
print("RESULT fakes=%d differs=%d" % (len(cases), differs))
