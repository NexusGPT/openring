"""Broken copies for the marks check (KiCad's Python): writes into evidence/marks/broken/
  broken_nomarks_pins   all silkscreen texts removed from the pin board
  broken_swapped_pins   the P1 and P4 wing texts exchange their wings (the swap the marks exist to prevent)
  broken_nomarks_main   all silkscreen texts removed from the main board
  broken_small_pins     the front texts of the pin board 0.6 mm high (below the maker's 1.0 mm)"""
import os, shutil, pcbnew
from pcbnew import FromMM, VECTOR2I
P = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/case/pcb")
OUT = P + "/evidence/marks/broken"
os.makedirs(OUT, exist_ok=True)
def load(good, name):
    shutil.copy(good.replace(".kicad_pcb", ".kicad_pro"), os.path.join(OUT, name + ".kicad_pro"))
    return pcbnew.LoadBoard(good)
def texts(b):
    return [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT"]
def save(b, name):
    pcbnew.SaveBoard(os.path.join(OUT, name + ".kicad_pcb"), b); print("wrote", name)
KEEP = []   # the SWIG board objects must stay alive until the script ends
def one(good, name, edit):
    b = load(good, name); KEEP.append(b); edit(b); save(b, name)
def nomarks(b):
    for t in texts(b): b.Remove(t)
def swap(b):
    for t in texts(b):
        x = t.GetPosition().x; y = t.GetPosition().y
        if t.GetText() in ("P1 +", "P4 -"):
            t.SetPosition(VECTOR2I(FromMM(200.0) - x, y))   # mirror about x = 100 mm: the P1 text on the P4 wing and the other way round
def small(b):
    for t in texts(b):
        if t.GetLayer() == pcbnew.F_SilkS: t.SetTextSize(VECTOR2I(FromMM(0.5), FromMM(0.6)))
import sys   # one copy per process (a second LoadBoard in the same KiCad Python process returns an unusable object)
JOBS = {"broken_nomarks_pins": ("/case_pins.kicad_pcb", nomarks), "broken_swapped_pins": ("/case_pins.kicad_pcb", swap),
        "broken_nomarks_main": ("/case_main.kicad_pcb", nomarks), "broken_small_pins": ("/case_pins.kicad_pcb", small)}
g, f = JOBS[sys.argv[1]]
one(P + g, sys.argv[1], f)
