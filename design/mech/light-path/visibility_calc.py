#!/usr/bin/env python3
"""Light at the surface of the recommended path: datasheet values times an [ESTIMATE] path transmission.
Inputs: logs/kpg_iv_curve.log (relative intensity at 1.5 mA, read from the KPG-1005SURC-TT p3 curve) and the p2 table
(Iv at 20 mA printed as '55 195' and '*20 *65'). Output: one line per figure."""
import math
import re
from pathlib import Path

LOGS = Path(__file__).resolve().parent / "logs"
rel = float(re.search(r"at x 1.5: y ([\d.]+)", (LOGS / "kpg_iv_curve.log").read_text()).group(1))
print(f"relative luminous intensity at 1.5 mA (p3 curve, 1.0 at 20 mA): {rel:.4f}")
for label, iv20 in (("typ 65 mcd (row marked *, CIE127-2007 traceable)", 65.0), ("typ 195 mcd (unmarked row)", 195.0),
                    ("min 20 mcd (row marked *)", 20.0)):
    i_led = iv20 * rel
    print(f"LED at 1.5 mA from {label}: {i_led:.2f} mcd on its axis [CALC]")
    for t in (0.05, 0.25):
        i_out = i_led * t
        area = math.pi * 0.20 ** 2 * 1e-6          # print window dia 0.4 mm, in m2
        lum = i_out * 1e-3 / area
        print(f"  path transmission {t:.2f} [ESTIMATE]: {i_out:.2f} mcd at the window, mean luminance over the 0.4 mm window {lum:.0f} cd/m2 [ESTIMATE]")
print("screen luminance for comparison: 450 cd/m2 (display_TOH095XVT-01.pdf p4, 'Luminance on surface')")
