"""Why copper lengths differ from band_calc: print, at US 13, the copper path of 4 nets, segment by segment."""
import heapq, os, sys
os.environ["WIRING_NO_DRC"] = "1"
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring"))
import build_wiring as bw
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/band"))
import band_layout as L
print("band_layout U_NEAR", L.U_NEAR, "U_FAR", L.U_FAR)
cases = [("FLEX1", "VMOT", ("J_BAND_A", "7"), ("M1", "1")), ("FLEX1", "GND", ("J_BAND_A", "6"), ("M1", "2")),
         ("FLEX2", "VBAT", ("J_BAND_B", "1"), ("PRT1", "1")), ("FLEX2", "GND", ("J_BAND_B", "2"), ("PRT1", "2"))]
for flex, net, A, B in cases:
    rel = bw.FLEX[flex].format(13)
    bd = bw.board(rel)
    adj = bw.copper_graph(rel, net)
    src, dst = ("P",) + A, ("P",) + B
    dist, prev = {src: 0.0}, {}
    h = [(0.0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]:
            continue
        for v, w in adj.get(u, []):
            if d + w < dist.get(v, 1e18) - 1e-12:
                dist[v] = d + w; prev[v] = u; heapq.heappush(h, (d + w, v))
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    path.reverse()
    tr = [t for t in bd["tracks"] if t["net"] == net]
    used = sorted({n[1] for n in path if n[0] in ("T",)} | {n[1] for n in path if n[0] == "X"} | {n[2] for n in path if n[0] == "X"})
    pa, pb = bd["pads"][A][0], bd["pads"][B][0]
    print("\n%s %s %s:%s -> %s:%s  path (copper outside the pads, my csv value) %.3f mm" % (flex, net, A[0], A[1], B[0], B[1], dist[dst]))
    print("  pad centres: %s (%.3f, %.3f) size %s ; %s (%.3f, %.3f) size %s ; straight x distance %.3f" % (
        A, pa["x"], pa["y"], tuple(round(v / 1e6, 3) for v in (pa["obj"].GetSize().x, pa["obj"].GetSize().y)),
        B, pb["x"], pb["y"], tuple(round(v / 1e6, 3) for v in (pb["obj"].GetSize().x, pb["obj"].GetSize().y)), abs(pb["x"] - pa["x"])))
    print("  nodes:", " ".join(str(n) for n in path))
    tot = 0.0
    for i in sorted({n[1] for n in path if n[0] == "T"}):
        t = tr[i]; tot += t["len"]
        print("  track %d %s %s -> %s w %.2f len %.3f" % (i, t["layer"], t["a"], t["b"], t["w"], t["len"]))
    print("  sum of full tracks touched by the path: %.3f" % tot)
    vs = [v for v in bd["vias"] if v["net"] == net]
    for n in path:
        if n[0] == "V":
            print("  via %d at (%.3f, %.3f)" % (n[1], vs[n[1]]["x"], vs[n[1]]["y"]))
    for u, v in zip(path, path[1:]):
        w = [w for x, w in adj[u] if x == v]
        print("  step %s -> %s %.3f" % (u, v, min(w)))
