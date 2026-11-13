# review 3: dump every pad (ref, pad number, net, layer set, x, y, size) and every silkscreen / fab text of one board
# usage: run_kipy.sh dump_board.py <board.kicad_pcb> <out_prefix>
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
out = sys.argv[2]
def mm(v): return round(pcbnew.ToMM(v), 4)
with open(out + "-pads.csv", "w") as f:
    f.write("ref,pad,net,face,x,y,sx,sy,layers\n")
    for fp in b.GetFootprints():
        for p in fp.Pads():
            ls = p.GetLayerSet()
            face = "F.Cu" if ls.Contains(pcbnew.F_Cu) and not ls.Contains(pcbnew.B_Cu) else ("B.Cu" if ls.Contains(pcbnew.B_Cu) and not ls.Contains(pcbnew.F_Cu) else "both")
            pos = p.GetPosition(); sz = p.GetSize()
            names = "|".join(b.GetLayerName(l) for l in ls.Seq())
            f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (fp.GetReference(), p.GetNumber(), p.GetNetname(), face, mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y), names))
with open(out + "-silk.csv", "w") as f:
    f.write("kind,layer,text,x,y,owner\n")
    silk = ("F.SilkS", "B.SilkS", "F.Fab", "B.Fab", "F.Silkscreen", "B.Silkscreen")
    for d in b.GetDrawings():
        ln = b.GetLayerName(d.GetLayer())
        if ln in silk:
            if d.GetClass() in ("PCB_TEXT", "PTEXT", "PCB_TEXTBOX"):
                p = d.GetPosition(); f.write("text,%s,%s,%s,%s,board\n" % (ln, d.GetText().replace(",", ";").replace("\n", " "), mm(p.x), mm(p.y)))
            else:
                f.write("shape,%s,%s,,,board\n" % (ln, d.GetClass()))
    for fp in b.GetFootprints():
        for t in [fp.Reference(), fp.Value()] + [g for g in fp.GraphicalItems()]:
            ln = b.GetLayerName(t.GetLayer())
            if ln not in silk: continue
            if hasattr(t, "GetText"):
                if hasattr(t, "IsVisible") and not t.IsVisible(): continue
                p = t.GetPosition(); f.write("text,%s,%s,%s,%s,%s\n" % (ln, t.GetText().replace(",", ";"), mm(p.x), mm(p.y), fp.GetReference()))
            else:
                f.write("shape,%s,%s,,,%s\n" % (ln, t.GetClass(), fp.GetReference()))
print("done", sys.argv[1])
