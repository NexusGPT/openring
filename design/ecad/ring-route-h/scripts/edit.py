# edit.py in out plan.txt : apply a plan of copper edits (model mm = KiCad - 100), refill zones, save.
# plan lines:  DELSEG net layer x1 y1 x2 y2   (either direction; must match exactly one track, else FAIL)
#              DELVIA net x y                  (must match exactly one via)
#              SEG net layer w x1 y1 x2 y2 [x3 y3 ...]   (a chain of tracks)
#              VIA net x y top bottom          (top/bottom: F In1 In2 B; 0.20/0.10)
import sys, pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1])
L = {"F": pcbnew.F_Cu, "In1": pcbnew.In1_Cu, "In2": pcbnew.In2_Cu, "B": pcbnew.B_Cu, "F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}
def V(x, y): return VECTOR2I(FromMM(float(x) + O), FromMM(float(y) + O))
def near(p, x, y): return abs(ToMM(p.x) - O - float(x)) < 0.0015 and abs(ToMM(p.y) - O - float(y)) < 0.0015
fail = 0; n = {"del": 0, "seg": 0, "via": 0}
for ln in open(sys.argv[3]):
    f = ln.split()
    if not f or f[0].startswith("#"): continue
    op = f[0]
    if op == "DELSEG":
        net, lay, x1, y1, x2, y2 = f[1:7]
        hit = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == net and t.GetLayer() == L[lay]
               and ((near(t.GetStart(), x1, y1) and near(t.GetEnd(), x2, y2)) or (near(t.GetStart(), x2, y2) and near(t.GetEnd(), x1, y1)))]
        if len(hit) != 1: print("FAIL", ln.strip(), "matches", len(hit)); fail += 1; continue
        b.Delete(hit[0]); n["del"] += 1
    elif op == "DELVIA":
        net, x, y = f[1:4]
        hit = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net and near(t.GetPosition(), x, y)]
        if len(hit) != 1: print("FAIL", ln.strip(), "matches", len(hit)); fail += 1; continue
        b.Delete(hit[0]); n["del"] += 1
    elif op == "SEG":
        net, lay, w = f[1], f[2], float(f[3]); pts = f[4:]
        ni = b.FindNet(net)
        if ni is None: print("FAIL no net", net); fail += 1; continue
        for i in range(0, len(pts) - 2, 2):
            t = pcbnew.PCB_TRACK(b); t.SetStart(V(pts[i], pts[i + 1])); t.SetEnd(V(pts[i + 2], pts[i + 3])); t.SetWidth(FromMM(w)); t.SetLayer(L[lay]); t.SetNet(ni); b.Add(t); n["seg"] += 1
    elif op == "VIA":
        net, x, y, top, bot = f[1:6]
        v = pcbnew.PCB_VIA(b); t, bo = L[top], L[bot]
        v.SetViaType(pcbnew.VIATYPE_THROUGH if (t, bo) == (pcbnew.F_Cu, pcbnew.B_Cu) else pcbnew.VIATYPE_BLIND if pcbnew.F_Cu in (t, bo) or pcbnew.B_Cu in (t, bo) else pcbnew.VIATYPE_BURIED)
        v.SetLayerPair(t, bo); v.SetPosition(V(x, y)); v.SetWidth(FromMM(0.2)); v.SetDrill(FromMM(0.1)); v.SetNet(b.FindNet(net)); b.Add(v); n["via"] += 1
    else:
        print("FAIL unknown op", ln.strip()); fail += 1
print("removed", n["del"], "added tracks", n["seg"], "added vias", n["via"], "failures", fail, flush=True)
if fail: print("NOT SAVED"); sys.exit(1)
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("refilled and saved", sys.argv[2], flush=True)
