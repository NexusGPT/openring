# dumps every pad of a board: ref, fp layer, pad number, net, pad layers, pad center x y (mm), fp x y rot
import pcbnew,sys,csv
b=pcbnew.LoadBoard(sys.argv[1])
w=csv.writer(open(sys.argv[2],'w'))
w.writerow(['ref','fp_layer','fp_x','fp_y','fp_rot','pad','net','pad_layers','x','y','sx','sy','attr'])
n=0
for fp in b.GetFootprints():
    for p in fp.Pads():
        ls=[b.GetLayerName(l) for l in p.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)]
        pos=p.GetPosition(); fpos=fp.GetPosition(); sz=p.GetSize()
        w.writerow([fp.GetReference(),b.GetLayerName(fp.GetLayer()),pcbnew.ToMM(fpos.x),pcbnew.ToMM(fpos.y),fp.GetOrientationDegrees(),p.GetNumber(),p.GetNetname(),'|'.join(ls),round(pcbnew.ToMM(pos.x),4),round(pcbnew.ToMM(pos.y),4),round(pcbnew.ToMM(sz.x),4),round(pcbnew.ToMM(sz.y),4),p.GetAttribute()])
        n+=1
# silk/fab text on board
t=0
for d in b.GetDrawings():
    if d.GetClass() in ('PCB_TEXT','PCB_SHAPE') and b.GetLayerName(d.GetLayer()) in ('F.Silkscreen','B.Silkscreen'): t+=1
fs=0
for fp in b.GetFootprints():
    for it in fp.GraphicalItems():
        if b.GetLayerName(it.GetLayer()) in ('F.Silkscreen','B.Silkscreen'): fs+=1
    for f in (fp.Reference(),fp.Value()):
        if f.IsVisible() and b.GetLayerName(f.GetLayer()) in ('F.Silkscreen','B.Silkscreen'): fs+=1
print(sys.argv[1].split('/')[-1],'footprints',len(b.GetFootprints()),'pads',n,'board silk items',t,'footprint silk items',fs)
