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
F0, FC = 2.5e9, float(os.environ.get("FC", "1.2e9"))
NF_FREQ = [2.40e9, 2.42e9, 2.44e9, 2.46e9, 2.48e9]
MIR = (case == "C")            # antenna side at +X
def X(x): return -x if MIR else x
def K(sig, eps, f=2.45e9): return sig            # conductivity given directly (S/m)
def kap(eps, tand, f=2.45e9): return 2 * np.pi * f * EPS0 * eps * tand

# ---------------------------------------------------------------- materials (antenna-sim.md section 0.6)
EC = float(os.environ.get("EC", "1e-4"))
FDTD = openEMS(NrTS=NRTS, EndCriteria=EC); FDTD.SetGaussExcite(F0, FC); FDTD.SetBoundaryCond(["PML_8"] * 6)
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
ZB0, ZBG, ZB1 = 1.5, 1.6, 1.8        # board bottom (L1), L2 ground, board top (L4)
ZA0, ZA1 = 0.3, 1.5                  # antenna body (terminal face up at 1.5)
ZP0, ZP1 = 1.9, 2.7                  # panel
ZAD1 = 2.8                           # adhesive top = body top = glass seat
ZG1 = 3.5                            # glass top (0.7 thick; the model has 0.57 to 0.94 over the antenna)
BX, BY = 14.7, 7.4                   # outer half sizes (design 14.65 and 7.375, snapped to the 0.1 mm grid)
IX, IY = 13.7, 6.5                   # inner half sizes (design 13.725 and 6.45, snapped)
R_IN = 18.9452 / 2; ZC = -0.4 - R_IN; R_LINER = R_IN + 0.3; R_OUT = R_IN + 2.6
FING = (-25.0, 45.0)
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
        corner = clip(outer, lambda p: -9.3 - p[0])           # X <= -9.3 (plan R1)
        corner = clip(corner, lambda p: p[1] - 2.1)           # Y >= 2.1 (plan 2.05, snapped)
        poly(M["resin"], corner, ZF0, ZAD1, 19)
        # the part of the corner above the cavity floor is cavity too: resin fills it; board and antenna drawn after at higher priority

# ---------------------------------------------------------------- board (ring-board-plan.md c.2 and e), screen stack
# board: 27.2 x 12.6, Z 1.5 to 1.8 (design 1.45 to 1.75, all of the stack above the floor is raised 0.05 mm to the 0.1 mm grid), no notch
bx(M["board"], (-13.6, -6.3, ZB0), (13.6, 6.3, ZB1), 22)
# ground: L2 at Z 1.6 and L4 at Z 1.8 over the whole outline except the keep-out (antenna side X to -9.5 (design -9.45), Y 3.1 to 6.3)
for zg in (1.6, 1.8):
    bx(M["gnd"], (-13.6, -6.3, zg), (13.6, 3.1, zg), 30)
    if not MIR: bx(M["gnd"], (-9.5, 3.1, zg), (13.6, 6.3, zg), 30)
    else:       bx(M["gnd"], (-13.6, 3.1, zg), (9.5, 6.3, zg), 30)
# stitching: PEC walls (0.1) joining L2 and L4 along the ground edges (stands for the 1 mm pitch via rows of the plan)
def wall(x0, y0, x1, y1): bx(M["gnd"], (x0, y0, 1.6), (x1, y1, 1.8), 30)
wall(-13.6, -6.3, 13.6, -6.2)                                  # -Y edge
if not MIR:
    wall(13.5, -6.3, 13.6, 6.3); wall(-9.5, 6.2, 13.6, 6.3)    # +X end, +Y edge east of the keep-out
    wall(-13.6, -6.3, -13.5, 3.1); wall(-13.6, 3.0, -9.5, 3.1); wall(-9.5, 3.1, -9.4, 6.3)   # -X end, keep-out border
else:
    wall(-13.6, -6.3, -13.5, 6.3); wall(-13.6, 6.2, 9.5, 6.3)
    wall(13.5, -6.3, 13.6, 3.1); wall(9.5, 3.0, 13.6, 3.1); wall(9.4, 3.1, 9.5, 6.3)
bx(M["panel"], (-13.7, -6.4, ZP0), (13.7, 6.4, ZP1), 25)
bx(M["adh"], (-13.7, -6.4, ZP1), (13.7, 6.4, ZAD1), 25)
poly(M["glass"], rrect(-14.7, 14.7, -7.2, 7.2, 2.5), ZAD1, ZG1, 25)

# ---------------------------------------------------------------- floor pocket under the antenna (R2: X -13.3 to -9.7, Y 4.25 to 6.25 -> 4.2 to 6.2, depth 0.2) in metal (A, C) or resin (B)
if not FREE:
    bx(M["air"], (X(-13.3), 4.2, 0.2), (X(-9.7), 6.2, ZF1), 21)

