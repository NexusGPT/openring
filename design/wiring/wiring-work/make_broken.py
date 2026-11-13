#!/usr/bin/env python3
"""Make 5 broken copies of product-wiring.csv, run check_wiring.py on each, and require that each fails its named check.

Output: wiring-work/broken/<name>.csv, wiring-work/broken/<name>.log, and a summary on stdout (one line per copy).
"""
import csv
import os
import subprocess
import sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
HERE = os.path.join(ROOT, "design/wiring")
OUT = os.path.join(HERE, "wiring-work/broken")
PY = os.path.join(ROOT, "design/.venv/bin/python")
os.makedirs(OUT, exist_ok=True)

src = os.path.join(HERE, "product-wiring.csv")
rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
cols = list(rows[0].keys())


def find(pred):
    for i, r in enumerate(rows):
        if pred(r):
            return i
    raise SystemExit("no row for a broken copy")


def write(name, rs):
    path = os.path.join(OUT, name + ".csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rs:
            w.writerow(r)
    return path


cases = []
# 1. a terminal in two lines: the line J_BAND_A 1 -> SW1 3 copied under a new id
i = find(lambda r: r["end_A_ref"] == "J_BAND_A" and r["end_A_pin"].startswith("1 "))
rs = [dict(r) for r in rows]
dup = dict(rs[i]); dup["id"] = "W999"
rs.append(dup)
cases.append(("terminal_twice", "terminal-twice", write("terminal_twice", rs), "J_BAND_A pin 1"))
# 2. a terminal in no line: the line of SW1 pin 1 removed
i = find(lambda r: r["end_A_ref"] == "SW1" and r["end_A_pin"] == "1")
rs = [dict(r) for k, r in enumerate(rows) if k != i]
cases.append(("terminal_missing", "terminal-missing", write("terminal_missing", rs), "SW1 pin 1"))
# 3. ends that disagree: the far end of J_BAND_B 4 (VBUS) renamed to VBAT, rule still "same net"
i = find(lambda r: r["end_A_ref"] == "J_BAND_B" and r["end_A_pin"].startswith("4 "))
rs = [dict(r) for r in rows]
rs[i]["signal_B"] = "VBAT"
cases.append(("ends_disagree", "ends-disagree", write("ends_disagree", rs), rs[i]["id"]))
# 4. a lead without a length: case wire W1 (already incomplete for its marking), US 10 length and the words blanked
i = find(lambda r: r["carrier_kind"] == "wire" and r["end_B_ref"] == "W1")
rs = [dict(r) for r in rows]
rs[i]["cut_mm_us10"] = ""
rs[i]["cut_note"] = ""
rs[i]["state"] = "drawn, not routed"  # kept consistent, so only the missing length is wrong
cases.append(("lead_no_length", "lead-length", write("lead_no_length", rs), rs[i]["id"]))
# 5. a proof line that does not hold the quoted text: the hot bar quote cited one line too low
i = find(lambda r: "band-interface.md:60|Soldering method: HOT BAR" in r["proof_join"])
rs = [dict(r) for r in rows]
rs[i]["proof_join"] = rs[i]["proof_join"].replace("band-interface.md:60|", "band-interface.md:61|")
cases.append(("proof_wrong_line", "proof-text", write("proof_wrong_line", rs), rs[i]["id"]))

# 6. `specified and landed` on a copper line (state-kind)
i = find(lambda r: r["carrier_kind"] == "copper" and r["state"] == "drawn and routed")
rs = [dict(r) for r in rows]
rs[i]["state"] = "specified and landed"
cases.append(("state_kind", "state-kind", write("state_kind", rs), rs[i]["id"]))

# 7. a line marked complete whose board pad is open: a screen contact (J1 pad not joined on the main board) set complete
i = find(lambda r: r["carrier_kind"] == "part cable" and "J1 pad" in r["state_reason"] and "not joined" in r["state_reason"])
rs = [dict(r) for r in rows]
rs[i]["state"] = "specified and landed"
cases.append(("complete_but_open", "complete-open", write("complete_but_open", rs), rs[i]["id"]))

# the good csv may fail checks of its own (for example `incomplete`): those are the base, run the same way
base_log = os.path.join(OUT, "good.log")
with open(base_log, "w") as lf:
    base_rc = subprocess.call(["nice", "-n", "19", PY, os.path.join(HERE, "check_wiring.py"), "--csv", src],
                              stdout=lf, stderr=subprocess.STDOUT)
base_text = open(base_log).read().split("\n")
base_fail = {}
for ln in base_text:
    if ln.startswith("FAIL["):
        k = ln.split("]")[0] + "]"
        base_fail[k] = base_fail.get(k, 0) + 1
print("good csv: exit %d, failing checks %s | %s" % (base_rc, base_fail or "none",
      [ln for ln in base_text if ln.startswith("RESULT")][-1]))

allok = True
for name, check, path, what in cases:
    log = os.path.join(OUT, name + ".log")
    with open(log, "w") as lf:
        rc = subprocess.call(["nice", "-n", "19", PY, os.path.join(HERE, "check_wiring.py"), "--csv", path],
                             stdout=lf, stderr=subprocess.STDOUT)
    text = open(log).read().split("\n")
    named = [ln for ln in text if ln.startswith("FAIL[%s]" % check)]
    named_new = [ln for ln in named if ln not in base_text]
    other = sorted({ln.split("]")[0] + "]" for ln in text if ln.startswith("FAIL[") and not ln.startswith("FAIL[%s]" % check)
                    and ln not in base_text})
    last = [ln for ln in text if ln.startswith("RESULT")]
    ok = rc == 1 and named_new and not other
    named = named_new
    allok = allok and bool(ok)
    print("%-18s exit %d, new FAIL[%s] lines %d, other new failing checks %s, changed: %s | %s" % (
        name, rc, check, len(named), other or "none", what, last[-1] if last else "no RESULT line"))
    for ln in named:
        print("    " + ln)
print("BROKEN COPIES PASS: %d copies, each fails its named check with new FAIL lines and no other new failure" % len(cases)
      if allok else "BROKEN COPIES FAIL")
sys.exit(0 if allok else 1)
