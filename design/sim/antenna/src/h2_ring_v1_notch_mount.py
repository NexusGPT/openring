"""H2: the ring (simplified) with the chip antenna. usage: h2_ring.py <tag> <case> <eps_r_ceramic>
case: A as designed (antenna at the hand-end thumb-side corner, metal body), B resin corner (body inside X -14.8..-10.6, Y 2.05..the skin is resin),
      C antenna at the fingertip end (X mirror of A), D control: board with antenna alone in free air (no body, no finger).
Inside-model axes: X along the finger, Y across (+Y thumb), Z up. All lengths mm. See antenna-sim.md section 2 for every simplification."""
import os, sys, json, time, datetime
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import EPS0
import chipant, ringsim_lib as RL

tag, case, EPS_R = sys.argv[1], sys.argv[2], float(sys.argv[3])
Sim_Path = os.path.join("/work/runs", tag); os.makedirs(Sim_Path, exist_ok=True); os.makedirs("/work/results", exist_ok=True)
NRTS = int(os.environ.get("NRTS", "220000")); THREADS = int(os.environ.get("THREADS", "16"))
F0, FC = 2.5e9, 0.6e9
NF_FREQ = [2.40e9, 2.42e9, 2.44e9, 2.46e9, 2.48e9]
MIR = (case == "C")            # antenna side at +X
def X(x): return -x if MIR else x
def K(sig, eps, f=2.45e9): return sig            # conductivity given directly (S/m)
def kap(eps, tand, f=2.45e9): return 2 * np.pi * f * EPS0 * eps * tand

# ---------------------------------------------------------------- materials (antenna-sim.md section 0.6)
FDTD = openEMS(NrTS=NRTS, EndCriteria=1e-5); FDTD.SetGaussExcite(F0, FC); FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX); mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)
M = {}
M["body"] = CSX.AddMetal("body_ti")
M["air"] = CSX.AddMaterial("air_cavity", epsilon=1.0)
M["board"] = CSX.AddMaterial("board_fr4", epsilon=4.3, kappa=kap(4.3, 0.02))
M["tab"] = CSX.AddMaterial("tab_polyimide", epsilon=3.4, kappa=kap(3.4, 0.02))
M["panel"] = CSX.AddMaterial("panel_glass", epsilon=6.5, kappa=kap(6.5, 0.01))
M["adh"] = CSX.AddMaterial("adhesive", epsilon=3.0, kappa=kap(3.0, 0.02))
M["glass"] = CSX.AddMaterial("cover_glass", epsilon=6.5, kappa=kap(6.5, 0.01))
M["resin"] = CSX.AddMaterial("resin", epsilon=3.0, kappa=kap(3.0, 0.02))
M["skin"] = CSX.AddMaterial("skin", epsilon=38.0, kappa=1.46)
M["muscle"] = CSX.AddMaterial("muscle", epsilon=52.73, kappa=1.74)
M["gnd"] = CSX.AddMetal("board_ground"); M["cu"] = CSX.AddMetal("tab_copper")

def bx(prop, a, b, prio):
    a = np.array(a, float); b = np.array(b, float); prop.AddBox(np.minimum(a, b), np.maximum(a, b), priority=prio)

def rrect(x0, x1, y0, y1, r, n=10):
    pts = []
    for (cx, cy, a0) in [(x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)]:
        for k in range(n + 1):
            a = np.radians(a0 + 90.0 * k / n); pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return pts

def clip(poly, keep):            # Sutherland-Hodgman, keep(p) -> signed distance >= 0 inside, linear
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        dp, dq = keep(p), keep(q)
        if dp >= 0: out.append(p)
        if (dp >= 0) != (dq >= 0):
            t = dp / (dp - dq); out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out

def poly(prop, pts, z0, z1, prio):
    arr = np.array(pts).T
    prop.AddLinPoly(arr.tolist(), "z", z0, z1 - z0, priority=prio)

