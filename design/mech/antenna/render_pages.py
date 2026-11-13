import sys, fitz
pdf, out = sys.argv[1], sys.argv[2]
d = fitz.open(pdf)
for n in [int(x) for x in sys.argv[3].split(",")]:
    pix = d[n - 1].get_pixmap(dpi=110)
    pix.save(f"{out}_p{n}.png")
    print("saved", f"{out}_p{n}.png", pix.width, pix.height)
