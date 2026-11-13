# shared: load a footprint, place it, return courtyard bbox (incl. stroke) and pads in model coordinates
import pcbnew
LIB={'OpenRing':(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/OpenRing.pretty"),
     'OpenRingBand':(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/band/OpenRingBand.pretty")}
_cache={}
def load(fpname):
    lib,n=fpname.split(':')
    if fpname not in _cache: _cache[fpname]=pcbnew.FootprintLoad(LIB[lib],n)
    return _cache[fpname]
def place(fpname,x,y,rot):
    fp=pcbnew.FOOTPRINT(load(fpname))
    fp.SetPosition(pcbnew.VECTOR2I(int(round(x*1e6)),int(round(y*1e6))))
    fp.SetOrientationDegrees(rot)
    c=fp.GetCourtyard(pcbnew.F_CrtYd)
    # bbox of the courtyard outline including its 0.05 stroke (as footprint-notes measures)
    bb=c.BBox()
    cy=(bb.GetX()/1e6-0.025,bb.GetY()/1e6-0.025,bb.GetRight()/1e6+0.025,bb.GetBottom()/1e6+0.025)
    pads=[]
    for p in fp.Pads():
        b=p.GetBoundingBox()
        pads.append((p.GetNumber(),p.GetPosition().x/1e6,p.GetPosition().y/1e6,(b.GetX()/1e6,b.GetY()/1e6,b.GetRight()/1e6,b.GetBottom()/1e6)))
    return cy,pads
