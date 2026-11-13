import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
x, y, r = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
for fp in b.GetFootprints():
    for p in fp.Pads():
        px, py = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
        if abs(px - x) < r and abs(py - y) < r:
            print(fp.GetReference(), p.GetNumber(), p.GetNetname(), round(px, 2), round(py, 2), round(pcbnew.ToMM(p.GetSize().x), 2), round(pcbnew.ToMM(p.GetSize().y), 2))
