import sys; sys.argv=['x','lib']
exec(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work/dots.py")).read())
def uniq(pts,tol=0.01):
    out=[]
    for p in pts:
        if not any(abs(p[0]-q[0])<tol and abs(p[1]-q[1])<tol for q in out): out.append(p)
    return out
ds=dots(0)
pads=uniq([(x,y) for x,y,w,c in ds if w==0.2 and c=='red' and 5.3<x<9.0 and 4.2<y<7.3])
holes=uniq([(x,y) for x,y,w,c in ds if w==0.0998 and c=='white' and 5.3<x<9.0 and 4.2<y<7.3])
print(len(pads),'pads',len(holes),'uvia holes')
for p in sorted(pads,key=lambda t:(round(t[1],2),t[0])): print(f'{p[0]:.4f} {p[1]:.4f}', 'UV' if any(abs(p[0]-h[0])<0.01 and abs(p[1]-h[1])<0.01 for h in holes) else '')
print('holes not on pads:',[ (round(h[0],3),round(h[1],3)) for h in holes if not any(abs(p[0]-h[0])<0.01 and abs(p[1]-h[1])<0.01 for p in pads)])
