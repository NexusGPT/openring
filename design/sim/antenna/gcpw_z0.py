# Z0 of a grounded coplanar waveguide (strip w, gap g, substrate h, eps_r), conformal mapping,
# Ghione and Naldi 1984 closed form as given in Simons, "Coplanar Waveguide Circuits, Components and Systems" (2001), eq 3.x (zero thickness).
# Used only to pick the gap g of the evaluation-board feed line; the solver then sees the real 3D line.
import numpy as np
from scipy.special import ellipk
def K(k): return ellipk(k*k)
def z0(w,g,h,er):
    a=w/2; b=w/2+g
    k=a/b; kp=np.sqrt(1-k*k)
    k3=np.tanh(np.pi*a/(2*h))/np.tanh(np.pi*b/(2*h)); k3p=np.sqrt(1-k3*k3)
    ee=(1+er*(K(kp)/K(k))*(K(k3)/K(k3p)))/(1+(K(kp)/K(k))*(K(k3)/K(k3p)))
    z=60*np.pi/np.sqrt(ee)/(K(k)/K(kp)+K(k3)/K(k3p))
    return z,ee
if __name__=="__main__":
    import sys
    h=0.8; er=4.4; w=0.5
    for g in [0.1,0.15,0.2,0.25,0.3,0.4,0.5]:
        z,ee=z0(w,g,h,er); print(f"w={w} g={g} h={h} er={er}: Z0={z:.1f} ohm, eps_eff={ee:.2f}")
