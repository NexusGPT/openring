"""Land patterns and lane plan shared by make_lib.py, build_band.py and check_band.py.  Pure Python.
Frames
  model (X, Y): the ring model axes (X along the finger, +Y toward the thumb side); J_BAND_B at Y > 0 (FLEX2), J_BAND_A at Y < 0 (FLEX1).
  tail (u, v): u along the tail from the tail end that goes under the board; v = X + 2.5 (so the neck centre is v = 0).
  KiCad board file of a tail: x = OX + u, y = OY + s * v with s = +1 (FLEX2) and s = -1 (FLEX1); looked at from the outer face (F.Cu).
"""
# ---- J_BAND lands under the board, 2 rows x 4 columns (band-interface.md section 2)
COLS_X = [-3.015, -2.505, -1.995, -1.485]      # model X of the 4 columns, pitch 0.51 (foot X -3.5 to -1.0, centre -2.25)
FAR_Y, NEAR_Y = 3.875, 4.775                   # |Y| of the two rows (tail end at |Y| 3.4; fold starts at |Y| 5.145)
LAND_U, LAND_V = 0.30, 0.30                    # tail land: along the tail x across
BOARD_LAND = (0.30, 0.55)                      # board land: X x Y
V_OFF = 2.5                                    # v = X + 2.5

# pin -> (pin name, net, row, column)
JBAND_A = {1: ("UP", "JOY_UP", "far", 3), 2: ("DOWN", "JOY_DOWN", "far", 0), 3: ("LEFT", "JOY_LEFT", "far", 1),
           4: ("RIGHT", "JOY_RIGHT", "near", 3), 5: ("CENTRE", "BTN_REC", "near", 0), 6: ("MOT-", "GND", "far", 2),
           7: ("MOT+", "VMOT", "near", 1), 8: ("GND", "GND", "near", 2)}
JBAND_B = {1: ("CELL+", "VBAT", "far", 0), 2: ("CELL-", "GND", "far", 2), 3: ("NTC", "NTC", "far", 1),
           4: ("VBUS", "VBUS", "near", 2), 5: ("D-", "USB_DN", "near", 1), 6: ("D+", "USB_DP", "near", 0),
           7: ("GND", "GND", "far", 3)}
# FLEX2: far row lands go to B.Cu through a via in the gap; near row lands carry F.Cu lines (USB). FLEX1: far row B.Cu (switch lines),
# near row F.Cu (CENTRE, VMOT) and the two GND lands (strap, one via in the land of pin 8).
U_FAR, U_NEAR = FAR_Y - 3.4, NEAR_Y - 3.4      # 0.475, 1.375 (centres, along the tail)
U_VIA = 0.925                                  # via row in the gap between the rows


def land_model_xy(table, pin, side):
    nm, net, row, col = table[pin]
    y = FAR_Y if row == "far" else NEAR_Y
    return COLS_X[col], side * y


def land_tail_uv(table, pin):
    nm, net, row, col = table[pin]
    return (U_FAR if row == "far" else U_NEAR), COLS_X[col] + V_OFF


# ---- switch (Alps SKTAAAE010, catalog w4_alps_skta_catalog.pdf page 2, drawing No.1)
SW_PAD = 0.55
SW_PAD_X, SW_PAD_Y = 1.325, 0.375              # pad centres from the switch centre (land dimensions 3.2 outer, 2.1 inner, 1.3 over, 0.2 gap)
SW_POS = {"SW2": (0.0, 0.0), "SW1": (0.0, 2.4), "SW3": (0.0, -2.4), "SW4": (-2.4, 0.0), "SW5": (2.4, 0.0)}   # head frame (x, t)
SW_UP = {"SW1": "JOY_UP", "SW2": "BTN_REC", "SW3": "JOY_DOWN", "SW4": "JOY_LEFT", "SW5": "JOY_RIGHT"}
SW_WANT = {   # populated pads: P1 (signal) and P2 (GND) centres in the head frame (x, t), from the routing plan
    "SW1": {"P1": (-1.325, 2.025), "P2": (1.325, 2.025)},
    "SW3": {"P1": (1.325, -2.025), "P2": (-1.325, -2.025)},
    "SW4": {"P1": (-2.025, -1.325), "P2": (-2.025, 1.325)},
    "SW5": {"P1": (2.025, 1.325), "P2": (2.025, -1.325)},
}

# ---- terminal maps: netlist (ref, pin) -> pads of the footprint on the tail
TERMINALS = {
    "SW": {"P1": ["1", "3"], "P2": ["2", "4"]},
}
# cell side: PRT1 stands for BT1 pins and RT1 pins on the tail (band-interface.md section 5)
PRT1_MAP = {("BT1", "1"): "1", ("BT1", "2"): "2", ("RT1", "1"): "3", ("RT1", "2"): "2"}
PRT1_PADS = {"1": ("P+", "VBAT"), "2": ("P-", "GND"), "3": ("NTC", "NTC")}

# ---- rules (JLCPCB flexible PCB capabilities page, evidence/web/jlc_flex_text.txt)
RULES = dict(track_min=0.08, clearance=0.10, pad_to_track=0.25, pad_to_pad=0.15, edge=0.30, via_dia=0.30, via_drill=0.10,
             ring_min=0.10, outline_tol=0.10)
