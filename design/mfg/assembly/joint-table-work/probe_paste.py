"""Probe: which pads of each board have a paste opening in its delivered paste Gerber.
Uses the same reader as check_joints.py. Prints, per paste file, the transform match rate and the
SMD pads on that face with no opening. Run with design/.venv/bin/python."""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_joints as cj

ROOT = cj.ROOT
FILES = [
    ("ring", "F", "design/ecad/ring/pcb/fab/gerber/ring-F_Paste.gbr"),
    ("ring", "B", "design/ecad/ring/pcb/fab/gerber/ring-B_Paste.gbr"),
    ("case_main", "F", "design/ecad/case/pcb/fab/case_main/gerber/case_main-F_Paste.gbr"),
    ("case_main", "B", "design/ecad/case/pcb/fab/case_main/gerber/case_main-B_Paste.gbr"),
    ("case_pins", "F", "design/ecad/case/pcb/fab/case_pins/gerber/case_pins-F_Paste.gbr"),
    ("case_pins", "B", "design/ecad/case/pcb/fab/case_pins/gerber/case_pins-B_Paste.gbr"),
]
for board, face, rel in FILES:
    flashes = cj.read_flashes(os.path.join(ROOT, rel))
    pads = cj.read_pads(board)
    cu = face + ".Cu"
    face_pads = [p for p in pads if cu in p["layers"].split() and p["attr"] == "SMD"]
    with_paste_layer = [p for p in face_pads if (face + ".Paste") in p["layers"].split()]
    hit_layer = sum(1 for p in with_paste_layer if cj.has_opening(p, flashes))
    print("FILE", rel, "flashes", len(flashes), "smd pads on", cu, len(face_pads),
          "with", face + ".Paste in footprint", len(with_paste_layer), "of these with an opening", hit_layer)
    for p in face_pads:
        if not cj.has_opening(p, flashes):
            print("  NO OPENING", board, p["ref"] + ":" + p["pad"], p["net"], p["layers"])
