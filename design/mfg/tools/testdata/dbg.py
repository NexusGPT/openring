import warnings; warnings.filterwarnings("ignore")
from build123d import *
s=import_step((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/tools/testdata/parts_real/body/body.step"))
print(type(s), len(s.solids()), len(s.faces()), s.bounding_box().size)
bb=s.bounding_box(); c=bb.center()
for nm,o,u in [("front",(c.X,c.Y-1000,c.Z),(0,0,1)),("top",(c.X,c.Y,c.Z+1000),(0,1,0))]:
    v,h=s.project_to_viewport(Vector(*o),Vector(*u)); print(nm,len(v),len(h))
import math
for eps in (1e-3, 1e-2, 0.1):
    o=(c.X+eps,c.Y+eps,c.Z+1000); v,h=s.project_to_viewport(Vector(*o),Vector(0,1,0)); print("eps",eps,len(v),len(h))
o=(c.X,c.Y,c.Z+1000); v,h=s.project_to_viewport(Vector(*o),Vector(0,1,0),look_at=Vector(c.X,c.Y,c.Z)); print("lookat",len(v),len(h))
tot=0
for i,so in enumerate(s.solids()):
    v,h=so.project_to_viewport(Vector(*o),Vector(0,1,0)); tot+=len(v); print(i,len(v),len(h))
