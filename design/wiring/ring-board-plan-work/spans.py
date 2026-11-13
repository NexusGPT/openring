import sys
exec(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work/escape.py")).read().replace("if __name__=='__main__':","if False:"))
from collections import Counter, defaultdict
pos=defaultdict(set)
def key(p): return (round(p[0]/0.01)*0.01, round(p[1]/0.01)*0.01)
allp=[]
for k in ['L1','L2','L3','L4']:
    for p,w in L[k]['holes']:
        if w<0.15:
            m=None
            for q in allp:
                if abs(q[0]-p[0])<0.01 and abs(q[1]-p[1])<0.01: m=q;break
            if m is None: allp.append(p); m=p
            pos[m].add(k)
c=Counter(''.join(sorted(v)) for v in pos.values())
print(c)
# pads sizes on each layer at those holes
for k in ['L1','L2','L3','L4']:
    print(k, Counter(w for p,w in L[k]['dots']).most_common(8))
# near chip only
near=Counter(''.join(sorted(v)) for p,v in pos.items() if abs(p[0]-CX)<1.6 and abs(p[1]-CY)<1.3)
print('in body',near)
