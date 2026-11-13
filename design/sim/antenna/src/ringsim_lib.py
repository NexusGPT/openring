"""Shared scoring and matching code for the antenna simulation (pure numpy/scipy, no openEMS needed)."""
import numpy as np
from scipy.optimize import minimize

Z0 = 50.0

def rl_db(s11):
    """return loss in dB (positive number) from complex S11"""
    return -20.0 * np.log10(np.maximum(np.abs(s11), 1e-12))

def gamma(zin, z0=Z0):
    return (zin - z0) / (zin + z0)

# ---------------------------------------------------------------- H1 scoring (pass line of antenna-sim.md section 0.2)
H1_LINE = dict(
    P1_rl_244_min_db=10.0,       # P1: RL at 2.44 GHz >= 10 dB
    P2_rl_240_min_db=6.0,        # P2: RL at 2.40 and 2.50 GHz >= 6 dB each
    P2_rl_250_min_db=6.0,
    P3_eff_min=0.52, P3_eff_max=0.92,   # P3: efficiency 52..92 percent at 2.44 GHz
    P4_gain_min_dbi=-1.0, P4_gain_max_dbi=4.0,  # P4: peak gain -1.0..+4.0 dBi at 2.44 GHz
    f_res_lo=2.440e9, f_res_hi=2.460e9,  # tuning window for the S11 minimum
)

def f_res(freq, s11):
    """frequency of the S11 minimum inside the given array (2.0 to 3.0 GHz)"""
    i = int(np.argmin(np.abs(s11)))
    return float(freq[i])

def interp_rl(freq, s11, f):
    """return loss at frequency f by linear interpolation of |S11| in dB"""
    return float(np.interp(f, freq, rl_db(s11)))

def score_h1(freq, s11, eff244, gain244_dbi, line=H1_LINE):
    out = {}
    out["f_res_Hz"] = f_res(freq, s11)
    out["f_res_in_window"] = bool(line["f_res_lo"] <= out["f_res_Hz"] <= line["f_res_hi"])
    out["rl_2.40_db"] = interp_rl(freq, s11, 2.40e9)
    out["rl_2.44_db"] = interp_rl(freq, s11, 2.44e9)
    out["rl_2.50_db"] = interp_rl(freq, s11, 2.50e9)
    out["eff_2.44"] = float(eff244)
    out["gain_2.44_dbi"] = float(gain244_dbi)
    out["P1"] = bool(out["rl_2.44_db"] >= line["P1_rl_244_min_db"])
    out["P2"] = bool(out["rl_2.40_db"] >= line["P2_rl_240_min_db"] and out["rl_2.50_db"] >= line["P2_rl_250_min_db"])
    out["P3"] = bool(line["P3_eff_min"] <= eff244 <= line["P3_eff_max"])
    out["P4"] = bool(line["P4_gain_min_dbi"] <= gain244_dbi <= line["P4_gain_max_dbi"])
    out["H1_all"] = bool(out["f_res_in_window"] and out["P1"] and out["P2"] and out["P3"] and out["P4"])
    return out

# ---------------------------------------------------------------- matching network: shunt, series, shunt (source side first)
def _z_elem(kind, val, w):
    """impedance of an ideal L (henry) or C (farad)"""
    return 1j * w * val if kind == "L" else 1.0 / (1j * w * val)

def pi_zin(pattern, vals, f, zant):
    """pattern like 'CLC' = (shunt at source side, series, shunt at antenna side); returns Zin seen from the source"""
    w = 2 * np.pi * np.asarray(f)
    z3 = _z_elem(pattern[2], vals[2], w)       # shunt at the antenna side
    za = 1.0 / (1.0 / zant + 1.0 / z3)
    z2 = _z_elem(pattern[1], vals[1], w)       # series
    zb = za + z2
    z1 = _z_elem(pattern[0], vals[0], w)       # shunt at the source side
    return 1.0 / (1.0 / zb + 1.0 / z1)

def pi_s11_abcd(pattern, vals, f, zant):
    """independent check: cascade of ABCD matrices (shunt Y, series Z, shunt Y) terminated in zant, S11 against 50 ohm"""
    f = np.atleast_1d(f); zant = np.broadcast_to(zant, f.shape)
    res = []
    for fi, za in zip(f, zant):
        w = 2 * np.pi * fi
        def sh(k, v): y = 1.0 / _z_elem(k, v, w); return np.array([[1, 0], [y, 1]], dtype=complex)
        def se(k, v): z = _z_elem(k, v, w); return np.array([[1, z], [0, 1]], dtype=complex)
        M = sh(pattern[0], vals[0]) @ se(pattern[1], vals[1]) @ sh(pattern[2], vals[2])
        A, Bm, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
        zin = (A * za + Bm) / (C * za + D)
        res.append((zin - Z0) / (zin + Z0))
    return np.array(res)

L_RANGE = (0.2e-9, 20e-9)
C_RANGE = (0.1e-12, 10e-12)

def _bounds(kind):
    return L_RANGE if kind == "L" else C_RANGE

def match_solve(f, zant, seed=12345, starts=120):
    """minimax search over the 8 L/C patterns; returns best dict. f in Hz, zant complex array on f."""
    rng = np.random.default_rng(seed)
    best = None
    for pat in [a + b + c for a in "LC" for b in "LC" for c in "LC"]:
        lo = np.log([_bounds(k)[0] for k in pat]); hi = np.log([_bounds(k)[1] for k in pat])
        def obj(x):
            x = np.clip(x, lo, hi)
            g = np.abs(gamma(pi_zin(pat, np.exp(x), f, zant)))
            return np.max(g) + 1e-4 * np.mean(g)
        pbest = None
        for _ in range(starts):
            x0 = lo + rng.random(3) * (hi - lo)
            r = minimize(obj, x0, method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-6, maxiter=800))
            if pbest is None or r.fun < pbest[0]:
                pbest = (r.fun, np.clip(r.x, lo, hi))
        vals = np.exp(pbest[1])
        g = np.abs(gamma(pi_zin(pat, vals, f, zant)))
        cand = dict(pattern=pat, values=[float(v) for v in vals], worst_s11_db=float(20 * np.log10(np.max(g))))
        if best is None or cand["worst_s11_db"] < best["worst_s11_db"]:
            best = cand
        best.setdefault("all", {})[pat] = cand["worst_s11_db"]
    return best

def snap(kind, val):
    """nearest 0.1 pF (C) or 0.1 nH (L) value, never below 0.1"""
    step = 0.1e-12 if kind == "C" else 0.1e-9
    return max(step, round(val / step) * step)

def case_verdict(rl_after_db_band, eff_by_f, rl_min=6.0, eff_min=0.10):
    """H2 rule of section 0.5: every point of the 81-point band >= 6 dB and efficiency >= 10 percent at 2.40, 2.44, 2.48"""
    rl_ok = bool(np.min(rl_after_db_band) >= rl_min)
    eff_ok = bool(all(eff_by_f[k] >= eff_min for k in ("2.40", "2.44", "2.48")))
    return dict(rl_ok=rl_ok, eff_ok=eff_ok, pass_=bool(rl_ok and eff_ok), worst_rl_db=float(np.min(rl_after_db_band)))
