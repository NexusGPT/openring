"""The two case boards as they are routed, read from their own files for the case model (case.py), version r4.

Source of every number here: the board files design/ecad/case/pcb/case_main.kicad_pcb and case_pins.kicad_pcb (read only), read on each run by
r4/board_read.py under KiCad's own Python (outline, thickness, footprints, pads) and exported on each run to STEP by kicad-cli (the part bodies,
with KiCad's 3D models as the board author attached them). Nothing about the boards is typed here except the sheet origin of each board, which
is read from design/ecad/case/pcb/build_boards.py (lines `OX, OY = ...` and `OX2, OY2 = ...`).

Frames (build_boards.py and geom.py):
  PCB1: u = KiCad x - OX (case x - pcb1_x0), d = KiCad y - OY (= - case y); STEP from kicad-cli: X = KiCad x, Y = - KiCad y, Z = 0 at the board's back.
  PCB2: kx = OX2 - case y, ky = OY2 - (case z - z_pin); seen from its front face (the pin face), which faces case -X; STEP Z = 0 at the back face.
"""
import json
import os
import re
import subprocess

from build123d import Compound, Face, Pos, Rot, Solid, Vector, Wire, import_step

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.normpath(os.path.join(HERE, "..", "..", "ecad", "case", "pcb"))
BOARD_MAIN = os.environ.get("CASE_BOARD_MAIN", os.path.join(ECAD, "case_main.kicad_pcb"))
BOARD_PINS = os.environ.get("CASE_BOARD_PINS", os.path.join(ECAD, "case_pins.kicad_pcb"))
BUILD_BOARDS = os.path.join(ECAD, "build_boards.py")


def sheet_origins():
    src = open(BUILD_BOARDS).read()
    m1 = re.search(r"^OX, OY = ([\d.]+), ([\d.]+)", src, re.M)
    m2 = re.search(r"^OX2, OY2 = ([\d.]+), ([\d.]+)", src, re.M)
    if not (m1 and m2):
        raise RuntimeError("build_boards.py: the lines 'OX, OY = ...' / 'OX2, OY2 = ...' changed; the board frame is unknown")
    return float(m1.group(1)), float(m1.group(2)), float(m2.group(1)), float(m2.group(2))


def read(out_dir):
    """read both boards (KiCad Python) and export their STEP (kicad-cli) into out_dir; returns dict main / pins with 'json' and 'step'"""
    os.makedirs(out_dir, exist_ok=True)
    log = os.path.join(out_dir, "read_boards.log")
    with open(log, "w") as fh:
        rc = subprocess.run(["bash", os.path.join(HERE, "run_read.sh"), BOARD_MAIN, BOARD_PINS, out_dir], stdout=fh, stderr=subprocess.STDOUT).returncode
    if rc != 0:
        raise RuntimeError("board read failed, exit %d, see %s" % (rc, log))
    res = {}
    for t, path in (("main", BOARD_MAIN), ("pins", BOARD_PINS)):
        j = json.load(open(os.path.join(out_dir, t + ".json")))
        if os.path.abspath(j["board"]) != os.path.abspath(path):
            raise RuntimeError("%s.json was read from %s, not %s" % (t, j["board"], path))
        res[t] = dict(json=j, step=import_step(os.path.join(out_dir, t + ".step")), file=path)
    return res


def _stem(fname):
    return os.path.splitext(os.path.basename(fname))[0].replace(".", "_")


