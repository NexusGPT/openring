"""Read, rewrite and compress GLB files with the standard library only.

Axis rule of the bundle: every GLB in it is glTF Y-up (x along the finger, y up, z toward the viewer,
mm). The design's models are CAD Z-up (x along the finger, y across, z up). `to_y_up` converts once, by
giving every top-level node the rotation of -90 degrees about X (CAD (x, y, z) -> glTF (x, z, -y)); a model
whose top-level nodes already carry that rotation (build123d exports do) is left alone.
"""
import json
import math
import struct
import subprocess
from pathlib import Path

_S = math.sqrt(0.5)
ROT_Z_UP_TO_Y_UP = (-_S, 0.0, 0.0, _S)  # quaternion x, y, z, w
MAGIC = 0x46546C67


class GlbError(Exception):
    pass


def read(path):
    """(json dict, binary chunk bytes or None)."""
    b = Path(path).read_bytes()
    if len(b) < 20 or struct.unpack("<I", b[:4])[0] != MAGIC:
        raise GlbError(f"{Path(path).name} is not a GLB file")
    off, js, binary = 12, None, None
    while off + 8 <= len(b):
        n, kind = struct.unpack("<II", b[off:off + 8])
        body = b[off + 8:off + 8 + n]
        if kind == 0x4E4F534A:
            js = json.loads(body.decode("utf-8"))
        elif kind == 0x004E4942 and binary is None:
            binary = body
        off += 8 + n
    if js is None:
        raise GlbError(f"{Path(path).name} has no JSON chunk")
    return js, binary


def write(path, js, binary):
    jb = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jb += b" " * (-len(jb) % 4)
    chunks = struct.pack("<II", len(jb), 0x4E4F534A) + jb
    if binary is not None:
        bb = binary + b"\0" * (-len(binary) % 4)
        chunks += struct.pack("<II", len(bb), 0x004E4942) + bb
    Path(path).write_bytes(struct.pack("<III", MAGIC, 2, 12 + len(chunks)) + chunks)


def node_names(js):
    return [n.get("name", "") for n in js.get("nodes", [])]


def scene_roots(js):
    scenes = js.get("scenes", [])
    if not scenes:
        return []
    return list(scenes[js.get("scene", 0)].get("nodes", []))


def _qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return [aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz]


def _rotate_vec(v):
    x, y, z = v
    return [x, z, -y]


def has_y_up_root(js):
    roots = scene_roots(js)
    for r in roots:
        q = js["nodes"][r].get("rotation")
        if not q or any(abs(a - b) > 1e-4 for a, b in zip(q, ROT_Z_UP_TO_Y_UP)):
            return False
    return bool(roots)


def to_y_up(js):
    """Convert in place; returns True when it changed something."""
    if has_y_up_root(js):
        return False
    for r in scene_roots(js):
        n = js["nodes"][r]
        if "matrix" in n:
            raise GlbError("a top-level node holds a matrix; cannot convert it")
        n["rotation"] = _qmul(ROT_Z_UP_TO_Y_UP, n.get("rotation", [0, 0, 0, 1]))
        if "translation" in n:
            n["translation"] = _rotate_vec(n["translation"])
    return True


def accessor_extent(js, node_index, axis):
    """(min, max) of the POSITION accessor of a node's mesh along `axis` (0, 1, 2), in the mesh's own space,
    or None when the node holds no mesh with bounds."""
    mesh = js["nodes"][node_index].get("mesh")
    if mesh is None:
        return None
    lo, hi = [], []
    for prim in js["meshes"][mesh].get("primitives", []):
        acc = js["accessors"][prim["attributes"]["POSITION"]]
        if "min" in acc and "max" in acc:
            lo.append(acc["min"][axis])
            hi.append(acc["max"][axis])
    return (min(lo), max(hi)) if lo else None


def compress(src, dst, tool, log):
    """meshopt-compress src into dst with the gltf-transform at `tool`. Raises GlbError when it fails; the
    tool's output goes to the file `log`."""
    with open(log, "w", encoding="utf-8") as fh:
        r = subprocess.run([str(tool), "meshopt", str(src), str(dst), "--level", "high"], stdout=fh,
                           stderr=subprocess.STDOUT, timeout=300)
    if r.returncode != 0 or not Path(dst).is_file():
        raise GlbError(f"gltf-transform meshopt failed with exit {r.returncode}")
