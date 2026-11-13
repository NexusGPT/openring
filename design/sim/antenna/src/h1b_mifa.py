"""H1b: Infineon AN91445 MIFA (Figure 10) as read in antenna-sim.md section 12.1. usage: h1b_mifa.py <tag>. mil -> mm."""
import os, sys, json, time
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import EPS0
import r2_common as R
tag = sys.argv[1]; MIL = 0.0254
Sim = "/work/runs/" + tag; os.makedirs(Sim, exist_ok=True)
THREADS = int(os.environ.get("THREADS", "16")); NRTS = int(os.environ.get("NRTS", "150000"))
def m(v): return v * MIL
H = 1.6; ER = 4.3; TAND = 0.02
FDTD = openEMS(NrTS=NRTS, EndCriteria=1e-4); FDTD.SetGaussExcite(2.45e9, 0.8e9); FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX); mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)
sub = CSX.AddMaterial("fr4", epsilon=ER, kappa=2 * np.pi * 2.45e9 * EPS0 * ER * TAND)
top = CSX.AddMetal("top"); bot = CSX.AddMetal("bot"); via = CSX.AddMetal("via")
def box(p, x0, y0, x1, y1, z0, z1, pr=10): p.AddBox([m(x0), m(y0), z0], [m(x1), m(y1), z1], priority=pr)
sub.AddBox([0, 0, 0], [m(565), m(518), H], priority=1)
for (x0, y0, x1, y1) in [(0, 0, 565, 200), (110, 200, 565, 260)]: box(bot, x0, y0, x1, y1, 0, 0)
# top ground pour with the feed cut-out
box(top, 0, 0, 75.5, 200, H, H); box(top, 164.5, 0, 565, 200, H, H)
# feed trace and taper (polygon), riser
top.AddPolygon(np.array([[m(87.5), m(87.5), m(110), m(130), m(152.5), m(152.5)], [0, m(160), m(200), m(200), m(160), 0]]), "z", H, priority=10) if False else None
box(top, 87.5, 0, 152.5, 160, H, H)
for k in range(8):   # taper by 8 steps from W to 20 mil over y 160..200
    y0 = 160 + 5 * k; w = 65 + (20 - 65) * (k + 0.5) / 8; box(top, 120 - w / 2, y0, 120 + w / 2, y0 + 5, H, H)
box(top, 110, 200, 130, 480, H, H)
bars = [110, 155, 200, 245, 290, 335, 380]
for x in bars[1:]: box(top, x, 310, x + 20, 480 if x != 380 else 480, H, H)
for a, b in [(0, 1), (2, 3), (4, 5)]: box(top, bars[a], 460, bars[b] + 20, 480, H, H)
for a, b in [(1, 2), (3, 4), (5, 6)]: box(top, bars[a], 310, bars[b] + 20, 330, H, H)
box(top, 380, 460, 545, 480, H, H)
box(top, 130, 230, 403, 250, H, H)
vs = 0.38
def vpost(xc, yc): via.AddBox([m(xc) - vs / 2, m(yc) - vs / 2, 0], [m(xc) + vs / 2, m(yc) + vs / 2, H], priority=11)
vpost(393, 240)
x = 15.0
while x < 565:
    if not (60 < x < 180): vpost(x, 180)
    x += 30
# ---- mesh: fixed coordinates, near-duplicates merged (< 0.06 mm), 0.2 mm fill over the board, graded outside
def merge(vals, tol=0.06):
    out = []
    for v in sorted(vals):
        if out and v - out[-1] < tol: continue
        out.append(v)
    return out
fx = [m(v) for v in (0, 75.5, 87.5, 110, 130, 152.5, 164.5, 565, 155, 175, 200, 220, 245, 265, 290, 310, 335, 355, 380, 400, 545, 403, 393)]
fy = [m(v) for v in (0, 160, 200, 230, 250, 260, 310, 330, 460, 480, 518, 180)]
fx += list(np.arange(0, m(565) + 0.01, 0.4)); fy += list(np.arange(0, m(518) + 0.01, 0.4))
fx += [m(x) for x in np.arange(15, 565, 30) if not 60 < x < 180]
mesh.AddLine("x", merge(fx)); mesh.AddLine("y", merge(fy))
mesh.AddLine("z", [0, 0.4, 0.8, 1.2, H])
MG = 15.0
mesh.AddLine("x", [-MG - 20, m(565) + MG + 20]); mesh.AddLine("y", [-MG - 20, m(518) + MG + 20]); mesh.AddLine("z", [-MG - 20, H + MG + 20])
port = FDTD.AddLumpedPort(1, 50, [m(87.5), 0, 0], [m(152.5), 0.4, H], "z", 1.0, priority=40)
for d in "xyz": mesh.SmoothMeshLines(d, 2.5, 1.3)
nf = [len(mesh.GetLines(d)) for d in (0, 1, 2)]
nf2ff = FDTD.CreateNF2FFBox()
assert min(float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)) > 0.05, "tiny cell"
info = dict(tag=tag, lines=nf, cells=int((nf[0] - 1) * (nf[1] - 1) * (nf[2] - 1)), min_dx=[float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)])
print(json.dumps(info))
if os.environ.get("GEOMDUMP") == "1":
    zz = H; rows = []
    for yy in np.arange(m(518) - 0.1, 0, -0.2):
        row = ""
        for xx in np.arange(0.1, m(565), 0.1):
            pr = CSX.GetPropertyByCoordPriority([xx, yy, zz])
            n = pr.GetName() if pr is not None else "none"
            row += {"top": "#", "via": "o", "fr4": ".", "none": " ", "bot": "b"}.get(n, "?")
        rows.append(row)
    open("/work/results/%s_geom_top.txt" % tag, "w").write("\n".join(rows)); print("GEOMDUMP done"); sys.exit(0)
R.ledger(tag, "start"); t0 = time.time()
FDTD.Run(Sim, cleanup=True, numThreads=THREADS, verbose=2)
info["run_seconds"] = time.time() - t0; R.ledger(tag, "end", "%.0f s" % info["run_seconds"])
f = np.arange(2.0e9, 3.0e9 + 1, 2.5e6); port.CalcPort(Sim, f, ref_impedance=50)
s11 = port.uf_ref / port.uf_inc; rl = -20 * np.log10(np.abs(s11)); zin = port.uf_tot / port.if_tot
np.savetxt("/work/results/%s_s11.csv" % tag, np.c_[f / 1e9, rl, zin.real, zin.imag], delimiter=",", header="f_GHz,RL_dB,Re_Z,Im_Z", comments="")
i = int(np.argmax(rl)); lo, hi = R.crossings(f, rl, 10.0)
info.update(f_min_GHz=float(f[i] / 1e9), rl_at_min_dB=float(rl[i]), cross_lo_GHz=None if lo is None else float(lo / 1e9), cross_hi_GHz=None if hi is None else float(hi / 1e9))
a = 2.367 <= info["f_min_GHz"] <= 2.513
b = lo is not None and hi is not None and 2.260 <= lo / 1e9 <= 2.400 and 2.483 <= hi / 1e9 <= 2.637
c = rl[i] >= 10
info.update(pass_a=bool(a), pass_b=bool(b), pass_c=bool(c), H1b_pass=bool(a and b and c))
json.dump(info, open("/work/results/%s.json" % tag, "w"), indent=1)
print("RESULT", json.dumps(info))
