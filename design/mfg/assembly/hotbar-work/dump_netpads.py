"""List every pad on the nets of the 15 J_BAND lands (copy of ring.kicad_pcb, KiCad Python). usage: run_kipy.sh dump_netpads.py <board> <out>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
nets = {"JOY_UP", "JOY_DOWN", "JOY_LEFT", "JOY_RIGHT", "BTN_REC", "VMOT", "GND", "VBAT", "NTC", "VBUS", "USB_DN", "USB_DP"}
out = ["ref,pad,net,side,x_model,y_model,footprint"]
for fp in b.GetFootprints():
    side = "F" if fp.GetLayer() == pcbnew.F_Cu else "B"
    for p in fp.Pads():
        if p.GetNetname() in nets and p.GetNetname() != "GND":
            c = p.GetPosition()
            out.append(f"{fp.GetReference()},{p.GetNumber()},{p.GetNetname()},{side},{c.x/1e6-100:.3f},{c.y/1e6-100:.3f},{fp.GetFPID().GetLibItemName()}")
open(sys.argv[2], "w").write("\n".join(out) + "\n")
print(len(out) - 1, "pads")
