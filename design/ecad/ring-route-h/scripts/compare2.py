# compare2.py base.kicad_pcb new.kicad_pcb base.kicad_dru new.kicad_dru  (route-h: board A2 against board A1; extends route-g's compare.py)
# Run with KiCad's Python (design/ecad/ring/pcb/run_kipy.sh). Model mm = KiCad mm - 100.
# Checks (each prints PASS or FAIL with the items that differ; exit 1 on any FAIL):
#  1 every footprint other than the eight parts (J1 and the 12 test pads included): same set, place, side, rotation, and pad nets
#  2 the eight parts C1 C2 C5 C7 C14 FB1 R71 R72: a on F.Cu (under face) with the base's pad nets; b the screen face (B.Cu) holds only
#    test pads (TP*); c their courtyards overlap no other courtyard, stay out of the ribbon-fold keep-free zones and the antenna zone, inside
#    the outline; d C7's DECA pad within 3.0 mm of U1 ball A8, plan view (the measure of board-notes-r2 step 13 gives 2.96 on A1) (each part's distance to its ball is printed)
#  3 antenna nets (ANT1_NODE ANT2_NODE ANT3_NODE RF_FEED ANT_TRIM) and USB pair (USB_DP USB_DN): tracks, vias and pads item for item identical
#  4 antenna copper-free zone X -13.60..-8.75, Y 3.10..6.30: the copper items (tracks, vias, pads) touching it are the same items as the base's
#    (the base keeps the antenna's own copper there), no other item touches it, and no zone fill there grows
#  5 layer count, stack (the board file's stackup block), board outline, rule areas, design rules (rules file bytes) unchanged
#  6 J1 courtyard: no overlap with any other courtyard on its face; inside the board outline
#  7 edge band: no track or via reaches beyond X -13.45 (X minus edge)
import sys, re, hashlib, collections, pcbnew
from pcbnew import ToMM
O = 100.0
RF = {"ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED", "ANT_TRIM"}; USB = {"USB_DP", "USB_DN"}
ZX0, ZX1, ZY0, ZY1 = -13.60, -8.75, 3.10, 6.30
J1POS, J1ROT = (-11.650, -0.150), 270.0
EDGE_X = -13.45
fails = []
def mm(v): return round(ToMM(v) - O, 4)
def P(p): return (mm(p.x), mm(p.y))
def W(v): return round(ToMM(v), 4)
def check(n, ok, msg):
    print("CHECK %s %s: %s" % (n, "PASS" if ok else "FAIL", msg), flush=True)
    if not ok: fails.append(n)
A = pcbnew.LoadBoard(sys.argv[1]); B = pcbnew.LoadBoard(sys.argv[2])
print("base", sys.argv[1]); print("new ", sys.argv[2])

def fpkey(b, m):
    pads = sorted((p.GetNumber(), P(p.GetPosition()), p.GetNetname()) for p in m.Pads())
    return (P(m.GetPosition()), b.GetLayerName(m.GetLayer()), round(m.GetOrientationDegrees() % 360, 3), tuple(pads))
fa = {m.GetReference(): fpkey(A, m) for m in A.GetFootprints()}
fb = {m.GetReference(): fpkey(B, m) for m in B.GetFootprints()}
EIGHT = ["C1", "C2", "C5", "C7", "C14", "FB1", "R71", "R72"]
others = sorted(r for r in set(fa) | set(fb) if r not in EIGHT)
bad = []
for r in others:
    if r not in fa or r not in fb: bad.append("%s missing in %s" % (r, "new" if r not in fb else "base")); continue
    a, c = fa[r], fb[r]
    why = [w for w, i in (("place", 0), ("side", 1), ("rotation", 2), ("pads", 3)) if a[i] != c[i]]
    if why: bad.append("%s %s: base %s %s %s, new %s %s %s" % (r, "/".join(why), a[0], a[1], a[2], c[0], c[1], c[2]))
check(1, not bad, "%d footprints other than the eight compared; differing: %s" % (len(others), bad if bad else "none"))

bad = []
for r in EIGHT:
    m0, m1 = A.FindFootprintByReference(r), B.FindFootprintByReference(r)
    n0 = sorted((p.GetNumber(), p.GetNetname()) for p in m0.Pads()); n1 = sorted((p.GetNumber(), p.GetNetname()) for p in m1.Pads())
    if m1.GetLayer() != pcbnew.F_Cu: bad.append("%s on %s" % (r, B.GetLayerName(m1.GetLayer())))
    if n0 != n1: bad.append("%s pad nets base %s new %s" % (r, n0, n1))
