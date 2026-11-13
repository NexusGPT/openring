"""Per size: the model's cap top (largest vertex radius) against the exterior's joystick top, and the surface radius used."""
import math, os, sys, subprocess
T = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin")
if len(sys.argv) > 1:
    sys.path.insert(0, T)
    import thin
    m = thin.build()
    c = m["ctx"]
    cap = [p for p in m["parts"] if p.name == "joystick_cap"][0].solids()["polymer"]
    capr = max(math.hypot(v.Y, v.Z - thin.ZC) for v in cap.vertices())
    print(f"US {thin.US_SIZE}: surface r {c['r_outer_joy']}, frame top r {c['joy_frame_top']}, cap rim r {c['joy_cap_rim']}, cap top r {capr:.3f}, exterior joystick top r {c['rtop_joy_exterior']}, difference {capr - c['rtop_joy_exterior']:+.3f}, cap rim to flange top {c['joy_cap_rim'] - thin.R_PL1:.4f}", flush=True)
else:
    EXT = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/look/s1/out")
    for n, b in ((7, 17.3196), (8, 18.1324), (9, 18.9452), (10, 19.758), (11, 20.5708), (12, 21.3836), (13, 22.1964)):
        env = dict(os.environ, THIN_EXTERIOR=f"{EXT}/ring-merged32h-us{n}.step", THIN_OVERRIDE=f"bore_d={b}")
        subprocess.run(["nice", "-n", "19", sys.executable, __file__, "one"], env=env, check=False)
