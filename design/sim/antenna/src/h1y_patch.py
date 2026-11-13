import os, sys, json, time
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import EPS0
import r2_common as R
tag = sys.argv[1]; Sim = "/work/runs/" + tag; os.makedirs(Sim, exist_ok=True)
ER, H, TAND = 4.4, 1.6, 0.02; W, L, GX = 38.0, 29.0, 60.0; YP = 8.0
FDTD = openEMS(NrTS=200000, EndCriteria=1e-4); FDTD.SetGaussExcite(2.45e9, 0.8e9); FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX); mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)
sub = CSX.AddMaterial("fr4", epsilon=ER, kappa=2 * np.pi * 2.45e9 * EPS0 * ER * TAND)
sub.AddBox([-GX / 2, -GX / 2, 0], [GX / 2, GX / 2, H], priority=1)
gnd = CSX.AddMetal("gnd"); gnd.AddBox([-GX / 2, -GX / 2, 0], [GX / 2, GX / 2, 0], priority=10)
pat = CSX.AddMetal("patch"); pat.AddBox([-W / 2, -L / 2, H], [W / 2, L / 2, H], priority=10)
pat.AddBox([-0.25, YP - 0.25, 0.4], [0.25, YP + 0.25, H], priority=10)
STEP = float(os.environ.get("STEP", "1.0"))
fx = list(np.arange(-GX / 2, GX / 2 + 1e-9, STEP)) + [-W / 2, W / 2, -0.25, 0.25, 0]
fy = list(np.arange(-GX / 2, GX / 2 + 1e-9, STEP)) + [-L / 2, L / 2, YP - 0.25, YP + 0.25]
fz = [0, 0.4, 0.8, 1.2, 1.6] if STEP >= 1 else [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
MG = 25.0
fx += [-GX / 2 - MG - 20, GX / 2 + MG + 20]; fy += [-GX / 2 - MG - 20, GX / 2 + MG + 20]; fz += [-MG - 20, H + MG + 20]
def merge(v, tol=0.2):
    o = []
    for a in sorted(v):
        if o and a - o[-1] < tol: continue
        o.append(a)
    return o
fx = merge(fx, 0.2 * STEP); fy = merge(fy, 0.2 * STEP)
mesh.AddLine("x", fx); mesh.AddLine("y", fy); mesh.AddLine("z", fz)
port = FDTD.AddLumpedPort(1, 50, [-0.25, YP - 0.25, 0], [0.25, YP + 0.25, 0.4], "z", 1.0, priority=40)
for d in "xyz": mesh.SmoothMeshLines(d, 3.0, 1.3)
nf2ff = FDTD.CreateNF2FFBox(frequency=[2.40e9, 2.45e9, 2.50e9])
nf = [len(mesh.GetLines(d)) for d in (0, 1, 2)]
info = dict(tag=tag, lines=nf, cells=int((nf[0] - 1) * (nf[1] - 1) * (nf[2] - 1)), min_dx=[float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)])
print(json.dumps(info)); R.ledger(tag, "start"); t0 = time.time()
FDTD.Run(Sim, cleanup=True, numThreads=16, verbose=2)
info["run_seconds"] = time.time() - t0; R.ledger(tag, "end", "%.0f s" % info["run_seconds"])
f = np.unique(np.r_[np.arange(2.0e9, 3.0e9 + 1, 5e6), 2.40e9, 2.45e9, 2.50e9]); port.CalcPort(Sim, f, ref_impedance=50)
s11 = port.uf_ref / port.uf_inc; rl = -20 * np.log10(np.abs(s11)); zin = port.uf_tot / port.if_tot; pacc = port.P_acc
i = int(np.argmax(rl)); fm = f[i]
np.savetxt("/work/results/%s_s11.csv" % tag, np.c_[f / 1e9, rl, zin.real, zin.imag], delimiter=",", header="f_GHz,RL_dB,Re_Z,Im_Z", comments="")
fq = [2.40e9, 2.45e9, 2.50e9]
res = nf2ff.CalcNF2FF(Sim, fq, np.arange(0, 181, 3.0), np.arange(0, 360, 6.0), center=[0, 0, H * 1e-3], read_cached=False)
eff = {"%.2f" % (q / 1e9): float(res.Prad[k] / pacc[int(np.argmin(abs(f - q)))]) for k, q in enumerate(fq)}
effm = float(np.interp(fm, fq, [eff["2.40"], eff["2.45"], eff["2.50"]]))
info.update(f_min_GHz=float(fm / 1e9), rl_at_min_dB=float(rl[i]), eff=eff, eff_at_min=effm, formula_GHz=2.4332)
info["p1"] = bool(2.360 <= fm / 1e9 <= 2.506); info["p2"] = bool(0.40 <= effm <= 0.90); info["pass_all"] = bool(info["p1"] and info["p2"])
json.dump(info, open("/work/results/%s.json" % tag, "w"), indent=1); print("RESULT", json.dumps(info))
