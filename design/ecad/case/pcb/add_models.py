#!/usr/bin/env python3
"""Attaches 3D models to the footprints of a finished board file (run with KiCad's Python):  run_kipy.sh add_models.py <board.kicad_pcb>
 - KiCad's own library models (path ${KICAD10_3DMODEL_DIR}/...): R 0402 (Resistor_SMD), C 0402 0603 0805 (Capacitor_SMD), U5 SOT-23-6, U2 QFN-24 4x4 EP 2.6 x 2.6, J1 USB4105 (GCT).
 - Plain boxes of the maker's body size, made by make_box_models.py (pcb/models/*.step): U1 module, L1, L2, U3, U4, U6, LED1, P1 to P4 (cylinder).
 - No model: wire pads, test pads, E1, TH1 (bead thermistor, no body drawn), BT1 (virtual cell), WP pads."""
import sys
import pcbnew

LIBM = "${KICAD10_3DMODEL_DIR}"
MODELS = "${KIPRJMOD}/models"


def lib(ref, fpname):
    if fpname == "SMD_0402":
        return LIBM + ("/Resistor_SMD.3dshapes/R_0402_1005Metric.step" if ref.startswith("R") else "/Capacitor_SMD.3dshapes/C_0402_1005Metric.step")
    if fpname == "SMD_0603":
        return LIBM + "/Capacitor_SMD.3dshapes/C_0603_1608Metric.step"
    if fpname == "SMD_0805":
        return LIBM + "/Capacitor_SMD.3dshapes/C_0805_2012Metric.step"
    if fpname == "SOT-23-6_DBV":
        return LIBM + "/Package_TO_SOT_SMD.3dshapes/SOT-23-6.step"
    if fpname == "WQFN-24_RTW_4x4":
        return LIBM + "/Package_DFN_QFN.3dshapes/QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm.step"
    if fpname == "USB4105-GF-A":
        return LIBM + "/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step"
    return None


BOXES = {"ESP32-S3-MINI-1": "box_esp32s3_mini1.step", "L_XFL40xx_4x4": None, "DFN-10_DLA_2x3": "box_dfn10.step", "LGA16_9x10_ZDSD": "box_lga16.step",
         "USON-10_DQA_1x2.5": "box_uson10.step", "LED_APTF1616": "box_led1616.step", "HARWIN_P70_6000045R": "cyl_harwin.step"}
INDUCTOR = {"L1": "box_xfl4020.step", "L2": "box_xfl4015.step"}

b = pcbnew.LoadBoard(sys.argv[1])
n_lib = n_box = 0
for fp in b.GetFootprints():
    ref = fp.GetReference()
    fpname = str(fp.GetFPID().GetLibItemName())
    path = lib(ref, fpname)
    kind = "library"
    if path is None:
        f = INDUCTOR.get(ref) if fpname == "L_XFL40xx_4x4" else BOXES.get(fpname)
        if f is None:
            continue
        path = MODELS + "/" + f
        kind = "box"
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = path
    m.m_Scale = pcbnew.VECTOR3D(1, 1, 1)
    m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
    m.m_Offset = pcbnew.VECTOR3D(0, 0, 0)
    m.m_Show = True
    fp.Add3DModel(m)
    if kind == "library":
        n_lib += 1
    else:
        n_box += 1
pcbnew.SaveBoard(sys.argv[1], b)
print("models attached: %d from KiCad's library, %d simple boxes/cylinders" % (n_lib, n_box))
