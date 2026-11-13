"""Round 2 ring model (antenna-sim.md section 18). usage: r2_ring.py <tag> <case> <eps> <a> <vs>
cases: D free air; A metal body + pocket, finger; A0 same no finger; B resin corner, finger; B0 no finger; B2 resin corner, floor under the antenna removed, finger;
E antenna on the screen face under the glass, resin corner, finger; F... see env.  Env: MESH (1 base, 2 fine), EC, NRTS, THREADS, CX (antenna centre X, default -10.8),
CORNER_X (resin corner east edge, default -8.6), GAPUP (extra gap raise of the antenna above the floor in mm, default 0), GEOMCHECK, SETUP_ONLY.
Axes: X along the finger, Y across (+Y thumb), Z up; mm. Positions from design/wiring/ring-board-plan.md R2.0 (ANT1 at -10.80, 5.25 -> 5.20 on the 0.1 grid)."""
import os, sys, json, time, datetime
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import EPS0
import chipant, chipant2, ringsim_lib as RL, r2_common as R2
tag, case = sys.argv[1], sys.argv[2]; EPS_R, A_SPAN, VS = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
Sim = "/work/runs/" + tag; os.makedirs(Sim, exist_ok=True)
NRTS = int(os.environ.get("NRTS", "120000")); THREADS = int(os.environ.get("THREADS", "16")); EC = float(os.environ.get("EC", "1e-4"))
MESH = int(os.environ.get("MESH", "1")); CX = float(os.environ.get("CX", "-10.8")); CORNER_X = float(os.environ.get("CORNER_X", "-8.6"))
GAPUP = float(os.environ.get("GAPUP", "0")); SCREENMETAL = os.environ.get("SCREENMETAL", "")
F0, FC = 2.5e9, 1.2e9; NF_FREQ = [2.40e9, 2.44e9, 2.48e9]
BODY = {"D": "none", "A": "metal", "A0": "metal", "B": "resin", "B0": "resin", "B2": "resin", "E": "resin", "F": os.environ.get("FBODY", "resin")}[case]
FINGER = case not in ("D", "A0", "B0")
TOP = (case == "E"); OPENFLOOR = (case == "B2")
def kap(eps, tand, f=2.45e9): return 2 * np.pi * f * EPS0 * eps * tand
FDTD = openEMS(NrTS=NRTS, EndCriteria=EC); FDTD.SetGaussExcite(F0, FC); FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX); mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)
M = dict(body=CSX.AddMetal("body_ti"), air=CSX.AddMaterial("air_cavity", epsilon=1.0), board=CSX.AddMaterial("board_fr4", epsilon=4.3, kappa=kap(4.3, 0.02)),
         panel=CSX.AddMaterial("panel_glass", epsilon=6.5, kappa=kap(6.5, 0.01)), adh=CSX.AddMaterial("adhesive", epsilon=3.0, kappa=kap(3.0, 0.02)),
         glass=CSX.AddMaterial("cover_glass", epsilon=6.5, kappa=kap(6.5, 0.01)), resin=CSX.AddMaterial("resin", epsilon=3.0, kappa=kap(3.0, 0.02)),
         liner=CSX.AddMaterial("liner_resin", epsilon=3.0, kappa=kap(3.0, 0.02)), skin=CSX.AddMaterial("skin", epsilon=38.0, kappa=1.46),
         muscle=CSX.AddMaterial("muscle", epsilon=52.73, kappa=1.74), gnd=CSX.AddMetal("board_ground"), cu=CSX.AddMetal("tab_copper"))
def bx(prop, a, b, prio):
    a = np.array(a, float); b = np.array(b, float); prop.AddBox(np.minimum(a, b), np.maximum(a, b), priority=prio)
def rrect(x0, x1, y0, y1, r, n=10):
    pts = []
    for (cx, cy, a0) in [(x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)]:
        for k in range(n + 1):
            a = np.radians(a0 + 90.0 * k / n); pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return pts
