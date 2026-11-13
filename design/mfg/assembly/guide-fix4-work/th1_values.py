#!/usr/bin/env python3
"""H3: expected ohmmeter readings that prove the two case thermistor joints TH1.1 and TH1.2.

Sources (read here, numbers typed from them; each printed with its line):
- design/ecad/case/netlist.csv: TS node = RT1 pin 2, RT2 pin 1, TH1 pin 1, U2 pin 11 (lines 224 to 227);
  GND: TH1 pin 2 (line 97), RT2 pin 2 (line 96); REGN: RT1 pin 1, C8 pin 1, U2 pin 22 (lines 163 to 165).
- design/ecad/case/parts.csv: RT1 5.23k (line 29), RT2 30.1k (line 30), TH1 10k 103AT (line 31), C8 4.7uF (line 26).
- design/datasheets/w16_semitec_P12-13-AT-Thermistor.txt: 103AT R25 10.0 kohm, B 3435 K +-1 % (line 105),
  R/T table 103AT column: 10 C 17.96, 20 C 12.09, 25 C 10.00, 30 C 8.313 kohm (lines 182 to 185);
  R25 tolerance: the table header line 92 names the column, line 101 holds "+-1 %" (my reading of the
  flattened table: the tolerance printed for the AT series rows).
Model of the meter reading between TP16 (GND) and the TS node, board unpowered:
  RT2 always; TH1 once fitted; RT1 leads to REGN, which has only C8 to GND and the unpowered charger pin.
  Once C8 has charged through the meter, the RT1 branch carries no steady current IF the unpowered charger
  pins draw none: no file states the TS or REGN pin's resistance with the chip unpowered (unverified), so the
  check also uses the difference method, which cancels any steady parallel branch:
  R_TH1 = R0 * R1 / (R0 - R1) for R1 = R0 || R_TH1.
"""
import math

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())


def show(path, lines):
    t = open(ROOT + '/' + path, encoding='utf-8').read().split('\n')
    for n in lines:
        print(f'  {path}:{n}: {t[n-1].strip()[:160]}')


def par(a, b):
    return a * b / (a + b)


print('SOURCES')
show('design/ecad/case/netlist.csv', [96, 97, 163, 164, 165, 224, 225, 226, 227])
show('design/ecad/case/parts.csv', [26, 29, 30, 31])
show('design/datasheets/w16_semitec_P12-13-AT-Thermistor.txt', [105, 182, 183, 184, 185])

RT1, RT2 = 5.23, 30.1          # kohm
TOL_RT = 0.01                  # 1 % resistors (RC0402FR: F = 1 %, parts.csv mpn)
B = 3435.0
table = {10: 17.96, 20: 12.09, 25: 10.00, 30: 8.313}


def r_b(tc):
    return 10.0 * math.exp(B * (1 / (tc + 273.15) - 1 / 298.15))


def r_table(tc):
    # log-linear between the two nearest table points
    ks = sorted(table)
    for a, b in zip(ks, ks[1:]):
        if a <= tc <= b:
            la, lb = math.log(table[a]), math.log(table[b])
            return math.exp(la + (lb - la) * (tc - a) / (b - a))
    raise ValueError


print('TH1 ALONE, kohm (table, log-linear between points; B-value formula for comparison)')
for tc in (15, 20, 25, 30):
    print(f'  {tc} C: table {r_table(tc):.3f}  B-formula {r_b(tc):.3f}')
lo = min(r_table(30), r_b(30)) * 0.99
hi = max(r_table(15), r_b(15)) * 1.01
print(f'  range 15 to 30 C with 1 % on R25: {lo:.2f} to {hi:.2f} kohm')

print('BEFORE TH1 (R0), between the TS pad of RT2 and TP16')
print(f'  steady, RT1 branch open: RT2 = {RT2:.2f} kohm ({RT2*(1-TOL_RT):.2f} to {RT2*(1+TOL_RT):.2f})')
print(f'  first instant, C8 empty (REGN at 0 V): RT2 || RT1 = {par(RT2, RT1):.3f} kohm, then it climbs')
print('AFTER TH1 (R1), same two points, steady, RT1 branch open')
r1 = {}
for tc in (15, 20, 25, 30):
    r1[tc] = par(RT2, r_table(tc))
    print(f'  {tc} C: RT2 || TH1 = {r1[tc]:.3f} kohm')
r1lo = par(RT2 * (1 - TOL_RT), lo)
r1hi = par(RT2 * (1 + TOL_RT), hi)
print(f'  range 15 to 30 C with tolerances: {r1lo:.2f} to {r1hi:.2f} kohm')
print('FAULTS')
print(f'  one lead joint open: R1 = R0 (no drop), about {RT2:.1f} kohm')
print('  the two leads touching each other or a ground point: R1 near 0 ohm')
print('DIFFERENCE METHOD (cancels any steady branch in parallel)')
for r0, r1v in ((30.1, r1[25]), (25.0, par(25.0, 10.0))):
    print(f'  example R0 {r0:.3f}, R1 {r1v:.3f}: R0*R1/(R0-R1) = {r0*r1v/(r0-r1v):.3f} kohm')
print(f'RESULT TH1 alone {lo:.2f} to {hi:.2f} kohm; R0 about {RT2:.1f} kohm; R1 {r1lo:.2f} to {r1hi:.2f} kohm (25 C: {r1[25]:.2f})')
