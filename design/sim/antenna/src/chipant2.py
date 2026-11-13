"""Stand-in for the chip antenna (round 2, section 12.2): inverted-F meander in a 3.2 x 1.6 x 1.2 mm ceramic block.
Free parameters: eps_r, a (span of legs 2 to 5), vs (position of the shorting post across leg 1). Local frame as chipant.Frame."""
import numpy as np
from chipant import Frame, BODY, TERM, W_RAD, LEG_U, LEG_W
def add_standin(CSX, fr, eps_r, a, vs, tand=0.005, name="ant", prio_body=26, prio_metal=30):
    eps0 = 8.8541878128e-12
    cer = CSX.AddMaterial(name + "_ceramic", epsilon=eps_r, kappa=2 * np.pi * 2.45e9 * eps0 * eps_r * tand)
    fr.box(cer, *BODY, priority=prio_body)
    m = CSX.AddMetal(name + "_pec")
    for k, (lo, hi) in TERM.items(): fr.box(m, lo, hi, prio_metal)
    wz = W_RAD
    # leg 1 full length; legs 2..5 span +-a
    fr.box(m, (LEG_U[0] - LEG_W / 2, -0.7, wz), (LEG_U[0] + LEG_W / 2, 0.7, wz), prio_metal)
    for uc in LEG_U[1:]:
        fr.box(m, (uc - LEG_W / 2, -a, wz), (uc + LEG_W / 2, a, wz), prio_metal)
    for i in range(len(LEG_U) - 1):
        v0, v1 = ((a - 0.2, a) if i % 2 == 0 else (-a, -a + 0.2))
        fr.box(m, (LEG_U[i] - LEG_W / 2, v0, wz), (LEG_U[i + 1] + LEG_W / 2, v1, wz), prio_metal)
    # feed post at the feed terminal, short post and grounding bar
    fr.box(m, (-1.5, -0.6, 0.1), (-1.4, -0.5, wz), prio_metal)
    fr.box(m, (-1.5, vs, 0.1), (-1.4, vs + 0.1, wz), prio_metal)
    lo = max(min(vs, 0.3), -0.2); hi = max(vs + 0.1, 0.3)
    fr.box(m, (-1.5, lo, 0.0), (-1.4, hi, 0.1), prio_metal)
    return m, cer
