"""H1: Johanson 2450AT18D0100001E on the maker's evaluation board (datasheet page 3). usage: h1_eval_board.py <tag> <eps_r> [post]
Writes /work/runs/<tag>/ ; results in /work/results/<tag>.json"""
import os, sys, json, time, datetime
import numpy as np
sys.path.insert(0, "/work/src")
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0, EPS0
import chipant, ringsim_lib

tag = sys.argv[1]; EPS_R = float(sys.argv[2]); POST_ONLY = (len(sys.argv) > 3 and sys.argv[3] == "post")
TAND_CER = 0.005
H_FR4, EPS_FR4, TAND_FR4 = 0.8, 4.4, 0.02
Sim_Path = os.path.join("/work/runs", tag)
os.makedirs(Sim_Path, exist_ok=True); os.makedirs("/work/results", exist_ok=True)
NRTS = int(os.environ.get("NRTS", "600000")); THREADS = int(os.environ.get("THREADS", "16"))
F0, FC = 2.5e9, 0.6e9
NF_FREQ = [2.40e9, 2.42e9, 2.44e9, 2.45e9, 2.46e9, 2.48e9, 2.50e9]

FDTD = openEMS(NrTS=NRTS, EndCriteria=1e-5)
FDTD.SetGaussExcite(F0, FC)
FDTD.SetBoundaryCond(["PML_8"] * 6)
CSX = ContinuousStructure(); FDTD.SetCSX(CSX)
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)

# ------------------------------------------------ board
fr4 = CSX.AddMaterial("fr4", epsilon=EPS_FR4, kappa=2 * np.pi * 2.45e9 * EPS0 * EPS_FR4 * TAND_FR4)
fr4.AddBox([-20, -20, 0], [20, 0, H_FR4], priority=1)
gnd = CSX.AddMetal("gnd")
gnd.AddBox([-20, -20, 0], [-2, 0, 0], priority=10)          # bottom ground, left of the clearance
gnd.AddBox([2, -20, 0], [20, 0, 0], priority=10)            # right of the clearance
gnd.AddBox([-2, -20, 0], [2, -6, 0], priority=10)           # below the clearance (4 x 6 mm at the edge)
top = CSX.AddMetal("top")
z = H_FR4
land = [(-2, -0.6, -1, 0), (1, -0.6, 2, 0), (-2, -1.9, -1, -1.3), (1, -1.9, 2, -1.3)]   # maker's lands 1/2/1 x 0.6/0.7/0.6
for x0, y0, x1, y1 in land:
    top.AddBox([x0, min(y0, y1), z], [x1, max(y0, y1), z], priority=10)
# grounded lands: top strips out of the clearance and PEC vias to the bottom ground
for (x0, x1) in [(2, 3), (-3, -2)]:
    ys = (-0.6, 0) if x0 == 2 or True else None
    top.AddBox([x0, -0.6, z], [x1, 0, z], priority=10)
via_p = CSX.AddMetal("vias")
via_p.AddBox([2.4, -0.6, 0], [3.0, 0, z], priority=10)
via_p.AddBox([-3.0, -0.6, 0], [-2.4, 0, z], priority=10)
# lower right land (grounded) also strips out and via
top.AddBox([2, -1.9, z], [3, -1.3, z], priority=10)
via_p.AddBox([2.4, -1.9, 0], [3.0, -1.3, z], priority=10)
# feed line: 50 ohm microstrip 1.5 wide (y -2.2 to -0.7) from the left edge to x = -4.5, neck 0.4 wide to the feed land
top.AddBox([-20, -2.2, z], [-4.5, -0.7, z], priority=10)
top.AddBox([-4.5, -1.6, z], [-1.3, -1.2, z], priority=10)
top.AddBox([-1.3, -1.6, z], [-1.0, -1.2, z], priority=10)   # reaches into the feed land (land x -2 to -1, y -1.9 to -1.3)

# ------------------------------------------------ antenna (local origin: u along x, v along y, land surface z = 0.8, centre y = -1.0)
fr = chipant.Frame((0.0, -1.0, H_FR4), (1, 0, 0), (0, 1, 0), (0, 0, 1))
ant_m, ant_c = chipant.add_antenna(CSX, fr, EPS_R, TAND_CER)

# ------------------------------------------------ port: microstrip port at the board's left edge, 50 ohm, reference plane in the port middle

