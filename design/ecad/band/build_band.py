#!/usr/bin/env python3
"""Writes the 14 flat board files of the band flexible circuits:
   flex1-us7.kicad_pcb ... flex1-us13.kicad_pcb (FLEX1, joystick side) and flex2-us7 ... flex2-us13 (FLEX2, cell side).

Run with KiCad's own Python:  ../ring/pcb/run_kipy.sh build_band.py [us ...]
Frames: see band_layout.py.  Each board is the FLAT tail, looked at from the outer face (F.Cu = outer face: lands toward the board,
switches, motor, protection circuit; B.Cu = inner face: charging pads).  KiCad x = OX + u, y = OY + s * v  (s = -1 FLEX1, +1 FLEX2).
Length of each tail: band_geom.py (formulas of design/mech/thin/thin.py, checked against the STEP files by measure_step.py).
"""
import csv, json, math, os, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import band_geom as G
import band_layout as L

LIBDIR = os.path.join(HERE, "OpenRingBand.pretty")
NETLIST = os.path.join(os.path.dirname(HERE), "ring", "netlist.csv")
OUTDIR = HERE
OX, OY = 50.0, 80.0
mm = FromMM

# ---------------------------------------------------------------- widths (mm)
W_SIG, W_HEAD_G, W_PWR, W_STUB = 0.08, 0.10, 0.20, 0.08
W_LAND_STUB = 0.08

# lanes in the neck (v = X + 2.5)
V1_B = dict(DOWN=-0.55, LEFT=-0.365, GND=0.07, UP=0.365, RIGHT=0.55)         # FLEX1 B.Cu
V1_F = dict(CENTRE=-0.54, VMOT=0.07)                                        # FLEX1 F.Cu
V1_HEAD = dict(DOWN=-0.35, LEFT=-0.165, GND=0.085, UP=0.285, RIGHT=0.47, CENTRE=-0.12)  # lanes inside the head (x = v - 2.5)
V2_B = dict(VBAT=-0.375, NTC=-0.08, GND=0.18)                              # FLEX2 B.Cu
V2_F = dict(DP=0.18, DN=0.36, VBUS=0.55, GND=-0.375)                       # FLEX2 F.Cu
LAND2_V = -0.375                                                            # centre of the PRT1 lands (width 0.45)

# solder paste on the disc lands (design/mfg/assembly/process.md section P8 change C2): four round openings per land,
# 0.58 mm across, centred 0.49 mm from the land centre on the diagonals (clear of the via 0.30 at the land centre)
PASTE_DISC_D, PASTE_DISC_OFF = 0.58, 0.49
# drawing of the board end (process.md P8 change C13): detail of the foot, K times the main view
DET_K, DET_V0 = 4.0, -14.0

MOT_V = 0.07
MOT_PITCH = 1.0
STIFF_FOOT_U1 = 1.65

pin_net = {}
with open(NETLIST, newline="") as f:
    for r in csv.DictReader(f):
        pin_net[(r["reference"], r["pin_number"])] = r["net"]


