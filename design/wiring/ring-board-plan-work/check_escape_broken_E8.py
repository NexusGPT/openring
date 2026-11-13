# Checks the U1 escape plan of ring-board-plan.md a.3: builds every land, via land and straight escape track
# per layer and reports the least copper-to-copper gap between different balls. Pass line: >= 0.075 mm (net class Default).
import csv, math
B={r['ball']:(4+float(r['x_mm']),float(r['y_mm'])) for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/w1-evidence/u1-measured-pads.csv")))}
L,R,T,Bt=4-1.51,4+1.51,-1.215,1.215; M=0.5
ring1=set('A4 A5 A6 A7 A8 A9 A10 H1 H2 H4 H5 H6 H7 H8 H9 H10 B2 B10 C1 D10 E1 E10 F1 F10 G1 G10'.split())
ring2=set('B4 B5 B6 B7 B8 B9 G2 G4 G5 G6 G7 G8 G9 E2 F2 D9 E9 F9'.split())
ring3=set('D5 D6 D7 D8 F4 F5 F6 F7 F8'.split())
def out(b,d):
    x,y=B[b]
    return {'N':(x,T-M),'S':(x,Bt+M),'W':(L-M,y),'E':(R+M,y)}[d]
def dir1(b):
    r,c=b[0],int(b[1:])
    if b in('B2','C1') or c==1: return 'W'
    if r=='A': return 'N'
    if r=='H': return 'S'
    return 'E'
items={l:[] for l in('L1','L2','L3')}  # (net, kind, geom, width)
for b,(x,y) in B.items(): items['L1'].append((b,'c',(x,y),0.2))
for b in ring1: items['L1'].append((b,'s',(B[b],out(b,dir1(b))),0.1))
for b in ring2:
    items['L2'].append((b,'c',B[b],0.2))
    d='N' if b[0]=='B' else 'S' if b[0]=='G' else 'W' if b in('E2','F2') else 'E'
    items['L2'].append((b,'s',(B[b],out(b,d)),0.1))
items['L2'].append(('D3','c',B['D3'],0.2)); items['L2'].append(('D3','s',(B['D3'],(L-M,B['D3'][1])),0.1))
for b in list(ring3)+['A1','A2','E4','E7','E8']:
    items['L2'].append((b,'c',B[b],0.2)); items['L3'].append((b,'c',B[b],0.2))
for b in ring3: items['L3'].append((b,'s',(B[b],out(b,'N' if b[0]=='D' else 'S')),0.1))
for b in ('A1','A2'): items['L3'].append((b,'s',(B[b],out(b,'S')),0.1))
items['L3'].append(('E4','s',(B['E4'],(B['E4'][0],T-M)),0.1))
items['L3'].append(('E7','s',(B['E7'],(R+M,B['E7'][1])),0.1))
def pseg(p,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((p[0]-ax)*dx+(p[1]-ay)*dy)/L2)); return math.dist(p,(ax+t*dx,ay+t*dy))
def segseg(a,b,c,d):
    return min(pseg(a,c,d),pseg(b,c,d),pseg(c,a,b),pseg(d,a,b)) if not inter(a,b,c,d) else 0
def inter(a,b,c,d):
    def o(p,q,r): return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    return o(a,b,c)*o(a,b,d)<0 and o(c,d,a)*o(c,d,b)<0
worst=[]
for l,its in items.items():
    m=(9,None)
    for i in range(len(its)):
        for j in range(i+1,len(its)):
            n1,k1,g1,w1=its[i]; n2,k2,g2,w2=its[j]
            if n1==n2: continue
            if k1=='c' and k2=='c': dd=math.dist(g1,g2)
            elif k1=='c': dd=pseg(g1,*g2)
            elif k2=='c': dd=pseg(g2,*g1)
            else: dd=segseg(*g1,*g2)
            gap=dd-w1/2-w2/2
            if gap<m[0]: m=(round(gap,3),(n1,n2))
    worst.append((l,m)); print(l,'items',len(its),'least gap',m)
print('RESULT', 'PASS' if all(m[0]>=0.075 for _,m in worst) else 'FAIL', 'least gap per layer', [(l,m[0]) for l,m in worst])