def clip(poly, keep):
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]; dp, dq = keep(p), keep(q)
        if dp >= 0: out.append(p)
        if (dp >= 0) != (dq >= 0):
            t = dp / (dp - dq); out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out
def poly(prop, pts, z0, z1, prio): prop.AddLinPoly(np.array(pts).T.tolist(), "z", z0, z1 - z0, priority=prio)
ZF1, ZB0, ZBG, ZB1 = 0.4, 1.5, 1.6, 1.8
ZP0, ZP1, ZAD1, ZG1 = 1.9, 2.7, 2.8, 3.5
BX, BY, IX, IY = 14.7, 7.4, 13.7, 6.5
R_IN = 18.9452 / 2; ZC = -0.4 - R_IN; R_OUT = R_IN + 2.6; R_LINER = R_IN + 0.3; FING = (-25.0, 45.0)
outer = rrect(-BX, BX, -BY, BY, 2.5); inner = rrect(-IX, IX, -IY, IY, 1.6)
if BODY != "none":
    poly(M["body"], outer, 0.0, ZAD1, 10)
    M["body"].AddCylinder([-4, 0, ZC], [4, 0, ZC], R_OUT, priority=10)
    M["liner"].AddCylinder([-4, 0, ZC], [4, 0, ZC], R_LINER, priority=11)
    poly(M["air"], inner, ZF1, ZAD1, 20)
    if BODY == "resin":
        corner = clip(outer, lambda p: CORNER_X - p[0]); corner = clip(corner, lambda p: p[1] - 2.1)
        poly(M["resin"], corner, 0.0, ZAD1, 19)
if FINGER:
    M["skin"].AddCylinder([FING[0], 0, ZC], [FING[1], 0, ZC], R_IN, priority=12)
    M["muscle"].AddCylinder([FING[0], 0, ZC], [FING[1], 0, ZC], R_IN - 1.5, priority=13)
# board, ground, stitching
bx(M["board"], (-13.6, -6.3, ZB0), (13.6, 6.3, ZB1), 22)
KX = -8.7   # copper-free zone east edge (plan -8.75, snapped)
for zg in (1.6, 1.8):
    bx(M["gnd"], (-13.6, -6.3, zg), (13.6, 3.1, zg), 30); bx(M["gnd"], (KX, 3.1, zg), (13.6, 6.3, zg), 30)
def wall(x0, y0, x1, y1): bx(M["gnd"], (x0, y0, 1.6), (x1, y1, 1.8), 30)
wall(-13.6, -6.3, 13.6, -6.2); wall(13.5, -6.3, 13.6, 6.3); wall(KX, 6.2, 13.6, 6.3); wall(-13.6, -6.3, -13.5, 3.1); wall(-13.6, 3.0, KX, 3.1); wall(KX, 3.1, KX + 0.1, 6.3)
bx(M["panel"], (-13.7, -6.4, ZP0), (13.7, 6.4, ZP1), 25); bx(M["adh"], (-13.7, -6.4, ZP1), (13.7, 6.4, ZAD1), 25)
poly(M["glass"], rrect(-14.7, 14.7, -7.2, 7.2, 2.5), ZAD1, ZG1, 25)
if TOP:   # screen ledge and glass recess over the antenna (section 18.3, case E)
    bx(M["air"], (-13.2, 2.9, ZB1), (-8.5, 6.4, ZAD1), 26)
    bx(M["air"], (-13.2, 3.0, ZAD1), (-8.6, 6.3, 3.1), 26)
if BODY != "none" and not TOP:   # pocket under the antenna (plan R2: X -12.6 to -9.0, Y 4.25 to 6.25 -> 4.2 to 6.2, 0.2 deep)
    bx(M["air"], (CX + 1.2 - 2.4 - 0.0 if False else CX - 1.8, 4.2, 0.2), (CX + 1.8, 6.2, ZF1), 21)
if OPENFLOOR:
    bx(M["air"], (CX - 2.0, 4.2, 0.0), (CX + 2.0, 6.2, ZF1), 22)
