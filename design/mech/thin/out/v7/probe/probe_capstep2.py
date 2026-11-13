import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin"))
import thin
from build123d import import_step, export_step, Solid, Compound
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
from OCP.ShapeFix import ShapeFix_Shape
D = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin/out/v7/probe/")
m = thin.build()
p = [q for q in m["parts"] if q.name == "joystick_cap"][0]
nub = p.subs["polymer"][0]
print("label", repr(getattr(nub, "label", None)), "color", getattr(nub, "color", None), flush=True)
def tryw(nm, sh):
    try:
        export_step(sh, D + nm + ".step"); r = import_step(D + nm + ".step")
        print(nm, "OK solids", len(r.solids()), [round(x.volume, 4) for x in r.solids()], flush=True)
    except Exception as e:
        print(nm, "FAIL", e, flush=True)
tryw("m_solid0", nub.solids()[0])
cp = Solid(BRepBuilderAPI_Copy(nub.wrapped).Shape())
tryw("m_copy", cp)
sf = ShapeFix_Shape(nub.wrapped); sf.Perform()
tryw("m_fix", Solid(sf.Shape()))
tryw("m_compound_fix", Compound(children=[Solid(sf.Shape()), p.subs["polymer"][1]]))
