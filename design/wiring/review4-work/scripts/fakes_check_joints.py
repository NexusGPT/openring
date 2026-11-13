# Fakes for design/mfg/assembly/check_joints.py through its --joints entry point (copies only in W).
import csv, os, re, subprocess, shutil
W = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work")
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
PY = ROOT + "/design/.venv/bin/python"
CHK = ROOT + "/design/mfg/assembly/check_joints.py"
J = ROOT + "/design/mfg/assembly/joints.csv"
FK = W + "/fakes-cj"; os.makedirs(FK, exist_ok=True)
rows = list(csv.DictReader(open(J))); hdr = list(rows[0].keys())
def write(name, rs):
    p = os.path.join(FK, name + ".csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); [w.writerow(r) for r in rs]
    return p
def mod(jid, **kw):
    out = []
    for r in rows:
        r = dict(r)
        if r["joint_id"] == jid: r.update(kw)
        out.append(r)
    return out
# broken paste file: the delivered ring F paste with the 15 J_BAND regions removed (regions whose box is on a J_BAND land)
src = ROOT + "/design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr"
bd = os.path.join(FK, "broken-gbr"); os.makedirs(bd, exist_ok=True)
txt = open(src).read()
lands = [(-3.015, 3.875), (-2.505, 3.875), (-1.995, 3.875), (-1.485, 3.875), (-3.015, 4.775), (-2.505, 4.775), (-1.995, 4.775), (-1.485, 4.775)]
def is_jband_region(block):
    pts = [(int(a) / 1e6, int(b) / 1e6) for a, b in re.findall(r"X(-?\d+)Y(-?\d+)D0[12]", block)]
    if not pts: return False
    cx = sum(p[0] for p in pts) / len(pts) - 100.0; cy = -sum(p[1] for p in pts) / len(pts) - 100.0
    return any(abs(cx - lx) < 0.2 and abs(abs(cy) - ly) < 0.3 for lx, ly in lands)
parts = re.split(r"(G36\*.*?G37\*)", txt, flags=re.S)
removed = 0; out = []
for p in parts:
    if p.startswith("G36*") and is_jband_region(p): removed += 1; continue
    out.append(p)
bg = os.path.join(bd, "ring-F_Paste.gbr"); open(bg, "w").write("".join(out))
print("broken gerber: regions removed", removed)
def repoint(rs):
    o = []
    for r in rs:
        r = dict(r); r["solder_source"] = r["solder_source"].replace("design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr", bg); o.append(r)
    return o
cases = [("honest_copy", write("honest", rows), 0)]
cases.append(("paste_removed_at_15_lands", write("brokenpaste", repoint(rows)), 1))
cases.append(("empty_table", write("empty", []), 1))
cases.append(("row_dropped", write("dropped", [r for r in rows if r["joint_id"] != "J-W026-A"]), 1))
cases.append(("check_empty", write("checkempty", mod("J-W026-A", check="")), 1))
cases.append(("check_meaningless", write("checkok", mod("J-W026-A", check="ok")), 1))
cases.append(("heat_meaningless", write("heatok", mod("J-W061-B", heat="hot")), 1))
cases.append(("step_unknown", write("stepbad", mod("J-W026-A", step="99")), 1))
cases.append(("gap_text", write("gap", mod("J-W026-A", gap="no solder named")), 1))
flood = [dict(r) for r in rows] + [dict(r, step="2", check="none") for r in rows]
cases.append(("flood_conflicting_dups", write("flood", flood), 1))
cases.append(("missing_paste_file", write("nofile", mod("J-W001-A", solder_source="paste layer design/ecad/ring/pcb/fab/gerber/ring-X_Paste.gbr for J_BAND_A:1")), 1))
differs = 0
for name, p, want in cases:
    r = subprocess.run([PY, CHK, "--joints", p], capture_output=True, text=True)
    open(os.path.join(FK, name + ".log"), "w").write(r.stdout + r.stderr)
    lines = (r.stdout + r.stderr).strip().splitlines(); last = lines[-1] if lines else ""
    got = 0 if r.returncode == 0 else 1; ok = got == want; differs += 0 if ok else 1
    print("CASE %-26s want_exit=%d got_exit=%d %s | %s" % (name, want, r.returncode, "as expected" if ok else "DIFFERS", last[:200]))
print("RESULT fakes=%d differs=%d" % (len(cases), differs))
