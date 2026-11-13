import os, sys, json, time
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
import r2_common as R
tag = sys.argv[1]; Sim = "/work/runs/" + tag; os.makedirs(Sim, exist_ok=True)
L = 58.0; W = 1.0; GAP = 1.0
FDTD = openEMS(NrTS=200000, EndCriteria=1e-4); FDTD.SetGaussExcite(2.45e9, 0.8e9); FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX); mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)
pec = CSX.AddMetal("dip")
pec.AddBox([-W / 2, 0, GAP / 2], [W / 2, 0, L / 2], priority=10); pec.AddBox([-W / 2, 0, -L / 2], [W / 2, 0, -GAP / 2], priority=10)
mesh.AddLine("x", list(np.arange(-W / 2, W / 2 + 1e-9, 0.25)) + [-60, 60]); mesh.AddLine("y", [-0.5, 0, 0.5, -60, 60])
mesh.AddLine("z", list(np.arange(-L / 2 - 2, L / 2 + 2.01, 1.0)) + [-0.5, 0.5, -90, 90])
port = FDTD.AddLumpedPort(1, 50, [-W / 2, 0, -GAP / 2], [W / 2, 0, GAP / 2], "z", 1.0, priority=40)
for d in "xyz": mesh.SmoothMeshLines(d, 3.0, 1.3)
nf2ff = FDTD.CreateNF2FFBox(frequency=[2.35e9, 2.45e9, 2.55e9])
nf = [len(mesh.GetLines(d)) for d in (0, 1, 2)]
info = dict(tag=tag, lines=nf, cells=int((nf[0] - 1) * (nf[1] - 1) * (nf[2] - 1)))
print(json.dumps(info)); R.ledger(tag, "start"); t0 = time.time()
FDTD.Run(Sim, cleanup=True, numThreads=16, verbose=2)
info["run_seconds"] = time.time() - t0; R.ledger(tag, "end", "%.0f s" % info["run_seconds"])
f = np.unique(np.r_[np.arange(2.0e9, 3.0e9 + 1, 5e6), 2.35e9, 2.45e9, 2.55e9]); port.CalcPort(Sim, f, ref_impedance=50)
zin = port.uf_tot / port.if_tot; pacc = port.P_acc
np.savetxt("/work/results/%s_zin.csv" % tag, np.c_[f / 1e9, zin.real, zin.imag], delimiter=",", header="f_GHz,Re_Z,Im_Z", comments="")
res = nf2ff.CalcNF2FF(Sim, [2.35e9, 2.45e9, 2.55e9], np.arange(0, 181, 3.0), np.arange(0, 360, 6.0), center=[0, 0, 0], read_cached=False)
eff = {}; dirv = {}
for i, fq in enumerate([2.35e9, 2.45e9, 2.55e9]):
    j = int(np.argmin(abs(f - fq))); eff["%.2f" % (fq / 1e9)] = float(res.Prad[i] / pacc[j]); dirv["%.2f" % (fq / 1e9)] = float(10 * np.log10(res.Dmax[i]))
k = np.where(np.diff(np.sign(zin.imag)) != 0)[0]
fr = float(np.interp(0, [zin.imag[k[0]], zin.imag[k[0] + 1]], [f[k[0]], f[k[0] + 1]])) if len(k) else None
rr = float(np.interp(fr, f, zin.real)) if fr else None
info.update(f_res_GHz=None if fr is None else fr / 1e9, R_at_res=rr, eff=eff, D_dBi=dirv)
ok = fr is not None and 2.33e9 <= fr <= 2.57e9 and 60 <= rr <= 85 and max(eff.values()) >= 0.95 and 2.0 <= dirv["2.45"] <= 2.3 + 0.0
info["pass_all"] = bool(ok)
json.dump(info, open("/work/results/%s.json" % tag, "w"), indent=1); print("RESULT", json.dumps(info))
