"""Distance along FLEX2 from the foot's outer end (u 1.745) to the first PRT1 tab land, per size.
u of the slot junction = FOOT_EXTRA + lv (band_geom.py lines 45, 70, 91); first PRT1 land at s after the junction:
0.586, 0.604, 0.620, 0.836, 1.154, 1.466, 1.774 mm for US 7 to 13 (band-interface.md line 116). usage: python3 -I prt1_distance.py <band_geom.py>"""
import sys, importlib.util
spec = importlib.util.spec_from_file_location("bg_ro", sys.argv[1]); bg = importlib.util.module_from_spec(spec); spec.loader.exec_module(bg)
S = dict(zip(bg.SIZES, (0.586, 0.604, 0.620, 0.836, 1.154, 1.466, 1.774)))
for us in bg.SIZES:
    s = bg.Size(us)
    u = s.u_j + S[us]
    print(f"US {us}: junction u {s.u_j:.3f}, first PRT1 land u {u:.3f}, from the foot's outer end {u - bg.LF:.3f} mm, from the blade edge (|Y| 5.05, u 1.65) {u - 1.65:.3f} mm")
