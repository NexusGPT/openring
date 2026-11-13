"""Print the x position of the column heads and of chosen values on a PDF page,
so the column a value sits in is read from the file, not assumed.
Usage: python columns.py <pdf> <page 1-based> <word> [<word> ...]
Also renders the page to page<N>.png beside this script."""
import sys, os, fitz
pdf, page = sys.argv[1], int(sys.argv[2])
want = set(sys.argv[3:]) | {"Min.", "Typ.", "Max.", "Unit"}
doc = fitz.open(pdf)
p = doc[page - 1]
for w in p.get_text("words"):
    x0, y0, x1, y1, text = w[:5]
    if text in want:
        print(f"page {page} x0={x0:7.1f} x1={x1:7.1f} y={y0:7.1f} word={text}")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"page{page}.png")
p.get_pixmap(dpi=110).save(out)
print("rendered", out)
