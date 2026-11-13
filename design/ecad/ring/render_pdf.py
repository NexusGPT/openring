#!/usr/bin/env python3
"""Renders ring-schematic.pdf pages to PNG (evidence/pdf_<tag>_p<n>.png) and checks
text overlap: every text span's box against every other span on the same page."""
import sys, os, fitz
R = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else 'run'
dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 150
d = fitz.open(os.path.join(R, 'ring-schematic.pdf'))
print('pages', len(d))
total = 0
for i, p in enumerate(d):
    p.get_pixmap(dpi=dpi).save(os.path.join(R, 'evidence', 'pdf_%s_p%d.png' % (tag, i + 1)))
    words = p.get_text('words')
    boxes = [(fitz.Rect(w[:4]), w[4]) for w in words]
    ov = []
    for a in range(len(boxes)):
        for b in range(a + 1, len(boxes)):
            ra, rb = boxes[a][0], boxes[b][0]
            inter = ra & rb
            if not inter.is_empty and inter.width > 0.3 and inter.height > 0.3:
                ov.append((boxes[a][1], boxes[b][1], round(inter.width, 2), round(inter.height, 2)))
    total += len(ov)
    print('page %d size %s words %d overlapping word pairs %d' % (i + 1, p.rect, len(words), len(ov)))
    for o in ov[:40]:
        print('   overlap', o)
print('TOTAL overlapping word pairs', total)
