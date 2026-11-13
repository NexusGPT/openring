# Checks the U2 escape plan of ring-board-plan.md b.2 (rotation 90): lands 0.22, microvia lands 0.20, tracks 0.10
# (power tracks drawn at 0.15 inside the field), straight to 0.5 mm past the body. Pass line: least gap >= 0.075 mm between different nets.
import math, csv
N={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))):
    if r['reference']=='U2': N[r['pin_number']]=r['net'] or 'NC_'+r['pin_number']
def pos(b):
    x=(int(b[1])-4)*0.419; y=('ABCDE'.index(b[0])-2)*0.44
    return (8.5-y, x)
balls=[r+str(c) for r in 'ABCDE' for c in range(1,8)]
HX,HY=1.189,1.539; M=0.5; C=(8.5,0.0)
def edge(p,d):
    x,y=p; return {'N':(x,C[1]-HY-M),'S':(x,C[1]+HY+M),'W':(C[0]-HX-M,y),'E':(C[0]+HX+M,y)}[d]
l1dir={'A4':'E','A5':'E','A6':'E','A7':'E','B1':'N','C1':'N','D1':'N','E1':'N','E2':'W','E3':'W','E4':'W','E5':'W','E7':'W','B7':'S','C7':'S','D7':'S'}
l2dir={'B4':'E','B5':'E','B6':'E','C3':'N','C6':'S','D3':'W','D4':'W','D6':'W'}
wide={'B1':0.15,'C1':0.15,'D1':0.15,'A7':0.15,'E7':0.15,'B7':0.15,'C7':0.15,'D7':0.15}
L1=[(N[b],'c',pos(b),0.225) for b in balls]+[(N[b],'s',(pos(b),edge(pos(b),d)),wide.get(b,0.1)) for b,d in l1dir.items()]
L1+=[(N['B1'],'s',(pos('B1'),pos('B2')),0.15),(N['C1'],'s',(pos('C1'),pos('C2')),0.15),(N['D1'],'s',(pos('D1'),pos('D2')),0.15)]
L2=[(N[b],'c',pos(b),0.2) for b in l2dir]+[(N[b],'s',(pos(b),edge(pos(b),d)),0.1) for b,d in l2dir.items()]
def ps(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];L=dx*dx+dy*dy;t=0 if L==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L));return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
def ss(a,b,c,d): return min(ps(a,c,d),ps(b,c,d),ps(c,a,b),ps(d,a,b))
res=[]
for name,its in (('L1',L1),('L2',L2)):
    m=(9,None)
    for i in range(len(its)):
        for j in range(i+1,len(its)):
            n1,k1,g1,w1=its[i];n2,k2,g2,w2=its[j]
            if n1==n2: continue
            d=math.dist(g1,g2) if k1==k2=='c' else ps(g1,*g2) if k1=='c' else ps(g2,*g1) if k2=='c' else ss(*g1,*g2)
            g=d-w1/2-w2/2
            if g<m[0]: m=(round(g,3),(n1,n2))
    res.append((name,m)); print(name,len(its),'least gap',m)
print('RESULT','PASS' if all(m[0]>=0.075 for _,m in res) else 'FAIL',[(n,m[0]) for n,m in res])
