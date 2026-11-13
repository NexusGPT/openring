#!/usr/bin/env python3
"""Glue between the board file and grid_router (run with KiCad's Python).
  route_io.py export <unrouted.kicad_pcb> <route_in.txt>
  route_io.py import <unrouted.kicad_pcb> <route_out.txt> <routed.kicad_pcb>
Net classes (track width): see build_boards.py (P_WIDE, P_MED, P_3V3, TRACK)."""
import json, os, sys
import pcbnew
from pcbnew import ToMM, FromMM, VECTOR2I
import geom
import build_boards as BB

HERE = os.path.dirname(os.path.abspath(__file__))
PITCH = 0.05
X0, Y0 = 97.0, 79.0
NX = int((124.5 - X0) / PITCH) + 1
NY = int((119.0 - Y0) / PITCH) + 1
WIDTHS = [BB.TRACK, BB.P_3V3, BB.P_MED, BB.P_WIDE]
LAYER_BIT = {pcbnew.F_Cu: 1, pcbnew.In1_Cu: 2, pcbnew.In2_Cu: 4, pcbnew.B_Cu: 8}
LAYER_OF_IDX = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
EXCLUDE_TERMS = {("U1", "61"), ("U2", "25"), ("J1", "SH")}


def net_class(name):
    if name in BB.WIDE_NETS:
        return 3
    if name in BB.MED_NETS:
        return 2
    if name in BB.NET_3V3:
        return 1
    return 0


def layers_mask(pad):
    m = 0
    for l, bit in LAYER_BIT.items():
        if pad.IsOnLayer(l):
            m |= bit
    return m


GND_MODE = os.environ.get("GND_MODE", "all")      # all | skip | only:<file of "ref pad" lines>


def gnd_only_set():
    if GND_MODE.startswith("only:"):
        return {tuple(l.split()[:2]) for l in open(GND_MODE[5:]) if l.strip()}
    return None


def do_export(src, dst):
    b = pcbnew.LoadBoard(src)
    only = gnd_only_set()
    names = sorted({n.GetNetname() for n in b.GetNetsByNetcode().values() if n.GetNetname()})
    nid = {n: i for i, n in enumerate(names)}
    out = []
    out.append("P %.4f %.4f %.4f %d %d" % (X0, Y0, PITCH, NX, NY))
    out.append("W 4 %s" % " ".join("%.3f" % w for w in WIDTHS))
    out.append("C %.3f %.3f %.3f %.3f %.3f" % (BB.CLEAR, BB.VIA_P / 2, BB.VIA_D / 2, BB.HOLE_CLEAR, BB.EDGE_CLEAR))
    for n in names:
        out.append("N %d %d %s" % (nid[n], net_class(n), n.replace(" ", "_")))
    for (u, d) in BB.pcb1_outline_points():
        out.append("G %.4f %.4f" % (BB.OX + u, BB.OY + d))
    u0, d0, u1, d1 = geom.ANT_KEEPOUT
    out.append("K 15 %.4f %.4f %.4f %.4f" % (BB.OX + u0, BB.OY + d0, BB.OX + u1, BB.OY + d1))
    nterm = 0
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        if ref == "BT1":
            continue
        for p in fp.Pads():
            num = p.GetNumber()
            netname = p.GetNetname()
            net = nid.get(netname, -1)
            ds = p.GetDrillSize()
            attr = p.GetAttribute()
            if ds.x > 0:
                out.append("%s %.4f %.4f %.4f %.4f" % ("Q" if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else "H", ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(ds.x) / 2, ToMM(ds.y) / 2))
            if attr == pcbnew.PAD_ATTRIB_NPTH:
                continue
            m = layers_mask(p)
            if m == 0:
                continue
            bb = p.GetBoundingBox()
            x0, y0, x1, y1 = ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom())
            if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
                out.append("O %d %d %.4f %.4f %.4f" % (m, net, ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(p.GetSize().x) / 2))
            else:
                out.append("R %d %d %.4f %.4f %.4f %.4f" % (m, net, x0, y0, x1, y1))
            is_term = net >= 0 and (ref, num) not in EXCLUDE_TERMS and not (netname == "GND" and attr == pcbnew.PAD_ATTRIB_PTH)
            if os.environ.get("ONLY_NETS"):
                is_term = is_term and netname in os.environ["ONLY_NETS"].split(",")
            elif only is not None:
                is_term = is_term and netname == "GND" and (ref, num) in only
            elif GND_MODE == "skip" and netname == "GND":
                is_term = False
            if ref in ("WP1", "WP2", "WP3", "WP4", "WP7"):
                is_term = False
            if is_term:
                if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
                    cx, cy, r = ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(p.GetSize().x) / 2
                    out.append("T %d %d %d %.4f %.4f %.4f %.4f" % (net, nterm, m, cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7))
                else:
                    sx = 0.075 if (x1 - x0) >= 0.2 else (x1 - x0) / 2 - 0.0
                    sy = 0.075 if (y1 - y0) >= 0.2 else (y1 - y0) / 2 - 0.0
                    out.append("T %d %d %d %.4f %.4f %.4f %.4f" % (net, nterm, m, x0 + sx, y0 + sy, x1 - sx, y1 - sy))
                nterm += 1
    for t in b.GetTracks():
        n = nid.get(t.GetNetname(), -1)
        if t.Type() == pcbnew.PCB_VIA_T:
            for bit in (1, 2, 4, 8):
                pass
            out.append("O 15 %d %.4f %.4f %.4f" % (n, ToMM(t.GetPosition().x), ToMM(t.GetPosition().y), ToMM(t.GetWidth()) / 2))
            out.append("H %.4f %.4f %.4f %.4f" % (ToMM(t.GetPosition().x), ToMM(t.GetPosition().y), ToMM(t.GetDrillValue()) / 2, ToMM(t.GetDrillValue()) / 2))
        else:
            a, c = t.GetStart(), t.GetEnd()
            w = ToMM(t.GetWidth()) / 2
            out.append("R %d %d %.4f %.4f %.4f %.4f" % (LAYER_BIT[t.GetLayer()], n, min(ToMM(a.x), ToMM(c.x)) - w, min(ToMM(a.y), ToMM(c.y)) - w, max(ToMM(a.x), ToMM(c.x)) + w, max(ToMM(a.y), ToMM(c.y)) + w))
    open(dst, "w").write("\n".join(out) + "\n")
    print("exported", len(names), "nets", nterm, "terminals to", dst)