check("2a", not bad, "the eight parts on F.Cu (under face) with their base pad nets; problems: %s" % (bad if bad else "none"))
onb = sorted(m.GetReference() for m in B.GetFootprints() if m.GetLayer() == pcbnew.B_Cu)
notp = [r for r in onb if not r.startswith("TP")]
check("2b", not notp, "footprints on the screen face (B.Cu): %d, %s; not a test pad: %s" % (len(onb), " ".join(onb), notp if notp else "none"))
KEEP = [("fold +Y", -3.5, 3.4, -0.9, 5.6), ("fold -Y", -3.5, -5.6, -0.9, -3.4), ("antenna zone", ZX0, ZY0, ZX1, ZY1)]
def ext(ps):
    pts = [ps.COutline(o).CPoint(i) for o in range(ps.OutlineCount()) for i in range(ps.COutline(o).PointCount())]
    return (min(ToMM(p.x) for p in pts), max(ToMM(p.x) for p in pts), min(ToMM(p.y) for p in pts), max(ToMM(p.y) for p in pts))
bad = []; ob_ = B.GetBoardEdgesBoundingBox()
for r in EIGHT:
    m = B.FindFootprintByReference(r); c = m.GetCourtyard(m.GetLayer())
    if c.OutlineCount() == 0: bad.append("%s no courtyard" % r); continue
    for o in B.GetFootprints():
        if o.GetReference() == r or o.GetLayer() != m.GetLayer(): continue
        oc = o.GetCourtyard(o.GetLayer())
        if oc.OutlineCount() == 0: continue
        x = pcbnew.SHAPE_POLY_SET(c); x.BooleanIntersection(oc)
        if x.Area() > 0: bad.append("%s overlaps %s (%.4f mm2)" % (r, o.GetReference(), x.Area() / 1e12))
    l, rr, t, bo = [v - O for v in ext(c)]
    for name, kx0, ky0, kx1, ky1 in KEEP:
        if m.GetLayer() == pcbnew.F_Cu and l < kx1 and rr > kx0 and t < ky1 and bo > ky0: bad.append("%s in %s" % (r, name))
    if l < mm(ob_.GetLeft()) or rr > mm(ob_.GetRight()) or t < mm(ob_.GetTop()) or bo > mm(ob_.GetBottom()): bad.append("%s outside outline" % r)
check("2c", not bad, "courtyards of the eight: overlaps, keep-free zones, outline; problems: %s" % (bad if bad else "none"))
u1 = B.FindFootprintByReference("U1"); u2 = B.FindFootprintByReference("U2")
balls = {(f.GetReference() + "." + p.GetNumber()): (P(p.GetPosition()), p.GetNetname()) for f in (u1, u2) for p in f.Pads()}
a8 = balls["U1.A8"][0]; c7 = [P(q.GetPosition()) for q in B.FindFootprintByReference("C7").Pads() if q.GetNetname() == "DECA"][0]
import math
dc7 = math.hypot(c7[0] - a8[0], c7[1] - a8[1])
rep = []
for r in EIGHT:
    m = B.FindFootprintByReference(r)
    for p in m.Pads():
        if p.GetNetname() == "GND": continue
        q = P(p.GetPosition()); best = min((math.hypot(q[0] - v[0][0], q[1] - v[0][1]), k) for k, v in balls.items() if v[1] == p.GetNetname()) if any(v[1] == p.GetNetname() for v in balls.values()) else (float("nan"), "-")
        rep.append("%s.%s %s (%.3f,%.3f) nearest ball %s %.3f mm" % (r, p.GetNumber(), p.GetNetname(), q[0], q[1], best[1], best[0]))
check("2d", dc7 <= 3.0, "C7 DECA pad (%.3f,%.3f) to U1 A8 (%.3f,%.3f): %.3f mm (limit 3.0); pad to ball, plan view: %s" % (c7[0], c7[1], a8[0], a8[1], dc7, "; ".join(rep)))
j = B.FindFootprintByReference("J1")
def items(b, nets):
    out = []
    for t in b.GetTracks():
        if t.GetNetname() not in nets: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            out.append(("via", t.GetNetname(), P(t.GetPosition()), b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer()), W(t.GetWidth(pcbnew.F_Cu)) , W(t.GetDrillValue()), t.IsLocked()))
        else:
            out.append(("track", t.GetNetname(), P(t.GetStart()), P(t.GetEnd()), b.GetLayerName(t.GetLayer()), W(t.GetWidth()), t.IsLocked()))
    for m in b.GetFootprints():
        for p in m.Pads():
            if p.GetNetname() in nets:
                out.append(("pad", p.GetNetname(), m.GetReference(), p.GetNumber(), P(p.GetPosition()), W(p.GetSize(pcbnew.F_Cu).x), W(p.GetSize(pcbnew.F_Cu).y), ",".join(b.GetLayerName(l) for l in p.GetLayerSet().CuStack())))
    return sorted(out, key=repr)
