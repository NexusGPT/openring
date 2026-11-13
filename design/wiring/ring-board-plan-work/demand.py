import pcbnew, math, sys
b=pcbnew.LoadBoard((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/ring.kicad_pcb"))
nets={}
for fp in b.GetFootprints():
    for p in fp.Pads():
        n=p.GetNetname()
        if not n: continue
        pos=p.GetPosition(); nets.setdefault(n,[]).append((pos.x/1e6,pos.y/1e6,fp.GetReference()))
def mst(pts):
    if len(pts)<2: return 0
    inT=[pts[0]]; rest=pts[1:]; tot=0
    while rest:
        best=min(((abs(a[0]-c[0])+abs(a[1]-c[1]),i) for i,c in enumerate(rest) for a in inT))
        tot+=best[0]; inT.append(rest.pop(best[1]))
    return tot
tot=0; gnd=0; rows=[]
for n,p in nets.items():
    l=mst(p); rows.append((l,n,len(p)))
    if n=='GND': gnd=l
    else: tot+=l
rows.sort(reverse=True)
print('nets',len(nets),'MST manhattan total excl GND %.0f mm, GND %.0f mm'%(tot,gnd))
for r in rows[:12]: print('%.1f %s %d'%r)
