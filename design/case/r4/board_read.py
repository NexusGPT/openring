"""Read a routed KiCad board (read only) with KiCad's own Python and write what the case model needs as JSON.
Usage: design/ecad/ring/pcb/run_kipy.sh board_read.py <board.kicad_pcb> <out.json>
Writes: thickness, outline polygons (KiCad sheet mm, y down), every footprint (ref, value, position, rotation, side,
3D model entries with offset / rotation / scale, pads with position, size, drill, layers, courtyard box).
Nothing is typed here: every number is the board file's."""
import json
import sys

import pcbnew

ToMM = pcbnew.ToMM


def main(path, out):
    b = pcbnew.LoadBoard(path)
    t = ToMM(b.GetDesignSettings().GetBoardThickness())
    polys = pcbnew.SHAPE_POLY_SET()
    ok = b.GetBoardPolygonOutlines(polys, False)
    outl = []
    for i in range(polys.OutlineCount()):
        o = polys.Outline(i)
        outl.append([(ToMM(o.CPoint(k).x), ToMM(o.CPoint(k).y)) for k in range(o.PointCount())])
    fps = []
    for f in b.GetFootprints():
        side = "B" if f.GetLayer() == pcbnew.B_Cu else "F"
        pos = f.GetPosition()
        models = []
        for m in f.Models():
            models.append(dict(file=m.m_Filename, show=bool(m.m_Show), offset=[m.m_Offset.x, m.m_Offset.y, m.m_Offset.z],
                               rot=[m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z], scale=[m.m_Scale.x, m.m_Scale.y, m.m_Scale.z]))
        pads = []
        for p in f.Pads():
            pp = p.GetPosition()
            ls = p.GetLayerSet()
            pads.append(dict(num=p.GetNumber(), net=p.GetNetname(), x=ToMM(pp.x), y=ToMM(pp.y), sx=ToMM(p.GetSize(pcbnew.F_Cu).x) if hasattr(p, "GetSize") else None,
                             sy=ToMM(p.GetSize(pcbnew.F_Cu).y), drill=ToMM(p.GetDrillSize().x), front=ls.Contains(pcbnew.F_Cu), back=ls.Contains(pcbnew.B_Cu)))
        cy = None
        for lay in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            for g in f.GraphicalItems():
                if g.GetLayer() == lay:
                    bb = g.GetBoundingBox()
                    box = [ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom())]
                    cy = box if cy is None else [min(cy[0], box[0]), min(cy[1], box[1]), max(cy[2], box[2]), max(cy[3], box[3])]
        fps.append(dict(ref=f.GetReference(), value=f.GetValue(), fpid=f.GetFPIDAsString(), x=ToMM(pos.x), y=ToMM(pos.y),
                        rot=f.GetOrientationDegrees(), side=side, models=models, pads=pads, courtyard=cy))
    res = dict(board=path, thickness=t, outline_ok=bool(ok), outlines=outl, footprints=sorted(fps, key=lambda d: d["ref"]),
               kicad=pcbnew.GetBuildVersion())
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("board_read: %s thickness %.3f mm, %d outline(s), %d footprints -> %s" % (path, t, len(outl), len(fps), out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
