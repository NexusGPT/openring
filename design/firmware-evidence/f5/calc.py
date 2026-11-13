"""Every figure F5 recomputes, from inputs read from files on disk.

Inputs (each with its source):
  cells per size: architecture.md 17.17 table (read from the file below)
  recording current base 4.0 mA: architecture 17.15 and 17.17 ("recording at 4.0 mA")
  microphone current 0.63 mA: Knowles text line 97; old part 0.58 mA: F4 section 8.5 caveat
  standby 0.03 mA: firmware F4 section 8.5 (architecture section 4)
  CHARGE_CURRENT 15 mA: architecture 17.13
  motor 80 mA running, 175 mA start: architecture 17.16
  light: Vf 1.767 V at 1.5 mA (architecture 17.21), R41 820 ohm, Q2 0.7 ohm (sch-notes 12.1 item 20)
  sensitivity -26 dBFS (Knowles text line 100), old -37 dBFS (im68d128b-brief.txt line 12)
  SNR 64.5 dB(A) (Knowles line 102), AOP 120 dB SPL (Knowles line 105)
  VDD_MIC capacitors C31, C32 1 uF, C35, C36 100 nF, C86 1.0 uF (netlist.csv, parts.csv)
"""
import re
import sys

arch = open(sys.argv[1], encoding="utf-8").read()
sec = arch[arch.index("### 17.17 "):arch.index("### 17.18 ")]
sizes = re.findall(r"^\| US (\d+) \| ([\d.]+) mm \| ([\d.]+) to ([\d.]+) mAh \| ([\d.]+) to ([\d.]+) \|$", sec, re.M)
print("17.17 rows read:", len(sizes))
lo_min = min(float(s[2]) for s in sizes)
hi_max = max(float(s[3]) for s in sizes)
print(f"smallest cell {lo_min} mAh, largest {hi_max} mAh")

I_REC = 4.0 + 2 * (0.63 - 0.58)
print(f"recording current = 4.0 + 2 x (0.63 - 0.58) = {I_REC:.2f} mA")
I_SB = 0.03
I_CHG = 15.0

print("\nPer size: battery, recording hours at 4.1 mA, charge time at 15 mA (constant-current bound), C-rate of 15 mA")
for us, length, lo, hi, h1, h2 in sizes:
    lo, hi = float(lo), float(hi)
    print(f"US {us}: {lo} to {hi} mAh; record {lo / I_REC:.2f} to {hi / I_REC:.2f} h "
          f"(17.17 at 4.0 mA: {h1} to {h2}); charge {lo / I_CHG:.2f} to {hi / I_CHG:.2f} h; "
          f"15 mA = {I_CHG / hi:.2f} to {I_CHG / lo:.2f} C")

print("\nThresholds (state of charge share x capacity / 4.1 mA x 60)")
for name, pct in (("B15", 15), ("B5", 5), ("B2", 2)):
    for cap in (lo_min, hi_max):
        mah = pct / 100 * cap
        print(f"{name} on {cap} mAh: {pct} % x {cap} = {mah:.3f} mAh; {mah:.3f} / {I_REC:.1f} x 60 = {mah / I_REC * 60:.1f} min")

print("\nHours")
print(f"recording: {lo_min} / {I_REC:.1f} = {lo_min / I_REC:.2f} h; {hi_max} / {I_REC:.1f} = {hi_max / I_REC:.2f} h")
print(f"standby: {lo_min} / {I_SB} = {lo_min / I_SB:.1f} h = {lo_min / I_SB / 24:.1f} days; {hi_max} / {I_SB} = {hi_max / I_SB:.1f} h = {hi_max / I_SB / 24:.1f} days")
print(f"Plaud 13 mA: {lo_min} / 13 = {lo_min / 13:.2f} h; {hi_max} / 13 = {hi_max / 13:.2f} h")
print(f"first charge to 50 % from empty: 0.5 x {lo_min} / 15 = {0.5 * lo_min / 15:.2f} h; 0.5 x {hi_max} / 15 = {0.5 * hi_max / 15:.2f} h")

