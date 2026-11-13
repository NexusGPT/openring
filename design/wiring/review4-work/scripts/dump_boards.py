# Dump pads, paste graphics, silkscreen texts and tracks count of the 17 boards (read only). Run with run_kipy.sh.
import pcbnew, sys, os, json
from pcbnew import ToMM
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad")
W=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work/pads")
boards=[("ring",R+"/ring/pcb/ring.kicad_pcb")]
for f in (1,2):
    for s in range(7,14): boards.append(("flex%d-us%d"%(f,s),R+"/band/flex%d-us%d.kicad_pcb"%(f,s)))
boards+= [("case_main",R+"/case/pcb/case_main.kicad_pcb"),("case_pins",R+"/case/pcb/case_pins.kicad_pcb")]
for name,path in boards:
    b=pcbnew.LoadBoard(path)
    out=open(os.path.join(W,name+"-pads.csv"),"w")
    out.write("ref,pad,net,x,y,sx,sy,layers,fp_layer,attr,fpname,orient\n")
    for fp in b.GetFootprints():
        ref=fp.GetReference()
        for p in fp.Pads():
            pos=p.GetPosition(); sz=p.GetSize()
            lays="|".join(b.GetLayerName(l) for l in p.GetLayerSet().Seq())
            out.write("%s,%s,%s,%.4f,%.4f,%.4f,%.4f,%s,%s,%d,%s,%.1f\n"%(ref,p.GetNumber(),p.GetNetname(),ToMM(pos.x),ToMM(pos.y),ToMM(sz.x),ToMM(sz.y),lays,b.GetLayerName(fp.GetLayer()),p.GetAttribute(),fp.GetFPIDAsString(),p.GetOrientation().AsDegrees()))
    out.close()
    g=open(os.path.join(W,name+"-graphics.csv"),"w")
    g.write("ref,layer,shape,x0,y0,x1,y1,width,text\n")
    for fp in b.GetFootprints():
        for it in fp.GraphicalItems():
            lay=b.GetLayerName(it.GetLayer())
            if "Paste" in lay or "Silk" in lay:
                if it.GetClass() in ("PCB_TEXT","FP_TEXT"):
                    pos=it.GetPosition(); g.write("%s,%s,text,%.4f,%.4f,,,,%s\n"%(fp.GetReference(),lay,ToMM(pos.x),ToMM(pos.y),it.GetText().replace(","," ")))
                else:
                    bb=it.GetBoundingBox()
                    g.write("%s,%s,%s,%.4f,%.4f,%.4f,%.4f,%.4f,\n"%(fp.GetReference(),lay,it.GetClass(),ToMM(bb.GetLeft()),ToMM(bb.GetTop()),ToMM(bb.GetRight()),ToMM(bb.GetBottom()),ToMM(it.GetWidth())))
    for it in b.GetDrawings():
        lay=b.GetLayerName(it.GetLayer())
        if "Paste" in lay or "Silk" in lay or "Fab" in lay:
            if it.GetClass()=="PCB_TEXT":
                pos=it.GetPosition(); g.write("BOARD,%s,text,%.4f,%.4f,,,,%s\n"%(lay,ToMM(pos.x),ToMM(pos.y),it.GetText().replace(","," ").replace("\n"," / ")))
            else:
                bb=it.GetBoundingBox(); g.write("BOARD,%s,%s,%.4f,%.4f,%.4f,%.4f,,\n"%(lay,it.GetClass(),ToMM(bb.GetLeft()),ToMM(bb.GetTop()),ToMM(bb.GetRight()),ToMM(bb.GetBottom())))
    g.close()
    bb=b.GetBoardEdgesBoundingBox()
    print(name,"footprints",len(b.GetFootprints()),"tracks",len(b.GetTracks()),"edge_bbox %.3f %.3f %.3f %.3f"%(ToMM(bb.GetLeft()),ToMM(bb.GetTop()),ToMM(bb.GetRight()),ToMM(bb.GetBottom())))
