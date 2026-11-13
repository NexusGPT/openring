# Distance of each regulator capacitor to the pin it serves, against its limit (ring-board-plan.md round 3).
# Distance = centre of the capacitor's pad on the served net to the centre of the served pin; for the flying
# capacitor both pads. Usage: run_kipy.sh capdist.py <placement csv>
import sys, csv, math
sys.path.insert(0,(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
NET={}
for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv"))):
    NET[(r['reference'],r['pin_number'])]=r['net']
P={}
for r in csv.DictReader(open(sys.argv[1])):
    cy,pads=place(r['footprint'],float(r['x_mm']),float(r['y_mm']),int(r['rotation_deg']))
    P[r['reference']]={n:(x,y) for n,x,y,_ in pads}
# capacitor: list of (served ref, served pin), class, limit
CAPS={
 'C21':([('U4','A1')],'must','U4 PVIN input'),
 'C23':([('U4','A4'),('U4','B4')],'must','U4 charge-pump flying capacitor'),
 'C24':([('U4','D1')],'must','U4 buck-boost output VOUT'),
 'C27':([('U4','C4')],'must','U4 charge-pump output VON'),
 'C74':([('U2','C7')],'must','U2 PVDD (buck input)'),
 'C78':([('L71','2')],'should','buck 1 output (VDD_1V8) at L71'),
 'C79':([('L72','2')],'should','buck 2 output (VDD_3V0) at L72'),
 'L1': ([('U1','A5')],'must','U1 DC/DC inductor at DCC'),
 'C6': ([('L1','2')],'must','U1 DC/DC output DECD, at the inductor end of the loop (L1 pad 2)'),
 'C4': ([('U1','A4')],'must','U1 VDD 10 uF: input of U1 DC/DC'),
 'C7': ([('U1','A8')],'should','U1 DECA'),
 'C22':([('U4','A2')],'should','U4 AVIN bypass'),
 'C26':([('U4','D2')],'should','U4 AVDD LDO output'),
 'C25':([('U4','D3')],'should','U4 OVDD (ELVDD) LDO output'),
 'C28':([('U4','D4')],'should','U4 OVSS (ELVSS) LDO output'),
 'C29':([('U4','D4')],'should','U4 OVSS (ELVSS) LDO output, or at J1 pin 1 (lead ruling, round 4)'),
 'C75':([('U2','C1')],'should','U2 VSYS'),
 'C88':([('U2','C7')],'should','U2 VSYS / PVDD bulk'),
 'C71':([('U2','B1')],'should','U2 VBUS input'),
 'C72':([('U2','B1')],'should','U2 VBUS input, 100 nF'),
 'C85':([('U2','D1')],'should','U2 VBAT'),
 'C11':([('U1','H9')],'should','U1 VBUS'),
 'C80':([('L71','2')],'may','VDD_1V8 100 nF'),
 'C73':([('U2','C3')],'may','U2 VBUSOUT'),
}
LIM={'must':1.5,'should':3.0,'may':99}
fails=0
print('cap  class   limit  distance  serves')
for c,(pins,cls,what) in CAPS.items():
    worst=0
    if c=='C29':   # either end of the ELVSS rail; C28 is the one at U4
        alts=[[('U4','D4')],[('J1','1')]]
    elif c in ('C75','C88'):   # any VSYS ball of U2 (C1, C2, C7)
        alts=[[('U2','C1')],[('U2','C2')],[('U2','C7')]]
    else: alts=[pins]
    best_alt=99
    for pins in alts:
      worst=0
      for ref,pin in pins:
        net=NET.get((ref,pin))
        if ref.startswith('L') and ref!='L1': net=NET.get((ref,pin))
        if c not in P: worst=99; break
        cp=[(n,xy) for n,xy in P[c].items() if NET.get((c,n))==net]
        if not cp: worst=99; break
        d=min(math.dist(xy,P[ref][pin]) for n,xy in cp)
        worst=max(worst,d)
      best_alt=min(best_alt,worst)
    worst=best_alt
    bad=worst>LIM[cls]+1e-6
    if bad and cls in('must','should'): fails+=1
    print(f"{c:4} {cls:6} {LIM[cls] if cls!='may' else '-':>5}  {worst:6.2f}   {what} {'OVER' if bad and cls!='may' else ''}")
print('RESULT','PASS' if fails==0 else 'FAIL %d'%fails)