# screen metal (round 2d): bond fingers and flat cable on the glass ledge, folded down the end and under the board (light-path.md lines 9 to 12)
if SCREENMETAL:
    sg = -1.0 if SCREENMETAL == "hand" else 1.0
    sc = M["gnd"]
    xa, xb = sorted((sg * 13.7, sg * 12.8)); bx(sc, (xa, -6.2, 2.3), (xb, 6.2, 2.3), 34)          # ledge: fingers and cable, Y +-6.2, X 12.8 to 13.7, on the lower glass top (Z 2.3)
    bx(sc, (sg * 13.7, -2.5, 1.4), (sg * 13.7, 2.5, 2.3), 34)                                      # fold down the end, 5.0 wide
    xa, xb = sorted((sg * 13.7, sg * 10.1)); bx(sc, (xa, -2.5, 1.4), (xb, 2.5, 1.4), 34)           # under the board end towards J1
# antenna
ZL = ZB1 if TOP else ZB0
if TOP:
    fr = chipant.Frame((CX, 5.2, ZL), (-1, 0, 0), (0, -1, 0), (0, 0, 1))
else:
    fr = chipant.Frame((CX, 5.2, ZL - GAPUP * 0 + 0.0), (-1, 0, 0), (0, -1, 0), (0, 0, -1))
chipant2.add_standin(CSX, fr, EPS_R, A_SPAN, VS, 0.005, prio_body=27, prio_metal=31)
CU = M["cu"]
xf0, xf1 = CX - 2.0, CX + 2.0      # far land x range centre CX-1.5 ; feed land centre CX+1.5
for (x0, x1) in ((CX - 2.0, CX - 1.0), (CX + 1.0, CX + 2.0)):
    for (y0, y1) in ((5.6, 6.2), (4.3, 4.9)): bx(CU, (x0, y0, ZL), (x1, y1, ZL), 32)
fx_end = CX + 1.5
if TOP:
    bx(CU, (fx_end - 0.1, 5.8, ZB0), (fx_end + 0.1, 6.0, ZL), 32)          # via from the feed land down to L1
    bx(CU, (fx_end - 0.1, 5.8, ZB0), (KX + 0.2, 6.0, ZB0), 32)             # L1 feed track to the port
else:
    bx(CU, (fx_end - 0.1, 5.8, ZL), (KX + 0.2, 6.0, ZL), 32)
bx(CU, (fx_end - 0.3, 4.3, ZL), (KX + 0.3, 4.5, ZL), 32)                   # pin 4 track east
bx(CU, (KX + 0.1, 4.3, ZL), (KX + 0.3, 4.5, ZB1), 32)                      # ground stack
bx(CU, (CX - 1.6, 4.3, ZL), (CX - 1.4, 6.2, ZL), 32)                       # far lands joined
bx(CU, (CX - 1.6, 3.0, ZL), (CX - 1.4, 4.3, ZL), 32)                       # to LT1 (0 ohm)
bx(CU, (CX - 1.6, 2.9, ZL), (CX - 1.4, 3.1, 1.6), 32)                      # ground stack at Y below 3.1
port = None
# mesh
def rng(a, b, s): return list(np.round(np.arange(a, b + 1e-9, s), 4))
S_B, S_F, S_X = ((1.0, 2.0, 3.0) if MESH == 0 else (0.5 / MESH, 1.5 / MESH, 2.0 / MESH))
fx = rng(-16, -14, S_B) + rng(CX - 3.5, CX + 3.5, 0.1) + rng(-9, 16, S_B) + rng(-14, -9, 0.1) + ((rng(-25, -16, S_X) + rng(16, 45, S_X)) if FINGER else rng(-22, 22, S_X))
fy = rng(2.0, 6.6, 0.1) + rng(-8, 1.5, S_B) + rng(6.6, 8.0, S_B) + (rng(-12.5, -8, S_F) + rng(8, 12.5, S_F) if FINGER else rng(-12, 12, S_F))
fz = rng(0, 3.6, 0.1) + rng(-1, 0, S_B) + rng(3.6, 5, S_B) + (rng(-20, -1.0, S_F) if FINGER else [])
for v in (-12.8, 12.8, -10.1, 10.1, -13.7, 13.7, -14.7, 14.7, -13.6, 13.6, -4, 4, KX, KX + 0.1, KX + 0.2, KX + 0.3, KX + 0.4, 13.5, CX - 1.8, CX + 1.8, CX - 2.0, CX + 2.0, CX - 1.0, CX + 1.0, CX - 1.6, CX - 1.4, fx_end - 0.1, fx_end + 0.1, fx_end - 0.3):
    fx.append(round(v, 2))
