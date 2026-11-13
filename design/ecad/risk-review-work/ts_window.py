# TS window of the case charger with RT1 5.23k, RT2 30.1k and 103AT (case sch-notes section 1)
import math
RT1,RT2=5.23,30.1
# Semitec 103AT table (w16_semitec_P12-13-AT-Thermistor.txt lines 180-189), kohm
tab=[(-10,42.47),(0,27.28),(10,17.96),(20,12.09),(25,10.00),(30,8.313),(40,5.827),(50,4.160),(60,3.020)]
def temp(r):
    for (t1,r1),(t2,r2) in zip(tab,tab[1:]):
        if r2<=r<=r1:
            # log interpolation
            return t1+(t2-t1)*(math.log(r1)-math.log(r))/(math.log(r1)-math.log(r2))
    return float('nan')
def rth(p):
    x=p*RT1/(1-p)
    return 1/(1/x-1/RT2)
for name,(lo,typ,hi) in {'LTF (cold, rising)':(0.7275,0.7325,0.7375),'HTF (hot, start)':(0.4775,0.4825,0.4875),'TCO (cut-off, during charge)':(0.4425,0.4475,0.4525)}.items():
    out=[]
    for p in (lo,typ,hi):
        r=rth(p); out.append(f"{p*100:.2f}% -> RTH {r:.3f} k -> {temp(r):.1f} C")
    print(name,' | '.join(out))
