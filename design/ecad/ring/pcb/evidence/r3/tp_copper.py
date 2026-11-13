# for TP8 TP9 TP11: pad net, pad layers, and every track, via and zone fill whose copper touches the pad on the pad's own layers
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
print("VIATYPE", {n: getattr(pcbnew, n) for n in dir(pcbnew) if n.startswith("VIATYPE_")})
fps = {f.GetReference(): f for f in b.GetFootprints()}
for r in ["TP8", "TP9", "TP11"]:
    f = fps.get(r)
    if f is None: print(r, "absent"); continue
    for p in f.Pads():
        lays = [l for l in p.GetLayerSet().CuStack()]
        print(r, "pad", p.GetNumber(), "net %r" % p.GetNetname(), "netcode", p.GetNetCode(), "copper layers", [b.GetLayerName(l) for l in lays])
        n = 0
        for l in lays:
            ps = p.GetEffectiveShape(l)
            for t in b.GetTracks():
                if t.IsOnLayer(l) and t.GetEffectiveShape(l).Collide(ps, 0):
                    n += 1; print("  touches", "via" if t.Type() == pcbnew.PCB_VIA_T else "track", t.GetNetname(), b.GetLayerName(l))
            for z in b.Zones():
                if z.IsOnLayer(l) and z.GetFilledPolysList(l).Collide(ps.Centre() if False else p.GetPosition(), 0):
                    n += 1; print("  zone fill at pad centre", z.GetNetname(), b.GetLayerName(l))
        print("  copper items touching:", n)
