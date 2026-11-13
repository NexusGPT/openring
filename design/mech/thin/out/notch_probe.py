import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
thin.CH["notch_motor"] = False
m = thin.build()
by = {p["name"]: p["solid"] for p in m["parts"]}
x = by["main_board"] & by["vibration_motor"]
bb = x.bounding_box()
print("motor x board overlap bbox: X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f  vol %.4f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z, x.volume))
mb = by["vibration_motor"].bounding_box()
print("motor bbox Z max %.3f Y min %.3f" % (mb.max.Z, mb.min.Y))