for tag, S in (("3a antenna nets", RF), ("3b USB pair", USB)):
    x, y = items(A, S), items(B, S)
    cx, cy = collections.Counter(map(repr, x)), collections.Counter(map(repr, y))
    check(tag.split()[0], x == y, "%s: base %d items, new %d items, only in base %s, only in new %s" % (tag[3:], len(x), len(y), list((cx - cy).elements())[:5], list((cy - cx).elements())[:5]))

def boxhit(bb):
    return not (mm(bb.GetRight()) <= ZX0 or mm(bb.GetLeft()) >= ZX1 or mm(bb.GetBottom()) <= ZY0 or mm(bb.GetTop()) >= ZY1)
def zone_items(b):
    out = []
    for t in b.GetTracks():
        if boxhit(t.GetBoundingBox()):
            if t.Type() == pcbnew.PCB_VIA_T: out.append(("via", t.GetNetname(), P(t.GetPosition())))
            else: out.append(("track", t.GetNetname(), b.GetLayerName(t.GetLayer()), P(t.GetStart()), P(t.GetEnd())))
    for m in b.GetFootprints():
        for p in m.Pads():
            if p.GetLayerSet().CuStack() and boxhit(p.GetBoundingBox()): out.append(("pad", m.GetReference(), p.GetNumber(), p.GetNetname()))
    return sorted(out, key=repr)
za, zb = zone_items(A), zone_items(B)
nets = sorted(set(i[1] if i[0] != "pad" else i[3] for i in zb))
check("4a", za == zb, "copper items touching the antenna zone (bounding box test): base %d, new %d, identical %s; nets there %s; items in new not in base: %s" % (len(za), len(zb), za == zb, nets, [i for i in zb if i not in za]))
def fill_area(b):
    box = pcbnew.SHAPE_POLY_SET(); box.NewOutline()
    for (x, y) in ((ZX0, ZY0), (ZX1, ZY0), (ZX1, ZY1), (ZX0, ZY1)): box.Append(pcbnew.FromMM(x + O), pcbnew.FromMM(y + O))
    res = {}
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        for l in z.GetLayerSet().CuStack():
            f = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(l)); f.BooleanIntersection(box)
            res[b.GetLayerName(l)] = res.get(b.GetLayerName(l), 0) + f.Area() / 1e12
    return res
fa_, fb_ = fill_area(A), fill_area(B)
grow = {k: (round(fa_.get(k, 0), 4), round(v, 4)) for k, v in fb_.items() if v > fa_.get(k, 0) + 1e-6}
check("4b", not grow, "zone fill inside the antenna zone (mm2 per layer) base %s new %s; grown: %s" % ({k: round(v, 4) for k, v in fa_.items()}, {k: round(v, 4) for k, v in fb_.items()}, grow if grow else "none"))

def block(path, word):
    s = open(path).read(); i = s.find("(" + word); d = 0
    for k in range(i, len(s)):
        d += s[k] == "("; d -= s[k] == ")"
        if d == 0: return s[i:k + 1]
sa, sb = block(sys.argv[1], "stackup"), block(sys.argv[2], "stackup")
check("5a", A.GetCopperLayerCount() == B.GetCopperLayerCount() and sa == sb and sa is not None,
      "copper layers base %d new %d; stackup block %d chars, identical %s; board thickness base %.3f new %.3f" % (A.GetCopperLayerCount(), B.GetCopperLayerCount(), len(sa or ""), sa == sb, ToMM(A.GetDesignSettings().GetBoardThickness()), ToMM(B.GetDesignSettings().GetBoardThickness())))
