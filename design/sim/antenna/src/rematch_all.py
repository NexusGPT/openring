"""Post-processing (no solver run): re-solves the three-part match for every one of the 8 L/C topologies from results/h2_*_zin.csv,
because ringsim_lib.match_solve loses the 'all' entries of the patterns that come before the winning one (a reporting defect found at the final audit;
the winner itself is chosen correctly). Uses the same search as the run (same seed, 60 starts) and writes results/h2_rematch_all.json."""
import sys, json, csv, numpy as np
sys.path.insert(0, "/work/src")
import ringsim_lib as L
from scipy.optimize import minimize
out = {}
for tag in ("h2_A", "h2_B"):
    rows = list(csv.DictReader(open("/work/results/%s_zin.csv" % tag)))
    f = np.array([float(r["f_GHz"]) for r in rows]) * 1e9
    z = np.array([float(r["Re_Zin"]) + 1j * float(r["Im_Zin"]) for r in rows])
    sel = (f >= 2.40e9 - 1) & (f <= 2.48e9 + 1)
    # keep exactly the 1 MHz grid points
    keep = np.isclose((f[sel] / 1e6) % 1, 0, atol=1e-6) | np.isclose((f[sel] / 1e6) % 1, 1, atol=1e-6)
    fb, zb = f[sel][keep], z[sel][keep]
    rng = np.random.default_rng(20261113); res = {}
    for pat in [a + b + c for a in "LC" for b in "LC" for c in "LC"]:
        lo = np.log([L._bounds(k)[0] for k in pat]); hi = np.log([L._bounds(k)[1] for k in pat])
        def obj(x):
            x = np.clip(x, lo, hi); g = np.abs(L.gamma(L.pi_zin(pat, np.exp(x), fb, zb))); return np.max(g) + 1e-4 * np.mean(g)
        pb = None
        for _ in range(60):
            x0 = lo + rng.random(3) * (hi - lo)
            r = minimize(obj, x0, method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-6, maxiter=800))
            if pb is None or r.fun < pb[0]: pb = (r.fun, np.clip(r.x, lo, hi))
        v = np.exp(pb[1]); g = np.abs(L.gamma(L.pi_zin(pat, v, fb, zb)))
        res[pat] = dict(worst_s11_db=float(20 * np.log10(g.max())), values_SI=[float(a) for a in v])
    out[tag] = dict(n_points=int(len(fb)), f_first_GHz=float(fb[0] / 1e9), f_last_GHz=float(fb[-1] / 1e9), patterns=res,
                    best=min(res, key=lambda k: res[k]["worst_s11_db"]))
json.dump(out, open("/work/results/h2_rematch_all.json", "w"), indent=1)
for t, o in out.items(): print(t, o["n_points"], o["best"], {k: round(v["worst_s11_db"], 2) for k, v in o["patterns"].items()})
