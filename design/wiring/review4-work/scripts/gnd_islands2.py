# Union-find over the flex copper (tracks, vias, pads; zones listed) to see which foot lands share a copper island. Run with run_kipy.sh.
import pcbnew, math
from pcbnew import ToMM
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/band")
def run(path, ref, a, b):
    bd=pcbnew.LoadBoard(path)
    items=[]  # (kind, layerset, geometry)
    for fp in bd.GetFootprints():
        for p in fp.Pads():
            bb=p.GetBoundingBox()
            items.append(("pad:%s:%s"%(fp.GetReference(),p.GetNumber()), set(bd.GetLayerName(l) for l in p.GetLayerSet().Seq() if "Cu" in bd.GetLayerName(l)), ("box",ToMM(bb.GetLeft()),ToMM(bb.GetTop()),ToMM(bb.GetRight()),ToMM(bb.GetBottom())), p.GetNetname()))
    for t in bd.GetTracks():
        if t.GetClass()=="PCB_VIA":
            pos=t.GetPosition(); r=ToMM(t.GetWidth(pcbnew.F_Cu))/2 if hasattr(t,"GetWidth") else 0.15
            items.append(("via", {"F.Cu","B.Cu"}, ("box",ToMM(pos.x)-r,ToMM(pos.y)-r,ToMM(pos.x)+r,ToMM(pos.y)+r), t.GetNetname()))
        else:
            s,e=t.GetStart(),t.GetEnd(); w=ToMM(t.GetWidth())/2
            items.append(("trk", {bd.GetLayerName(t.GetLayer())}, ("seg",ToMM(s.x),ToMM(s.y),ToMM(e.x),ToMM(e.y),w), t.GetNetname()))
    nz=len(list(bd.Zones()))
    par=list(range(len(items)))
    def f(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    def pts(g):
        if g[0]=="box": return [((g[1]+g[3])/2,(g[2]+g[4])/2)]
        return [(g[1],g[2]),(g[3],g[4])]
    def touch(g,pt,tol):
        x,y=pt
        if g[0]=="box": return g[1]-tol<=x<=g[3]+tol and g[2]-tol<=y<=g[4]+tol
        x1,y1,x2,y2,w=g[1:]; dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy
        t=0 if L==0 else max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L))
        return math.hypot(x-(x1+t*dx),y-(y1+t*dy))<=w+tol
    for i,(ki,li,gi,ni) in enumerate(items):
        for j,(kj,lj,gj,nj) in enumerate(items):
            if j<=i or not (li&lj) or ni!=nj: continue
            if any(touch(gj,p,0.001) for p in pts(gi)) or any(touch(gi,p,0.001) for p in pts(gj)):
                par[f(i)]=f(j)
    idx={k:i for i,(k,_,_,_) in enumerate(items)}
    ia,ib=idx["pad:%s:%s"%(ref,a)],idx["pad:%s:%s"%(ref,b)]
    isl=[k for i,(k,_,_,_) in enumerate(items) if k.startswith("pad") and f(i)==f(ia)]
    return f(ia)==f(ib), isl, nz
for fl,ref,a,b in ((1,"J_BAND_A","6","8"),(2,"J_BAND_B","2","7")):
    for s in range(7,14):
        j,isl,nz=run("%s/flex%d-us%d.kicad_pcb"%(R,fl,s),ref,a,b)
        print("flex%d-us%d zones=%d %s:%s and %s:%s joined by ribbon copper: %s ; pads on the island of %s:%s: %s"%(fl,s,nz,ref,a,ref,b,j,ref,a,isl))
