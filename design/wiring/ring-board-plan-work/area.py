import pcbnew
b=pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/ring.kicad_pcb"))
tot=0; rows=[]
for fp in b.GetFootprints():
    bb=fp.GetCourtyard(pcbnew.F_CrtYd)
    a=bb.Area()/1e12 if bb.OutlineCount() else 0
    tot+=a; rows.append((fp.GetReference(),round(a,3)))
print('total courtyard mm2 %.1f over %d footprints'%(tot,len(rows)))
print(sorted(rows,key=lambda r:-r[1])[:25])
print([r for r in rows if r[0] in ('C1','C4','C21','R2','Q1','D1','Q2','LED1','R41','TP20','TP21','C13','ANT1','L4','U9','R66')])
