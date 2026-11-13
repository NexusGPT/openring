import sys; sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
for (x,y) in ((-12.0,0.0),(-11.65,-0.15)):
    cy,p=place('OpenRing:FPC_Hirose_FH35C-15S-0.3SHW',x,y,270)
    xs=[b[0] for n,px,py,b in p]+[b[2] for n,px,py,b in p]; ys=[b[1] for n,px,py,b in p]+[b[3] for n,px,py,b in p]
    mp=[(round(b[0],3),round(b[1],3),round(b[2],3),round(b[3],3)) for n,px,py,b in p if n=='MP']
    print((x,y),'pads X %.3f..%.3f Y %.3f..%.3f'%(min(xs),max(xs),min(ys),max(ys)),'MP',mp,'library courtyard',[round(v,3) for v in cy])
for ref,(x,y,r) in (('U5',(-10.8,-4.8,90)),('U6',(10.8,-4.8,270))):
    cy,p=place('OpenRing:LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0',x,y,r); print(ref,[(n,round(a,3),round(b,3)) for n,a,b,_ in p if n=='4'])
