import sys, json, numpy as np
sys.path.insert(0, "/work/src")
import ringsim_lib as L
out = {}
# ---- C1: known-pass and known-fail curves for the H1 scorer
f = np.arange(2.0e9, 3.0e9 + 1, 5e6)
def curve(dips):  # dips: list of (f0, depth_db, width)
    rl = np.zeros_like(f)
    for f0, d, wdt in dips: rl = np.maximum(rl, d * np.exp(-((f - f0) / wdt) ** 2))
    return 10 ** (-(rl + 0.3) / 20)   # complex not needed: magnitude only
# known pass: through the maker's three markers (13.935 at 2.40, 24.894 at 2.45, 14.774 at 2.50); piecewise through them
fm = np.array([2.0e9, 2.4e9, 2.45e9, 2.5e9, 3.0e9]); rlm = np.array([1.0, 13.935, 24.894, 14.774, 1.0])
s_pass = 10 ** (-np.interp(f, fm, rlm) / 20)
r_pass = L.score_h1(f, s_pass, 0.72, 1.5)
# known fail: a notch only 3 dB deep at 2.45, efficiency 30 percent
s_fail = 10 ** (-(0.5 + 2.5 * np.exp(-((f - 2.45e9) / 40e6) ** 2)) / 20)
r_fail = L.score_h1(f, s_fail, 0.30, 1.5)
out["C1_known_pass"] = r_pass; out["C1_known_fail"] = r_fail
assert r_pass["H1_all"] is True, r_pass
assert r_fail["H1_all"] is False and not r_fail["P1"] and not r_fail["P3"], r_fail
# ---- C2: match solver against an independent ABCD calculation, known-solvable and known-unsolvable loads
band = np.arange(2.40e9, 2.48e9 + 1, 1e6)
z_easy = 12.0 + 8j + 0 * band                      # flat 12 + j8 ohm: a perfect narrow match exists
m1 = L.match_solve(band, z_easy, seed=1, starts=40)
g_abcd = L.pi_s11_abcd(m1["pattern"], m1["values"], band, z_easy)
out["C2_easy"] = dict(m1, abcd_worst_db=float(20 * np.log10(np.max(np.abs(g_abcd)))))
assert abs(out["C2_easy"]["abcd_worst_db"] - m1["worst_s11_db"]) < 0.05, out["C2_easy"]
assert m1["worst_s11_db"] < -20, m1
w = 2 * np.pi * band; z_hard = 1.0 + 1j * (w * 10e-9 - 1 / (w * 2 * np.pi * 2.44e9 * 10e-9 * 2 * np.pi * 2.44e9 * 0 + 1e-30)) if False else None
Lh, Ch = 10e-9, 1.0 / ((2 * np.pi * 2.44e9) ** 2 * 10e-9)
z_hard = 1.0 + 1j * (w * Lh - 1 / (w * Ch))        # series R-L-C, R = 1 ohm, Q about 150: 80 MHz band cannot be matched to -6 dB
m2 = L.match_solve(band, z_hard, seed=2, starts=40)
g2 = L.pi_s11_abcd(m2["pattern"], m2["values"], band, z_hard)
out["C2_hard"] = dict(m2, abcd_worst_db=float(20 * np.log10(np.max(np.abs(g2)))))
assert abs(out["C2_hard"]["abcd_worst_db"] - m2["worst_s11_db"]) < 0.05, out["C2_hard"]
assert m2["worst_s11_db"] > -6, m2
# ---- H2 case rule: pass and fail examples
ok = L.case_verdict(np.full(81, 8.0), {"2.40": .3, "2.44": .3, "2.48": .3})
bad = L.case_verdict(np.r_[np.full(80, 8.0), 5.0], {"2.40": .3, "2.44": .3, "2.48": .3})
bad2 = L.case_verdict(np.full(81, 8.0), {"2.40": .3, "2.44": .05, "2.48": .3})
assert ok["pass_"] and not bad["pass_"] and not bad2["pass_"]
out["case_rule"] = dict(ok=ok, bad_rl=bad, bad_eff=bad2)
json.dump(out, open("/work/results/test_scorer.json", "w"), indent=1, default=float)
print("test_scorer: C1 and C2 and case rule all as expected")
print(json.dumps({k: (v if k.startswith("C2") else None) for k, v in out.items() if k.startswith("C2")}, default=float)[:600])
