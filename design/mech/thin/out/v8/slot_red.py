"""The arithmetic of check_thin.py's 'SLOT end clearance to the ribbon under 0.15' lines (check_thin.py: rx0, rx1, sx0, sx1), evaluated with thin.P for the
drawn neck at slot_w 2.0 (the v7 value) and 2.1 (v8). Not a full run: the model is not built."""
import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin"))
import thin
P = thin.P
sx0, sx1 = P["slot_x"] - P["slot_w"] / 2, P["slot_x"] + P["slot_w"] / 2
rx0, rx1 = P["tail_x"] - P["tail_w"] / 2, P["tail_x"] + P["tail_w"] / 2
a, b = rx0 - sx0, sx1 - rx1
print(f"slot_w {P['slot_w']}: ribbon X {rx0:.2f} to {rx1:.2f} in the slot X {sx0:.2f} to {sx1:.2f}: free space to the -X end {a:.3f}, to the +X end {b:.3f} mm (rule 0.15) -> {'FINDING: SLOT end clearance to the ribbon under 0.15' if min(a, b) < 0.15 - 1e-9 else 'ok'}")