print("\nC-rates")
for i, what in ((80, "motor running"), (175, "motor start"), (15, "charge")):
    print(f"{what} {i} mA: {i} / {lo_min} = {i / lo_min:.2f} C; {i} / {hi_max} = {i / hi_max:.2f} C")
print(f"charge limit 1 C of the smallest cell = {lo_min} mA = {int(lo_min * 1000)} uA")
print(f"termination current 10 % of 15 mA = {0.10 * 15:.1f} mA; cool region 50 % = {0.5 * 15:.1f} mA")
print(f"charge current accuracy +-10 %: {15 * 0.9:.1f} to {15 * 1.1:.1f} mA")

print("\nMotor charge per pattern: sum over pulses of (t_on x 80 mA + 10 ms x 175 mA)")
pats = {"M1": [80], "M2": [80, 80], "M3": [80, 80, 80], "MH": [40], "MT": [25], "MW": [60], "MF": [300, 300]}
for k, pulses in pats.items():
    q = sum(t / 1000 * 80 + 0.010 * 175 for t in pulses)
    print(f"{k}: pulses {pulses} ms: {q:.2f} mA.s = {q / 3600:.5f} mAh")
print(f"start delay 0.55 ms as a share of MT 25 ms: {0.55 / 25 * 100:.1f} %")

print("\nLight")
i_led = (3.0 - 1.767) / (820 + 0.7)
print(f"R41 820 ohm: (3.0 - 1.767) / (820 + 0.7) = {i_led * 1000:.3f} mA")
i_old = (3.0 - 1.767) / (680 + 0.7)
print(f"R41 680 ohm: (3.0 - 1.767) / (680 + 0.7) = {i_old * 1000:.3f} mA")
print(f"from the cell: 1.50 x 3.0 / (3.8 x 0.9) = {1.5 * 3.0 / (3.8 * 0.9):.3f} mA")

print("\nMicrophone levels")
gain = -26 - (-37)
print(f"sensitivity change: -26 - (-37) = {gain} dB; gain_db = -{gain}; register 2 x (-{gain}) + 0x28 = {2 * -gain + 0x28} = 0x{2 * -gain + 0x28:02X}")
print(f"94 dB SPL at gain -11: -26 - 11 = {-26 - 11} dBFS (F4 old part at 0 dB: -37 dBFS)")
print(f"full scale reached at 94 + 37 = {94 + 37} dB SPL; microphone AOP 120 dB SPL is stored at 120 - 94 - 37 = {120 - 94 - 37} dBFS")
print(f"at gain 0 dB (not chosen): full scale at 94 + 26 = {94 + 26} dB SPL")
print(f"microphone noise: -26 - 64.5 = {-26 - 64.5} dBFS(A) at 0 dB; {-26 - 64.5 - 11} dBFS(A) at -11 dB")
q16 = -(6.02 * 16 + 1.76)
print(f"16-bit quantization noise against a full-scale sine: -(6.02 x 16 + 1.76) = {q16:.1f} dBFS")
import math
def psum(a, b):
    return 10 * math.log10(10 ** (a / 10) + 10 ** (b / 10))
n0 = psum(-90.5, q16)
n11 = psum(-101.5, q16)
print(f"noise sum at 0 dB: {n0:.1f} dBFS, SNR at 94 dB SPL {-26 - n0:.1f} dB; at -11 dB: {n11:.1f} dBFS, SNR {-37 - n11:.1f} dB [CALC, assumes 16-bit truncation after the gain, not A-weighted]")

print("\nVDD_MIC rise")
c = 1.0 + 1.0 + 0.1 + 0.1 + 1.0
print(f"C31 + C32 + C35 + C36 + C86 = 1.0 + 1.0 + 0.1 + 0.1 + 1.0 = {c:.1f} uF; {c:.1f} uF x 1.8 V / 25 mA = {c * 1.8 / 25:.3f} ms")
