import fitz, sys
M=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg")
names=sys.argv[2:]; out=sys.argv[1]
pix=[fitz.open(f"{M}/drawings/{n}.pdf")[0].get_pixmap(dpi=62) for n in names]
w,h=pix[0].width,pix[0].height
doc=fitz.open(); page=doc.new_page(width=w*2,height=h*2)
for i,p in enumerate(pix):
    page.insert_image(fitz.Rect((i%2)*w,(i//2)*h,(i%2+1)*w,(i//2+1)*h),pixmap=p)
page.get_pixmap(dpi=72).save(out)
