"""Q1 arithmetic: paste aperture on each J_BAND land and the solder height it leaves after reflow.
Land 0.30 x 0.55 (band-interface.md line 23). Target height h = 0.03 (thin.py line 81, joint=0.03, the joint between land and tail).
f = metal share of the paste by volume after reflow: STARTING VALUE 0.50 (no project file gives it; lead to confirm with the paste's sheet).
Height = f x t x (aperture area) / (land area), the molten solder spread over the whole wetted land.
Area ratio = aperture area / (aperture perimeter x t); STARTING VALUE rule: at least 0.66 for a clean release (no project file gives it)."""
LX, LY, H, F = 0.30, 0.55, 0.03, 0.50
print(f"land {LX} x {LY} = {LX*LY:.4f} mm2; target h {H}; f {F}")
for t in (0.05, 0.08, 0.10, 0.12):
    ly = round(LY * H / (F * t), 3)
    ly = min(ly, LY)
    h = F * t * (LX * ly) / (LX * LY)
    ar = (LX * ly) / (2 * (LX + ly) * t)
    h_full = F * t
    print(f"stencil {t:.2f}: full-land aperture {LX} x {LY} leaves h {h_full:.3f}; for h {H}: aperture {LX:.2f} x {ly:.3f} (area {LX*ly:.4f}), h {h:.4f}, area ratio {ar:.2f} -> {'OK' if ar >= 0.66 else 'BELOW 0.66'}")
