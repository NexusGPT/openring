"""render_page.py <pdf> <page 1-based> <out.png> [zoom] [clip x0,y0,x1,y1 in points]: PyMuPDF raster of one datasheet page (no browser)."""
import sys
import pymupdf

pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
zoom = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
doc = pymupdf.open(pdf)
p = doc[page - 1]
clip = None
if len(sys.argv) > 5:
    x0, y0, x1, y1 = (float(v) for v in sys.argv[5].split(","))
    clip = pymupdf.Rect(x0, y0, x1, y1)
pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
pix.save(out)
print(f"page {page} of {len(doc)} size {p.rect} -> {out} {pix.width}x{pix.height}")