for v in (-2.5, 2.5, -6.2, -7.4, 7.4, -6.5, 6.5, -6.3, 6.3, -6.4, 6.4, 7.2, -7.2, 2.1, 2.9, 3.0, 3.1, 4.2, 4.3, 4.5, 4.9, 5.6, 5.8, 6.0, 6.2, 6.3): fy.append(v)
for v in (0.2, 0.3, 0.4, 0.5, 1.4, 2.3, 1.5, 1.6, 1.7, 1.8, 1.9, 2.7, 2.8, 3.0, 3.1, 3.5): fz.append(v)
MARG = 10.0 if MESH == 0 else 12.0
if FINGER: fx += [-25 - MARG - 24, 45 + MARG + 24]; fz += [-20 - MARG - 24, 3.5 + MARG + 24]
else: fx += [-22 - MARG - 24, 22 + MARG + 24]; fz += [-MARG - 24, 3.5 + MARG + 24]
fy += [-48, 48]
def merge(v, tol):
    o = []
    for a in sorted(v):
        if o and a - o[-1] < tol: continue
        o.append(a)
    return o
fx, fy, fz = ([float(np.round(v / 0.05) * 0.05) for v in a] for a in (fx, fy, fz))
mesh.AddLine("x", merge(fx, 0.09)); mesh.AddLine("y", merge(fy, 0.09)); mesh.AddLine("z", merge(fz, 0.09))
port = FDTD.AddLumpedPort(1, 50, [KX + 0.1, 5.8, ZB0], [KX + 0.2, 6.0, ZBG], "z", 1.0, priority=40)
for d in "xyz": mesh.SmoothMeshLines(d, 3.0, 1.3)
nf = [len(mesh.GetLines(d)) for d in (0, 1, 2)]
assert min(float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)) > 0.0999, "cell under 0.1 mm"
nf2ff = FDTD.CreateNF2FFBox(frequency=NF_FREQ)
info = dict(tag=tag, case=case, screenmetal=SCREENMETAL, eps=EPS_R, a=A_SPAN, vs=VS, mesh=MESH, cx=CX, corner_x=CORNER_X, lines=nf, cells=int((nf[0] - 1) * (nf[1] - 1) * (nf[2] - 1)), ec=EC)
def prop_at(pt):
    pr = CSX.GetPropertyByCoordPriority(pt); return pr.GetName() if pr is not None else "none"
if os.environ.get("GEOMCHECK") == "1":
    ex = [((CX, 5.2, 0.9 if not TOP else 2.4), "ant_ceramic"), ((0, 0, 1.65), "board_fr4"), ((0, 0, 1.0), "air_cavity" if BODY != "none" else "none"),
          ((CX, 5.2, 0.25), ("air_cavity" if BODY != "none" and not OPENFLOOR and not TOP else ("air_cavity" if BODY != "none" and not TOP else "none"))) if not TOP else ((CX, 5.2, 0.1), "resin")]
    if BODY == "metal": ex += [((CX - 3.0, 5.2, 0.3), "body_ti"), ((0, 6.9, 1.0), "body_ti")]
    if BODY == "resin": ex += [((CX - 3.0, 5.2, 0.3), "resin"), ((0, 6.9, 1.0), "body_ti"), ((-14.3, 4.4, 1.0), "resin")]
    if FINGER: ex += [((0, 0, ZC), "muscle")]
    else: ex += [((0, 0, ZC), "none")]
    bad = 0
    for pt, want in ex:
        got = prop_at(pt); ok = got == want; bad += (not ok); print("GEOM", "ok " if ok else "BAD", pt, "want", want, "got", got)
    print("GEOMCHECK fails:", bad, "of", len(ex))