# ---------------------------------------------------------------- geometry numbers (design files; see antenna-sim.md 2.1)
ZF0, ZF1 = 0.0, 0.4                 # floor
ZB0, ZBG, ZB1 = 1.5, 1.6, 1.8        # board bottom, board ground sheet, board top
ZA0, ZA1 = 0.5, 1.7                  # antenna body (terminal face up at 1.7)
ZP0, ZP1 = 1.9, 2.7                  # panel
ZAD1 = 2.8                           # adhesive top = body top = glass seat
ZG1 = 3.5                            # glass top (0.7 thick; the model has 0.57 to 0.94 over the antenna)
BX, BY = 14.7, 7.4                   # outer half sizes (design 14.65 and 7.375, snapped to the 0.1 mm grid)
IX, IY = 13.7, 6.5                   # inner half sizes (design 13.725 and 6.45, snapped)
R_IN = 18.9452 / 2; ZC = -0.4 - R_IN; R_LINER = R_IN + 0.3; R_OUT = R_IN + 2.6
FING = (-30.0, 60.0)
FREE = (case == "D")

# ---------------------------------------------------------------- body, band, finger
if not FREE:
    outer = rrect(-BX, BX, -BY, BY, 2.5); inner = rrect(-IX, IX, -IY, IY, 1.6)
    poly(M["body"], outer, ZF0, ZAD1, 10)
    M["band"] = M["body"]
    M["body"].AddCylinder([-4, 0, ZC], [4, 0, ZC], R_OUT, priority=10) if False else None
    cyl_axis_start, cyl_axis_stop = [-4.0, 0.0, ZC], [4.0, 0.0, ZC]
    M["body"].AddCylinder(cyl_axis_start, cyl_axis_stop, R_OUT, priority=10)
    liner = CSX.AddMaterial("liner_resin", epsilon=3.0, kappa=kap(3.0, 0.02))
    liner.AddCylinder(cyl_axis_start, cyl_axis_stop, R_LINER, priority=11)
    M["skin"].AddCylinder([FING[0], 0.0, ZC], [FING[1], 0.0, ZC], R_IN, priority=12)
    M["muscle"].AddCylinder([FING[0], 0.0, ZC], [FING[1], 0.0, ZC], R_IN - 1.5, priority=13)
    poly(M["air"], inner, ZF1, ZAD1, 20)
    if case == "B":
        corner = clip(outer, lambda p: -10.6 - p[0])          # X <= -10.6
        corner = clip(corner, lambda p: p[1] - 2.05)          # Y >= 2.05
        poly(M["resin"], corner, ZF0, ZAD1, 19)
        # the part of the corner above the cavity floor is cavity too: resin fills it; board and antenna drawn after at higher priority

# ---------------------------------------------------------------- board, ground, tab, screen stack
bx(M["board"], (-13.6, -6.3, ZB0), (13.6, 6.3, ZB1), 22) if False else None
bxx = [(-13.6, 13.6)]
bx(M["board"], (-13.6, -6.3, ZB0), (13.6, 6.3, ZB1), 22)
# notch (hand-end thumb-side corner, 1.8 x 3.6) back to air
bx(M["air"], (X(-13.6), 2.7, ZB0), (X(-11.8), 6.3, ZB1), 23)
# tab over the notch (0.1 polyimide at Z 1.7 to 1.8)
bx(M["tab"], (X(-13.6), 2.7, 1.7), (X(-11.8), 6.3, 1.8), 24)
# ground sheet at Z 1.6: board outline minus the keep-out (X -14.8..-10.6, Y 2.0..6.75 on the antenna side)
bx(M["gnd"], (-13.6, -6.3, ZBG), (13.6, 2.0, ZBG), 30)
if not MIR: bx(M["gnd"], (-10.6, 2.0, ZBG), (13.6, 6.3, ZBG), 30)
else:       bx(M["gnd"], (-13.6, 2.0, ZBG), (10.6, 6.3, ZBG), 30)
bx(M["panel"], (-13.7, -6.4, ZP0), (13.7, 6.4, ZP1), 25)
bx(M["adh"], (-13.7, -6.4, ZP1), (13.7, 6.4, ZAD1), 25)
poly(M["glass"], rrect(-14.7, 14.7, -7.2, 7.2, 2.5), ZAD1, ZG1, 25)

