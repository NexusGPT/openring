#!/usr/bin/env python3
"""usage: view.py <board> <out.png> <layers> <cx_mm> <cy_mm> <half_w_mm> <half_h_mm> [dpi]  -- PDF via kicad-cli (no sheet border), cropped PNG via pymupdf"""
import subprocess, sys, os
import pymupdf
board, out, layers, cx, cy, hw, hh = sys.argv[1:8]
dpi = int(sys.argv[8]) if len(sys.argv) > 8 else 600
pdf = out[:-4] + ".pdf"
KC = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
subprocess.check_call([KC, "pcb", "export", "pdf", "--layers", layers, "--black-and-white", "-o", pdf, board], stdout=open(out + ".log", "w"), stderr=subprocess.STDOUT)
d = pymupdf.open(pdf)
pg = d[0]
f = 72 / 25.4
# the pdf page is the board bounding box plus margin only when no border; find drawing bbox
r = pg.get_drawings()
print("page", pg.rect, "drawings", len(r))
cx, cy, hw, hh = float(cx), float(cy), float(hw), float(hh)
clip = pymupdf.Rect((cx - hw) * f, (cy - hh) * f, (cx + hw) * f, (cy + hh) * f)
pix = pg.get_pixmap(dpi=dpi, clip=clip)
pix.save(out)
print(out, pix.width, pix.height)
