#!/usr/bin/env python3
"""Order-of-magnitude acoustic figures for mic-path.md section 6. Every output line is an [ESTIMATE]:
textbook lumped formulas, air at 20 C, no maker source. Bench B7 settles them.

Paths compared:
  P1 recommended: straight bore, diameter 1.0, length 0.43 (gasket 0.13 + floor 0.30, check.log C24)
  P2 second best: slit 0.6 wide under the lid, 0.13 high (0.03 to 0.23 with the part's height tolerance, check.log C16),
     from the gasket bore edge to the outside of the end wall: 1.455 in the pocket + 0.570 through the wall at Z 0.35 (check.log C28)
  Leak: the block's inside air (taken as 250 mm3, [ESTIMATE]) reached through a gasket leak.
"""
import math

RHO, C, MU = 1.2, 343.0, 1.81e-5   # kg/m3, m/s, Pa s


def mm(x):
    return x * 1e-3


def tube_res_closed_open(L):
    return C / (4 * L)


def r_tube(r, L):          # Poiseuille resistance of a round tube
    return 8 * MU * L / (math.pi * r ** 4)


def m_tube(r, L):          # acoustic mass of a round tube with end corrections 0.85 r at each end
    return RHO * (L + 1.7 * r) / (math.pi * r * r)


def r_slit(w, h, L):       # resistance of a wide slit, w >> h
    return 12 * MU * L / (w * h ** 3)


def m_slit(w, h, L):
    return RHO * L / (w * h)


def main():
    print("all lines [ESTIMATE]: lumped textbook formulas, air at 20 C")
    for f in (1000.0, 8000.0):
        d = math.sqrt(2 * MU / (RHO * 2 * math.pi * f))
        print(f"viscous boundary layer at {f:.0f} Hz: {d * 1e3:.3f} mm")
    r1, L1 = mm(0.5), mm(0.43)
    print(f"P1 bore d 1.0 L 0.43: quarter-wave resonance {tube_res_closed_open(L1 + 0.85 * r1) / 1000:.0f} kHz; "
          f"resistance {r_tube(r1, L1):.3e} Pa s/m3; mass impedance at 8 kHz {2 * math.pi * 8000 * m_tube(r1, L1):.3e} Pa s/m3")
    V = 250e-9
    for f in (1000.0, 8000.0):
        zc = RHO * C * C / (2 * math.pi * f * V)
        z1 = abs(complex(r_tube(r1, L1), 2 * math.pi * f * m_tube(r1, L1)))
        print(f"leak check at {f:.0f} Hz: inside air 250 mm3 compliance impedance {zc:.3e}; P1 path {z1:.3e}; ratio {zc / z1:.2f} (inside-air impedance over P1 path impedance; near or under 1 means an open leak to the inside air would cut the level, so the gasket must seal)")
    for h in (0.03, 0.13, 0.23):
        w, L = mm(0.6), mm(1.455 + 0.570)
        hh = mm(h)
        rs = r_slit(w, hh, L)
        ms = m_slit(w, hh, L)
        zc8 = RHO * C * C / (2 * math.pi * 8000 * V)
        print(f"P2 slit 0.6 x {h:.2f} x 2.025: quarter-wave {tube_res_closed_open(L) / 1000:.0f} kHz; resistance {rs:.3e} Pa s/m3 "
              f"({rs / r_tube(r1, L1):.0f} x P1); mass impedance at 8 kHz {2 * math.pi * 8000 * ms:.3e}; inside-air impedance at 8 kHz {zc8:.3e}")


if __name__ == "__main__":
    main()
