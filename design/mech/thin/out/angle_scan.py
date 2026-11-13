import sys, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from build123d import Box, Pos
thin.CH["notch_motor"] = False
ang = [float(a) for a in sys.argv[1:]]
for a in ang:
    thin.P["motor_angle"] = -a; thin.P["motor_pocket_angle"] = -a
    m = thin.build(); by = {p["name"]: p["solid"] for p in m["parts"]}
    inter = by["vibration_motor"] & (Pos(0, 0, 1.575) * Box(27.45, 12.9, 2.35))
    blk = inter.volume if inter is not None else 0.0
    bd = by["main_board"] & by["vibration_motor"]
    w, where = thin.motor_rim_min_wall(by["outer_body"], n=24)
    print(f"angle {a}: min wall {w:.2f} at {where}; motor x block interior {blk:.4f} mm3; motor x board {bd.volume if bd is not None else 0:.4f}", flush=True)
