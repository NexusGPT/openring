import sys, csv, math
exec(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work/escape.py")).read().replace("if __name__=='__main__':","if False:"))
from collections import defaultdict
ORDER=['L1','L2','L3','L4','L5','L6','L7','L8']
# via table: position -> set of layers with hole (0.1 = microvia, 0.2 = through)
vias=[]
for k in ORDER:
    for p,w in L[k]['holes']:
        typ='u' if w<0.15 else 't'
        for v in vias:
            if v['t']==typ and abs(v['p'][0]-p[0])<0.01 and abs(v['p'][1]-p[1])<0.01:
                v['ls'].add(k); break
        else: vias.append(dict(p=p,t=typ,ls={k}))
def via_at(p,tol=0.02):
    return [v for v in vias if math.dist(v['p'],p)<tol]
balls=list(csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/w1-evidence/u1-measured-pads.csv"))))
nets={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))):
    if r['reference']=='U1': nets[r['pin_number']]=(r['net'],r['pin_name'])
HX,HY=1.51+0.12,1.215+0.12
def outside(p): return abs(p[0]-CX)>HX or abs(p[1]-CY)>HY
rows=[]
for b in balls:
    B=(CX+float(b['x_mm']),CY+float(b['y_mm']))
    seen=set(); stack=[('L1',B)]; exits=set(); used=[]; planes=set(); widths=set()
    while stack:
        lay,p=stack.pop()
        k=(lay,round(p[0],2),round(p[1],2))
        if k in seen: continue
        seen.add(k)
        if outside(p): exits.add(lay); continue
        for f in L[lay]['fills']:
            try:
                if f.contains_point(p): planes.add(lay)
            except Exception: pass
        for v in via_at(p):
            span=sorted(v['ls'],key=ORDER.index)
            tag=('uvia' if v['t']=='u' else 'thru')+':'+span[0]+'-'+span[-1]+('@pad' if math.dist(v['p'],B)<0.02 else f"@({v['p'][0]-CX:+.2f},{v['p'][1]-CY:+.2f})")
            if tag not in used: used.append(tag)
            for l2 in v['ls']: stack.append((l2,p))
        for A,Bb,w in L[lay]['segs']:
            for P,Q in ((A,Bb),(Bb,A)):
                if math.dist(P,p)<0.02:
                    widths.add((lay,w)); stack.append((lay,Q))
    net,name=nets.get(b['ball'],('?','?'))
    rows.append(dict(ball=b['ball'],name=name,net=net,x=b['x_mm'],y=b['y_mm'],exit=' '.join(sorted(exits,key=ORDER.index)),vias=' '.join(used),planes=' '.join(sorted(planes,key=ORDER.index)),tracks=' '.join(f'{l}:{w}' for l,w in sorted(widths))))
w=csv.DictWriter(open('nordic-escape.csv','w'),fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r['ball'],r['name'],r['net'],'| exit',r['exit'],'| vias',r['vias'],'| planes',r['planes'],'|',r['tracks'])

# ---- clearance measurement: track of one ball vs pad/via/track of another ball, per layer
def seg_pt(p,a,b):
    ax,ay=a;bx,by=b;px,py=p
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2))
    return math.dist(p,(ax+t*dx,ay+t*dy))
own={}  # ball -> {layer: [segs]}, pads
for b in balls:
    B=(CX+float(b['x_mm']),CY+float(b['y_mm']))
    seen=set(); stack=[('L1',B)]; segs=defaultdict(list); pts=defaultdict(list)
    while stack:
        lay,p=stack.pop()
        k=(lay,round(p[0],2),round(p[1],2))
        if k in seen: continue
        seen.add(k); pts[lay].append(p)
        if outside(p): continue
        for v in via_at(p):
            for l2 in v['ls']: stack.append((l2,p))
        for A,Bb,w in L[lay]['segs']:
            for P,Q in ((A,Bb),(Bb,A)):
                if math.dist(P,p)<0.02:
                    segs[lay].append((A,Bb,w)); stack.append((lay,Q))
    own[b['ball']]=(segs,pts)
best=[]
names=list(own)
for lay in ['L1','L2','L3','L4']:
    m=(9,None)
    for x in names:
        for A,Bb,w in own[x][0][lay]:
            for y in names:
                if y==x: continue
                # pads/vias of y on this layer: points visited (ball pad 0.2 or via land 0.2)
                for p in own[y][1][lay]:
                    if abs(p[0]-CX)>1.7 or abs(p[1]-CY)>1.4: continue
                    has_land = (lay=='L1' and any(math.dist(p,(CX+float(bb['x_mm']),CY+float(bb['y_mm'])))<0.02 for bb in balls if bb['ball']==y)) or via_at(p)
                    if not has_land: continue
                    g=seg_pt(p,A,Bb)-w/2-0.1
                    if g<m[0]: m=(g,(x,y,lay,w,round(p[0]-CX,3),round(p[1]-CY,3)))
    best.append((lay,m))
for b in best: print('min track-to-land gap',b)
