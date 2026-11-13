import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
print('version', pcbnew.GetBuildVersion())
tr = list(b.GetTracks())
print('tracks', len(tr), 'segments', sum(1 for t in tr if t.GetClass() == 'PCB_TRACK'), 'vias', sum(1 for t in tr if t.GetClass() == 'PCB_VIA'), 'arcs', sum(1 for t in tr if t.GetClass() == 'PCB_ARC'))
con = b.GetConnectivity()
print([m for m in dir(con) if 'nconn' in m.lower() or 'Rats' in m or 'Count' in m or 'Net' in m][:30])
sc = [t for t in tr if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'LCD_SCK']
print('LCD_SCK segments', len(sc), [(round(pcbnew.ToMM(t.GetLength()), 3), b.GetLayerName(t.GetLayer())) for t in sc])
