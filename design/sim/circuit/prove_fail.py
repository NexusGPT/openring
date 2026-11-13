#!/usr/bin/env python3
"""Proof that the bench can fail: three broken copies of the ring netlist, each run through the real bench.

    python prove_fail.py [--out DIR]

The copies are made from design/ecad/ring/netlist.csv and parts.csv by exact text edits (one edit each, checked to
happen exactly once).  Expected failures are in expected-failures.md (written before the first run).  The script runs
`run_tests.py` on each copy for the named test and compares the rows that fail with the expected ones.
Ends with `PROOF RESULT OK` (exit 0) when every copy fails its named test on every expected row.
"""
import argparse
import csv
import os
import re
import subprocess
import sys

import circuit_lib as cl

HERE = os.path.dirname(os.path.abspath(__file__))

EXPECT = {
    "broken1_capacitor": {"test": "R4", "fail": ["R4.7", "R4.8"], "green": ["R4.1", "R4.2", "R4.3", "R4.4", "R4.5", "R4.6"]},
    "broken2_pullup": {"test": "R5", "fail": ["R5.6"], "green": ["R5.1", "R5.2", "R5.3", "R5.4", "R5.5", "R5.7", "R5.8", "R5.9", "R5.10"]},
    "broken3_swapped": {"test": "R2", "fail": ["R2.2", "R2.3", "R2.7", "R2.12", "R2.13", "R2.17"], "green": []},
    # case copies (13 Nov): written in pass-lines.md section D and expected-failures.md before they ran
    "broken_case2_ce_gnd": {"case": True, "test": "C2", "fail": ["C2.5", "C2.6"], "green": ["C2.4", "C2.7", "C2.8", "C2.9", "C2.10", "C2.11", "C2.12", "C2.13"]},
    "broken_case4_anode_3v3": {"case": True, "test": "C4", "fail": ["C4.6", "C4.7"], "green": ["C4.5", "C4.8", "C4.9"]},
}


def edit(path_in, path_out, fn, what):
    text = open(path_in, newline="").read()
    new, n = fn(text)
    if n != 1 and what != "pullup":
        raise SystemExit("edit %s changed %d places, expected 1" % (what, n))
    open(path_out, "w", newline="").write(new)
    return n


