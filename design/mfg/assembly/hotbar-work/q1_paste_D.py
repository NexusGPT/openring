"""Option D: paste aperture for a 0.30 x 0.30 board land (3 x 3 grid at 0.45) and its solder height. Same rule and starting values as q1_paste.py:
h = f x t x aperture / land, f 0.50 [START], target h 0.03 (thin.py line 81), area ratio at least 0.66 [START]."""
import math
LAND, H, F = 0.30, 0.03, 0.50
for t in (0.05, 0.08, 0.10, 0.12):
    side = min(math.sqrt(H * LAND * LAND / (F * t)), LAND)
    ar = side * side / (4 * side * t)
    h = F * t * side * side / (LAND * LAND)
    if ar < 0.66:
        side = LAND; ar = side * side / (4 * side * t); h = F * t
        note = "square for 0.03 fails the area ratio; full land used"
    else:
        note = "ok"
    print(f"stencil {t:.2f}: aperture {side:.3f} x {side:.3f}, h {h:.4f}, area ratio {ar:.2f} ({note})")
