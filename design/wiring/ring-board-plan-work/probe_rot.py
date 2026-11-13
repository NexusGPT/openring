import sys; sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
for rot in (0,90,180,270):
    cy,p=place('OpenRing:WLCSP-35_nPM1304-CAAA',8.5,0,rot); d={n:(round(x,3),round(y,3)) for n,x,y,_ in p}
    print('U2',rot,'B7',d['B7'],'A1',d['A1'],'cy',[round(v,3) for v in cy])
for rot in (0,90,180,270):
    cy,p=place('OpenRing:ANT_Johanson_2450AT18D0100001E_3.2x1.6',-11.5,5.25,rot); d={}
    for n,x,y,_ in p: d.setdefault(n,(round(x,2),round(y,2)))
    print('ANT',rot,d)
for rot in (0,90,180,270):
    cy,p=place('OpenRing:LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0',-10.8,-4.8,rot); d={n:(round(x,3),round(y,3)) for n,x,y,_ in p}
    print('U5',rot,'p4',d['4'],'p7',d['7'],'cy',[round(v,3) for v in cy])
for rot in (0,90,180,270):
    cy,p=place('OpenRing:FPC_Hirose_FH35C-15S-0.3SHW',-11.65,-0.15,rot); d={}
    for n,x,y,bb in p: d.setdefault(n,[]).append((round(x,3),round(y,3)))
    print('J1',rot,'p1',d['1'],'p15',d['15'],'MP',d['MP'],'cy',[round(v,3) for v in cy])
for ref,(x,y) in (('A',(-2.25,-4.325)),('B',(-2.25,4.325))):
  for rot in (0,180):
    cy,p=place('OpenRingBand:J_BAND_%s_BOARD'%ref,x,y,rot); print('J_BAND',ref,rot,[(n,round(px,3),round(py,3)) for n,px,py,_ in p])