# ------------------------------------------------ mesh
MAXRES, RATIO = 2.0, 1.3
us, vs, ws = chipant.local_edges()
fx = set(np.round(np.arange(-3.5, 3.51, 0.1), 3)); fy = set(np.round(np.arange(-3.0, 0.51, 0.1), 3)); fz = set(np.round(np.arange(0.0, 2.81, 0.1), 3))
fx |= {-20, 20, -19, -15, -4.5, -3, -2, -1.3, -1.0, 2, 3, 2.4, 3.0}
fy |= {-20, 0, -6, -2.2, -0.7, -1.6, -1.2, -1.9, -1.3, -0.6}
fz |= {0, 0.2, 0.4, 0.6, 0.8}
MARG, PML = 18.0, 8 * MAXRES
fx |= set(np.round(np.arange(-19, -14.9, 0.5), 3))
fx |= {-20 - MARG - PML, 20 + MARG + PML}; fy |= {-20 - MARG - PML, 0 + MARG + PML}; fz |= {-MARG - PML, 2.0 + MARG + PML}
mesh.AddLine("x", sorted(fx)); mesh.AddLine("y", sorted(fy)); mesh.AddLine("z", sorted(fz))
port = FDTD.AddMSLPort(1, top, [-19, -2.2, H_FR4], [-15, -0.7, 0], "x", "z", excite=1, FeedShift=0.5, MeasPlaneShift=2.5, Feed_R=50, priority=20)
mesh.SmoothMeshLines("all", MAXRES, RATIO)
nx, ny, nz = (len(mesh.GetLines(d)) for d in (0, 1, 2))
nf2ff = FDTD.CreateNF2FFBox(frequency=NF_FREQ)
info = dict(tag=tag, eps_r=EPS_R, tand_ceramic=TAND_CER, fr4_h=H_FR4, fr4_eps=EPS_FR4, fr4_tand=TAND_FR4,
            lines_xyz=[nx, ny, nz], cells=int((nx - 1) * (ny - 1) * (nz - 1)), max_res_mm=MAXRES, ratio=RATIO,
            min_dx=[float(np.min(np.diff(mesh.GetLines(d)))) for d in (0, 1, 2)], nrts_cap=NRTS, end_criteria=1e-5,
            conductor_length_mm=chipant.conductor_length_mm(), threads=THREADS,
            start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
print(json.dumps(info))

if os.environ.get("SETUP_ONLY") == "1":
    FDTD.Run(Sim_Path, cleanup=True, setup_only=True, verbose=3)
    json.dump(info, open(os.path.join("/work/results", tag + "_setup.json"), "w"), indent=1, default=float)
    print("SETUP_ONLY done"); sys.exit(0)
if not POST_ONLY:
    t0 = time.time()
    FDTD.Run(Sim_Path, cleanup=True, numThreads=THREADS, verbose=2)
    info["run_seconds"] = time.time() - t0
    info["end_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ------------------------------------------------ post-processing
f = np.arange(2.0e9, 3.0e9 + 1, 5e6)
fe = np.union1d(f, np.array(NF_FREQ))
port.CalcPort(Sim_Path, fe, ref_impedance=50)
s11 = port.uf_ref / port.uf_inc
pacc = port.P_acc
np.savetxt(os.path.join("/work/results", tag + "_s11.csv"),
           np.c_[fe / 1e9, np.abs(s11), np.angle(s11, deg=True), 20 * np.log10(np.abs(s11)), pacc, port.P_inc],
           delimiter=",", header="f_GHz,abs_s11,phase_deg,s11_dB,P_acc_W,P_inc_W", comments="")
theta = np.arange(0, 181, 3.0); phi = np.arange(0, 360, 6.0)
res = nf2ff.CalcNF2FF(Sim_Path, NF_FREQ, theta, phi, center=[0, -1.0e-3, 1.4e-3], read_cached=False)
eff, gain, dmax = {}, {}, {}
for i, fq in enumerate(NF_FREQ):
    j = int(np.argmin(np.abs(fe - fq)))
    e = float(res.Prad[i] / pacc[j]); eff["%.2f" % (fq / 1e9)] = e
    dmax["%.2f" % (fq / 1e9)] = float(res.Dmax[i])
    gain["%.2f" % (fq / 1e9)] = float(10 * np.log10(res.Dmax[i] * e))
m = np.isin(fe, f); sc = ringsim_lib.score_h1(fe[m], s11[m], eff["2.44"], gain["2.44"])
info.update(dict(eff_by_ghz=eff, dmax_by_ghz=dmax, peak_gain_dbi_by_ghz=gain, score=sc,
                 s11_db_at={"%.3f" % (fq / 1e9): float(20 * np.log10(abs(s11[int(np.argmin(np.abs(fe - fq)))]))) for fq in [2.4e9, 2.44e9, 2.45e9, 2.5e9]}))
json.dump(info, open(os.path.join("/work/results", tag + ".json"), "w"), indent=1, default=float)
print("RESULT", json.dumps(sc, default=float))
