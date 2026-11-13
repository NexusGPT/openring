import sys, math
sys.argv=[sys.argv[0]]
import importlib.util
spec=importlib.util.spec_from_file_location("bw",(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/build_wiring.py"))
bw=importlib.util.module_from_spec(spec); spec.loader.exec_module(bw)
rel="design/ecad/band/flex1-us9.kicad_pcb"
bd=bw.board(rel)
for key in [("SW2","2"),("SW2","4"),("M1","2"),("J_BAND_A","6"),("J_BAND_A","8")]:
    d=bd["pads"][key][0]; print(key, d["x"], d["y"], d["layers"], d["obj"].GetSize().x/1e6, d["obj"].GetSize().y/1e6)
for t in bd["tracks"]:
    if t["net"]=="GND": print("T", t["layer"], t["a"], t["b"], t["w"])
for v in bd["vias"]:
    if v["net"]=="GND": print("V", v["x"], v["y"], v["r"])
