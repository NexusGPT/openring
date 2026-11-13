"""Metal between the motor pocket and the -Y floor slot, and between the pocket and the panel cavity, as check_thin.py computes them (ctx motor_cut, panel_cut, slot box),
built from thin.py's own helpers and constants without the exterior (a few seconds). Env THIN_OVERRIDE sets bore_d, motor_x, slot_w."""
import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin"))
import thin
from thin import P, R_LINER, lplace, rbox, MOTOR_ROOF
from build123d import Cylinder, Pos, Box
zf = 0.40
mh = P["motor_t"] + MOTOR_ROOF + P["motor_glue"]
cut = lplace(P["motor_pocket_angle"], Cylinder((P["motor_d"] + 0.2) / 2, mh), x=P["motor_x"], r=R_LINER - P["motor_glue"] + mh / 2)
slot = Pos(P["slot_x"], -P["tail_y"], (zf + 0.6 + P["slot_z0"]) / 2) * Box(P["slot_w"], 0.6, zf + 0.6 - P["slot_z0"])
panel = rbox(P["scr_x"] + 0.1, P["scr_y"] + 0.1, 8.0, 0, 0, zf + 4.0, 0.1)
print(f"US {thin.US_SIZE} motor_x {P['motor_x']} slot_w {P['slot_w']}: pocket to the -Y floor slot {cut.distance_to(slot):.4f}, pocket to the panel cavity {cut.distance_to(panel):.4f}")