def label_bodies(board):
    """match every part body of the board's STEP to its footprint (same 3D model, body centre inside that footprint's courtyard, nearest
    footprint position); returns {ref: shape in the STEP frame}. Fails when a footprint with a shown model has no body or a body has no footprint."""
    j = board["json"]
    fps = [f for f in j["footprints"] if any(m["show"] for m in f["models"])]
    bodies = [c for c in board["step"].children if not (c.label or "").endswith(tuple("_PCB_%d" % i for i in range(1, 10))) and not (c.label or "").endswith("_PCB")]
    out = {}
    for c in bodies:
        bb = c.bounding_box()
        cx, cy = (bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2            # KiCad sheet frame
        cand = []
        for f in fps:
            if not any(_stem(m["file"]) == c.label for m in f["models"]):
                continue
            x0, y0, x1, y1 = f["courtyard"]
            if x0 - 0.01 <= cx <= x1 + 0.01 and y0 - 0.01 <= cy <= y1 + 0.01:
                cand.append(((cx - f["x"]) ** 2 + (cy - f["y"]) ** 2, f["ref"]))
        if not cand:
            raise RuntimeError("STEP body %s at (%.3f, %.3f) matches no footprint" % (c.label, cx, cy))
        ref = min(cand)[1]
        if ref in out:
            raise RuntimeError("two STEP bodies for %s" % ref)
        out[ref] = c
    missing = sorted(set(f["ref"] for f in fps) - set(out))
    if missing:
        raise RuntimeError("footprints with a 3D model but no body in the STEP: %s" % missing)
    return out


def body_u_front(boards, ref):
    """smallest u (board frame, toward case -X) of the body of `ref` in the main board's STEP"""
    OX = sheet_origins()[0]
    return label_bodies(boards["main"])[ref].bounding_box().min.X - OX


def prism(poly, z0, z1):
    face = Face(Wire.make_polygon([Vector(x, y, z0) for x, y in poly], close=True))
    return Solid.extrude(face, Vector(0, 0, z1 - z0))


def main_board(boards, x0, z0):
    """PCB1 in the case frame: board edge u = 0 at case x = x0, board back at z = z0.
    Returns (compound named main_board with one child per part, info dict)."""
    OX, OY, _, _ = sheet_origins()
    b = boards["main"]
    j = b["json"]
    t = float(j["thickness"])
    if len(j["outlines"]) != 1:
        raise RuntimeError("main board: %d outlines, expected 1" % len(j["outlines"]))
    poly = [(x0 + (X - OX), -(Y - OY)) for X, Y in j["outlines"][0]]
    pcb = prism(poly, z0, z0 + t)
    pcb.label = "PCB1"
    kids = [pcb]
    info = dict(file=b["file"], thickness=t, outline_case=poly, parts={}, back_side=[], no_model=[])
    us = [X - OX for X, Y in j["outlines"][0]]
    ds = [Y - OY for X, Y in j["outlines"][0]]
    info["u_range"], info["d_range"] = (min(us), max(us)), (min(ds), max(ds))
    bodies = label_bodies(b)
    mv = Pos(x0 - OX, OY, z0)                                                      # STEP frame -> case frame (pure shift)
    for f in j["footprints"]:
        if f["side"] == "B":
            info["back_side"].append(dict(ref=f["ref"], has_model=bool(f["models"]), pads=len(f["pads"])))
        if f["ref"] not in bodies:
            info["no_model"].append(f["ref"])
            continue
        s = mv * bodies[f["ref"]]
        s.label = f["ref"]
        kids.append(s)
        bb = s.bounding_box()
        info["parts"][f["ref"]] = dict(x=(bb.min.X, bb.max.X), y=(bb.min.Y, bb.max.Y), z=(bb.min.Z, bb.max.Z), height_above_top=bb.max.Z - (z0 + t),
                                       u=f["x"] - OX, d=f["y"] - OY, rot=f["rot"], side=f["side"], model=[m["file"] for m in f["models"]])
    pads = {}
    for f in j["footprints"]:
        for p in f["pads"]:
            key = f["ref"] if len(f["pads"]) == 1 else "%s.%s" % (f["ref"], p["num"])
            pads[key] = dict(x=x0 + p["x"] - OX, y=-(p["y"] - OY), drill=p["drill"], front=p["front"], back=p["back"], net=p["net"])
    info["pads"] = pads
    return Compound(children=kids, label="main_board"), info


def pin_board(boards, x_face_of_pin, z_pin):
    """PCB2's islands in the case frame. x_face_of_pin(ref) gives the case x of the front face of the island that carries pin `ref` (P1 to P4).
    Returns (dict island name -> solid, info): islands named pin_board_pcb2 (the one with P2 and P3), _wing_R (P1, +y), _wing_L (P4, -y)."""
    _, _, OX2, OY2 = sheet_origins()
    b = boards["pins"]
    j = b["json"]
    t = float(j["thickness"])
    fp = {f["ref"]: f for f in j["footprints"]}
    pins = {r: (OX2 - fp[r]["x"], z_pin + (OY2 - fp[r]["y"])) for r in ("P1", "P2", "P3", "P4")}
    out, info = {}, dict(file=b["file"], thickness=t, pins=pins, islands={}, pads={})
    for o in j["outlines"]:
        ys = [OX2 - X for X, Y in o]
        zs = [z_pin + (OY2 - Y) for X, Y in o]
        y0, y1, zz0, zz1 = min(ys), max(ys), min(zs), max(zs)
        if len(o) != 4:
            raise RuntimeError("pin board island with %d corners (expected a rectangle)" % len(o))
        on = [r for r, (py, pz) in pins.items() if y0 <= py <= y1 and zz0 <= pz <= zz1]
        if not on:
            raise RuntimeError("pin board island y %.3f..%.3f carries no pin" % (y0, y1))
        xs = sorted({round(x_face_of_pin(r), 6) for r in on})
        if len(xs) != 1:
            raise RuntimeError("island with pins %s whose base planes differ: %s" % (on, xs))
        xf = xs[0]
        name = "pin_board_pcb2" if set(on) == {"P2", "P3"} else ("pin_board_pcb2_wing_R" if on == ["P1"] else "pin_board_pcb2_wing_L" if on == ["P4"] else None)
        if name is None:
            raise RuntimeError("unexpected pin set on an island: %s" % on)
        out[name] = Pos((xf + xf + t) / 2, (y0 + y1) / 2, (zz0 + zz1) / 2) * __import__("build123d").Box(t, y1 - y0, zz1 - zz0)
        info["islands"][name] = dict(x=(xf, xf + t), y=(y0, y1), z=(zz0, zz1), pins=on)
    for f in j["footprints"]:
        for p in f["pads"]:
            info["pads"][f["ref"]] = dict(y=OX2 - p["x"], z=z_pin + (OY2 - p["y"]), sx=p["sx"], sy=p["sy"], front=p["front"], net=p["net"])
    return out, info