class Board:
    def __init__(self, kind, us):
        self.kind, self.us = kind, us
        self.s = -1 if kind == "FLEX1" else 1
        self.S = G.Size(us)
        self.b = pcbnew.BOARD()
        self.nets = {}
        self.info = {}
        self.fps = {}

    # ---- geometry helpers
    def P(self, u, v):
        return VECTOR2I(mm(OX + u), mm(OY + self.s * v))

    def net(self, name):
        if name not in self.nets:
            n = pcbnew.NETINFO_ITEM(self.b, name)
            self.b.Add(n)
            self.nets[name] = n
        return self.nets[name]

    def track(self, layer, net, pts, w):
        for (u0, v0), (u1, v1) in zip(pts[:-1], pts[1:]):
            if abs(u0 - u1) < 1e-9 and abs(v0 - v1) < 1e-9:
                continue
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(self.P(u0, v0)); t.SetEnd(self.P(u1, v1))
            t.SetWidth(mm(w)); t.SetLayer(pcbnew.F_Cu if layer == "F" else pcbnew.B_Cu)
            t.SetNet(self.net(net))
            self.b.Add(t)

    def via(self, net, u, v):
        x = pcbnew.PCB_VIA(self.b)
        x.SetPosition(self.P(u, v))
        x.SetViaType(pcbnew.VIATYPE_THROUGH)
        x.SetWidth(mm(L.RULES["via_dia"]))
        x.SetDrill(mm(L.RULES["via_drill"]))
        x.SetNet(self.net(net))
        for fn in ("SetFrontTentingMode", "SetBackTentingMode"):
            if hasattr(x, fn) and hasattr(pcbnew, "TENTING_MODE_TENTED"):
                getattr(x, fn)(pcbnew.TENTING_MODE_TENTED)
        self.b.Add(x)

    def place(self, ref, name, u, v, rot=0.0):
        fp = pcbnew.FootprintLoad(LIBDIR, name)
        assert fp is not None, name
        fp.SetReference(ref)
        fp.SetPosition(self.P(u, v))
        if rot:
            fp.SetOrientationDegrees(rot)
        self.fps[ref] = fp
        return fp

    def pad_uv(self, ref, num):
        fp = self.fps[ref]
        for p in fp.Pads():
            if p.GetNumber() == str(num):
                pos = p.GetPosition()
                return ToMM(pos.x) - OX, self.s * (ToMM(pos.y) - OY)
        raise KeyError((ref, num))

    def setnet_pad(self, ref, num, net):
        for p in self.fps[ref].Pads():
            if p.GetNumber() == str(num):
                p.SetNet(self.net(net))
                return
        raise KeyError((ref, num))

    def seg(self, layer, p0, p1, w=0.05):
        s = pcbnew.PCB_SHAPE(self.b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(layer)
        s.SetStart(self.P(*p0)); s.SetEnd(self.P(*p1)); s.SetWidth(mm(w))
        self.b.Add(s)
        return s

    def text(self, layer, u, v, txt, h=0.5):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(txt); t.SetLayer(layer)
        t.SetPosition(self.P(u, v))
        t.SetTextSize(VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(h / 8))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        self.b.Add(t)

    def textp(self, x, y, txt, h, hj="left", angle=0.0, layer=None):
        """text at a page point (KiCad mm, x right, y down); hj left, centre or right"""
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(txt); t.SetLayer(pcbnew.Dwgs_User if layer is None else layer)
        t.SetPosition(VECTOR2I(mm(x), mm(y)))
        t.SetTextSize(VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(h / 8))
        t.SetHorizJustify({"left": pcbnew.GR_TEXT_H_ALIGN_LEFT, "centre": pcbnew.GR_TEXT_H_ALIGN_CENTER,
                           "right": pcbnew.GR_TEXT_H_ALIGN_RIGHT}[hj])
        if angle:
            t.SetTextAngleDegrees(angle)
        self.b.Add(t)

    def segp(self, p0, p1, w=0.03, layer=None):
        s = pcbnew.PCB_SHAPE(self.b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Dwgs_User if layer is None else layer)
        s.SetStart(VECTOR2I(mm(p0[0]), mm(p0[1]))); s.SetEnd(VECTOR2I(mm(p1[0]), mm(p1[1]))); s.SetWidth(mm(w))
        self.b.Add(s)

    def page(self, u, v):
        return OX + u, OY + self.s * v

    def paste_disc(self, layer, u, v, d):
        """round paste opening as a filled circle drawn on the paste layer (a board graphic, not a pad: the wiring check
        design/wiring/check_wiring.py counts every pad of a band board, and the land keeps its single pad)"""
        c = pcbnew.PCB_SHAPE(self.b)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE); c.SetLayer(layer); c.SetFilled(True); c.SetWidth(0)
        c.SetStart(self.P(u, v)); c.SetEnd(self.P(u + d / 2, v))
        self.b.Add(c)

    def poly(self, layer, pts, w=0.05):
        for a, b in zip(pts, pts[1:] + pts[:1]):
            self.seg(layer, a, b, w)

    def dash(self, p0, p1, layer=pcbnew.Dwgs_User):
        s = self.seg(layer, p0, p1, 0.05)
        try:
            s.SetLineStyle(pcbnew.LINE_STYLE_DASH)
        except Exception:
            pass

    def dim(self, p0, p1, h, layer=pcbnew.Dwgs_User):
        d = pcbnew.PCB_DIM_ALIGNED(self.b)
        d.SetLayer(layer)
        d.SetStart(self.P(*p0)); d.SetEnd(self.P(*p1))
        d.SetHeight(mm(h))
        d.SetUnitsMode(pcbnew.DIM_UNITS_MODE_MM)
        d.SetUnitsFormat(pcbnew.DIM_UNITS_FORMAT_BARE_SUFFIX)
        d.SetPrecision(pcbnew.DIM_PRECISION_X_XX)
        d.SetTextSize(VECTOR2I(mm(0.45), mm(0.45)))
        d.SetLineThickness(mm(0.04))
        self.b.Add(d)


# ---------------------------------------------------------------- common pieces
def tangent(theta_deg):
    return G.RC * math.tan(math.radians(theta_deg) / 2)


def foot_lands(B, table, ref):
    fpname = "J_BAND_A_TAIL" if B.kind == "FLEX1" else "J_BAND_B_TAIL"
    fp = B.place(ref, fpname, 0.9, 0.25)
    for pin, (nm, net, row, col) in table.items():
        B.setnet_pad(ref, pin, net)


def foot_common(B, table):
    """stub from each far-row land to its via in the gap"""
    for pin, (nm, net, row, col) in table.items():
        u, v = L.land_tail_uv(table, pin)
        if row == "far":
            B.track("F", net, [(u, v), (L.U_VIA, v)], W_LAND_STUB)
            B.via(net, L.U_VIA, v)


