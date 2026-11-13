import pymupdf, sys
D=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/")
f=sys.argv[1]; pages=[int(x) for x in sys.argv[2].split(',')]; dpi=int(sys.argv[3]) if len(sys.argv)>3 else 110
d=pymupdf.open(D+f)
for p in pages:
    pix=d[p-1].get_pixmap(dpi=dpi)
    out=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/evidence/pages/%s_p%d.png")%(f[:-4],p)
    pix.save(out); print(out)
