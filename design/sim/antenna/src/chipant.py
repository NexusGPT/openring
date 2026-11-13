"""Chip antenna model shared by H1 and H2 (Johanson 2450AT18D0100001E as ASSUMED inside; see antenna-sim.md section 0.4).
Local frame: u along the length (3.2), v across (1.6), w up from the land surface (1.2). All numbers in mm."""
import numpy as np

class Frame:
    def __init__(self, origin, ux, uy, uz):
        self.o = np.array(origin, float)
        self.M = np.array([ux, uy, uz], float)   # rows: global direction of local u, v, w
    def pt(self, u, v, w):
        return self.o + u * self.M[0] + v * self.M[1] + w * self.M[2]
    def box(self, prop, lo, hi, priority):
        a = self.pt(*lo); b = self.pt(*hi)
        prop.AddBox(np.minimum(a, b), np.maximum(a, b), priority=priority)
    def corners(self, lo, hi):
        a = self.pt(*lo); b = self.pt(*hi)
        return np.minimum(a, b), np.maximum(a, b)

# ---------------------------------------------------------------- geometry numbers (local frame)
BODY = ((-1.6, -0.8, 0.0), (1.6, 0.8, 1.2))                       # datasheet page 2: 3.2 x 1.6 x 1.2
TERM = {  # four bottom terminals a = 0.3 (along u) by b = 0.5 (across v), datasheet page 2; thickness 0.1
    "feed":  ((-1.6, -0.8, 0.0), (-1.3, -0.3, 0.1)),             # feed terminal: (-u, -v) corner
    "g_pv":  ((-1.6, 0.3, 0.0), (-1.3, 0.8, 0.1)),               # grounded, same end
    "g_mu_pv": ((1.3, 0.3, 0.0), (1.6, 0.8, 0.1)),
    "g_pu_mv": ((1.3, -0.8, 0.0), (1.6, -0.3, 0.1)),
}
W_RAD = 1.0                                                      # radiator plane height above the land surface
LEG_U = [-1.4, -0.8, -0.2, 0.4, 1.0]                             # leg centres along u, pitch 0.6
LEG_W = 0.2
LEG_V = (-0.7, 0.7)
POST = ((-1.5, -0.6, 0.1), (-1.4, -0.5, W_RAD))                  # feed post from the feed terminal up to the radiator plane

def conductor_length_mm():
    legs = len(LEG_U) * (LEG_V[1] - LEG_V[0])
    conn = sum(LEG_U[i + 1] - LEG_U[i] for i in range(len(LEG_U) - 1))
    return legs + conn + (W_RAD - 0.1)

def add_antenna(CSX, fr, eps_r, tand, f_for_kappa=2.45e9, name="ant", prio_body=5, prio_metal=30):
    """adds ceramic block and PEC parts; returns (metal_property, list of local edge coordinates (u,v,w) for the mesh)"""
    eps0 = 8.8541878128e-12
    kappa = 2 * np.pi * f_for_kappa * eps0 * eps_r * tand
    cer = CSX.AddMaterial(name + "_ceramic", epsilon=eps_r, kappa=kappa)
    fr.box(cer, *BODY, priority=prio_body)
    m = CSX.AddMetal(name + "_pec")
    for k, (lo, hi) in TERM.items():
        fr.box(m, lo, hi, prio_metal)
    fr.box(m, *POST, prio_metal)
    wz = W_RAD
    for i, uc in enumerate(LEG_U):
        fr.box(m, (uc - LEG_W / 2, LEG_V[0], wz), (uc + LEG_W / 2, LEG_V[1], wz), prio_metal)
    for i in range(len(LEG_U) - 1):
        top = (i % 2 == 0)
        v0, v1 = (LEG_V[1] - 0.2, LEG_V[1]) if top else (LEG_V[0], LEG_V[0] + 0.2)
        fr.box(m, (LEG_U[i] - LEG_W / 2, v0, wz), (LEG_U[i + 1] + LEG_W / 2, v1, wz), prio_metal)
    return m, cer

def local_edges():
    """local coordinates that must be mesh lines (all multiples of 0.1)"""
    us = {BODY[0][0], BODY[1][0]}; vs = {BODY[0][1], BODY[1][1]}; ws = {0.0, 0.1, W_RAD, 1.2}
    for lo, hi in TERM.values():
        us |= {lo[0], hi[0]}; vs |= {lo[1], hi[1]}
    for uc in LEG_U: us |= {round(uc - LEG_W / 2, 3), round(uc + LEG_W / 2, 3)}
    vs |= set(LEG_V) | {LEG_V[1] - 0.2, LEG_V[0] + 0.2}
    us |= {POST[0][0], POST[1][0]}; vs |= {POST[0][1], POST[1][1]}
    return sorted(us), sorted(vs), sorted(ws)
