import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from build123d import Box, Pos
thin.CH["notch_joy"] = False if "notch_joy" in thin.CH else None
m = thin.build(); by = {p["name"]: p["solid"] for p in m["parts"]}
x = by["main_board"] & by["joystick_cap"]
bb = x.bounding_box()
print("cap x board bbox: X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f vol %.4f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z, x.volume))
