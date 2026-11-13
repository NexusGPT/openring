#!/usr/bin/env python3
"""Writes the fabrication outputs of the 14 band boards with kicad-cli (plain Python 3, no pcbnew needed).
usage: python3 make_fab.py [--boards DIR] [--out FABDIR] [--log FILE] [names ...]   (log default evidence/make_fab.log)
Per board flexK-usN, in FABDIR/flexK-usN/:
  Gerber F.Cu, B.Cu, F.Mask, B.Mask (coverlay openings), Edge.Cuts, User.1 (stiffener outline) and the paste layer of the face that is printed:
  F.Paste on FLEX1 (switch face, process.md P8 change C1), B.Paste on FLEX2 (disc face, change C2); a Gerber job file; Excellon drill;
  flexK-usN-fab-notes.txt (panel instruction of process.md P7, layer names; change C4 without copper).
In FABDIR: flexK-usN-drawing.pdf (layers F.Cu, B.Cu, Edge.Cuts, Dwgs.User, User.1, F.Fab, autoscaled to A4).
Prints one line per command: '<what> <board> <exit code>'; exit 1 if any command failed."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
GERBER_LAYERS = ["F.Cu", "B.Cu", "F.Mask", "B.Mask", "Edge.Cuts", "User.1"]
PDF_LAYERS = "F.Cu,B.Cu,Edge.Cuts,Dwgs.User,User.1,F.Fab"

args = sys.argv[1:]
boards, out, names, logp = HERE, os.path.join(HERE, "fab"), [], os.path.join(HERE, "evidence", "make_fab.log")
while args:
    a = args.pop(0)
    if a == "--boards":
        boards = args.pop(0)
    elif a == "--out":
        out = args.pop(0)
    elif a == "--log":
        logp = args.pop(0)
    else:
        names.append(a)
names = names or [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]

NOTES = """Fabrication notes, {name} (band ribbon {kind}, ring size US {us}); written by design/ecad/band/make_fab.py
Project: ring recorder, band ribbons. Board files: design/ecad/band/{name}.kicad_pcb (generator build_band.py).

1. Layers in this folder
   {name}-F_Cu.gbr, {name}-B_Cu.gbr: copper, 12 um, two layers.
   {name}-F_Mask.gbr, {name}-B_Mask.gbr: COVERLAY openings (polyimide coverlay, not liquid mask).
   {name}-User_1.gbr: STIFFENER outline, polyimide 0.10 mm, bonded on the back (B.Cu) face.
   {name}-Edge_Cuts.gbr: outline. {name}.drl: vias 0.30 / 0.10 drill.
   {paste_file}: SOLDER PASTE openings, {paste_face} ({paste_what}). For the stencil: stainless steel, laser cut,
   foil 0.08 mm (design/mfg/assembly/process.md section P2, rows "Band ribbon FLEX1" and "Band ribbon FLEX2").
   No paste opening on the board-end lands (hot bar joint) nor on the {other} (soldered by hand).

2. Panel (process.md section P7 "Locating features (fiducials)", change C4 of section P8)
   The ribbon itself carries no fiducial (no copper added). The panel carries them:
   - tooling rails of 5 mm on the panel;
   - three fiducials of 1 mm, on the rails, on the paste face ({paste_face_short}), centred 3.85 mm from the panel edges, not in a line.
   Source: process.md P7, quoting the board maker's capability page (JL :102: "1 mm fiducials centered at 3.85 mm from the panel edges")
   and P7 line "FLEX1 panel (each size): three on the switch face (F). FLEX2 panel (each size): three on the pad face (B)."
   "Three" is marked [CHOICE] in process.md (the other option is two). The coverlay opening round each fiducial is not in a saved
   document (process.md P7): the panel maker uses its own fiducial opening.
"""


def run(cmd, log):
    r = subprocess.run(cmd, capture_output=True, text=True)
    log.write(" ".join(cmd) + "\n" + r.stdout + r.stderr)
    return r.returncode


bad = 0
os.makedirs(out, exist_ok=True)
with open(logp, "w") as log:
    for n in names:
        kind = "FLEX1" if n.startswith("flex1") else "FLEX2"
        us = n.split("us")[1]
        pcb = os.path.join(boards, n + ".kicad_pcb")
        d = os.path.join(out, n)
        os.makedirs(d, exist_ok=True)
        paste = "F.Paste" if kind == "FLEX1" else "B.Paste"
        c = run([KICAD_CLI, "pcb", "export", "gerbers", "--no-protel-ext", "--layers", ",".join(GERBER_LAYERS + [paste]), "-o", d + "/", pcb], log)
        print("gerber", n, c); bad += c != 0
        c = run([KICAD_CLI, "pcb", "export", "drill", "-o", d + "/", pcb], log)
        print("drill", n, c); bad += c != 0
        c = run([KICAD_CLI, "pcb", "export", "pdf", "--mode-single", "--layers", PDF_LAYERS, "--scale", "0", "-o",
                 os.path.join(out, n + "-drawing.pdf"), pcb], log)
        print("pdf", n, c); bad += c != 0
        if kind == "FLEX1":
            kw = dict(paste_file=f"{n}-F_Paste.gbr", paste_face="switch face F (F.Cu side)", paste_face_short="F",
                      paste_what="12 openings 0.55 x 0.55 mm, 1:1 on the 12 soldered lands of SW1 to SW5", other="motor lead lands")
        else:
            kw = dict(paste_file=f"{n}-B_Paste.gbr", paste_face="disc face B (B.Cu side)", paste_face_short="B",
                      paste_what="16 round openings 0.58 mm, four on each 1.6 mm disc land CP1 to CP4, centred 0.49 mm from the land centre on the diagonals, clear of the centre via",
                      other="cell tab lands P+, NTC, P-")
        with open(os.path.join(d, n + "-fab-notes.txt"), "w") as f:
            f.write(NOTES.format(name=n, kind=kind, us=us, **kw))
        print("notes", n, 0)
sys.exit(1 if bad else 0)
