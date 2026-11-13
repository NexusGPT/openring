"""Arithmetic of process.md (P2, P3, P5). Writes logs/calc.log."""
import math, os
W = os.path.dirname(os.path.abspath(__file__))
L = []
def ar_rect(w, h, t): return w * h / (2 * (w + h) * t)
def ar_circ(d, t): return d / (4 * t)
L.append("J1 Hirose stencil, t 0.10: top row 0.23x0.55 AR %.3f; bottom row 0.23x0.65 AR %.3f; tab 0.30x0.70 AR %.3f" % (ar_rect(0.23, 0.55, 0.10), ar_rect(0.23, 0.65, 0.10), ar_rect(0.30, 0.70, 0.10)))
L.append("ring screen face 0201 0.27x0.30 at t 0.10: AR %.3f" % ar_rect(0.27, 0.30, 0.10))
L.append("ring parts face U1 circle 0.200 at t 0.075: AR %.3f ; at t 0.080: AR %.3f" % (ar_circ(0.200, 0.075), ar_circ(0.200, 0.080)))
L.append("ring parts face U2 circle 0.225 at t 0.075: AR %.3f ; U4 circle 0.260 at t 0.075: AR %.3f" % (ar_circ(0.225, 0.075), ar_circ(0.260, 0.075)))
L.append("case main U6 0.565x0.200 (corner r 0.04, from stencil_calc.log) at t 0.10: see stencil_calc.log; TI example U2 t 0.125 would give U6 (rect approx) AR %.3f" % ar_rect(0.565, 0.200, 0.125))
L.append("flex1 switch land 0.55x0.55 at t 0.08: AR %.3f" % ar_rect(0.55, 0.55, 0.08))
d, r, n, t = 0.58, 0.49, 4, 0.08
L.append("flex2 disc opening d %.2f at r %.2f: inner edge %.3f mm from land centre, outer edge %.3f mm (land radius 0.80, via land radius 0.15), gap between openings %.3f mm, AR at t 0.08 %.3f" % (d, r, r - d / 2, r + d / 2, r * math.sqrt(2) - d, ar_circ(d, t)))
a_open = n * math.pi * d * d / 4
a_land = math.pi * 0.8 ** 2
v = a_open * t
L.append("flex2 disc: openings area %.4f mm2, land area %.4f mm2, coverage %.1f %%, paste volume %.4f mm3" % (a_open, a_land, 100 * a_open / a_land, v))
h = v / a_land
L.append("flex2 disc: solder layer upper bound (paste counted as all metal) %.3f mm; disc 0.070 mm; disc top above land copper between %.3f and %.3f mm" % (h, 0.070, 0.070 + h))
L.append("case U2 thermal pad: four 1.1x1.1 openings %.2f mm2 against the 2.6x2.6 land %.2f mm2: %.1f %%; against the package pad 2.7x2.7 %.2f mm2: %.1f %%" % (4 * 1.21, 2.6 ** 2, 100 * 4.84 / 2.6 ** 2, 2.7 ** 2, 100 * 4.84 / 2.7 ** 2))
peak_hi = 245
for name, lim in [("J1 Hirose peak", 250), ("Murata 1269AS peak", 250), ("ESP32-S3-MINI-1 peak", 250), ("Knowles peak", 260), ("Alps peak", 260), ("TI Level-1/2 260C", 260), ("SGM38046 lead 260C 10 s", 260), ("AVX X7R 260C 10 s", 260), ("Coilcraft XFL 260C", 260), ("Harwin P70 260C 10 s", 260)]:
    L.append("margin %s: limit %d C - profile upper %d C = %d C" % (name, lim, peak_hi, lim - peak_hi))
for name, lim in [("J1 above 230 C", 60), ("Alps above 230 C", 40), ("Murata 230 C min test 30+-10 s", 40)]:
    L.append("margin %s: limit %d s - profile 35 s = %d s" % (name, lim, lim - 35))
open(os.path.join(W, "logs", "calc.log"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
