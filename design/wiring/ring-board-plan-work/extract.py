import fitz, sys, json
from collections import Counter
PDF=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf")
S=25.4/72/12  # mm per pt
X0,Y0=255.1175537109375, 97.51171875  # board frame top-left
d=fitz.open(PDF)
def circles(pn):
    out=[]
    for dr in d[pn].get_drawings():
        ops=[it[0] for it in dr['items']]
        r=dr['rect']
        w,h=r.width*S,r.height*S
        if 'c' in ops and abs(w-h)<0.02 and w<0.6 and w>0.03:
            out.append(dict(x=round((r.x0+r.x1)/2*1-X0,3), y=0, cx=round(((r.x0+r.x1)/2-X0)*S,4), cy=round(((r.y0+r.y1)/2-Y0)*S,4), dia=round(w,4), fill=dr.get('fill'), stroke=dr.get('color'), type=dr['type'], lw=dr.get('width')))
    return out
if __name__=='__main__':
    pn=int(sys.argv[1])-1
    cs=circles(pn)
    c=Counter((x['dia'] ,str(x['fill']),x['type']) for x in cs)
    for k,v in sorted(c.items()): print(k,v)
