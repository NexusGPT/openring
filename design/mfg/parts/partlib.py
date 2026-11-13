"""Shared helpers for export_parts.py and check_parts.py (mesh reading, closed-mesh test, bounding box)."""
import struct
import numpy as np


def read_stl(path):
    """Return an (n,3,3) float array of triangles from a binary or ASCII STL."""
    data = open(path, "rb").read()
    if len(data) >= 84:
        n = struct.unpack("<I", data[80:84])[0]
        if 84 + 50 * n == len(data):
            dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
            return np.frombuffer(data, dtype=dt, count=n, offset=84)["v"].astype(np.float64)
    txt = data.decode("ascii", "replace").split()
    vs = [float(txt[i + 1]) for i, w in enumerate(txt) if w == "vertex" for i in (i,)]
    idx = [i for i, w in enumerate(txt) if w == "vertex"]
    arr = np.array([[float(txt[i + 1]), float(txt[i + 2]), float(txt[i + 3])] for i in idx])
    return arr.reshape(-1, 3, 3)


def mesh_info(tris):
    """(triangle_count, closed, bbox(min3,max3)). Closed = no open edge: every undirected edge is shared by an even number
    of triangles (2 = manifold) after merging vertices at 1e-5 mm; zero-area triangles are ignored."""
    n = len(tris)
    flat = np.round(tris.reshape(-1, 3), 5)
    _, inv = np.unique(flat, axis=0, return_inverse=True)
    f = inv.reshape(-1).reshape(n, 3)
    nondeg = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    f = f[nondeg]
    degenerate = int((~nondeg).sum())
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    e.sort(axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    closed = bool(len(cnt) > 0 and np.all(cnt % 2 == 0))        # no open (boundary) edge
    manifold = bool(closed and np.all(cnt == 2))
    return n, closed, manifold, (tris.reshape(-1, 3).min(axis=0), tris.reshape(-1, 3).max(axis=0))


def bbox_of(shape):
    b = shape.bounding_box()
    return (b.min.X, b.min.Y, b.min.Z), (b.max.X, b.max.Y, b.max.Z)


def write_clean_stl(path):
    """Rewrite a binary STL without zero-area triangles (two corners equal at 1e-5 mm); returns how many were dropped."""
    tris = read_stl(path)
    r = np.round(tris, 5)
    bad = (np.all(r[:, 0] == r[:, 1], axis=1) | np.all(r[:, 1] == r[:, 2], axis=1) | np.all(r[:, 0] == r[:, 2], axis=1))
    good = tris[~bad].astype("<f4")
    a, b, c = good[:, 0], good[:, 1], good[:, 2]
    nrm = np.cross(b - a, c - a); ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    out = np.zeros(len(good), dtype=dt); out["n"] = nrm / ln; out["v"] = good
    with open(path, "wb") as f:
        f.write(b"ring parts STL, units mm".ljust(80, b" ")); f.write(np.uint32(len(good)).tobytes()); f.write(out.tobytes())
    return int(bad.sum())
