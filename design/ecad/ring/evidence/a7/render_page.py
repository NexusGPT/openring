"""Render the page of a PDF that holds a given text to a PNG. usage: render_page.py pdf text out.png [dpi]"""
import sys, fitz
pdf, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 200
d = fitz.open(pdf)
hits = [i for i, p in enumerate(d) if text in p.get_text()]
print('pages (0-based index) holding %r: %s' % (text, hits))
if hits:
    d[hits[0]].get_pixmap(dpi=dpi).save(out)
    print('saved', out)
