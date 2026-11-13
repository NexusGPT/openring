import sys; sys.argv=['x','lib']
exec(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work/dots.py")).read())
ds=dots(0)
b=[(round(x,3),round(y,3)) for x,y,w,c in ds if w==0.2 and c=='red']
xs=sorted(set(round(x,2) for x,y in b)); ys=sorted(set(round(y,2) for x,y in b))
print('x',xs); print('y',ys)