# ---------------------------------------------------------------- antenna on the board's under face (plan e.1 and e.2)
# body X -13.1 to -9.9, Y 4.4 to 6.0 (design Y 4.45 to 6.05, moved 0.05 to the 0.1 mm grid), Z 0.3 to 1.5 (design 0.25 to 1.45); terminal face up at Z 1.5; feed end at +X (pin 1 on the edge row)
fr = chipant.Frame((X(-11.5), 5.2, ZA1), (1 if MIR else -1, 0, 0), (0, -1, 0), (0, 0, -1))
ant_m, ant_c = chipant.add_antenna(CSX, fr, EPS_R, 0.005, prio_body=26)
CU = M["cu"]
# lands 1.0 x 0.6 at Z 1.5 (L1 copper): far end X -13.5 to -12.5, feed end X -10.5 to -9.5; edge row Y 5.6 to 6.2, inner row Y 4.3 to 4.9
for (x0, x1) in ((-13.5, -12.5), (-10.5, -9.5)):
    for (y0, y1) in ((5.6, 6.2), (4.3, 4.9)):
        bx(CU, (X(x0), y0, ZA1), (X(x1), y1, ZA1), 31)
bx(CU, (X(-10.0), 5.8, ZA1), (X(-9.3), 6.0, ZA1), 31)          # feed track from pin 1 (the 50 ohm line, drawn as a 0.2 mm trace) to the port
bx(CU, (X(-9.5), 4.3, ZA1), (X(-9.2), 4.5, ZA1), 31)           # pin 4 (GND): 0.15 mm track east to the ground stack
bx(CU, (X(-9.3), 4.3, ZA1), (X(-9.1), 4.5, 1.8), 31)           # ground stack at (-9.2, 4.4): L1 to L2 to L4
bx(CU, (X(-13.1), 4.3, ZA1), (X(-12.9), 6.2, ZA1), 31)         # far-end lands (pins 2 and 3) joined on L1
bx(CU, (X(-13.1), 3.0, ZA1), (X(-12.9), 4.3, ZA1), 31)         # down to LT1 (0201, fitted as 0 ohm: a short)
bx(CU, (X(-13.5), 2.9, ZA1), (X(-12.9), 3.1, ZA1), 31)         # and to the ground stack at (-13.4, 2.95)
bx(CU, (X(-13.5), 2.9, ZA1), (X(-13.3), 3.1, 1.6), 31)         # stack: L1 to L2 (ground exists at Y below 3.1)
# port: 50 ohm lumped, vertical, 0.1 x 0.2 x 0.1, between the feed track (Z 1.5) and the L2 ground (Z 1.6) at X -9.4 to -9.3 (keep-out edge X -9.5)

# ---------------------------------------------------------------- mesh
def rng(a, b, s): return list(np.round(np.arange(a, b + 1e-9, s), 4))
# lean mesh (amendment A4): 0.1 mm lines only where the antenna and the layers are; coarse elsewhere
if not MIR:
    fx = rng(-16, -14, 0.5) + rng(-14, -9, 0.1) + rng(-9, 16, 0.5)
else:
    fx = rng(-16, 9, 0.5) + rng(9, 14, 0.1) + rng(14, 16, 0.5)
fx += (rng(-25, -16, 2.0) + rng(16, 45, 2.0)) if not FREE else rng(-20, 20, 2.0)
fy = rng(2.0, 6.6, 0.1) + rng(-8, 1.5, 0.5) + rng(6.6, 8.0, 0.5) + rng(-12.5, -8, 1.5) + rng(8, 12.5, 1.5)
fz = rng(0, 3.5, 0.1) + rng(-1, 0, 0.5) + rng(3.5, 5, 0.5) + (rng(-20, -1.0, 1.5) if not FREE else [])
for v in (-13.7, 13.7, -14.7, 14.7, -13.6, 13.6, -4, 4): fx.append(v)
for v in (-7.4, 7.4, -6.5, 6.5, -6.3, 6.3, -6.4, 6.4, 7.2, -7.2): fy.append(v)
for v in (0.2, 0.3, 0.4, 0.5, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.7, 2.8, 3.5): fz.append(v)
for v in (-9.5, -9.4, -9.3, -9.2, -9.1, -9.9, -10.0, -10.2, -10.5, -9.7, -13.1, -12.9, -13.3, -13.5, -12.5, -11.5, -13.6, -13.0, -9.0):
    fx.append(v); fx.append(-v)