# ---------------------------------------------------------------- antenna with its tab wiring
fr = chipant.Frame((X(-12.7), 4.4, ZA1), (0, 1, 0), (-1 if MIR else 1, 0, 0), (0, 0, -1))
ant_m, ant_c = chipant.add_antenna(CSX, fr, EPS_R, 0.005, prio_body=26)
# wires on the tab (Z 1.7): feed trace from the feed terminal down to the port, ground frame from the three ground terminals to the board ground
bx(M["cu"], (X(-13.3), 1.9, 1.7), (X(-13.1), 3.1, 1.7), 31)          # feed trace (feed terminal at X -13.5..-13.0, Y 2.8..3.1)
bx(M["cu"], (X(-12.4), 1.9, 1.7), (X(-11.6), 2.0, 1.7), 31)          # ground strip B foot (to the via)
bx(M["cu"], (X(-11.8), 2.0, 1.7), (X(-11.6), 6.3, 1.7), 31)          # ground strip B along Y at X -11.8..-11.6 (touches terminals at X -11.9..-12.4)
bx(M["cu"], (X(-13.5), 6.1, 1.7), (X(-11.6), 6.3, 1.7), 31)          # ground strip A over the +Y end of the antenna
bx(M["cu"], (X(-12.4), 2.8, 1.7), (X(-11.8), 3.1, 1.7), 31)          # lands of the two ground terminals at the -Y end ...
bx(M["cu"], (X(-12.4), 5.7, 1.7), (X(-11.8), 6.1, 1.7), 31)          # ... and +Y end
bx(M["cu"], (X(-13.5), 5.7, 1.7), (X(-13.0), 6.1, 1.7), 31)          # land of the grounded terminal at the +Y end, hand-end side
bx(M["cu"], (X(-11.8), 1.9, ZBG), (X(-11.6), 2.0, 1.7), 31)          # via, strip B to the ground sheet
# port: 50 ohm lumped, vertical, between the trace (Z 1.7) and the ground sheet (Z 1.6) at Y 1.9 to 2.0
port = FDTD.AddLumpedPort(1, 50, [X(-13.3), 1.9, ZBG], [X(-13.1), 2.0, 1.7], "z", 1.0, priority=40, edges2grid="xy") if False else None

# ---------------------------------------------------------------- mesh
def rng(a, b, s): return list(np.round(np.arange(a, b + 1e-9, s), 4))
fx = rng(-16, -9, 0.1) if not MIR else rng(9, 16, 0.1)
fx += rng(-9, 16, 0.2) if not MIR else rng(-16, 9, 0.2)
fx += rng(-30, -16, 1.0) + rng(16, 60, 1.0) if not FREE else rng(-20, 20, 1.0)
if FREE: fx += rng(-16, 16, 0.2)
fy = rng(1.5, 7.9, 0.1) + rng(-8, 1.4, 0.2) + rng(-12.5, -8, 0.5) + rng(7.9, 12.5, 0.5)
fz = rng(-1.0, 4.0, 0.1) + (rng(-20, -1.0, 0.5) if not FREE else [])
for v in (-13.7, 13.7, -14.7, 14.7, -13.6, 13.6, -11.8, 11.8, -10.6, 10.6, -13.3, -13.1, 13.3, 13.1, -11.6, 11.6, -13.5, 13.5, -13.0, 13.0, -12.4, 12.4, -4, 4): fx.append(v)
for v in (-7.4, 7.4, -6.5, 6.5, -6.3, 6.3, -6.4, 6.4, 2.0, 2.7, 6.0, 2.8, 1.9, 3.1, 5.7, 6.1, 7.2, -7.2): fy.append(v)
for v in (0.4, 0.5, 1.5, 1.6, 1.7, 1.8, 1.9, 2.7, 2.8, 3.5): fz.append(v)
MARG = 20.0
fx += [-30 - MARG - 20, 60 + MARG + 20] if not FREE else [-20 - 40, 20 + 40]
fy += [-52, 52]; fz += [-59 if not FREE else -40, 44 if not FREE else 44]
fx, fy, fz = ([float(np.round(v / 0.05) * 0.05) for v in a] for a in (fx, fy, fz))
mesh.AddLine("x", sorted(set(np.round(fx, 4)))); mesh.AddLine("y", sorted(set(np.round(fy, 4)))); mesh.AddLine("z", sorted(set(np.round(fz, 4))))
port = FDTD.AddLumpedPort(1, 50, [X(-13.3), 1.9, ZBG], [X(-13.1), 2.0, 1.7], "z", 1.0, priority=40)
mesh.SmoothMeshLines("x", 2.5, 1.3); mesh.SmoothMeshLines("y", 2.5, 1.3); mesh.SmoothMeshLines("z", 2.5, 1.3)
nx, ny, nz = (len(mesh.GetLines(d)) for d in (0, 1, 2))
for d in (0, 1, 2):
    ln = mesh.GetLines(d); df = np.diff(ln); bad = np.where(df < 0.0999)[0]
    if len(bad): print("SMALL CELLS dir", d, [(float(ln[i]), float(ln[i + 1])) for i in bad[:12]])
