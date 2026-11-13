# lists silkscreen and fab texts of a board with position, layer, mirrored flag, and the board's Edge.Cuts x extents
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
for d in b.GetDrawings():
    ln=b.GetLayerName(d.GetLayer())
    if d.GetClass()=='PCB_TEXT':
        p=d.GetPosition(); print('TEXT',ln,repr(d.GetText()),round(pcbnew.ToMM(p.x),3),round(pcbnew.ToMM(p.y),3),'mirrored',d.IsMirrored(),'h',round(pcbnew.ToMM(d.GetTextHeight()),2))
for fp in b.GetFootprints():
    for it in list(fp.GraphicalItems())+[fp.Reference(),fp.Value()]:
        ln=b.GetLayerName(it.GetLayer())
        if 'Silk' in ln and it.GetClass() in ('PCB_TEXT','PCB_FIELD') and getattr(it,'IsVisible',lambda:True)():
            p=it.GetPosition(); print('FPTEXT',fp.GetReference(),ln,repr(it.GetText()),round(pcbnew.ToMM(p.x),3),round(pcbnew.ToMM(p.y),3))
        elif 'Silk' in ln: print('FPSILK',fp.GetReference(),ln,it.GetClass())
