# review 3: honest-control fault for the rules check: copy of flex2-us9 with every track of net VBUS removed, saved in review3-work/broken
import pcbnew
src = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/band/flex2-us9.kicad_pcb")
dst = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review3-work/broken/flex2-us9-novbus.kicad_pcb")
b = pcbnew.LoadBoard(src)
gone = [t for t in b.GetTracks() if t.GetNetname() == "VBUS"]
for t in gone: b.Remove(t)
pcbnew.SaveBoard(dst, b)
print("removed", len(gone), "track items of VBUS")
