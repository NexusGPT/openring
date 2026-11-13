import sys; sys.argv=['x','lib']
exec(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work/dots.py")).read())
for pn in [1,3,4,5,6,10]:
    ds=dots(pn-1)
    sel=[(x,y,w,c) for x,y,w,c in ds if 5.3<x<9.0 and 4.2<y<7.3]
    print('== page',pn,len(sel))
    for x,y,w,c in sorted(sel,key=lambda t:(round(t[1],2),t[0])):
        print(f'{x:.4f} {y:.4f} {w} {c[:12] if c else c}')
