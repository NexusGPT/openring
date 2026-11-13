#!/usr/bin/env python3
"""Builds the decks from netlist.csv / parts.csv, runs every test of the bench, compares each result with the
pass lines of pass-lines.md by script and prints one line per test.

    python run_tests.py [--ring-dir DIR] [--case-dir DIR] [--out DIR] [--only R1,R5]

Ends with `RESULT PASS` (exit 0) when every row of every test holds, else `RESULT FAIL` (exit 1).
A missing value (a deck that did not run, a measurement that failed) is a FAIL with the reason, never a pass.
"""
import argparse
import ast
import csv
import json
import operator
import os
import re
import sys
import time

import bench
import circuit_lib as cl
import make_decks as md

HERE = os.path.dirname(os.path.abspath(__file__))

TEST_NAMES = {
    "R1": "ring1 motor start",
    "R2": "ring2 power-up",
    "R3": "ring3 charge path",
    "R4": "ring4 storage inrush",
    "R5": "ring5 level shifter and storage lines",
    "R6": "ring6 joystick and record lines",
    "R7": "ring7 pads on the finger",
    "R8": "ring8 microphone supply ripple",
    "C1": "case1 boost to VRING",
    "C2": "case2 cell charger",
    "C3": "case3 thermistor window",
    "C4": "case4 LED currents",
    "C5": "case5 design risks",
}


