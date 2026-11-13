#!/usr/bin/env python3
"""Software pictures of the inside model v5, no browser (owner, 2026-11-10: no Chrome, no headless browser).
Reads out/thin-inside.glb (Z-up CAD axes), keeps the named nodes and the triangles inside a crop box, shades each triangle
by its normal against one light, and draws them back to front with matplotlib (Agg). The v4 Playwright version is kept as
out/v5/render_v4_playwright.py.
Usage: render.py [out_dir]   writes v5-joystick.png and v5-hand-end-below.png
"""
import json
import struct
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

HERE = Path(__file__).resolve().parent
GLB = HERE / "out" / "thin-inside.glb"
OUTD = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "out" / "v5"
ZC = -9.875

COL = {"metal": (0.72, 0.73, 0.76), "gold": (0.85, 0.65, 0.2), "pcb": (0.10, 0.45, 0.25), "chip": (0.15, 0.15, 0.17),
       "ceramic": (0.8, 0.75, 0.62), "polymer": (0.35, 0.35, 0.42), "glass": (0.6, 0.8, 0.95), "screen": (0.1, 0.1, 0.18),
       "foam": (0.45, 0.45, 0.47), "flex": (0.9, 0.6, 0.1), "cell": (0.75, 0.78, 0.8), "resin": (0.9, 0.85, 0.7), "mark": (0.9, 0.9, 0.9)}
OVR = {"light_guide": (0.95, 0.25, 0.25), "recording_led": (1.0, 0.1, 0.1), "joystick_dam": (0.3, 0.7, 0.9), "mic_gasket_1": (0.4, 0.9, 0.4)}


def load():
    g = GLB.read_bytes()
    n, _ = struct.unpack("<II", g[12:20])
    j = json.loads(g[20:20 + n])
    off = 20 + n
    bl, _ = struct.unpack("<II", g[off:off + 8])
    buf = g[off + 8:off + 8 + bl]

    def acc(i):
        a = j["accessors"][i]
        v = j["bufferViews"][a["bufferView"]]
        dt = np.float32 if a["componentType"] == 5126 else np.uint32
        k = {"VEC3": 3, "SCALAR": 1}[a["type"]]
        return np.frombuffer(buf, dtype=dt, count=a["count"] * k, offset=v["byteOffset"]).reshape(-1, k) if k > 1 else \
            np.frombuffer(buf, dtype=dt, count=a["count"], offset=v["byteOffset"])
    out = []
    for i in j["scenes"][0]["nodes"]:
        nd = j["nodes"][i]
        for c in nd.get("children", []):
            ch = j["nodes"][c]
            pr = j["meshes"][ch["mesh"]]["primitives"][0]
            out.append((nd["name"], ch["extras"]["class"], acc(pr["attributes"]["POSITION"]), acc(pr["indices"]).reshape(-1, 3)))
    return out


def view(meshes, names, crop, eye, up, path, title, hide=(), panels=None):
    """panels: list of (title, hide) drawn side by side with the same camera; else one panel"""
    if panels is None:
        panels = [(title, hide)]
    fig, axs = plt.subplots(1, len(panels), figsize=(9 * len(panels), 8), dpi=150, squeeze=False)
    total = 0
    for ax, (ttl, hd) in zip(axs[0], panels):
        total += draw(ax, meshes, names, crop, eye, up, ttl, hd)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print(f"wrote {path}: {total} triangles drawn")


def draw(ax, meshes, names, crop, eye, up, title, hide):
    eye = np.array(eye, float)
    eye /= np.linalg.norm(eye)
    up = np.array(up, float)
    rt = np.cross(up, eye)
    rt /= np.linalg.norm(rt)
    up2 = np.cross(eye, rt)
    light = eye * 0.7 + up2 * 0.5 + rt * 0.3
    light /= np.linalg.norm(light)
    polys, cols, depth = [], [], []
    lo, hi = np.array(crop[0]), np.array(crop[1])
    for name, cls, V, T in meshes:
        if names is not None and name not in names:
            continue
        if any(name.startswith(h) for h in hide):
            continue
        tri = V[T]
        cen = tri.mean(axis=1)
        keep = np.all((cen >= lo) & (cen <= hi), axis=1)
        tri = tri[keep]
        if not len(tri):
            continue
        nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(nrm, axis=1)
        ok = ln > 0
        tri, nrm = tri[ok], nrm[ok] / ln[ok, None]
        facing = nrm @ eye
        tri, nrm, facing = tri[facing > 0], nrm[facing > 0], facing[facing > 0]
        base = np.array(OVR.get(name, COL[cls]))
        sh = 0.35 + 0.65 * np.clip(nrm @ light, 0, 1)
        c = np.clip(base[None, :] * sh[:, None], 0, 1)
        p2 = np.stack([tri @ rt, tri @ up2], axis=-1)
        polys.append(p2)
        cols.append(c)
        depth.append(tri.mean(axis=1) @ eye)
    P = np.concatenate(polys)
    C = np.concatenate(cols)
    D = np.concatenate(depth)
    o = np.argsort(D)
    ax.add_collection(PolyCollection(P[o], facecolors=C[o], edgecolors="none", antialiased=False))
    ax.set_xlim(P[..., 0].min() - 0.3, P[..., 0].max() + 0.3)
    ax.set_ylim(P[..., 1].min() - 0.3, P[..., 1].max() + 0.3)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
    return len(P)


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    meshes = load()
    print("nodes:", sorted({m[0] for m in meshes}))
    joy = {"joystick_cap", "joy_sw_fingertip", "joy_sw_hand", "joy_sw_up", "joy_sw_down", "joy_sw_centre", "joystick_dam",
           "band_flex_thumb", "vibration_motor", "cell", "band_liner"}
    a = np.radians(-78.0)
    centre = np.array([0.0, 11.0 * np.sin(a), ZC + 11.0 * np.cos(a)])
    crop = (centre - [5.0, 5.5, 5.5], centre + [5.0, 5.5, 5.5])
    eye = np.array([0.55, np.sin(a), np.cos(a)]) + np.array([0, 0, 0.35])
    view(meshes, joy, crop, eye, (0, 0, 1), OUTD / "v5-joystick.png", "",
         panels=[("joystick at -78 deg, body hidden: nub 4.6 (X) x 3.6, metal frame 6.4 x 5.4, dam (blue), motor, cell end", ()),
                 ("same view, nub, flange and frame hidden: five switches at cross 2.4, dam (blue), ribbon head", ("joystick_cap",))])
    hand = None
    crop2 = ((-14.5, -7.5, -0.5), (-6.5, 7.5, 2.0))
    view(meshes, hand, crop2, (-0.25, -0.35, -1.0), (1, 0, 0), OUTD / "v5-hand-end-below.png",
         "v5 hand end of the board seen from below (body, cover glass, seal and membranes hidden): U5, gasket (green), LG1 (red), LED1",
         hide=("outer_body", "cover_glass", "glass_seal", "mic_membrane", "band_liner", "cell", "band_flex"))


if __name__ == "__main__":
    main()