def outline(b): return sorted((d.GetShape(), P(d.GetStart()), P(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts)
def rareas(b):
    return sorted((z.GetZoneName(), tuple(b.GetLayerName(l) for l in z.GetLayerSet().CuStack()), tuple(P(z.Outline().CVertex(i)) for i in range(z.Outline().TotalVertices())),
                   z.GetDoNotAllowTracks(), z.GetDoNotAllowVias(), z.GetDoNotAllowPads(), z.GetDoNotAllowFootprints(), z.GetDoNotAllowZoneFills()) for z in b.Zones() if z.GetIsRuleArea())
oa, ob, ra, rb = outline(A), outline(B), rareas(A), rareas(B)
check("5b", oa == ob and ra == rb, "board outline %d shapes identical %s; rule areas base %d new %d identical %s (%s)" % (len(oa), oa == ob, len(ra), len(rb), ra == rb, ", ".join(r[0] for r in rb)))
ha, hb = hashlib.sha256(open(sys.argv[3], "rb").read()).hexdigest(), hashlib.sha256(open(sys.argv[4], "rb").read()).hexdigest()
check("5c", ha == hb, "rules file sha256 base %s new %s" % (ha[:16], hb[:16]))
import os
pa, pb = sys.argv[1][:-len(".kicad_pcb")] + ".kicad_pro", sys.argv[2][:-len(".kicad_pcb")] + ".kicad_pro"
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest() if os.path.exists(f) else "missing"
check("5e", sha(pa) == sha(pb) != "missing", "project file beside each board (holds the board minimum rules and net classes): base %s %s, new %s %s" % (os.path.basename(pa), sha(pa)[:16], os.path.basename(pb), sha(pb)[:16]))
da, db = A.GetDesignSettings(), B.GetDesignSettings()
ka = (da.m_MinClearance, da.m_TrackMinWidth, da.m_ViasMinSize, da.m_MinThroughDrill, da.m_CopperEdgeClearance, da.m_HoleToHoleMin, da.m_HoleClearance)
kb = (db.m_MinClearance, db.m_TrackMinWidth, db.m_ViasMinSize, db.m_MinThroughDrill, db.m_CopperEdgeClearance, db.m_HoleToHoleMin, db.m_HoleClearance)
check("5d", ka == kb, "board minimum rules (clearance, track, via, drill, edge, hole to hole, hole clearance) base %s new %s" % ([ToMM(v) for v in ka], [ToMM(v) for v in kb]))

def ext(ps):
    pts = [ps.COutline(o).CPoint(i) for o in range(ps.OutlineCount()) for i in range(ps.COutline(o).PointCount())]
    return (min(ToMM(p.x) for p in pts), max(ToMM(p.x) for p in pts), min(ToMM(p.y) for p in pts), max(ToMM(p.y) for p in pts))
cyj = j.GetCourtyard(j.GetLayer()); hits = []; near = (9e9, "")
for m in B.GetFootprints():
    if m.GetReference() == "J1" or m.GetLayer() != j.GetLayer(): continue
    c = m.GetCourtyard(m.GetLayer())
    if c.OutlineCount() == 0: continue
    x = pcbnew.SHAPE_POLY_SET(cyj); x.BooleanIntersection(c)
    if x.Area() > 0: hits.append((m.GetReference(), round(x.Area() / 1e12, 5)))
    (jl, jr, jt, jb_), (ml, mr, mt, mb) = ext(cyj), ext(c)
    gx = max(ml - jr, jl - mr); gy = max(mt - jb_, jt - mb)
    g = max(gx, gy)
    if g < near[0]: near = (round(g, 4), m.GetReference())
jl, jr, jt, jb_ = ext(cyj); ob_ = B.GetBoardEdgesBoundingBox()
inside = jl >= ToMM(ob_.GetLeft()) and jr <= ToMM(ob_.GetRight()) and jt >= ToMM(ob_.GetTop()) and jb_ <= ToMM(ob_.GetBottom())
check("6", not hits and inside, "J1 courtyard polygon x %.4f..%.4f y %.4f..%.4f; overlap area with other %s courtyards: %s; nearest courtyard %s, gap %.4f mm (polygon extents); board outline x %.3f..%.3f y %.3f..%.3f, courtyard inside %s, %.4f mm from the X minus edge"
      % (jl - O, jr - O, jt - O, jb_ - O, B.GetLayerName(j.GetLayer()), hits if hits else "none", near[1], near[0], mm(ob_.GetLeft()), mm(ob_.GetRight()), mm(ob_.GetTop()), mm(ob_.GetBottom()), inside, jl - ToMM(ob_.GetLeft())))

beyond = []
for t in B.GetTracks():
    if mm(t.GetBoundingBox().GetLeft()) < EDGE_X - 1e-4: beyond.append((t.GetNetname(), "via" if t.Type() == pcbnew.PCB_VIA_T else "track", mm(t.GetBoundingBox().GetLeft())))
lx = min(mm(t.GetBoundingBox().GetLeft()) for t in B.GetTracks())
check("7", not beyond, "tracks and vias beyond X %.2f: %s; leftmost copper edge of any track or via X %.3f" % (EDGE_X, beyond if beyond else "none", lx))
print("RESULT", "PASS" if not fails else "FAIL %d: %s" % (len(fails), " ".join(map(str, fails))))
sys.exit(1 if fails else 0)
