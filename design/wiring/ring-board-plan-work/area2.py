import sys,csv
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
from rules import *
parts={r['reference']:r for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/parts.csv")))}
FP={k:v['footprint'] for k,v in parts.items()}; FP.update(FP_OVERRIDE)
refs=[r for r in parts if r not in OFF_BOARD and r not in REMOVED]+ADDED
tot=0; by={}
for r in refs:
    x,y,rot=(FIXED[r][:3] if r in FIXED else (0,0,0))
    cy,_=place(FP[r],x,y,rot); cy=override_cy(r,cy,x,y,rot)
    a=(cy[2]-cy[0])*(cy[3]-cy[1]); tot+=a; by[FP[r]]=by.get(FP[r],0)+a
board=27.2*12.6-4*(0.8**2-math.pi*0.8**2/4)
ko=(4.15*3.40-0)  # antenna keep-out on the board
tails=2*2.5*2.2
print('parts',len(refs),'courtyard bbox sum %.1f'%tot,'board %.1f'%board)
print('by footprint',{k.split(':')[1]:round(v,2) for k,v in sorted(by.items(),key=lambda t:-t[1])})
ant=[v for k,v in by.items() if 'ANT' in k][0]; jb=sum(v for k,v in by.items() if 'J_BAND' in k); lt1=0.667
print('keep-out rest: antenna %.2f, tails %.2f'%(ko-ant-lt1, tails-jb))
tot2=tot+(ko-ant-lt1)+(tails-jb)
print('RESULT sum %.1f of %.1f = %.1f percent'%(tot2,board,100*tot2/board))
