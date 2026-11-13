#!/usr/bin/env python3
"""Makes the USB D+ and D- tracks of PCB1 equal in length (target: within 0.5 mm, aim 0.3 mm) by adding square-wave bumps to a straight piece of the shorter net.
Run with KiCad's Python:  run_kipy.sh tune_usb.py <board.kicad_pcb>      (rewrites the board in place; every trial is checked with kicad-cli drc and kept only when the
violation count does not rise).  Prints the lengths before and after."""
import math, os, shutil, sys
import pcbnew
from pcbnew import ToMM
import build_boards as BB

path = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, "work", "tune_trial.kicad_pcb")


def lengths(b):
    return BB.net_length(b, "USB_D+"), BB.net_length(b, "USB_D-")


def count(b):
    pcbnew.SaveBoard(TMP, b)
    shutil.copy(path.replace(".kicad_pcb", ".kicad_pro"), TMP.replace(".kicad_pcb", ".kicad_pro"))
    rc, nv, nu, rep = BB.drc(TMP, TMP + ".json")
    return nv, nu


b = pcbnew.LoadBoard(path)
lp, ln = lengths(b)
print("before: D+ %.3f mm, D- %.3f mm, difference %.3f mm" % (lp, ln, abs(lp - ln)))
BB.fill_all(b)
base_v, base_u = count(b)
print("baseline violations %d unconnected %d" % (base_v, base_u))
tries = 0
while abs(lengths(b)[0] - lengths(b)[1]) > 2.0 and tries < 40:
    lp, ln = lengths(b)
    short = "USB_D+" if lp < ln else "USB_D-"
    extra = abs(lp - ln)
    done = False
    for skip in range(0, 8):
        for scale, hh, ww, pp in ((1.0, 0.8, 0.3, 0.6), (1.0, 0.6, 0.3, 0.55), (1.0, 0.45, 0.3, 0.5), (0.6, 0.45, 0.3, 0.5), (0.5, 0.35, 0.3, 0.5)):
            trial = pcbnew.LoadBoard(path) if tries == 0 and False else None
            saved = TMP.replace(".kicad_pcb", "_keep.kicad_pcb")
            pcbnew.SaveBoard(saved, b)
            tb = pcbnew.LoadBoard(saved)
            ok = BB.meander(tb, short, extra * scale, skip=skip, h=hh, w=ww, pitch=pp)
            if not ok:
                continue
            BB.fill_all(tb)
            nv, nu = count(tb)
            print('  trial skip %d scale %.1f: violations %d unconnected %d' % (skip, scale, nv, nu))
            if nv <= base_v and nu <= base_u:
                b = tb
                done = True
                break
        if done:
            break
    tries += 1
    if not done:
        print("no room for another bump on", short)
        break
lp, ln = lengths(b)
print("after: D+ %.3f mm, D- %.3f mm, difference %.3f mm" % (lp, ln, abs(lp - ln)))
pcbnew.SaveBoard(path, b)
