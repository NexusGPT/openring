"""Dimension-chain arithmetic from numbers stated in the design files (read-only; my CALC, not a CAD run).
Each input names its source line."""
import math

print("== 1. block stack (architecture.md line 424, 17.2; glass 1.10 from 17.8 line 488)")
stack = [0.40, 0.05, 1.00, 0.30, 0.10, 0.80, 0.10]
s = sum(stack)
print("  stack below glass =", round(s, 3))
print("  + glass 0.40 (17.2) =", round(s + 0.40, 3), " stated total 3.15, block 3.20")
print("  + glass 1.10 (17.8) =", round(s + 1.10, 3), " stated block 3.85 at centre line")
R = 30.7
for xe in (6.40,):  # screen panel half width 12.8/2 (architecture line 315)
    drop = R - math.sqrt(R * R - xe * xe)
    top = 3.85 - drop
    print("  glass top over panel edge (x=6.40):", round(top, 3), " glass there =", round(top - s, 3), " stated 0.42")

print("== 2. band radial stack (architecture line 433)")
print("  liner 0.3 + cell 1.6 + gap 0.2 + shell 0.5 =", round(0.3 + 1.6 + 0.2 + 0.5, 3), " stated band 2.6")
print("  joystick stack liner 0.3 + flex 0.15 + switch 0.53 + flange 0.4 + shell 0.5 =", round(0.3 + 0.15 + 0.53 + 0.4 + 0.5, 3),
      " (17.3 says inside 3.6; bom.csv CAP1 says '= 3.1 inside')")

print("== 3. cell arc at US 9 (architecture 17.10 line 519)")
r9 = 18.95 / 2 + 0.3 + 0.8
span = (180 - 39) + (180 - 167)
print("  centre radius", round(r9, 3), " span deg", span, " length", round(r9 * math.radians(span), 2), " stated 28.4, 154 deg")

print("== 4. per-size check of the constant angles used by specs/cell.md lines 47-52")
def bore(size):
    return 11.63 + 0.8128 * size  # mech-notes line 7 as cited by specs/body.md line 93
# joystick switch footprint: switches +133 to +167 at US 9 (architecture line 519) -> half span 17 deg about +150
r_sw9 = bore(9) / 2 + 0.3 + 0.15 + 0.53 / 2  # switch mid-height radius (liner 0.3, flex 0.15, switch 0.53)
half_mm = r_sw9 * math.radians(17)
# floor-slot entry: away ribbon enters the channel at -36.8 deg at US 9 (thin-notes.md V2), slot at Y -5.9
r_ch9 = 5.9 / math.sin(math.radians(36.8))
for size in (5, 6, 7, 8, 9, 10, 11, 12, 13):
    b = bore(size)
    r_sw = b / 2 + 0.3 + 0.15 + 0.53 / 2
    half = math.degrees(half_mm / r_sw)
    joy_edge = 150 + half
    r_ch = r_ch9 + (b - bore(9)) / 2
    slot = math.degrees(math.asin(min(1.0, 5.9 / r_ch)))
    print(f"  US {size:2d}: bore {b:5.2f}  joystick switch edge +{joy_edge:6.1f} (cell ends +167: overlap {max(0, joy_edge-167):4.1f} deg)"
          f"  ribbon slot angle -{slot:5.1f} (cell starts -39: overlap {max(0, slot-39):4.1f} deg)")

print("== 5. antenna against the metal body (placement.csv antenna row; body.md line 87 panel pocket 27.45 x 12.9; architecture line 156 keep-out 4.2 x 4.7)")
ax, ay, sx, sy = -12.7, 4.4, 1.6, 3.2
xmin, xmax, ymin, ymax = ax - sx / 2, ax + sx / 2, ay - sy / 2, ay + sy / 2
wall_x, wall_y = -27.45 / 2, 12.9 / 2
print("  antenna x", round(xmin, 3), "to", round(xmax, 3), " y", round(ymin, 3), "to", round(ymax, 3))
print("  gap to hand-end metal wall (x", wall_x, "):", round(xmin - wall_x, 3), "mm")
print("  gap to thumb-side metal wall (y", wall_y, "):", round(wall_y - ymax, 3), "mm")
print("  keep-out half sizes 2.1 / 2.35 reach x", round(ax - 2.1, 3), " y", round(ay + 2.35, 3), " -> inside metal:", (ax - 2.1) < wall_x or (ay + 2.35) > wall_y)
print("  floor: 0.40 mm metal at Z 0 to 0.40; antenna centre Z 1.05, size 1.2 -> bottom Z", round(1.05 - 0.6, 3))