def make_copies(base, only=()):
    ring = cl.RING_DIR
    out = {}
    for name in EXPECT:
        if only and name not in only:
            continue
        if EXPECT[name].get("case"):
            continue
        d = os.path.join(base, name, "ring")
        os.makedirs(d, exist_ok=True)
        out[name] = d
    # 1: wrong capacitor value
    d = out["broken1_capacitor"]
    open(os.path.join(d, "netlist.csv"), "w", newline="").write(open(os.path.join(ring, "netlist.csv"), newline="").read())
    edit(os.path.join(ring, "parts.csv"), os.path.join(d, "parts.csv"),
         lambda t: re.subn(r"^(C60,C,)2\.2uF(,)", r"\g<1>470uF\g<2>", t, flags=re.M), "C60")
    # 2: missing pull-up R63 (SD_DAT1 to VDD_SD)
    d = out["broken2_pullup"]
    t = open(os.path.join(ring, "netlist.csv"), newline="").read()
    lines = t.splitlines(keepends=True)
    kept = [l for l in lines if not re.match(r"^SD_DAT1,R63,|^VDD_SD,R63,", l)]
    if len(lines) - len(kept) != 2:
        raise SystemExit("pull-up edit removed %d netlist rows, expected 2" % (len(lines) - len(kept)))
    open(os.path.join(d, "netlist.csv"), "w", newline="").write("".join(kept))
    t = open(os.path.join(ring, "parts.csv"), newline="").read()
    lines = t.splitlines(keepends=True)
    kept = [l for l in lines if not l.startswith("R63,")]
    if len(lines) - len(kept) != 1:
        raise SystemExit("pull-up edit removed %d parts rows, expected 1" % (len(lines) - len(kept)))
    open(os.path.join(d, "parts.csv"), "w", newline="").write("".join(kept))
    # 3: swapped regulator outputs
    d = out["broken3_swapped"]
    open(os.path.join(d, "parts.csv"), "w", newline="").write(open(os.path.join(ring, "parts.csv"), newline="").read())
    t = open(os.path.join(ring, "netlist.csv"), newline="").read()
    a = "VDD_1V8,U2,B6,VOUT1,"
    b = "VDD_3V0,U2,C6,VOUT2,"
    if t.count(a) != 1 or t.count(b) != 1:
        raise SystemExit("swap edit: rows not found once each")
    t = t.replace(a, "VDD_3V0,U2,B6,VOUT1,").replace(b, "VDD_1V8,U2,C6,VOUT2,")
    open(os.path.join(d, "netlist.csv"), "w", newline="").write(t)
    # case copies: one exact text edit of design/ecad/case/netlist.csv each, parts.csv unchanged
    case = cl.CASE_DIR
    for name, a, b in (("broken_case2_ce_gnd", "3V3,R21,2,~,passive", "GND,R21,2,~,passive"),
                       ("broken_case4_anode_3v3", "SYS,LED1,1,A,passive", "3V3,LED1,1,A,passive")):
        if only and name not in only:
            continue
        d = os.path.join(base, name, "case")
        os.makedirs(d, exist_ok=True)
        t = open(os.path.join(case, "netlist.csv"), newline="").read()
        if t.count(a) != 1:
            raise SystemExit("case edit %s: row %r found %d times, expected 1" % (name, a, t.count(a)))
        open(os.path.join(d, "netlist.csv"), "w", newline="").write(t.replace(a, b))
        for f in ("parts.csv", "sch-notes.md"):
            open(os.path.join(d, f), "w", newline="").write(open(os.path.join(case, f), newline="").read())
        out[name] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "results", "broken"))
    ap.add_argument("--only", default="", help="comma list of copy names (default all)")
    a = ap.parse_args()
    only = [x for x in a.only.split(",") if x]
    copies = {n: d for n, d in make_copies(a.out).items() if not only or n in only}
    all_ok = True
    for name, d in copies.items():
        exp = EXPECT[name]
        od = os.path.join(a.out, name, "out")
        log = os.path.join(a.out, name, "run.log")
        with open(log, "w") as f:
            pr = subprocess.run([sys.executable, os.path.join(HERE, "run_tests.py"), "--case-dir" if exp.get("case") else "--ring-dir", d, "--out", od, "--only", exp["test"]], stdout=f, stderr=subprocess.STDOUT)
        rows = {}
        with open(os.path.join(od, "rows.csv"), newline="") as f:
            for r in csv.DictReader(f):
                rows[r["id"]] = r
        failing = sorted(i for i, r in rows.items() if r["ok"] == "FAIL")
        missing = [i for i in exp["fail"] if rows.get(i, {}).get("ok") != "FAIL"]
        wrong_green = [i for i in exp["green"] if rows.get(i, {}).get("ok") != "PASS"]
        extra = [i for i in failing if i not in exp["fail"]]
        ok = pr.returncode == 1 and not missing and not wrong_green
        all_ok = all_ok and ok
        print("%s %s: bench exit %d, expected failing rows %s, failing rows %s, expected rows that did not fail %s, rows expected green that did not pass %s, extra failing rows %s" % (
            "PROOF OK" if ok else "PROOF FAILED", name, pr.returncode, ",".join(exp["fail"]), ",".join(failing), ",".join(missing) or "none", ",".join(wrong_green) or "none", ",".join(extra) or "none"))
        for i in exp["fail"]:
            r = rows.get(i)
            if r:
                print("    %s %s = %s needs %s %s" % (i, r["qty"], r["value"] or "no value", r["op"], r["limit"]))
    print("PROOF RESULT " + ("OK" if all_ok else "FAILED"))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
