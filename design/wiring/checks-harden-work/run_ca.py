import json, os, re, shutil, subprocess, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work"))
from runlib import *
A = ROOT + "/design/mfg/assembly"
# 1. snapshots of the three live files as they stand now (the fakes are made from them), then the fakes
shutil.copy(A + "/assembly.md", W + "/copies/ca/live-snapshot.md")
shutil.copy(A + "/joints.csv", W + "/copies/joints-snapshot-2.csv")
shutil.copy(ROOT + "/design/wiring/product-wiring.csv", W + "/copies/product-wiring-snapshot-2.csv")
subprocess.run([PY, W + "/make_assembly_fakes.py"], check=True)
man = json.load(open(W + "/copies/ca/manifest.json"))
RV = ROOT + "/design/wiring/review4-work/fakes-ca/"
for nm, f in [("rev_g1", "g1"), ("rev_tabs", "tabs"), ("rev_cite", "cite"), ("rev_cite2", "cite2"), ("rev_nocheck", "nocheck"), ("rev_noresult", "noresult"), ("rev_flood", "flood"), ("rev_empty", "empty")]:
    man.append({"name": nm, "md": RV + f + ".md", "joints": W + "/copies/joints-snapshot-2.csv", "wiring": W + "/copies/product-wiring-snapshot-2.csv", "want_exit": 1, "want_tag": None, "want_id": None})
man.append({"name": "rev_honest_guide_of_review4", "md": RV + "honest.md", "joints": W + "/copies/joints-snapshot-2.csv", "wiring": W + "/copies/product-wiring-snapshot-2.csv", "want_exit": 1, "want_tag": "T1 FAIL", "want_id": None})
CHK = ROOT + "/design/mfg/assembly/check_assembly.py"
def cmd(c): return [PY, "-I", CHK, c["md"], "--joints", c["joints"], "--wiring", c["wiring"]]
def lines_of(c):
    r = subprocess.run(["nice", "-n", "19"] + cmd(c), capture_output=True, text=True)
    return [l for l in (r.stdout + r.stderr).splitlines()], r.returncode
# 2. the control: the guide copy. Its failing lines (if any) are real faults of the live files; a fake must ADD a line of its own tag to them
base, base_rc = lines_of(man[0])
keep = lambda l: not l.startswith(("RESULT", "INFO", "CITE", "FWCITE", "T1 ", "P1 ", "L1 ")) or l.startswith(("P1 FAIL", "L1 FAIL"))
base_set = {l for l in base if keep(l)}
os.makedirs(W + "/logs/ca", exist_ok=True)
open(W + "/logs/ca/base_live_guide_copy.log", "w").write("\n".join(base) + "\nEXIT %d\n" % base_rc)
ok = n = 0
print("BASE the live guide copy: exit %d, %d failing lines (real faults of the live files, listed in the notes)" % (base_rc, len([l for l in base if " FAIL" in l])))
for c in man:
    lines, rc = lines_of(c)
    open(W + "/logs/ca/" + c["name"] + ".log", "w").write("\n".join(lines) + "\nEXIT %d\n" % rc)
    new = [l for l in lines if keep(l) and l not in base_set]
    if c["name"] == "honest_snapshot":
        good = not new; line = "no new line against itself"
    elif c["name"].startswith("rev_"):
        good = rc == 1 and (c["want_tag"] is None or any(c["want_tag"] in l for l in lines)); line = next((l for l in lines if " FAIL" in l), "")[:150]
    else:
        hits = [l for l in new if c["want_tag"] and c["want_tag"] in l]
        good = rc == 1 and (len(new) > 0 if c["want_tag"] is None else len(hits) > 0)
        line = (hits or new or [""])[0][:170]
    n += 1; ok += good
    print("CASE check_assembly/%-42s exit=%d new_lines=%d %s | %s" % (c["name"], rc, len(new), "as expected" if good else "DIFFERS", line), flush=True)
print("SECTION check_assembly ok=%d of %d" % (ok, n))