# ------------------------------------------------------------------------------------------------
# pass lines
# ------------------------------------------------------------------------------------------------
_OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def safe_eval(expr):
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            return _BIN[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        raise ValueError("bad limit expression: %s" % expr)
    return ev(ast.parse(expr.strip(), mode="eval"))


def read_pass_lines(path):
    rows = []
    for line in open(path):
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not re.match(r"^[RC][0-9]+\.[0-9]+$", cells[0]):
            continue
        rid, qty, op, limit, unit, source = cells[:6]
        if op not in _OPS:
            continue
        rows.append({"id": rid, "qty": qty, "op": op, "limit_text": limit, "limit": safe_eval(limit), "unit": unit, "source": source})
    return rows


def kind_of(source):
    """Label of a row in rows.csv: SIMULATED or DATASHEET FACT when the source cell of pass-lines.md starts with it, else empty (ring rows and older case rows)."""
    for k in ("SIMULATED", "DATASHEET FACT"):
        if source.startswith(k):
            return k
    return ""


def evaluate(rows, values):
    out = []
    for r in rows:
        v = values.get(r["qty"])
        if v is None or isinstance(v, str):
            out.append(dict(r, value=None, ok=False, why="no value (%s)" % (v if v is not None else "not measured")))
        else:
            out.append(dict(r, value=v, ok=bool(_OPS[r["op"]](v, r["limit"])), why=""))
    return out


# ------------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------------
class Ctx:
    def __init__(self, ring, case, out, rows):
        self.ring, self.case, self.out, self.rows = ring, case, out, rows
        self.decks = os.path.join(out, "decks")
        self.work = os.path.join(out, "run")
        self.info = []
        self.values = {}
        self.errors = {}

    def deck(self, name):
        return os.path.join(self.decks, name + ".cir")

    def run(self, deck, params=None, tag=None, test=None):
        res, err = bench.run_deck(self.deck(deck), params, tag=tag, workdir=self.work)
        if err:
            # an aborted, timed-out or failed run gives no value at all (it is a FAIL with its reason, never a pass)
            self.errors.setdefault(test or "?", []).append("%s %s: %s" % (deck, tag or "", err[0][:160]))
            return {}
        if res.get("_measfail"):
            self.errors.setdefault(test or "?", []).append("%s %s: threshold never crossed: %s" % (deck, tag or "", res["_measfail"][0][-90:]))
        return res

    def note(self, text):
        self.info.append(text)

    def row_ok(self, ids, values):
        sel = [r for r in self.rows if r["id"] in ids]
        return all(e["ok"] for e in evaluate(sel, values))


def merge_max(vals):
    vals = [v for v in vals if isinstance(v, float)]
    return max(vals) if vals else None


def merge_min(vals):
    vals = [v for v in vals if isinstance(v, float)]
    return min(vals) if vals else None


# ------------------------------------------------------------------------------------------------
# ring tests
# ------------------------------------------------------------------------------------------------
V20 = 3.45
I_SPEC = 0.230


def t_ring1(c):
    keys = {"motor.vbat_min": "motor.vbat_min_spec", "motor.v18_min": "motor.v18_min_spec", "motor.v18_max": "motor.v18_max_spec",
            "motor.v30_min": "motor.v30_min_spec", "motor.v30_max": "motor.v30_max_spec", "motor.vmot_min": "motor.vmot_min_spec",
            "motor.vsys_min": "motor.vsys_min_spec", "motor.ibat_max": "motor.ibatpath_max_spec", "motor.ildo_max": "motor.ildo_max_spec"}
    rspec = (V20 - 3.0) / I_SPEC
    base = c.run("ring1_motor", {"ocv": V20, "rcell": rspec}, tag="rspec", test="R1")
    for k, q in keys.items():
        c.values[q] = base.get(k)
    c.values["motor.rspec_ohm"] = rspec
    c.values["motor.icell_pk_at_rspec"] = base.get("motor.icell_pk")
    c.note("ring1 info at R_SPEC %.4f ohm: the cell terminal is %.4f V just before the start is over (settled, motor %.0f mA) and dips to %.4f V when U11 finishes charging C84 and the motor draws its start current; the cell gives %.1f mA at the peak (decision 41 names 230 mA)" % (
        rspec, base.get("motor.vbat_settled", float("nan")), 1000 * 0.175, base.get("motor.vbat_min", float("nan")), -1000 * base.get("motor.icell_pk", float("nan"))))
    rows_motor = [r["id"] for r in c.rows if r["qty"] in keys.values()]

    def passes(ocv, rcell):
        res = c.run("ring1_motor", {"ocv": ocv, "rcell": rcell}, tag="s_%g_%g" % (ocv, rcell), test="R1")
        vals = {q: res.get(k) for k, q in keys.items()}
        sel = [r for r in c.rows if r["id"] in rows_motor]
        ev = evaluate(sel, vals)
        return all(e["ok"] for e in ev), [e["id"] for e in ev if not e["ok"]], res

    def rmax(ocv):
        lo, hi = 0.01, 12.0
        ok, bad, _ = passes(ocv, lo)
        if not ok:
            return 0.0, bad
        ok, bad, _ = passes(ocv, hi)
        if ok:
            return hi, []
        for _ in range(16):
            mid = (lo + hi) / 2
            ok, bad, _ = passes(ocv, mid)
            if ok:
                lo = mid
            else:
                hi = mid
        _, bad, res = passes(ocv, hi)
        return lo, bad

    r345, lim345 = rmax(V20)
    c.values["motor.rmax_ocv345"] = r345
    c.note("ring1: largest cell resistance that passes at open-circuit %.2f V = %.4f ohm; first rows to fail just above it: %s" % (V20, r345, ",".join(lim345)))
    for ocv in (3.30, 3.60):
        r, lim = rmax(ocv)
        c.note("ring1 info: largest cell resistance that passes at open-circuit %.2f V = %.4f ohm; limiting rows %s" % (ocv, r, ",".join(lim)))
    # 175 mA pulse: the cell current at the largest passing resistance
    res = c.run("ring1_motor", {"ocv": V20, "rcell": r345}, tag="at_rmax", test="R1")
    c.note("ring1 info: at that resistance the cell gives %.1f mA at the start, the cell terminal falls to %.4f V, the chip battery path carries %.1f mA, U11 carries %.1f mA, VDD_3V0 falls to %.3f V, VMOT to %.3f V" % (
        -1000 * res.get("motor.icell_pk", float("nan")), res.get("motor.vbat_min", float("nan")), 1000 * res.get("motor.ibat_max", float("nan")),
        1000 * res.get("motor.ildo_max", float("nan")), res.get("motor.v30_min", float("nan")), res.get("motor.vmot_min", float("nan"))))
    # which cell resistance limits each pass line: sweep of the resistance at the same cell voltage, value of every row at each
    # point, the resistance at which the row crosses its limit by linear interpolation between the two points around it
    pts = [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    table = {}
    for rc in pts:
        res = c.run("ring1_motor", {"ocv": V20, "rcell": rc}, tag="row_%g" % rc, test="R1")
        table[rc] = {q: res.get(k) for k, q in keys.items()}
    lines = ["row,quantity,op,limit,largest_cell_resistance_ohm_at_%.2fV" % V20]
    for r in c.rows:
        if r["id"] not in rows_motor:
            continue
        prev = None
        found = None
        for rc in pts:
            v = table[rc].get(r["qty"])
            if not isinstance(v, float):
                continue
            ok = _OPS[r["op"]](v, r["limit"])
            if not ok:
                if prev is None:
                    found = "below %.2f" % rc
                else:
                    rc0, v0 = prev
                    found = "%.3f" % (rc0 + (rc - rc0) * (r["limit"] - v0) / (v - v0))
                break
            prev = (rc, v)
        lines.append("%s,%s,%s,%s,%s" % (r["id"], r["qty"], r["op"], r["limit_text"], found or "at least %.1f (row holds over the whole sweep)" % pts[-1]))
    with open(os.path.join(c.out, "r1_row_limits.csv"), "w") as f:
        f.write("\n".join(lines) + "\n")
    c.note("ring1 info: largest cell resistance for each pass line at %.2f V is in r1_row_limits.csv: %s" % (V20, "; ".join(l.split(",")[0] + "=" + l.split(",")[-1] for l in lines[1:])))
    return


def t_ring2(c):
    names = ["v18_min", "v18_peak", "v30_min", "v30_peak", "vmot_peak", "vsd_pre_peak", "vsd_min", "vsd_peak", "vmic_min", "order_sd"]
    for tag, ocv in (("c330", 3.30), ("c435", 4.35)):
        res = c.run("ring2_powerup", {"ocv": ocv, "rcell": 1.0}, tag=tag, test="R2")
        for n in names:
            c.values["powerup.%s_%s" % (n.replace("order_sd", "order_sd_after_3v0"), tag)] = res.get("powerup." + n)
        c.note("ring2 info cell %.2f V: VDD_1V8 valid at %s s, VDD_3V0 valid at %s s, VDD_SD (host enable at %g s) valid at %s s, VDD_MIC (host enable at %g s) valid at %s s" % (
            ocv, res.get("powerup.t18"), res.get("powerup.t30"), md.T_LS2, res.get("powerup.tsd"), md.T_LS1, res.get("powerup.tmic")))


def t_ring3(c):
    icc, vend = [], []
    for ocv in (3.0, 3.6, 4.0):
        for rcell in (0.5, 3.0):
            res = c.run("ring3_charge", {"ocv": ocv, "rcell": rcell, "rpath": 0.5, "loads": 0}, tag="cc_%g_%g" % (ocv, rcell), test="R3")
            icc.append(res.get("charge.icc"))
            vend.append(res.get("charge.vbat_t"))
    c.values["charge.icc_min"] = merge_min(icc)
    c.values["charge.icc_max"] = merge_max(icc)
    for ocv in (4.2, 4.3):
        res = c.run("ring3_charge", {"ocv": ocv, "rcell": 1.0, "rpath": 0.5, "loads": 0}, tag="cv_%g" % ocv, test="R3")
        vend.append(res.get("charge.vbat_t"))
    res = c.run("ring3_charge", {"ocv": 4.349, "rcell": 1.0, "rpath": 0.5, "loads": 0}, tag="cv_end", test="R3")
    vend.append(res.get("charge.vbat_t"))
    c.values["charge.vbat_end_max"] = merge_max(vend)
    c.values["charge.vbat_end_min"] = res.get("charge.vbat_t")
    c.note("ring3 info: terminal voltage at open-circuit 4.349 V (charge current has fallen to %.2f mA): %.4f V" % (1000 * res.get("charge.icc", float("nan")), res.get("charge.vbat_t", float("nan"))))
    res = c.run("ring3_charge", {"ocv": 3.45, "rcell": 1.0, "rpath": 0.5, "loads": 1, "ibuslim": 1.5}, tag="ibus", test="R3")
    c.values["charge.ibus_max"] = res.get("charge.ibus_pk")
    c.note("ring3 info: VBUS demand with a recording running and 15 mA charge: peak %.1f mA" % (1000 * res.get("charge.ibus_pk", float("nan"))))
    res = c.run("ring3_charge", {"ocv": 3.45, "rcell": 1.0, "rpath": 2.0, "loads": 1, "ibuslim": 1.5}, tag="rpath2", test="R3")
    c.values["charge.vbus_chip_min"] = res.get("charge.vbus_chip")
    res = c.run("ring3_charge", {"ocv": 4.349, "rcell": 1.0, "rpath": 2.0, "loads": 1, "ibuslim": 1.5}, tag="valid", test="R3")
    if isinstance(res.get("charge.vbus_chip"), float) and isinstance(res.get("charge.vbat_t"), float):
        c.values["charge.vbus_chip_valid_margin"] = res["charge.vbus_chip"] - res["charge.vbat_t"]
    res = c.run("ring3_charge", {"ocv": 3.45, "rcell": 1.0, "rpath": 0.5, "loads": 1, "ibuslim": 0.1}, tag="ilim100", test="R3")
    c.note("ring3 info: with the default 100 mA input limit and a recording running: VSYS %.3f V, charge current %.2f mA, VBUS current %.1f mA" % (
        res.get("charge.vsys", float("nan")), 1000 * res.get("charge.icc", float("nan")), 1000 * res.get("charge.ibus", float("nan"))))


def t_ring4(c):
    r50 = c.run("ring4_inrush", {"ss": 0.05, "ssdis": 0}, tag="ss50", test="R4")
    r25 = c.run("ring4_inrush", {"ss": 0.025, "ssdis": 0}, tag="ss25", test="R4")
    c.values["inrush.ils_peak_ss50"] = r50.get("inrush.ils_abs")
    c.values["inrush.ils_peak_ss25"] = r25.get("inrush.ils_abs")
    c.values["inrush.ibuck2_peak_ss50"] = r50.get("inrush.ibuck2_peak")
    c.values["inrush.v30_min_ss50"] = r50.get("inrush.v30_min")
    c.values["inrush.vsd_final_ss50"] = r50.get("inrush.vsd_final")
    c.values["inrush.t90_ss50"] = r50.get("inrush.t90")
    c.values["inrush.t90_ss25"] = r25.get("inrush.t90")
    # decision 24: C60 2.2 uF (3.4 uF total), deck made from the same files with one value replaced
    def variant(tag, c60):
        r_ = cl.Design(c.ring.folder, dict(c.ring.overrides, C60=c60))
        dk = md.deck_inrush(r_)
        os.makedirs(os.path.join(c.decks, "variants"), exist_ok=True)
        p = os.path.join(c.decks, "variants", "ring4_inrush_%s.cir" % tag)
        open(p, "w").write(dk.text())
        res, err = bench.run_deck(p, {"ss": 0.05, "ssdis": 0}, tag=tag, workdir=c.work)
        if err:
            c.errors.setdefault("R4", []).append("variant %s: %s" % (tag, err[0][:160]))
            return {}
        return res
    res = variant("d24", "2.2uF")
    c.values["inrush.ils_peak_ss50_d24"] = res.get("inrush.ils_abs")
    old = variant("old47", "4.7uF")
    c.note("ring4 info: C60 in parts.csv now reads %s; with C60 2.2 uF (3.4 uF total on VDD_SD) the soft start ends in %.3f ms; with the earlier 4.7 uF (5.9 uF total) %.3f ms" % (
        c.ring.parts["C60"]["value"], 1000 * res.get("inrush.t90", float("nan")), 1000 * old.get("inrush.t90", float("nan"))))
    rn = c.run("ring4_inrush", {"ss": 0.05, "ssdis": 1}, tag="ssoff", test="R4")
    c.note("ring4 info (what-if, soft start disabled in the chip): peak current into VDD_SD %.2f A, VDD_3V0 minimum %.3f V" % (rn.get("inrush.ils_abs", float("nan")), rn.get("inrush.v30_min", float("nan"))))
    tot = sum(cl.parse_value(c.ring.parts[x]["value"]) for x in ("C60", "C61", "C82", "C87"))
    c.note("ring4 info: capacitors on VDD_SD read from parts.csv: C60 %s, C61 %s, C82 %s, C87 %s, total %.2f uF" % (
        c.ring.parts["C60"]["value"], c.ring.parts["C61"]["value"], c.ring.parts["C82"]["value"], c.ring.parts["C87"]["value"], tot * 1e6))


def t_ring5(c):
    res = c.run("ring5_shifter", {}, tag="base", test="R5")
    for k, v in res.items():
        c.values[k] = v


def t_ring6(c):
    pm, rmn, imx, imn = [], [], [], []
    for rpu in ("5k", "13k", "100k"):
        res = c.run("ring6_joystick", {"rpu": rpu}, tag="rpu_" + rpu, test="R6")
        pm.append(res.get("joy.pressed_max"))
        rmn.append(res.get("joy.released_min"))
        imx.append(res.get("joy.pressed_current_max"))
        imn.append(res.get("joy.pressed_current_min"))
    c.values["joy.pressed_max"] = merge_max(pm)
    c.values["joy.released_min"] = merge_min(rmn)
    c.values["joy.pressed_current_max"] = merge_max(imx)
    c.values["joy.pressed_current_min"] = merge_min(imn)


def t_ring7(c):
    vb, dp, dn, vd, vdn = [], [], [], [], []
    for ocv in (3.3, 3.8, 4.35):
        res = c.run("ring7_pads", {"ocv": ocv}, tag="ocv_%g" % ocv, test="R7")
        vb.append(res.get("pads.v_vbus"))
        dp.append(res.get("pads.v_dp"))
        dn.append(res.get("pads.v_dn"))
        vd.append(res.get("pads.vbus_dp"))
        c.note("ring7 info: cell %.2f V: VBUS pad before removal %.3f V, 1 s after %.3f V, 10 s after %.3f V" % (
            ocv, res.get("pads.v_vbus_early", float("nan")), res.get("pads.v_vbus_1s", float("nan")), res.get("pads.v_vbus", float("nan"))))
    c.values["pads.vbus_gnd_10s"] = merge_max(vb)
    c.values["pads.dp_gnd_10s"] = merge_max(dp)
    c.values["pads.dn_gnd_10s"] = merge_max(dn)
    c.values["pads.vbus_dp_10s"] = merge_max(vd)
    c.values["pads.vbus_gnd_10s_hist"] = merge_max(vb)
    # what-if only, never a pass line: a bleeder from VBUS to ground
    for rb in (1e6, 440e3, 330e3):
        res = c.run("ring7_pads", {"ocv": 3.8, "rbleed": rb}, tag="bleed_%d" % rb, test="R7")
        c.note("ring7 what-if (not in the design): a %.0f kohm bleeder from VBUS to GND gives %.4f V on the VBUS pad 10 s after removal (cell 3.8 V)" % (rb / 1000, res.get("pads.v_vbus", float("nan"))))


def t_ring8(c):
    for mm in (2, 5):
        res = c.run("ring8_mic", {"lmm": mm}, tag="%dmm" % mm, test="R8")
        c.values["mic.ripple_%dmm" % mm] = res.get("mic.pp")
        c.note("ring8 info: track %d mm: ripple at the Vdd pin %.2f mV peak to peak (limit 10 mV, the lead's; the microphone sheet gives none)" % (mm, 1000 * res.get("mic.pp", float("nan"))))


RING_TESTS = [("R1", t_ring1), ("R2", t_ring2), ("R3", t_ring3), ("R4", t_ring4), ("R5", t_ring5), ("R6", t_ring6), ("R7", t_ring7), ("R8", t_ring8)]


def case_tests():
    try:
        import case_tests as ct
        return ct.CASE_TESTS
    except ImportError:
        return []


# ------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ring-dir", default=cl.RING_DIR)
    ap.add_argument("--case-dir", default=cl.CASE_DIR)
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--only", default="")
    ap.add_argument("--pass-lines", default=os.path.join(HERE, "pass-lines.md"))
    ap.add_argument("--set", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ov = dict(s.split("=", 1) for s in a.set)
    ring0 = cl.Design(a.ring_dir)
    ring = cl.Design(a.ring_dir, {k: v for k, v in ov.items() if k in ring0.parts})
    case0 = cl.Design(a.case_dir)
    case = cl.Design(a.case_dir, {k: v for k, v in ov.items() if k in case0.parts and k not in ring0.parts})
    rows = read_pass_lines(a.pass_lines)
    c = Ctx(ring, case, a.out, rows)
    t0 = time.time()
    import hashlib
    with open(os.path.join(a.out, "inputs.txt"), "w") as f:
        for fol in (a.ring_dir, a.case_dir):
            for nm in ("netlist.csv", "parts.csv"):
                pth = os.path.join(fol, nm)
                f.write("%s  %d bytes  mtime %s  sha256 %s\n" % (pth, os.path.getsize(pth), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(pth))), hashlib.sha256(open(pth, "rb").read()).hexdigest()))
        f.write("pass-lines.md  sha256 %s\n" % hashlib.sha256(open(a.pass_lines, "rb").read()).hexdigest())
        f.write("overrides: %s\n" % (ov or "none"))
    manifest = md.build_all(ring, case, c.decks)
    print("decks: %d written to %s from %s and %s" % (len(manifest), c.decks, a.ring_dir, a.case_dir))
    only = set(x for x in a.only.split(",") if x)
    tests = RING_TESTS + case_tests()
    summary = []
    allrows = []
    for tid, fn in tests:
        if only and tid not in only:
            continue
        before = set(c.values)
        try:
            fn(c)
        except Exception as e:  # a crash is a FAIL with its own reason, never a pass
            c.errors.setdefault(tid, []).append("test script crashed: %r" % (e,))
        sel = [r for r in rows if r["id"].startswith(tid + ".")]
        ev = evaluate(sel, c.values)
        allrows += ev
        bad = [e for e in ev if not e["ok"]]
        ok = not bad and bool(ev)
        if bad:
            parts = []
            for e in bad:
                parts.append("%s: %s = %s needs %s %s %s" % (e["id"], e["qty"], "no value" if e["value"] is None else ("%.6g" % e["value"]), e["op"], e["limit_text"], e["unit"]))
            detail = "; ".join(parts)
        else:
            tight = min(ev, key=lambda e: abs(e["value"] - e["limit"]) / (abs(e["limit"]) + 1e-12)) if ev else None
            detail = "tightest row %s: %s = %.6g %s %s %s" % (tight["id"], tight["qty"], tight["value"], "holds" if True else "", tight["op"], tight["limit_text"]) if tight else "no rows"
        line = "%s %s: %d of %d rows hold; %s" % ("PASS" if ok else "FAIL", TEST_NAMES.get(tid, tid), len(ev) - len(bad), len(ev), detail)
        print(line)
        summary.append((tid, ok, line))
        for err in c.errors.get(tid, [])[:3]:
            print("    note: " + err[:200])
    # files
    with open(os.path.join(a.out, "rows.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "qty", "op", "limit", "unit", "value", "ok", "why", "source", "kind"])
        for e in allrows:
            w.writerow([e["id"], e["qty"], e["op"], e["limit_text"], e["unit"], "" if e["value"] is None else "%.9g" % e["value"], "PASS" if e["ok"] else "FAIL", e["why"], e["source"], kind_of(e["source"])])
    with open(os.path.join(a.out, "values.json"), "w") as f:
        json.dump({k: v for k, v in sorted(c.values.items())}, f, indent=1)
    with open(os.path.join(a.out, "info.txt"), "w") as f:
        f.write("\n".join(c.info) + "\n")
    with open(os.path.join(a.out, "deck_parts.json"), "w") as f:
        json.dump({k: {"included": v["included"], "excluded": v["excluded"]} for k, v in manifest.items()}, f, indent=1)
    for line in c.info:
        print("  " + line)
    nfail = sum(1 for _, ok, _ in summary if not ok)
    print("tests: %d, pass: %d, fail: %d, seconds: %.0f" % (len(summary), len(summary) - nfail, nfail, time.time() - t0))
    final = "RESULT FAIL" if nfail or not summary else "RESULT PASS"
    print(final)
    with open(os.path.join(a.out, "summary.txt"), "w") as f:
        f.write("\n".join(l for _, _, l in summary) + "\n" + final + "\n")
    sys.exit(1 if final.endswith("FAIL") else 0)


if __name__ == "__main__":
    main()
