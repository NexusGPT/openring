import pcbnew, os
for lib in [(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/OpenRing.pretty"),(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/band/OpenRingBand.pretty")]:
    for f in sorted(os.listdir(lib)):
        n=f[:-10]; fp=pcbnew.FootprintLoad(lib,n)
        c=fp.GetCourtyard(pcbnew.F_CrtYd); bb=c.BBox() if c.OutlineCount() else None
        pads=[(p.GetNumber(),round(p.GetPosition().x/1e6,3),round(p.GetPosition().y/1e6,3)) for p in fp.Pads()]
        print(n, 'crtyd', None if bb is None else (round(bb.GetX()/1e6,3),round(bb.GetY()/1e6,3),round(bb.GetWidth()/1e6,3),round(bb.GetHeight()/1e6,3)), 'area', round(c.Area()/1e12,3) if bb else 0, 'npads',len(pads), pads[:2] if len(pads)<=20 else '')