def outline(B):
    S = B.S
    u_n0 = G.LF + G.LARC
    if B.kind == "FLEX1":
        h0, h1 = S.u_head0, S.u_head1
        pts = [(0, -1.0), (0, 1.5), (G.LF, 1.5), (u_n0, 0.9), (h0 - 0.3, 0.9), (h0, 1.2), (h0, 5.7), (h1, 5.7), (h1, -0.7), (h0, -0.7),
               (h0 - 0.2, -0.9), (u_n0, -0.9), (G.LF, -1.0)]
    else:
        lo, hi = S.u_j + S.s_lo, S.u_j + S.s_hi
        pts = [(0, -1.0), (0, 1.5), (G.LF, 1.5), (u_n0, 0.9), (lo - 0.3, 0.9), (lo, 1.2), (lo, 2.75), (hi, 2.75), (hi, -0.9), (u_n0, -0.9),
               (G.LF, -1.0)]
    return pts


def draw_common(B, pts):
    B.poly(pcbnew.Edge_Cuts, pts, 0.05)
    S = B.S
    u_n0 = G.LF + G.LARC
    # fold lines (Dwgs.User): board fold A (90 deg), slot bend B
    tj = tangent(90 - S.a_in)
    B.dash((G.LF, -1.2), (G.LF, 1.7)); B.dash((u_n0, -1.2), (u_n0, 1.2))
    B.text(pcbnew.Dwgs_User, G.LF + 0.05, -4.3, "FOLD A: 90 deg, inner radius 0.70, outer face (F.Cu) out", 0.3)
    B.dash((S.u_j - tj, -1.2), (S.u_j - tj, 1.2)); B.dash((S.u_j + tj, -1.2), (S.u_j + tj, 1.2))
    B.text(pcbnew.Dwgs_User, S.u_j - tj, -4.9, "FOLD B: %.1f deg, r 0.755 centre line" % (90 - S.a_in), 0.3)
    # foot stiffener on the back face (User.1): PI 0.10
    B.poly(pcbnew.User_1, [(0.05, -0.95), (0.05, 1.45), (STIFF_FOOT_U1, 1.45), (STIFF_FOOT_U1, -0.95)], 0.05)
    B.text(pcbnew.User_1, 0.1, 2.1, "STIFFENER PI 0.10 on back face", 0.3)


# ---------------------------------------------------------------- drawing: land numbers and nets (process.md P8 change C13)
TXT_NUM, TXT_NET, TXT_NOTE = 0.6, 0.3, 0.3          # text heights on the board drawing, mm (board scale)


