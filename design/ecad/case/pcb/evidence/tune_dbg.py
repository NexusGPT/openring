import sys, shutil, pcbnew
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb"))
import build_boards as BB
from pcbnew import ToMM
path = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/case_main.kicad_pcb")
b = pcbnew.LoadBoard(path)
for net in ("USB_D+", "USB_D-"):
    ts = [t for t in b.GetTracks() if t.GetNetname() == net and t.Type() == pcbnew.PCB_TRACE_T]
    print(net, len(ts), sorted([round(ToMM(t.GetLength()), 2) for t in ts], reverse=True)[:8], [pcbnew.LayerName(t.GetLayer()) for t in ts][:6])
