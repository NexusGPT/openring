import sys
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb"))
sys.argv=[sys.argv[0]]
import place_pcb1 as P
tot=0; rows=[]
for r,it in P.items.items():
    if it.side!='F' or r in ('U1','J1','LED1'): continue
    c=P.world_court(it)
    a=(c[2]-c[0])*(c[3]-c[1]); tot+=a; rows.append((round(a,2),r,round(c[2]-c[0],2),round(c[3]-c[1],2)))
rows.sort(reverse=True)
print('movable F-side courtyard area',round(tot,1),'count',len(rows))
print(rows[:14])
board=23*35.4+ (1.85*10.2)
u1=15.6*20.7; ant=(16.5*7.15); j1=(3.9+3.45)*8.94
led=2.8*2.2
print('board',round(board,1),'U1 court',round(u1,1),'antenna strip (outside U1 part)',round(16.5*2.1,1),'J1 region',round(j1,1))
free=board-u1-16.5*2.1-j1-led-(23-16.5)*7.15*0
print('free approx',round(free,1),'utilisation',round(tot/free,2))