def board_end_detail(B, table, jref, notes):
    """Detail of the foot, DET_K times the main view, same side up (the land face F.Cu, as the main view): each land as a box with its
    number (big) and net (small, under the box); a legend 'LAND n = NET (function)' beside it; notes under the legend.
    Numbers and nets: band_layout.JBAND_A / JBAND_B = band-interface.md section 2."""
    K = DET_K
    D = lambda u, v: B.page(K * u, DET_V0 + K * (v - 0.25))          # foot centre v 0.25 -> detail centre
    corners = [D(0, -1.0), D(0, 1.5), D(G.LF, 1.5), D(G.LF, -1.0)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        B.segp(a, b, 0.05)
    xs = [c[0] for c in corners]; ys = [c[1] for c in corners]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    side = "J_BAND_A on the ring board" if jref == "J_BAND_A" else "J_BAND_B on the ring board"
    B.textp(x0, y0 - 1.5, f"BOARD END OF THE RIBBON: LAND NUMBERS AND NETS", 0.4)
    B.textp(x0, y0 - 0.9, f"detail, {K:.0f} x the ribbon view on this sheet, same face up (land face F.Cu, it lies on {side})", TXT_NOTE)
    B.textp(x0, y0 - 0.45, "big number = land number, small text = net", TXT_NOTE)
    for pin, (nm, net, row, col) in sorted(table.items()):
        u, v = L.land_tail_uv(table, pin)
        cx, cy = D(u, v)
        hw = K * L.LAND_U / 2
        bx = [(cx - hw, cy - hw), (cx + hw, cy - hw), (cx + hw, cy + hw), (cx - hw, cy + hw)]
        for a, b in zip(bx, bx[1:] + bx[:1]):
            B.segp(a, b, 0.05)
        B.textp(cx, cy, str(pin), TXT_NUM, "centre")
        B.textp(cx, cy + hw + 0.35, net, TXT_NET, "centre")
    B.textp(x0, y1 + 0.6, "<- ribbon end", TXT_NOTE)
    B.textp(x1, y1 + 0.6, "fold A ->", TXT_NOTE, "right")
    lx, ly = x1 + 1.2, y0 + 0.4
    B.textp(lx, ly, f"{jref} lands (band-interface.md section 2):", TXT_NOTE)
    for i, (pin, (nm, net, row, col)) in enumerate(sorted(table.items())):
        B.textp(lx, ly + 0.5 * (i + 1), f"LAND {pin} = {net} ({nm}, {row} row)", TXT_NOTE)
    for j, line in enumerate(notes):
        B.textp(lx, ly + 0.5 * (len(table) + 2 + j), line, TXT_NOTE)


def leader_label(B, u_pad, v_pad_edge, v_row, txt, h=TXT_NOTE, hj="left"):
    """vertical leader from a land edge to a text row (main view); the text starts (hj left) or ends (hj right) at the leader"""
    p0 = B.page(u_pad, v_pad_edge); p1 = B.page(u_pad, v_row)
    B.segp(p0, p1, 0.03)
    B.textp(p1[0] + (0.05 if hj == "left" else -0.05), p1[1], txt, h, hj)


# ---------------------------------------------------------------- FLEX1
def build_flex1(B):
    S = B.S
    table = L.JBAND_A
    foot_lands(B, table, "J_BAND_A")
    foot_common(B, table)
    c = lambda pin: L.land_tail_uv(table, pin)[1]
    uN = L.U_NEAR
    LB, LH = V1_B, V1_HEAD
    # --- far row (via in the gap) -> B.Cu lanes
    B.track("B", "JOY_DOWN", [(L.U_VIA, c(2)), (1.4, c(2)), (1.435, LB["DOWN"])], W_SIG)
    uL = 1.2
    B.track("B", "JOY_LEFT", [(L.U_VIA, c(3)), (uL, c(3)), (uL + abs(c(3) - LB["LEFT"]), LB["LEFT"])], W_SIG)
    uG = 1.05
    B.track("B", "GND", [(L.U_VIA, c(6)), (uG, c(6)), (uG + abs(c(6) - LB["GND"]), LB["GND"])], W_PWR)
    B.track("F", "GND", [(L.U_FAR, c(6)), (uN, c(6))], W_PWR)                   # strap from land 6 to land 8 through the via of land 6
    uU = L.U_VIA
    B.track("B", "JOY_UP", [(uU, c(1)), (uU + abs(c(1) - LB["UP"]), LB["UP"])], W_SIG)
    # --- near row: RIGHT (via in the land of pin 4), CENTRE and VMOT on F.Cu
    B.via("JOY_RIGHT", uN, c(4))
    B.track("B", "JOY_RIGHT", [(uN, c(4)), (uN + abs(c(4) - LB["RIGHT"]), LB["RIGHT"])], W_SIG)
    B.track("F", "BTN_REC", [(uN, c(5)), (1.6, c(5)), (1.6 + abs(c(5) - V1_F["CENTRE"]), V1_F["CENTRE"])], W_SIG)
    B.track("F", "VMOT", [(uN, c(7)), (1.85, c(7)), (1.85 + abs(c(7) - V1_F["VMOT"]), V1_F["VMOT"])], W_PWR)
    start_u = {"DOWN": 1.435, "LEFT": uL + abs(c(3) - LB["LEFT"]), "GND": uG + abs(c(6) - LB["GND"]),
               "UP": uU + abs(c(1) - LB["UP"]), "RIGHT": uN + abs(c(4) - LB["RIGHT"])}
    vm_u = 1.85 + abs(c(7) - V1_F["VMOT"])
    cen_u = 1.6 + abs(c(5) - V1_F["CENTRE"])
    # --- motor lands (F.Cu, 0.60 x 0.30) on the VMOT / GND lane
    tj = tangent(90 - S.a_in)
    lo = S.u_j + tj + 0.1 + 0.3
    hi = S.u_trunk1 - 0.30 - 0.1 - 0.3 - MOT_PITCH
    m_model = S.u_j + S.motor_s_model[0]
    assert lo <= hi, (S.us, lo, hi)
    m1 = min(max(m_model, lo), hi)
    B.info.update(mot_m1_u=m1, mot_model_u=m_model, mot_slide_mm=m1 - m_model, mot_v=MOT_V)
    B.place("M1", "W0525AB001D_Lands", m1 + MOT_PITCH / 2, MOT_V)
    B.setnet_pad("M1", "1", "VMOT"); B.setnet_pad("M1", "2", "GND")
    # drawing: which motor land is + (band-interface.md section 6: land 1 = red lead = VMOT, the land nearer the slot)
    for num, v_row, txt in (("1", 1.25, "1 +: VMOT (red)"), ("2", 1.65, "2 -: GND (blue)")):
        pu, pv = B.pad_uv("M1", num)
        leader_label(B, pu, pv + 0.40, v_row, txt, hj="right")
    B.track("F", "VMOT", [(vm_u, V1_F["VMOT"]), (m1, V1_F["VMOT"])], W_PWR)
    B.via("GND", m1 + MOT_PITCH, MOT_V)
    # --- lanes to the head
    sh0 = S.u_trunk1 - 0.4
    sh1 = S.u_head0
    for nm, net, w0, w1 in (("DOWN", "JOY_DOWN", W_SIG, W_SIG), ("LEFT", "JOY_LEFT", W_SIG, W_SIG), ("UP", "JOY_UP", W_SIG, W_SIG),
                            ("RIGHT", "JOY_RIGHT", W_SIG, W_SIG), ("GND", "GND", W_PWR, W_HEAD_G)):
        B.track("B", net, [(start_u[nm], LB[nm]), (sh0, LB[nm])], w0)
        B.track("B", net, [(sh0, LB[nm]), (sh1, LH[nm])], w1)
    sc0 = max(sh0, m1 + MOT_PITCH + 0.3 + 0.3)
    B.track("F", "BTN_REC", [(cen_u, V1_F["CENTRE"]), (sc0, V1_F["CENTRE"]), (sh1, LH["CENTRE"])], W_SIG)
    # --- head
    h0 = S.u_head0
    H = lambda x, t: (h0 + 3.2 - t, x + 2.5)                          # head frame (x, t) -> tail (u, v)
    sw_u = {}
    for ref, (cx, ct) in L.SW_POS.items():
        want = L.SW_WANT.get(ref)
        found = None
        variants = [("Alps_SKTAAAE010_pads34", ("3", "4"))] if ref != "SW2" else [("Alps_SKTAAAE010_4pad", ("1", "2", "3", "4"))]
        for name, pads in variants:
            for rot in (0, 90, 180, 270):
                fp = B.place(ref, name, *H(cx, ct), rot)
                pos = {}
                for p in fp.Pads():
                    pu = ToMM(p.GetPosition().x) - OX
                    pv = B.s * (ToMM(p.GetPosition().y) - OY)
                    pos[p.GetNumber()] = (round(pv - 2.5, 3), round(h0 + 3.2 - pu, 3))
                if ref == "SW2":
                    ok = abs(pos["1"][0] + 1.325) < 0.01 and abs(pos["3"][0] + 1.325) < 0.01
                else:
                    ok = (abs(pos["3"][0] - want["P1"][0]) < 0.01 and abs(pos["3"][1] - want["P1"][1]) < 0.01 and
                          abs(pos["4"][0] - want["P2"][0]) < 0.01 and abs(pos["4"][1] - want["P2"][1]) < 0.01)
                if ok:
                    found = (name, rot, pos)
                    break
                del B.fps[ref]
            if found:
                break
        assert found, (ref,)
        name, rot, pos = found
        sw_u[ref] = (name, rot, pos)
        up = L.SW_UP[ref]
        for n in pos:
            B.setnet_pad(ref, n, up if n in ("1", "3") else "GND")
    B.info["switch_rot"] = {k: (v[0], v[1]) for k, v in sw_u.items()}

    def hb(net, pts, w=W_SIG):
        B.track("B", net, [H(*p) for p in pts], w)
    xd, xl, xg, xu, xr = (LH[k] - 2.5 for k in ("DOWN", "LEFT", "GND", "UP", "RIGHT"))
    hb("JOY_DOWN", [(xd, 3.2), (xd, -2.8), (1.325, -2.8), (1.325, -2.025)])
    hb("JOY_LEFT", [(xl, 3.2), (xl, -1.325), (-2.025, -1.325)])
    hb("JOY_UP", [(xu, 3.2), (xu, 2.025), (-1.325, 2.025)])
    hb("JOY_RIGHT", [(xr, 3.2), (xr, 2.85), (2.7, 2.85), (2.7, 1.325), (2.025, 1.325)])
    hb("GND", [(xg, 3.2), (xg, 0.0)], W_HEAD_G)
    hb("GND", [(xg, 1.325), (-2.025, 1.325)], W_HEAD_G)
    hb("GND", [(xg, 0.0), (1.7, 0.0), (1.7, -1.325), (2.025, -1.325)], W_HEAD_G)
    hb("GND", [(0.5, 0.0), (0.5, 2.025), (1.325, 2.025)], W_HEAD_G)
    hb("GND", [(1.325, -0.375), (1.325, 0.375)], W_HEAD_G)
    hb("GND", [(-0.2, 0.0), (-0.2, -2.025), (-1.325, -2.025)], W_HEAD_G)
    for net, (x, t) in (("JOY_DOWN", (1.325, -2.025)), ("JOY_LEFT", (-2.025, -1.325)), ("JOY_UP", (-1.325, 2.025)), ("JOY_RIGHT", (2.025, 1.325)),
                        ("GND", (1.325, 2.025)), ("GND", (-2.025, 1.325)), ("GND", (1.325, 0.375)), ("GND", (1.325, -0.375)),
                        ("GND", (2.025, -1.325)), ("GND", (-1.325, -2.025))):
        B.via(net, *H(x, t))
    xc = LH["CENTRE"] - 2.5
    B.track("F", "BTN_REC", [H(xc, 3.2), H(xc, 0.375), H(-1.325, 0.375)], 0.10)
    B.track("F", "BTN_REC", [H(-1.85, 0.375), H(-1.85, -0.375), H(-1.325, -0.375)], 0.10)
    B.poly(pcbnew.User_1, [(h0, -0.7), (h0, 5.7), (S.u_head1, 5.7), (S.u_head1, -0.7)], 0.05)
    B.text(pcbnew.User_1, h0 + 0.1, 6.0, "STIFFENER PI 0.10 on back (B.Cu) face, 6.4 x 6.4", 0.3)
    B.dash((h0, -1.0), (h0, 1.1))
    B.text(pcbnew.Dwgs_User, h0 - 1.6, -5.5, "head edge: flat from here", 0.3)
    B.info.update(h0=h0, h1=S.u_head1)
    board_end_detail(B, table, "J_BAND_A", [
        "MOTOR LANDS (M1): land 1 = + (VMOT, red lead), the land nearer the slot;",
        "land 2 = - (GND, blue lead). Marked 1 + and 2 - in the ribbon view.",
        "PASTE: F_Paste, 12 openings 0.55 x 0.55 on the switch lands, stencil 0.08 mm.",
        "PANEL: rails 5 mm; three 1 mm fiducials on the switch face (F),",
        "centred 3.85 mm from the panel edges, not in a line (process.md P7).",
        "Fab notes: fab/%s/%s-fab-notes.txt" % ((f"flex1-us{B.us}",) * 2)])


# ---------------------------------------------------------------- FLEX2
def build_flex2(B):
    S = B.S
    table = L.JBAND_B
    foot_lands(B, table, "J_BAND_B")
    foot_common(B, table)
    c = lambda pin: L.land_tail_uv(table, pin)[1]
    uN = L.U_NEAR
    # far row: CELL+ (pin 1, c0), NTC (3, c1), CELL- (2, c2), GND (7, c3): B.Cu
    B.track("B", "VBAT", [(L.U_VIA, c(1)), (1.2, c(1)), (1.2 + abs(c(1) - V2_B["VBAT"]), V2_B["VBAT"])], W_PWR)
    B.track("B", "NTC", [(L.U_VIA, c(3)), (1.0, c(3)), (1.0 + abs(c(3) - V2_B["NTC"]), V2_B["NTC"])], W_SIG)
    gl = V2_B["GND"]
    ga_end = 1.2 + (c(2) - gl)
    B.track("B", "GND", [(L.U_VIA, c(2)), (1.2, c(2)), (ga_end, gl)], W_PWR)
    gb_end = L.U_VIA + (c(7) - gl)
    B.track("B", "GND", [(L.U_VIA, c(7)), (gb_end, gl)], W_PWR)
    # near row: D+ (6, c0), D- (5, c1), VBUS (4, c2): F.Cu to their lanes
    B.track("F", "USB_DP", [(uN, c(6)), (1.6, c(6)), (1.6 + (V2_F["DP"] - c(6)), V2_F["DP"])], W_SIG)
    B.track("F", "USB_DN", [(uN, c(5)), (1.6, c(5)), (1.6 + (V2_F["DN"] - c(5)), V2_F["DN"])], W_SIG)
    B.track("F", "VBUS", [(uN, c(4)), (1.6, c(4)), (1.6 + (V2_F["VBUS"] - c(4)), V2_F["VBUS"])], W_SIG)
    f_start = {"USB_DP": 1.6 + (V2_F["DP"] - c(6)), "USB_DN": 1.6 + (V2_F["DN"] - c(5)), "VBUS": 1.6 + (V2_F["VBUS"] - c(4))}
    # --- PRT1 lands
    tj = tangent(90 - S.a_in)
    l1_min = max(S.pcm_s0 + 0.13 + 0.10, tj + 0.13 + 0.12)
    l3_max = S.pcm_s0 + S.pcm_len - 0.02 - 0.13
    l1 = l1_min
    assert l1 + 0.86 <= l3_max + 1e-9, (S.us, l1, l3_max)
    sc = l1 + 0.43                                                    # centre land (pad 3, NTC)
    uc = S.u_j + sc
    B.info.update(prt1_l1_s=l1, prt1_l2_s=sc, prt1_l3_s=l1 + 0.86, pcm_s0=S.pcm_s0, pcm_end_s=S.pcm_s0 + S.pcm_len)
    B.place("PRT1", "PRT1_Tabs", uc, LAND2_V)
    B.setnet_pad("PRT1", "1", "VBAT"); B.setnet_pad("PRT1", "3", "NTC"); B.setnet_pad("PRT1", "2", "GND")
    # drawing: the three cell tab lands with their names (band-interface.md section 5: P+ VBAT, NTC, P- GND; order 1, 3, 2 from the slot)
    for num, v_row in (("2", -1.35), ("3", -1.85), ("1", -2.35)):
        pu, pv = B.pad_uv("PRT1", num)
        tab, net = L.PRT1_PADS[num]
        leader_label(B, pu, pv - 0.225, v_row, f"{tab} tab: {net}")
    B.fps["PRT1"].Reference().SetPosition(B.P(uc, -3.0))            # reference text above the tab names
    uL1, uL2, uL3 = uc - 0.43, uc, uc + 0.43
    for net, vv in (("VBAT", uL1), ("NTC", uL2), ("GND", uL3)):
        B.via(net, vv, LAND2_V)
    lead = 0.35
    # VBAT lane -> via at L1
    B.track("B", "VBAT", [(1.2 + abs(c(1) - V2_B["VBAT"]), V2_B["VBAT"]), (uL1, V2_B["VBAT"])], W_PWR)
    # NTC lane -> L2 via
    B.track("B", "NTC", [(1.0 + abs(c(3) - V2_B["NTC"]), V2_B["NTC"]), (uL2 - 0.3, V2_B["NTC"]), (uL2, LAND2_V)], W_SIG)
    # GND lane -> L3 via
    gd0 = uL3 - 0.36
    B.track("B", "GND", [(min(ga_end, gb_end), gl), (gd0, gl), (uL3, LAND2_V)], W_PWR)
    # F.Cu: USB lanes
    u_lo = S.u_j + S.s_lo
    pads_u = [S.u_j + s for s in S.pad_s]
    pad_net = ["VBUS", "USB_DN", "USB_DP", "GND"]
    lane = {"VBUS": V2_F["VBUS"], "USB_DN": V2_F["DN"], "USB_DP": V2_F["DP"], "GND": V2_F["GND"]}
    wd = {"VBUS": W_SIG, "USB_DN": W_SIG, "USB_DP": W_SIG, "GND": W_PWR}
    for k, net in enumerate(pad_net):
        p0 = [(f_start[net], lane[net])] if net != "GND" else [(uL3 + 0.1, lane[net])]
        pts = p0 + [(pads_u[k] - 0.0, lane[net]), (pads_u[k], 1.5)]
        B.track("F", net, pts, wd[net])
    # charging pads on B.Cu with a via each
    for k, (ref, net) in enumerate(zip(("CP1", "CP2", "CP3", "CP4"), pad_net)):
        B.place(ref, "CP_Pad_1.6", pads_u[k], 1.5)
        B.setnet_pad(ref, "1", net)
        B.via(net, pads_u[k], 1.5)
        o = PASTE_DISC_OFF / math.sqrt(2)
        for du, dv in ((o, o), (o, -o), (-o, o), (-o, -o)):
            B.paste_disc(pcbnew.B_Paste, pads_u[k] + du, 1.5 + dv, PASTE_DISC_D)
    B.info.update(pad_u=pads_u, strip_u=(u_lo, S.u_j + S.s_hi))
    # fold lines of the jog
    B.dash((u_lo, -1.2), (u_lo, 2.95))
    B.text(pcbnew.Dwgs_User, u_lo + 0.05, -5.5, "strip starts (flat, no fold on the pad strip)", 0.3)
    board_end_detail(B, table, "J_BAND_B", [
        "CELL TAB LANDS (PRT1), from the slot: P+ (VBAT, land 1 of J_BAND_B),",
        "NTC (NTC, land 3), P- (GND, land 2). Named in the ribbon view.",
        "PASTE: B_Paste, 4 round openings 0.58 on each disc land CP1 to CP4, stencil 0.08 mm.",
        "PANEL: rails 5 mm; three 1 mm fiducials on the pad face (B),",
        "centred 3.85 mm from the panel edges, not in a line (process.md P7).",
        "Fab notes: fab/%s/%s-fab-notes.txt" % ((f"flex2-us{B.us}",) * 2)])


def dims(B, pts):
    try:
        _dims(B, pts)
    except Exception as e:
        print("WARNING dims:", repr(e))


def _dims(B, pts):
    S = B.S
    L_end = max(p[0] for p in pts)
    B.dim((0, -1.0), (L_end, -1.0), 2.4)
    B.dim((0, -1.0), (0, 1.5), -1.4)
    B.dim((G.LF, -1.0), (G.LF + G.LARC, -1.0), 1.2)
    B.text(pcbnew.Dwgs_User, 0.0, -6.4, f"{B.kind} US {B.us}: flat length {L_end:.3f} mm = model path {S.path1 if B.kind == 'FLEX1' else S.path2:.3f} + fold and foot {G.FOOT_EXTRA:.3f}", 0.4)


def write(B, pts):
    b = B.b
    for ref, fp in B.fps.items():
        for fld in fp.GetFields():
            if fld.GetName() != "Reference":
                fld.SetVisible(False)
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetTextSize(VECTOR2I(mm(0.3), mm(0.3)))
        fp.Value().SetVisible(False)
        b.Add(fp)
    name = f"{B.kind.lower()}-us{B.us}"
    path = os.path.join(OUTDIR, name + ".kicad_pcb")
    ds = b.GetDesignSettings()
    for attr in ("m_TentViasFront", "m_TentViasBack"):
        if hasattr(ds, attr):
            setattr(ds, attr, True)
    pcbnew.SaveBoard(path, b)
    cu, di, cv = 0.012, 0.025, 0.030
    lines = ["\t\t(stackup", '\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))', '\t\t\t(layer "F.Paste" (type "Top Solder Paste"))',
             f'\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness {cv}))', f'\t\t\t(layer "F.Cu" (type "copper") (thickness {cu}))',
             f'\t\t\t(layer "dielectric 1" (type "core") (thickness {di}) (material "Polyimide"))',
             f'\t\t\t(layer "B.Cu" (type "copper") (thickness {cu}))', f'\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness {cv}))',
             '\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))', '\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))',
             '\t\t\t(copper_finish "ENIG")', '\t\t\t(dielectric_constraints no)', "\t\t)"]
    txt = open(path).read()
    assert "\t(setup\n" in txt and "(stackup" not in txt
    txt = txt.replace("\t(setup\n", "\t(setup\n" + "\n".join(lines) + "\n", 1)
    open(path, "w").write(txt)
    pro = {"board": {"design_settings": {"rules": {
        "min_clearance": L.RULES["clearance"], "min_copper_edge_clearance": L.RULES["edge"], "min_track_width": L.RULES["track_min"],
        "min_via_diameter": L.RULES["via_dia"], "min_through_hole_diameter": L.RULES["via_drill"], "min_via_annular_width": L.RULES["ring_min"],
        "min_hole_clearance": 0.1, "min_hole_to_hole": 0.2, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
        "min_silk_clearance": 0.0, "min_text_height": 0.2, "min_text_thickness": 0.03}}},
        "net_settings": {"classes": [{"name": "Default", "clearance": L.RULES["clearance"], "track_width": 0.1, "via_diameter": L.RULES["via_dia"],
                                      "via_drill": L.RULES["via_drill"], "microvia_diameter": 0.2, "microvia_drill": 0.1}], "meta": {"version": 4}},
        "meta": {"filename": name + ".kicad_pro", "version": 1}}
    with open(os.path.join(OUTDIR, name + ".kicad_pro"), "w") as f:
        json.dump(pro, f, indent=1)
    with open(os.path.join(OUTDIR, name + ".kicad_dru"), "w") as f:
        f.write("(version 1)\n"
                f"(rule \"exposed land to line\" (condition \"A.Type == 'Pad' && B.Type == 'Track'\") (constraint clearance (min {L.RULES['pad_to_track']}mm)))\n"
                f"(rule \"exposed land to line 2\" (condition \"A.Type == 'Track' && B.Type == 'Pad'\") (constraint clearance (min {L.RULES['pad_to_track']}mm)))\n"
                f"(rule \"land to land\" (condition \"A.Type == 'Pad' && B.Type == 'Pad'\") (constraint clearance (min {L.RULES['pad_to_pad']}mm)))\n"
                f"(rule \"land to via\" (condition \"A.Type == 'Pad' && B.Type == 'Via'\") (constraint clearance (min 0.15mm)))\n"
                f"(rule \"land to via 2\" (condition \"A.Type == 'Via' && B.Type == 'Pad'\") (constraint clearance (min 0.15mm)))\n")
    return path


def build(kind, us):
    B = Board(kind, us)
    pts = outline(B)
    draw_common(B, pts)
    if kind == "FLEX1":
        build_flex1(B)
    else:
        build_flex2(B)
    dims(B, pts)
    path = write(B, pts)
    S = B.S
    length = max(p[0] for p in pts)
    row = dict(kind=kind, us=us, flat_length=round(length, 4), model_path=round(S.path1 if kind == "FLEX1" else S.path2, 4),
               foot_extra=round(G.FOOT_EXTRA, 4), file=os.path.basename(path), **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in B.info.items()
                                                                                    if not isinstance(v, (list, tuple, dict))})
    row["pad_u"] = [round(x, 4) for x in B.info.get("pad_u", [])]
    return row


if __name__ == "__main__":
    sizes = [int(a) for a in sys.argv[1:]] or G.SIZES
    rows = []
    for kind in ("FLEX1", "FLEX2"):
        for us in sizes:
            r = build(kind, us)
            rows.append(r)
            print(json.dumps(r))
    with open(os.path.join(HERE, "evidence", "build_rows.json"), "w") as f:
        json.dump(rows, f, indent=1)
    print("boards written:", len(rows))
