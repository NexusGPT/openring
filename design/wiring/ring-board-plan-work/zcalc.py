import math
def ms(w,h,t,er):
    # Hammerstad-Jensen microstrip with Wheeler thickness correction
    if t>0:
        dw=t/math.pi*math.log(1+4*math.e/(t/h*(1/math.tanh(math.sqrt(6.517*w/h)))**2))
        dwr=0.5*(1+1/math.cosh(math.sqrt(er-1)))*dw
    else: dw=dwr=0
    def z(u,er):
        a=1+1/49*math.log((u**4+(u/52)**2)/(u**4+0.432))+1/18.7*math.log(1+(u/18.1)**3)
        b=0.564*((er-0.9)/(er+3))**0.053
        ee=(er+1)/2+(er-1)/2*(1+10/u)**(-a*b)
        f=6+(2*math.pi-6)*math.exp(-(30.666/u)**0.7528)
        z0=60*math.log(f/u+math.sqrt(1+4/u**2))
        return z0,ee
    z1,_=z((w+dw)/h,1); zr,ee=z((w+dwr)/h,er)
    eeff=ee*(z1/zr)**2 if False else ee
    return zr/math.sqrt(ee),ee
def solve(target,h,t,er,lo=0.01,hi=2):
    for _ in range(60):
        m=(lo+hi)/2
        if ms(m,h,t,er)[0]>target: lo=m
        else: hi=m
    return m
er=4.1
for h,lab in [(0.065,'L1 over L2'),(0.145,'L1 over L3 (L2 cleared)')]:
    w=solve(50,h,0.018,er); print(lab,'h',h,'50 ohm w=%.3f mm eeff=%.2f'%(w,ms(w,h,0.018,er)[1]))
# edge-coupled diff approx (IPC-2141 style): Zdiff = 2*Z0*(1-0.48*exp(-0.96*s/h))
for h in (0.065,0.145):
  for w in (0.065,0.075,0.08,0.09,0.1,0.12,0.15):
    z0=ms(w,h,0.018,er)[0]
    for s in (0.065,0.075,0.1,0.15):
        zd=2*z0*(1-0.48*math.exp(-0.96*s/h))
        if 85<zd<95: print('diff h',h,'w',w,'s',s,'Z0 %.1f Zdiff %.1f'%(z0,zd))
# IPC-2221 widths: I=k*dT^0.44*A^0.725, A in mil^2
def width(I,dT,oz_um,k):
    A=(I/(k*dT**0.44))**(1/0.725); t_mil=oz_um/25.4; return A/t_mil*0.0254
for I in (0.1,0.2,0.3,0.5,1.5):
    print('I %.1f A: external 18um w=%.3f mm, internal 15um w=%.3f mm (dT 10 C)'%(I,width(I,10,18,0.048),width(I,10,15,0.024)))