def do_import(src, res, dst):
    b = pcbnew.LoadBoard(src)
    nets = {n.GetNetname(): n for n in b.GetNetsByNetcode().values()}
    cur = None
    segs = {}
    vias = []
    unrouted = []
    summary = ""
    for line in open(res):
        t = line.split()
        if not t:
            continue
        if t[0] == "NET":
            cur = t[2]
            segs.setdefault(cur, [])
        elif t[0] == "S":
            segs[cur].append((int(t[1]), float(t[2]), float(t[3]), float(t[4]), float(t[5])))
        elif t[0] == "V":
            vias.append((cur, float(t[1]), float(t[2])))
        elif t[0] == "UNROUTED":
            unrouted.append(line.strip())
        elif t[0] == "SUMMARY":
            summary = line.strip()
    ntr = 0
    for name, sl in segs.items():
        w = WIDTHS[net_class(name)]
        # merge collinear continuing segments on the same layer
        sl = list(sl)
        merged = []
        for (l, x1, y1, x2, y2) in sl:
            if merged:
                (ml, mx1, my1, mx2, my2) = merged[-1]
                if ml == l and abs(mx2 - x1) < 1e-6 and abs(my2 - y1) < 1e-6:
                    dx1, dy1 = mx2 - mx1, my2 - my1
                    dx2, dy2 = x2 - x1, y2 - y1
                    if abs(dx1 * dy2 - dy1 * dx2) < 1e-9 and dx1 * dx2 + dy1 * dy2 > 0:
                        merged[-1] = (ml, mx1, my1, x2, y2)
                        continue
            merged.append((l, x1, y1, x2, y2))
        for (l, x1, y1, x2, y2) in merged:
            BB.track(b, VECTOR2I(FromMM(x1), FromMM(y1)), VECTOR2I(FromMM(x2), FromMM(y2)), LAYER_OF_IDX[l], w, nets[name])
            ntr += 1
    seen = set()
    for name, x, y in vias:
        key = (name, round(x, 3), round(y, 3))
        if key in seen:
            continue
        seen.add(key)
        BB.via(b, VECTOR2I(FromMM(x), FromMM(y)), nets[name])
    pcbnew.SaveBoard(dst, b)
    print("imported %d tracks, %d vias; %s; unrouted lines %d" % (ntr, len(seen), summary, len(unrouted)))
    for u in unrouted:
        print(u)


if __name__ == "__main__":
    if sys.argv[1] == "export":
        do_export(sys.argv[2], sys.argv[3])
    else:
        do_import(sys.argv[2], sys.argv[3], sys.argv[4])
