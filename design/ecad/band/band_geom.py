"""Geometry of the two band flex tails, taken from the inside model v7 (design/mech/thin/thin.py) and the flat-pattern
choices of this design.  Pure Python, no KiCad needed.  All lengths in mm, angles in degrees.

Model lines used (thin.py): SIZE_TABLE 94-103; R_IN 113; ZC 114; R_F0, R_F1 120-121; tail_w, tail_y 66; ribbon pieces 576-613
(a_in 560, z_in 561, phi 592, tr_a 601, pad_ang 604, pa_lo, pa_hi 605); bend polygon 596-598; head_t, stiff 67, 64.
Z_BD0 (board underside, top of the v7 vertical piece) = 1.45 from the v7 STEP files (evidence/step_solids.csv).
Model v8 (2026-11-13): the delivered STEP files hold the fold and the foot already (neck ends at the fold start Z 0.59); FOOT_EXTRA is the
length this module adds to the v7 path to get the same total, and check_band.py compares each board with BOTH this formula and the v8 files
(model_lengths.csv, measure_step.py) without adding FOOT_EXTRA to the latter.
"""
import math

SIZE_TABLE = {  # US size: (bore, joystick deg, motor deg, pcm_a0 deg, slot_z0)   thin.py 94-103
    7: (17.3196, -84.0, -47.0, 43.8, -0.20),
    8: (18.1324, -81.0, -45.5, 41.5, -0.20),
    9: (18.9452, -78.0, -44.0, 39.5, -0.23),
    10: (19.7580, -78.0, -45.0, 39.5, -0.63),
    11: (20.5708, -78.0, -43.5, 39.5, -1.04),
    12: (21.3836, -78.0, -42.5, 39.5, -1.45),
    13: (22.1964, -78.0, -42.5, 39.5, -1.85),
}
SIZES = sorted(SIZE_TABLE)

# model constants (thin.py P dict)
BORE_GAP = 0.4
LINER_T = 0.30
FLEX_T_MODEL = 0.15
TAIL_Y = 5.9
HEAD = 6.4              # head_x*2 = head_t*2
POCKET_STIFF = 6.4
PAD_D, PAD_PITCH, PAD_X, PAD_MARGIN = 1.6, 2.4, -1.0, 0.45
PROT_ALONG, CELL_GAP, SEAL = 1.5, 0.2, 2.0
Z_BD0 = 1.45            # board underside (STEP zmax of the vertical piece)
Z_LAND = Z_BD0 - 0.02   # copper lands of the board (pad_t 0.02, thin.py 52)

# ---- this design (band-interface.md section 3, 4)
T_FLEX = 0.11           # finished two-layer flex, JLCPCB flex capability page (finished thickness 2-layer 0.11 mm)
JOINT = 0.03            # solder joint between board land and tail land (hot bar)
R_FOLD_IN = 0.70        # inner radius of the board fold (6.4 x 0.11 mm, static bend 6 to 10 x thickness, same page)
RC = R_FOLD_IN + T_FLEX / 2
Y_FOOT_END = 3.4        # inboard end of the free room beside the slot (band-flex-tails.md line 46)
LF = (TAIL_Y - RC) - Y_FOOT_END          # flat run under the board
LARC = math.pi / 2 * RC
Z_ARC0 = (Z_LAND - JOINT) - T_FLEX / 2 - RC   # where the fold starts on the vertical piece
FOOT_EXTRA = LF + LARC - (Z_BD0 - Z_ARC0)     # tail length added by the fold and the flat foot, beyond the model path
TAIL_W = 1.8            # neck width (model 1.4: see band-interface.md section 9)
TAIL_X = -2.5           # neck centre X (model -2.6)


def deg(r):
    return math.degrees(r)


def rad(d):
    return math.radians(d)


