#!/usr/bin/env python3
"""Sensitivity runs behind the findings (information only, no pass lines).
Output: results/sensitivity.txt.  Run: python sensitivity.py
1. ring1 at R_SPEC: cell minimum with C84 (the capacitor on the motor rail) at three values, and the numerical convergence of the minimum.
2. case4: green and blue LED current with the typical forward voltage at 20 mA moved down in steps (the sheet gives no minimum).
"""
import os
import re

import bench
import case_decks
import circuit_lib as cl
import make_decks as md

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results", "sensitivity.txt")
W = os.path.join(HERE, "work", "sens")
os.makedirs(W, exist_ok=True)
lines = []
rspec = (3.45 - 3.0) / 0.230

ring0 = cl.Design(cl.RING_DIR)
lines.append("ring1 at R_SPEC = %.4f ohm, cell open-circuit 3.45 V: cell minimum during the motor start (limit 3.0 V)" % rspec)
for c84 in (ring0.parts["C84"]["value"], "4.7uF", "3.3uF", "2.0uF"):
    ring = cl.Design(cl.RING_DIR, {"C84": c84})
    dk = md.deck_motor(ring)
    p = os.path.join(W, "ring1_c84_%s.cir" % c84)
    open(p, "w").write(dk.text())
    res, err = bench.run_deck(p, {"ocv": 3.45, "rcell": rspec}, tag="c84_%s" % c84, workdir=W)
    lines.append("  C84 = %-6s (parts.csv value %s): cell minimum %.4f V, settled before the end of the start %.4f V, cell peak current %.1f mA%s" % (
        c84, ring0.parts["C84"]["value"], res.get("motor.vbat_min", float("nan")), res.get("motor.vbat_settled", float("nan")), -1000 * res.get("motor.icell_pk", float("nan")), (" ERR " + err[0][:80]) if err else ""))
# numerical convergence of the minimum: same deck, different maximum time step and tolerance
dk = md.deck_motor(ring0)
base = dk.text()
lines.append("ring1 numerical check at R_SPEC (cell minimum in V for a few solver settings):")
for opt, tmax in ((".options reltol=1e-3", "5u"), (".options reltol=1e-4", "5u"), (".options reltol=1e-4", "2u"), (".options reltol=1e-4 abstol=1e-12 vntol=1e-7", "1u"), (".options reltol=1e-3", "20u")):
    t = re.sub(r"^\.options reltol=.*$", opt, base, flags=re.M)
    t = re.sub(r"^\.tran 1u (\S+) 0 \S+ uic", lambda m: ".tran 1u %s 0 %s uic" % (m.group(1), tmax), t, flags=re.M)
    p = os.path.join(W, "ring1_num.cir")
    open(p, "w").write(t)
    res, err = bench.run_deck(p, {"ocv": 3.45, "rcell": rspec}, tag="num_%s_%s" % (opt.split("=")[1].split()[0], tmax), workdir=W)
    lines.append("  %-50s tmax %-4s cell minimum %.5f V%s" % (opt, tmax, res.get("motor.vbat_min", float("nan")), (" ERR " + err[0][:60]) if err else ""))

case = cl.Design(cl.CASE_DIR)
lines.append("case4 green and blue LED current (mA) for the typical Vf at 20 mA moved down from the sheet value 3.3 V (best ideality n over 2, 3, 4); limit 2 mA")
for vf in (3.3, 3.2, 3.1, 3.0, 2.9):
    case_decks.LED_VF20["G"] = vf
    case_decks.LED_VF20["B"] = vf
    dk = case_decks.deck_led(case)
    p = os.path.join(W, "case4_led.cir")
    open(p, "w").write(dk.text())
    best = []
    for n in (2.0, 3.0, 4.0):
        res, err = bench.run_deck(p, {"n": n}, tag="vf%g_n%g" % (vf, n), workdir=W)
        best.append(res.get("led.green", float("nan")))
    lines.append("  Vf at 20 mA = %.1f V: green %.2f mA (n = 2), %.2f mA (n = 3), %.2f mA (n = 4)" % (vf, 1000 * best[0], 1000 * best[1], 1000 * best[2]))
open(OUT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
