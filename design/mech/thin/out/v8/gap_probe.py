"""Neck-to-motor gap by size and motor_x, on small solids built with thin.py's own constants (no exterior, no body: a few seconds).
Usage (env THIN_OVERRIDE sets the bore and motor_x): gap_probe.py ; prints 'US n motor_x v: neck to motor coin a, neck to pigtail b, group least c'.
Validation: the check's line 'RIBBON-CLEARANCE band_flex_thumb foot to vibration_motor' of the same size at motor_x 0.7."""
import math, os, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin"))
import thin
from thin import P, ZC, R_LINER, R_IN, R_F0, R_F1, lplace, box
from build123d import Cylinder, fillet

t_fin = P["flex_fin"]
R_FM = (R_F0 + R_F1) / 2
z_in = ZC + math.sqrt(R_FM ** 2 - P["tail_y"] ** 2)
RC = P["fold_r_in"] + t_fin / 2
Z_BD0 = 1.45
Z_ARC0 = Z_BD0 - P["pad_t"] - P["joint"] - t_fin / 2 - RC
tx, tw = P["tail_x"], P["tail_w"]
sg = -1
neck = box(tw, t_fin, Z_ARC0 - z_in, tx, sg * P["tail_y"], (z_in + Z_ARC0) / 2)
mA, mX = P["motor_angle"], P["motor_x"]
coin = lplace(mA, fillet(Cylinder(P["motor_d"] / 2, P["motor_t"]).edges(), 0.2), x=mX, r=R_LINER + P["motor_t"] / 2)
px_ = mX - P["motor_d"] / 2 - 0.45
pig1 = lplace(mA, box(0.5, 1.0, 0.1, 0, 0, 0), x=px_ + 0.15, t=-1.2, r=R_LINER + P["motor_t"] / 2)
pig2 = lplace(mA, box(0.1, 1.0, P["motor_t"] / 2, 0, 0, 0), x=px_ - 0.1, t=-1.2, r=R_LINER + P["motor_t"] / 4)
d1 = neck.distance_to(coin)
d2 = min(neck.distance_to(pig1), neck.distance_to(pig2))
print(f"US {thin.US_SIZE} bore {P['bore_d']} motor angle {mA} motor_x {mX}: neck to motor coin {d1:.4f}, neck to pigtail {d2:.4f}, least {min(d1, d2):.4f}")
