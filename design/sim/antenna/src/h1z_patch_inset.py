import os, sys, json, time
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import EPS0
import r2_common as R
tag = sys.argv[1]; Sim = "/work/runs/" + tag; os.makedirs(Sim, exist_ok=True)
ER, H, TAND = 4.4, 1.6, 0.02; W, L, GX = 38.0, 29.0, 60.0; WL = 3.0; INS = 7.0; GAPN = 1.0
FDTD = openEMS(NrTS=200000, EndCriteria=1e-4); FDTD.SetGaussExcite(2.45e9, 0.8e9); FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX); mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)
sub = CSX.AddMaterial("fr4", epsilon=ER, kappa=2 * np.pi * 2.45e9 * EPS0 * ER * TAND)
sub.AddBox([-GX / 2, -GX / 2, 0], [GX / 2, GX / 2, H], priority=1)
gnd = CSX.AddMetal("gnd"); gnd.AddBox([-GX / 2, -GX / 2, 0], [GX / 2, GX / 2, 0], priority=10)
pat = CSX.AddMetal("patch")
# patch with inset notch: three boxes
yb = -L / 2; ye = L / 2; xn = WL / 2 + GAPN
pat.AddBox([-W / 2, yb + INS, H], [W / 2, ye, H], priority=10)
pat.AddBox([-W / 2, yb, H], [-xn, yb + INS, H], priority=10); pat.AddBox([xn, yb, H], [W / 2, yb + INS, H], priority=10)
pat.AddBox([-WL / 2, -GX / 2 + 10, H], [WL / 2, yb + INS, H], priority=10)   # line, port covers y -30..-20
STEP = 0.5
fx = list(np.arange(-GX / 2, GX / 2 + 1e-9, STEP)) + [-W / 2, W / 2, -WL / 2, WL / 2, -xn, xn]
fy = list(np.arange(-GX / 2, GX / 2 + 1e-9, STEP)) + [yb, ye, yb + INS]
fz = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
MG = 25.0
fx += [-GX / 2 - MG - 20, GX / 2 + MG + 20]; fy += [-GX / 2 - MG - 20, GX / 2 + MG + 20]; fz += [-MG - 20, H + MG + 20]
def merge(v, tol):
    o = []
    for a in sorted(v):
        if o and a - o[-1] < tol: continue
        o.append(a)
    return o
mesh.AddLine("x", merge(fx, 0.1)); mesh.AddLine("y", merge(fy, 0.1)); mesh.AddLine("z", fz)
port = FDTD.AddMSLPort(1, pat, [-WL / 2, -GX / 2 + 0.5, H], [WL / 2, -GX / 2 + 10, 0], "y", "z", excite=1, FeedShift=1.0, MeasPlaneShift=4.0, Feed_R=50, priority=40)
for d in "xyz": mesh.SmoothMeshLines(d, 3.0, 1.3)
nf2ff = FDTD.CreateNF2FFBox(frequency=[2.30e9, 2.35e9, 2.40e9, 2.45e9])
nf = [len(mesh.GetLines(d)) for d in (0, 1, 2)]
info = dict(tag=tag, lines=nf, cells=int((nf[0] - 1) * (nf[1] - 1) * (nf[2] - 1)), min_dx=[float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)])
print(json.dumps(info)); R.ledger(tag, "start"); t0 = time.time()
FDTD.Run(Sim, cleanup=True, numThreads=16, verbose=2)
info["run_seconds"] = time.time() - t0; R.ledger(tag, "end", "%.0f s" % info["run_seconds"])
f = np.unique(np.r_[np.arange(2.0e9, 3.0e9 + 1, 5e6), 2.30e9, 2.35e9, 2.40e9, 2.45e9]); port.CalcPort(Sim, f)
s11 = port.uf_ref / port.uf_inc; rl = -20 * np.log10(np.abs(s11)); pacc = port.P_acc
i = int(np.argmax(rl)); fm = f[i]
np.savetxt("/work/results/%s_s11.csv" % tag, np.c_[f / 1e9, rl], delimiter=",", header="f_GHz,RL_dB", comments="")
fq = [2.30e9, 2.35e9, 2.40e9, 2.45e9]
res = nf2ff.CalcNF2FF(Sim, fq, np.arange(0, 181, 3.0), np.arange(0, 360, 6.0), center=[0, 0, H * 1e-3], read_cached=False)
eff = {"%.2f" % (q / 1e9): float(res.Prad[k] / pacc[int(np.argmin(abs(f - q)))]) for k, q in enumerate(fq)}
info.update(f_min_GHz=float(fm / 1e9), rl_at_min_dB=float(rl[i]), eff=eff, formula_GHz=2.4332, offset_pct=float((fm / 1e9 / 2.4332 - 1) * 100))
json.dump(info, open("/work/results/%s.json" % tag, "w"), indent=1); print("RESULT", json.dumps(info))
