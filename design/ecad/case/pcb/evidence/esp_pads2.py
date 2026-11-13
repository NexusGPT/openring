import pymupdf
d=pymupdf.open((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/datasheets/case_esp32s3_mini1.pdf"))
pg=d[44]
for s in pg.get_drawings():
    r=s['rect']
    if r.width>90 and r.height>20 and r.y0>250 and r.y1<780:
        print([round(v,2) for v in (r.x0,r.y0,r.x1,r.y1)], s.get('fill'), s.get('color'), len(s['items']))
