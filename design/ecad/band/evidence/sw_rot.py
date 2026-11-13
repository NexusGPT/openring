import pcbnew
b=pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/band/flex1-us9.kicad_pcb"))
for f in b.GetFootprints():
    print(f.GetReference(), f.GetFPID().GetLibItemName(), f.GetOrientationDegrees(), [ (p.GetNumber(), p.GetNetname()) for p in f.Pads()][:8])