for v in (2.1, 2.9, 3.0, 3.1, 4.2, 4.3, 4.5, 4.9, 5.6, 5.8, 6.0, 6.2, 6.3): fy.append(v)
MARG = 12.0
fx += [-25 - MARG - 24, 45 + MARG + 24] if not FREE else [-20 - MARG - 24, 20 + MARG + 24]
fy += [-48, 48]; fz += [-20 - 9.9 + 9.87 - MARG - 24 if not FREE else -40, 3.5 + MARG + 24]
fx, fy, fz = ([float(np.round(v / 0.05) * 0.05) for v in a] for a in (fx, fy, fz))
mesh.AddLine("x", sorted(set(np.round(fx, 4)))); mesh.AddLine("y", sorted(set(np.round(fy, 4)))); mesh.AddLine("z", sorted(set(np.round(fz, 4))))
port = FDTD.AddLumpedPort(1, 50, [X(-9.4), 5.8, 1.5], [X(-9.3), 6.0, 1.6], "z", 1.0, priority=40)
mesh.SmoothMeshLines("x", 3.0, 1.3); mesh.SmoothMeshLines("y", 3.0, 1.3); mesh.SmoothMeshLines("z", 3.0, 1.3)
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
    exp = [  # (point, expected property name), written before the run from the design numbers (plan e, thin.py, placement.csv)
        ((0, 0, ZC), "muscle"), ((0, 0, ZC + 8.5), "skin"), ((0, 0, ZC + R_IN + 0.15), "liner_resin"), ((0, 0, 0.1), "body_ti"),
        ((20, 0, ZC), "muscle"), ((0, 7.2, 0.2), "body_ti"),
        ((0, 0, 1.0), "air_cavity"), ((0, 0, 1.65), "board_fr4"), ((0, 0, 2.3), "panel_glass"), ((0, 0, 2.75), "adhesive"), ((0, 0, 3.2), "cover_glass"),
        ((-14.2, 0, 1.0), "body_ti"), ((14.2, 0, 1.0), "body_ti"), ((0, 6.9, 1.0), "body_ti"), ((0, -6.9, 1.0), "body_ti"),
        ((X(-11.5), 5.2, 0.9), "ant_ceramic"), ((X(-11.5), 5.2, 1.65), "board_fr4"), ((X(-11.5), 5.2, 0.25), "air_cavity"),
        ((X(-10.05), 5.8, 1.45), "ant_pec"), ((X(-10.0), 5.9, 1.5), "tab_copper"),
        ((0, 0, 1.6), "board_ground"), ((X(-11.5), 4.0, 1.6), "board_fr4"), ((X(-9.0), 4.0, 1.6), "board_ground"),
        ((X(-13.4), 5.2, 0.3), "resin" if case == "B" else "body_ti"), ((X(-11.5), 5.2, 0.1), "resin" if case == "B" else "body_ti"),
        ((X(-14.3), 4.4, 1.0), "resin" if case == "B" else "body_ti"), ((X(-9.0), 4.4, 0.3), "body_ti"),
        ((X(-11.5), 1.5, 0.2), "body_ti"), ((X(-13.6), 5.2, 1.0), "air_cavity"),
    ]
    if case == "B":
        exp += [((X(-12.0), 6.9, 1.0), "resin"), ((X(-9.5), 6.9, 1.0), "resin"), ((X(-8.5), 6.9, 1.0), "body_ti"), ((X(-9.0), 4.4, 0.2), "body_ti")]
    else:
        exp += [((X(-9.0), 6.9, 1.0), "body_ti"), ((X(-12.0), 6.9, 1.0), "body_ti")]
    if case == "D":
        exp = [((X(-11.5), 5.2, 0.9), "ant_ceramic"), ((0, 0, 1.65), "board_fr4"), ((0, 0, 3.2), "cover_glass"), ((0, 0, 1.0), "none"), ((0, 0, ZC), "none"),
               ((0, 0, 1.6), "board_ground"), ((X(-11.5), 4.0, 1.6), "board_fr4")]
    for pt, want in exp:
        got = prop_at(pt)
        print("GEOM", "ok " if got == want else "BAD", pt, "expected", want, "got", got)
        if got != want: GEOM_FAILS.append((pt, want, got))
    print("GEOMCHECK fails:", len(GEOM_FAILS), "of", len(exp))
nf2ff = FDTD.CreateNF2FFBox(frequency=NF_FREQ)
info = dict(tag=tag, case=case, eps_r_ceramic=EPS_R, lines_xyz=[nx, ny, nz], cells=int((nx - 1) * (ny - 1) * (nz - 1)), nrts_cap=NRTS,
            end_criteria=EC, threads=THREADS, min_dx=[float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)],
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
res = nf2ff.CalcNF2FF(Sim_Path, NF_FREQ, np.arange(0, 181, 3.0), np.arange(0, 360, 6.0), center=[X(-11.5) * 1e-3, 5.2e-3, 0.9e-3], read_cached=False)
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