assert min(float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)) > 0.0999, "mesh has a cell under 0.1 mm"
def prop_at(pt):
    pr = CSX.GetPropertyByCoordPriority(pt)
    return pr.GetName() if pr is not None else "none"
GEOM_FAILS = []
if os.environ.get("GEOMCHECK") == "1":
    sx = -1.0 if not MIR else 1.0           # antenna side sign
    exp = [  # (point, expected property name), written before the run from the design numbers
        ((0, 0, ZC), "muscle"), ((0, 0, ZC + 8.5), "skin"), ((0, 0, ZC + R_IN + 0.15), "liner_resin"), ((0, 0, 0.1), "body_ti"),
        ((20, 0, ZC), "muscle"), ((0, 7.2, 0.2), "body_ti"), ((-13.3 * sx * -1, 0, 0.2), "body_ti"),
        ((0, 0, 1.0), "air_cavity"), ((0, 0, 1.7), "board_fr4"), ((0, 0, 2.3), "panel_glass"), ((0, 0, 2.75), "adhesive"), ((0, 0, 3.2), "cover_glass"),
        ((-14.2, 0, 1.0), "body_ti"), ((14.2, 0, 1.0), "body_ti"), ((0, 6.9, 1.0), "body_ti"), ((0, -6.9, 1.0), "body_ti"),
        ((X(-12.7), 4.4, 1.0), "ant_ceramic"), ((X(-12.0), 4.4, 1.75), "tab_polyimide"), ((X(-12.7), 4.4, 2.3), "panel_glass"),
        ((X(-12.7), 4.4, 0.45), "air_cavity"), ((X(-13.6), 4.4, 1.0), "air_cavity"),
    ]
    if case == "B":
        exp += [((X(-14.3), 4.4, 1.0), "resin"), ((X(-12.7), 6.8, 1.0), "resin"), ((X(-12.7), 4.4, 0.2), "resin"), ((-9.0, 4.4, 0.2), "body_ti"), ((X(-12.7), 1.5, 0.2), "body_ti")]
    else:
        exp += [((X(-14.3), 4.4, 1.0), "body_ti"), ((X(-12.7), 4.4, 0.2), "body_ti")]
    if case == "D":
        exp = [((X(-12.7), 4.4, 1.0), "ant_ceramic"), ((0, 0, 1.7), "board_fr4"), ((0, 0, 3.2), "cover_glass"), ((0, 0, 1.0), "none"), ((0, 0, ZC), "none")]
    for pt, want in exp:
        got = prop_at(pt)
        print("GEOM", "ok " if got == want else "BAD", pt, "expected", want, "got", got)
        if got != want: GEOM_FAILS.append((pt, want, got))
    print("GEOMCHECK fails:", len(GEOM_FAILS), "of", len(exp))
