import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
ok = pcbnew.ImportSpecctraSES(b, sys.argv[2])
print("import ok:", ok)
tr = [t for t in b.GetTracks()]
vias = [t for t in tr if t.Type() == pcbnew.PCB_VIA_T]
print("tracks:", len(tr) - len(vias), "vias:", len(vias))
pcbnew.SaveBoard(sys.argv[3], b)
