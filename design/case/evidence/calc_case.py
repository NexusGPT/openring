# Arithmetic for case-architecture.md. Every printed line is cited there.
import math

print("== data per recorded hour (architecture.md T1: raw, 16 kHz, 16 bits, 4 channels)")
bps = 16000 * 2 * 4
mb_h = bps * 3600 / 1e6
print(f"bytes per second = 16000 x 2 x 4 = {bps}")
print(f"MB per recorded hour = {bps} x 3600 / 1e6 = {mb_h:.1f}")

print("== full speed, raw line rate 12 Mbit/s")
fs_raw = 12e6 / 8
t = mb_h * 1e6 / fs_raw
print(f"12 Mbit/s = {fs_raw/1e6:.3f} MB/s; {mb_h:.1f} MB / {fs_raw/1e6:.3f} MB/s = {t:.1f} s = {t/60:.2f} min (bound, never reached)")

print("== full speed, bulk ceiling 19 packets x 64 bytes per 1 ms frame")
fs_bulk = 19 * 64 * 1000
t_fs = mb_h * 1e6 / fs_bulk
print(f"19 x 64 x 1000 = {fs_bulk} B/s = {fs_bulk/1e6:.3f} MB/s; {mb_h:.1f} MB / {fs_bulk/1e6:.3f} MB/s = {t_fs:.1f} s = {t_fs/60:.2f} min per recorded hour")
print(f"10-hour day: {10*t_fs/60:.1f} min; 17-hour full ring: {17*t_fs/60:.1f} min")
print(f"hours of recording copied inside 90 min: 90 x 60 x {fs_bulk} / {mb_h*1e6:.0f} = {90*60*fs_bulk/(mb_h*1e6):.2f} h")

print("== high speed (ESP32-P4), limited by the ring's storage read over SPI, 2 MB/s (architecture.md section 8)")
t_hs = mb_h / 2.0
print(f"{mb_h:.1f} MB / 2.0 MB/s = {t_hs:.1f} s = {t_hs/60:.2f} min per recorded hour; 10-hour day {10*t_hs/60:.1f} min")
print(f"difference full speed minus high speed = {(t_fs-t_hs)/60:.2f} min per recorded hour")

print("== case cell sizing")
e_ring = 0.135 * 3.85
print(f"ring cell energy = 0.135 Ah x 3.85 V = {e_ring:.3f} Wh")
boostv = 4.55 + 0.064 * 7
print(f"BOOSTV code 7 = 4.55 + 0.064 x 7 = {boostv:.3f} V")
eta_lin = 3.85 / boostv
eta_boost = 0.85
e_case = e_ring / (eta_lin * eta_boost)
print(f"ring linear charger efficiency = 3.85 / {boostv:.3f} = {eta_lin:.3f}; boost efficiency taken {eta_boost}")
print(f"case energy per ring charge = {e_ring:.3f} / ({eta_lin:.3f} x {eta_boost}) = {e_case:.3f} Wh; 3 charges = {3*e_case:.3f} Wh")
for mah in (500, 700):
    wh = mah / 1000 * 3.7
    print(f"{mah} mAh x 3.7 V = {wh:.2f} Wh -> {wh/e_case:.2f} ring charges")
print(f"minimum case cell for 3 charges = {3*e_case/3.7*1000:.0f} mAh")

print("== ring supply current limit, TPS2553 IOSmin = 25230 / RILIM^1.016 (RILIM in kilo-ohm)")
r = (25230 / 400) ** (1 / 1.016)
print(f"RILIM for 400 mA minimum = {r:.1f} kOhm; chosen 59.0 kOhm gives IOSmin = {25230/59.0**1.016:.0f} mA")

print("== 3.3 V rail, TPS63802 R1 = R2 x (VOUT/VFB - 1), VFB 0.5 V")
print(f"R2 = 100 kOhm -> R1 = {100*(3.3/0.5-1):.0f} kOhm; VOUT with 560/100 = {0.5*(1+560/100):.3f} V")

print("== case cell charge, DNK852338 allowed max 0.5C")
print(f"0.5C x 700 mAh = {0.5*700:.0f} mA; time at constant current to full >= 700/350 = {700/350:.1f} h")
print("== pin compression")
free = 5.182
mid = 0.70
print(f"free height {free} mm, mid stroke {mid} mm -> board top {-(free-mid):.3f} mm below the seat")
