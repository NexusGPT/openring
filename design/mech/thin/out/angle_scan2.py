import sys, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from build123d import Box, Pos
thin.CH["notch_motor"] = False
blkbox = Pos(0, 0, 1.575) * Box(27.45, 12.9, 2.35)
for a in [48, 49, 50, 51, 52]:
    thin.P["motor_angle"] = -a
    m = thin.P  # motor solid only
    mo = thin.lcyl(-a, thin.P["motor_d"], thin.R_LINER, thin.R_LINER + thin.P["motor_t"])
    x = mo & blkbox
    blk = x.volume if x is not None else 0.0
    row = f"angle {a}: motor x block interior {blk:.4f} mm3; analytic far-rim wall by roof gap:"
    for roof in (0.0, 0.05, 0.1):
        rim = math.hypot(thin.R_LINER + thin.P["motor_t"] + roof, 3.5)
        d = math.degrees(math.atan2(3.5, thin.R_LINER + thin.P["motor_t"] + roof))
        row += f" {roof}: {thin.r_outer(a + d) - rim:.3f}"
    print(row, flush=True)
