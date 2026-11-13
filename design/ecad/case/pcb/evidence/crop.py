import pymupdf, sys
D=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/")
f,p,x0,y0,x1,y1,dpi,out=sys.argv[1],int(sys.argv[2]),*[float(v) for v in sys.argv[3:7]],int(sys.argv[7]),sys.argv[8]
d=pymupdf.open(D+f)
pix=d[p-1].get_pixmap(dpi=dpi,clip=pymupdf.Rect(x0,y0,x1,y1))
o=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/evidence/pages/")+out
pix.save(o); print(o)
