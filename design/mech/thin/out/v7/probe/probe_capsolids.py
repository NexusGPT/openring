import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin"))
import thin
from build123d import import_step
m = thin.build()
p = [q for q in m["parts"] if q.name == "joystick_cap"][0]
for i, s in enumerate(p.subs["polymer"]):
    print(i, type(s).__name__, "solids", len(s.solids()), "volume", round(s.volume, 4), "bbox", s.bounding_box().size)
c = p.solids()["polymer"]
print("compound", type(c).__name__, len(c.solids()), round(c.volume, 4))
st = import_step((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mfg/parts/joystick-cap/joystick-cap.step"))
print("STEP", len(st.solids()), [round(x.volume, 4) for x in st.solids()], st.bounding_box().size)
from build123d import export_step, Compound
nub, fl = p.subs["polymer"][0], p.subs["polymer"][1]
print("nub valid", nub.is_valid, "flange valid", fl.is_valid)
for nm, sh in (("nub", nub), ("fused", nub + fl)):
    f = f"{__import__('pathlib').Path(__file__).resolve().parents[6].as_posix()}/design/mech/thin/out/v7/probe/{nm}.step"
    export_step(sh, f)
    r = import_step(f)
    print(nm, "type", type(sh).__name__, "solids", len(sh.solids()), "valid", sh.is_valid, "-> STEP solids", len(r.solids()), [round(x.volume, 4) for x in r.solids()], r.bounding_box().size)
