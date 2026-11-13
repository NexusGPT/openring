import pymupdf
d=pymupdf.open((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/case_esp32s3_mini1.pdf"))
pg=d[44]
dr=pg.get_drawings()
print(len(dr))
rects=[]
for s in dr:
    if s.get('fill') is not None and s['rect'].y0>250 and s['rect'].y1<760 :
        r=s['rect']
        rects.append((round(r.x0,2),round(r.y0,2),round(r.width,2),round(r.height,2),s['fill']))
print(len(rects))
for r in sorted(rects,key=lambda r:(r[1],r[0]))[:200]: print(r)
