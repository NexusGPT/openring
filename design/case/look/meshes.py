"""Tessellate out/case_assembly_US9.step (every named node) into look/meshes.npz for render.py (this step needs build123d; render.py does not).
Run: nice -n 19 ../.venv/bin/python look/meshes.py   (from design/case). CASE_OUT picks another output folder."""
import json, os
import numpy as np
from build123d import import_step

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("CASE_OUT", os.path.join(HERE, "..", "out"))
LOOK = os.environ.get("LOOK_OUT", HERE)


def leaves(shape, prefix=""):
    kids = list(shape.children)
    if not kids:
        yield (shape.label or prefix), shape
    for k in kids:
        yield from leaves(k)


def main():
    asm = import_step(os.path.join(OUT, "case_assembly_US9.step"))
    data, names = {}, []
    for name, shp in leaves(asm):
        if not name:
            continue
        tol = 0.015 if name in ("shell", "lid", "base_plate", "post") else 0.06
        v, t = shp.tessellate(0.006 if name == "lid" else tol, 0.05 if name == "lid" else 0.1)
        v = np.array([[p.X, p.Y, p.Z] for p in v], float)
        t = np.array(t, int)
        if len(t) == 0:
            continue
        data[name + "__v"] = v
        data[name + "__t"] = t
        names.append(name)
        print(name, len(v), len(t))
    np.savez_compressed(os.path.join(LOOK, "meshes.npz"), names=np.array(names), **data)
    print("meshes.npz", len(names), "parts")


def c4_meshes():
    """the C4 outer parts (shell, lid, base plate) for the comparison picture"""
    data, names = {}, []
    for n in ("shell", "lid", "base_plate"):
        shp = import_step(os.path.join(HERE, "c4_out", "parts", n + ".step"))
        v, t = shp.tessellate(0.05, 0.15)
        data["c4_" + n + "__v"] = np.array([[p.X, p.Y, p.Z] for p in v], float)
        data["c4_" + n + "__t"] = np.array(t, int)
        names.append("c4_" + n)
    np.savez_compressed(os.path.join(LOOK, "c4_meshes.npz"), names=np.array(names), **data)
    print("c4_meshes.npz", names)


if __name__ == "__main__":
    main()
    c4_meshes()