class Size:
    def __init__(self, us):
        self.us = us
        bore, self.ja, self.ma, self.pcm_a0, self.slot_z0 = SIZE_TABLE[us]
        self.bore = bore
        self.r_in = bore / 2
        self.zc = -BORE_GAP - self.r_in
        self.r_fm = self.r_in + LINER_T / 2           # ribbon mid radius (R_F0 + 0.075)
        self.r_liner = self.r_in + LINER_T
        self.r_cell_c = self.r_liner + 0.8
        self.a_in = deg(math.asin(TAIL_Y / self.r_fm))
        self.z_in = self.zc + math.sqrt(self.r_fm ** 2 - TAIL_Y ** 2)
        self.lv = Z_BD0 - self.z_in                    # vertical piece, model (solid 0 of the STEP file)
        # thumb (FLEX1)
        phi = math.asin(3.6 / self.r_fm)
        self.tr_a = self.ja + deg(phi)
        sweep = (-self.a_in - self.tr_a) % 360
        self.l_trunk1 = self.r_fm * rad(sweep)
        zh1 = self.r_liner
        r_f0, r_f1 = self.r_in + 0.075, self.r_in + 0.225
        p_start = (3.2, (self.r_in + 0.15 + zh1) / 2)
        p_end = (self.r_fm * math.sin(phi), self.r_fm * math.cos(phi))
        self.l_bend = math.hypot(p_start[0] - p_end[0], p_start[1] - p_end[1])
        self.l_head = HEAD
        self.path1 = self.lv + self.l_trunk1 + self.l_bend + self.l_head      # model path of FLEX1 (top of vertical to far edge of head)
        # away (FLEX2)
        row = [(-1.5 + k) * PAD_PITCH for k in range(4)]
        self.pad_ang = [180 + deg(o / self.r_in) for o in row]
        m = deg((PAD_D / 2 + PAD_MARGIN) / self.r_in)
        self.pa_lo = self.pad_ang[0] - m
        self.pa_hi = self.pad_ang[-1] + m
        self.path2 = self.lv + self.r_fm * rad(self.pa_hi - self.a_in)          # model path of FLEX2
        # flat positions (u from the tail end)
        self.u_j = FOOT_EXTRA + self.lv                 # the slot junction (model: bottom of the vertical piece)
        self.len1 = FOOT_EXTRA + self.path1
        self.len2 = FOOT_EXTRA + self.path2
        # FLEX1 landmarks
        self.u_trunk0 = self.u_j
        self.u_trunk1 = self.u_j + self.l_trunk1
        self.u_head0 = self.u_trunk1 + self.l_bend      # near edge of the head
        self.u_head1 = self.u_head0 + HEAD
        # FLEX2 landmarks (arc length at the ribbon mid radius from the junction)
        self.s2 = lambda ang: self.r_fm * rad(ang - self.a_in)
        self.pcm_s0 = self.s2(self.pcm_a0)
        self.pcm_len = PROT_ALONG * self.r_fm / self.r_cell_c
        self.pad_s = [self.s2(a) for a in self.pad_ang]
        self.s_lo = self.s2(self.pa_lo)
        self.s_hi = self.s2(self.pa_hi)
        self.s_jog1 = self.s2(self.pa_lo + 5.0)         # the model's 5 degree wide jog piece (thin.py 608)
        # motor (FLEX1): model pigtail lands at t = -0.7 and -1.7 from the motor centre, toward the head
        d_motor = self.r_fm * rad(-self.ma - self.a_in)      # arc from the junction to the motor centre angle
        self.motor_s_model = (d_motor + 0.7, d_motor + 1.7)


if __name__ == "__main__":
    print(f"fold: Rc {RC:.3f} LF {LF:.3f} LARC {LARC:.3f} Z_ARC0 {Z_ARC0:.3f} FOOT_EXTRA {FOOT_EXTRA:.3f}")
    for us in SIZES:
        s = Size(us)
        print(us, f"a_in {s.a_in:.3f} lv {s.lv:.4f} trunk {s.l_trunk1:.4f} bend {s.l_bend:.4f} path1 {s.path1:.4f} path2 {s.path2:.4f} len1 {s.len1:.3f} len2 {s.len2:.3f}")