nf2ff = FDTD.CreateNF2FFBox(frequency=NF_FREQ)
info = dict(tag=tag, case=case, eps_r_ceramic=EPS_R, lines_xyz=[nx, ny, nz], cells=int((nx - 1) * (ny - 1) * (nz - 1)), nrts_cap=NRTS,
            end_criteria=1e-5, threads=THREADS, min_dx=[float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)],
            max_dx=[float(np.max(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)], start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
print(json.dumps(info))
if os.environ.get("SETUP_ONLY") == "1":
    FDTD.Run(Sim_Path, cleanup=True, setup_only=True, verbose=3, debug_material=bool(os.environ.get("DEBUGMAT")))
    json.dump(info, open("/work/results/%s_setup.json" % tag, "w"), indent=1, default=float); print("SETUP_ONLY done"); sys.exit(0)

t0 = time.time()
FDTD.Run(Sim_Path, cleanup=True, numThreads=THREADS, verbose=2)
info["run_seconds"] = time.time() - t0; info["end_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ---------------------------------------------------------------- post-processing
f = np.arange(2.0e9, 3.0e9 + 1, 5e6); fb = np.arange(2.40e9, 2.48e9 + 1, 1e6)
fe = np.union1d(np.union1d(f, fb), np.array(NF_FREQ))
port.CalcPort(Sim_Path, fe, ref_impedance=50)
s11 = port.uf_ref / port.uf_inc; zin = port.uf_tot / port.if_tot; pacc = port.P_acc
np.savetxt("/work/results/%s_zin.csv" % tag, np.c_[fe / 1e9, zin.real, zin.imag, np.abs(s11), 20 * np.log10(np.abs(s11)), pacc],
           delimiter=",", header="f_GHz,Re_Zin,Im_Zin,abs_s11,s11_dB,P_acc_W", comments="")
res = nf2ff.CalcNF2FF(Sim_Path, NF_FREQ, np.arange(0, 181, 3.0), np.arange(0, 360, 6.0), center=[X(-12.7) * 1e-3, 4.4e-3, 1.1e-3], read_cached=False)
eff = {}; dmax = {}
for i, fq in enumerate(NF_FREQ):
    j = int(np.argmin(np.abs(fe - fq))); eff["%.2f" % (fq / 1e9)] = float(res.Prad[i] / pacc[j]); dmax["%.2f" % (fq / 1e9)] = float(res.Dmax[i])
# match solution on the 81-point band
ib = np.array([int(np.argmin(np.abs(fe - q))) for q in fb])
zb = zin[ib]
before = np.abs(RL.gamma(zb)); sol = RL.match_solve(fb, zb, seed=20261113, starts=60)
after = np.abs(RL.gamma(RL.pi_zin(sol["pattern"], sol["values"], fb, zb)))
snapv = [RL.snap(k, v) for k, v in zip(sol["pattern"], sol["values"])]
after_snap = np.abs(RL.gamma(RL.pi_zin(sol["pattern"], snapv, fb, zb)))
abcd = np.abs(RL.pi_s11_abcd(sol["pattern"], sol["values"], fb, zb))
ver = RL.case_verdict(-20 * np.log10(after), {"2.40": eff["2.40"], "2.44": eff["2.44"], "2.48": eff["2.48"]})
info.update(dict(eff_by_ghz=eff, dmax_by_ghz=dmax,
                 s11_before_db_worst=float(20 * np.log10(before.max())), s11_before_db_best=float(20 * np.log10(before.min())),
                 s11_before_db_at={"%.2f" % (q / 1e9): float(20 * np.log10(before[int(np.argmin(abs(fb - q)))])) for q in [2.40e9, 2.44e9, 2.48e9]},
                 zin_at={"%.2f" % (q / 1e9): [float(zb[int(np.argmin(abs(fb - q)))].real), float(zb[int(np.argmin(abs(fb - q)))].imag)] for q in [2.40e9, 2.44e9, 2.48e9]},
                 match=dict(pattern=sol["pattern"], values_SI=sol["values"], snapped_SI=snapv, all_patterns_worst_db=sol["all"]),
                 s11_after_db_worst=float(20 * np.log10(after.max())), s11_after_snapped_db_worst=float(20 * np.log10(after_snap.max())),
                 s11_after_abcd_db_worst=float(20 * np.log10(abcd.max())), verdict=ver))
json.dump(info, open("/work/results/%s.json" % tag, "w"), indent=1, default=float)
print("RESULT", json.dumps({k: info[k] for k in ("case", "eff_by_ghz", "s11_before_db_worst", "s11_after_db_worst", "match", "verdict")}, default=float))