print(json.dumps(info))
if os.environ.get("SETUP_ONLY") == "1":
    FDTD.Run(Sim, cleanup=True, setup_only=True, verbose=3); print("SETUP_ONLY done"); sys.exit(0)
R2.ledger(tag, "start"); t0 = time.time()
FDTD.Run(Sim, cleanup=True, numThreads=THREADS, verbose=2)
info["run_seconds"] = time.time() - t0; R2.ledger(tag, "end", "%.0f s" % info["run_seconds"])
f = np.arange(2.0e9, 3.0e9 + 1, 5e6); fb = np.arange(2.40e9, 2.48e9 + 1, 1e6)
fe = np.union1d(np.union1d(f, fb), np.array(NF_FREQ)); port.CalcPort(Sim, fe, ref_impedance=50)
s11 = port.uf_ref / port.uf_inc; zin = port.uf_tot / port.if_tot; pacc = port.P_acc
np.savetxt("/work/results/%s_zin.csv" % tag, np.c_[fe / 1e9, zin.real, zin.imag, np.abs(s11), 20 * np.log10(np.abs(s11)), pacc], delimiter=",", header="f_GHz,Re_Zin,Im_Zin,abs_s11,s11_dB,P_acc_W", comments="")
res = nf2ff.CalcNF2FF(Sim, NF_FREQ, np.arange(0, 181, 3.0), np.arange(0, 360, 6.0), center=[CX * 1e-3, 5.2e-3, 0.9e-3], read_cached=False)
eff = {}; dmax = {}
for i, fq in enumerate(NF_FREQ):
    j = int(np.argmin(np.abs(fe - fq))); eff["%.2f" % (fq / 1e9)] = float(res.Prad[i] / pacc[j]); dmax["%.2f" % (fq / 1e9)] = float(res.Dmax[i])
ib = np.array([int(np.argmin(np.abs(fe - q))) for q in fb]); zb = zin[ib]
before = np.abs(RL.gamma(zb)); sol = RL.match_solve(fb, zb, seed=20261113, starts=60)
after = np.abs(RL.gamma(RL.pi_zin(sol["pattern"], sol["values"], fb, zb)))
snapv = [RL.snap(k, v) for k, v in zip(sol["pattern"], sol["values"])]
ver = RL.case_verdict(-20 * np.log10(after), {"2.40": eff["2.40"], "2.44": eff["2.44"], "2.48": eff["2.48"]})
pinc = {"%.2f" % (q / 1e9): float(port.P_inc[int(np.argmin(np.abs(fe - q)))]) for q in NF_FREQ}
prad = {"%.2f" % (q / 1e9): float(res.Prad[i]) for i, q in enumerate(NF_FREQ)}
info.update(prad_W_by_ghz=prad, pinc_W_by_ghz=pinc, total_eff_by_ghz={k: prad[k] / pinc[k] for k in prad}, eff_by_ghz=eff, dmax_by_ghz=dmax, s11_before_db_at={"%.2f" % (q / 1e9): float(20 * np.log10(before[int(np.argmin(abs(fb - q)))])) for q in [2.40e9, 2.44e9, 2.48e9]},
            zin_at={"%.2f" % (q / 1e9): [float(zb[int(np.argmin(abs(fb - q)))].real), float(zb[int(np.argmin(abs(fb - q)))].imag)] for q in [2.40e9, 2.44e9, 2.48e9]},
            match=dict(pattern=sol["pattern"], values_SI=sol["values"], snapped_SI=snapv), s11_after_db_worst=float(20 * np.log10(after.max())), verdict=ver)
json.dump(info, open("/work/results/%s.json" % tag, "w"), indent=1, default=float)
print("RESULT", json.dumps({k: info[k] for k in ("case", "eff_by_ghz", "s11_after_db_worst", "verdict")}, default=float))
