#!/usr/bin/env python3
"""Exterior pictures of the ring (merged32h: round joystick, no recording light), software render, no browser.
Reads design/look/s1/out/ring-merged32h-us9.glb, skips its separate 'light' skin node (a removed part), applies the node
transforms (metres to mm), and draws with the functions of render_v7.py. Usage: render_exterior_v7.py [out_dir]
Writes v7-ring-exterior-*.png and prints the glb's sha256.
"""
import hashlib, importlib.util, json, struct, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUTD = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
sys.argv = [sys.argv[0], str(OUTD)]
spec = importlib.util.spec_from_file_location("rv7", HERE / "render_v7.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
GLB = HERE.parents[4] / "look" / "s1" / "out" / "ring-merged32h-us9.glb"
CLS = {"body": "metal", "glass": "screen", "screen": "screen", "joystick": "polymer", "mic_1": "pcb", "mic_2": "pcb"}
SKIP = {"light"}


def quat(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def load():
    g = GLB.read_bytes()
    n, _ = struct.unpack("<II", g[12:20]); j = json.loads(g[20:20 + n])
    off = 20 + n; bl, _ = struct.unpack("<II", g[off:off + 8]); buf = g[off + 8:off + 8 + bl]
    def acc(i):
        a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a["componentType"]]
        k = {"VEC3": 3, "SCALAR": 1}[a["type"]]
        arr = np.frombuffer(buf, dtype=dt, count=a["count"] * k, offset=v.get("byteOffset", 0) + a.get("byteOffset", 0))
        return arr.reshape(-1, 3) if k == 3 else arr
    out, names = [], []
    for c in j["nodes"][0]["children"]:
        nd = j["nodes"][c]; names.append(nd["name"])
        if nd["name"] in SKIP:
            continue
        Vs, Ts, base = [], [], 0
        for pr in j["meshes"][nd["mesh"]]["primitives"]:
            Vp = acc(pr["attributes"]["POSITION"]).astype(float) * 1000.0
            Vs.append(Vp); Ts.append(acc(pr["indices"]).reshape(-1, 3).astype(np.int64) + base); base += len(Vp)
        V = np.concatenate(Vs); T = np.concatenate(Ts)
        if "rotation" in nd:
            V = V @ quat(nd["rotation"]).T
        if "translation" in nd:
            V = V + np.array(nd["translation"]) * 1000.0
        print(nd["name"], len(Vs), "primitives", len(T), "triangles", V.min(0).round(2).tolist(), V.max(0).round(2).tolist())
        if nd["name"] == "body":   # the body's top face is under the cover glass at the same height: drop it so the painter's sort does not mix them
            T = T[V[T][:, :, 2].min(axis=1) < 2.7]
        out.append((nd["name"], CLS[nd["name"]], V, T))
    return out, names


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    meshes, names = load()
    print("glb:", GLB, hashlib.sha256(GLB.read_bytes()).hexdigest())
    print("nodes in file:", names, "drawn:", [m[0] for m in meshes])
    allv = np.concatenate([m[2] for m in meshes]); print("bbox mm", allv.min(0).round(2).tolist(), allv.max(0).round(2).tolist())
    big = ((-20, -30, -30), (20, 30, 12))
    R.view(meshes, None, big, (0.7, -0.8, 0.6), (0, 0, 1), OUTD / "v7-ring-exterior-iso.png", "Ring US 9, exterior (merged32h), from the joystick side above: titanium body, black glass, round joystick cap. No recording light.")
    R.view(meshes, None, big, (0, 0, 1), (0, 1, 0), OUTD / "v7-ring-exterior-top.png", "Ring US 9, exterior, seen from above onto the screen (black cover glass over the whole face).")
    a = np.radians(-78.0)
    c = np.array([0.0, 14.0 * np.sin(a), -9.875 + 14.0 * np.cos(a)])
    R.view(meshes, None, (c - [6, 6, 6], c + [6, 6, 6]), (0, np.sin(a), np.cos(a)), (1, 0, 0), OUTD / "v7-ring-exterior-joystick.png", "Joystick side at -78 deg, seen along the surface normal: round opening 5.6, round frame 5.4, round cap 4.4 with dish and three ridges.")
    R.view(meshes, None, ((-20, -30, -4), (20, 30, 12)), (0, 0, -1), (0, 1, 0), OUTD / "v7-ring-exterior-underside.png", "Underside of the block seen from below, band cut away: the two 1.0 mm microphone holes (green discs are the microphone parts behind them).")


if __name__ == "__main__":
    main()
