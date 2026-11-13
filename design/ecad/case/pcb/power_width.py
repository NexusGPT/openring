#!/usr/bin/env python3
"""IPC-2221 track width for a current: I = k * dT^0.44 * A^0.725 (A in mil^2, k = 0.048 outer layers, 0.024 inner layers), A = width * thickness.
1 oz copper = 1.378 mil (35 um) outer, inner layers in the JLCPCB stack-up 0.5 oz default = 0.69 mil (page w5_jlcpcb_capabilities.html: 'Finished copper weight of inner layer is 0.5oz by default').
Currents (all from the case files, see board-notes.md section c): VBUS_IN 1.5 A (input limit with a 1.5 A source: case-architecture.md section 4), BAT/SYS/SW/PMID 1.5 A
(charge 350 mA = 0.5C, boost to the ring about 0.64 A from the cell, Wi-Fi 0.38 A; 1.5 A is the design bound), VRING 0.401 A (TPS2553 IOSmin with R5 59 k, sch-notes section 1), 3V3 0.355 A (U1 TX peak)."""
import math
def width_mm(I, dT=10.0, outer=True, oz=1.0):
    k = 0.048 if outer else 0.024
    thick_mil = 1.378 * oz
    A = (I / (k * dT ** 0.44)) ** (1 / 0.725)
    return A / thick_mil * 0.0254
for name, I in (("VBUS_IN/SYS/BAT/SW/PMID design bound", 1.5), ("VRING (TPS2553 limit)", 0.401), ("3V3 (U1 peak)", 0.355)):
    print("%-40s I=%.3f A  outer 1 oz dT 10 K: %.3f mm   dT 20 K: %.3f mm   inner 0.5 oz dT 10 K: %.3f mm" % (name, I, width_mm(I), width_mm(I, 20), width_mm(I, 10, False, 0.5)))
print("chosen widths (outer 1 oz): VBUS_IN 0.40 mm; SYS BAT SW PMID U3_L1 U3_L2 0.30 mm; VRING and 3V3 0.20 mm; everything else 0.15 mm")
def rise_K(I, w_mm, outer=True, oz=1.0):
    k = 0.048 if outer else 0.024
    A = w_mm / 0.0254 * 1.378 * oz
    return (I / (k * A ** 0.725)) ** (1 / 0.44)
for name, I, w in (("VBUS_IN", 1.5, 0.40), ("SYS BAT SW PMID (charge 0.35 A + system up to 1.0 A)", 1.0, 0.30), ("U3_L1 U3_L2 (U3 input side at 0.6 A)", 0.6, 0.30), ("VRING (TPS2553 limit)", 0.401, 0.20), ("3V3 (U1 peak)", 0.355, 0.20)):
    print("%-55s %.3f A on %.2f mm: temperature rise %.1f K" % (name, I, w, rise_K(I, w)))
