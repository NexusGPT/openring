import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
for fp in b.GetFootprints():
    print(fp.GetReference(), fp.GetLayerName(), [ (p.GetNumber(), p.GetNetname(), p.GetPosition().x/1e6, p.GetPosition().y/1e6, p.GetLayerSet().Seq()[0] if p.GetLayerSet().Seq() else None, p.GetShape()) for p in fp.Pads()][:3])
ts = list(b.GetTracks())
print(len(ts), set(type(t).__name__ for t in ts))
t=ts[0]; print(t.GetStart().x, t.GetEnd().x, t.GetLayerName(), t.GetNetname(), t.GetLength())
v=[t for t in ts if type(t).__name__=='PCB_VIA'][0]; print(v.GetPosition().x, v.GetWidth(pcbnew.F_Cu) if hasattr(v,'GetWidth') else None, v.TopLayer(), v.BottomLayer())
print(pcbnew.Version() if hasattr(pcbnew,'Version') else pcbnew.GetBuildVersion())
