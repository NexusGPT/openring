import fitz, sys
from collections import Counter
PDF=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf")
S=25.4/72/12
X0,Y0=255.1175537109375, 97.51171875
d=fitz.open(PDF)
def col(c):
    if c is None: return None
    if c[0]>0.9 and c[1]>0.9: return 'white'
    if c[0]>0.9: return 'red'
    if c[0]<0.3: return 'dark' if c[2]<0.5 else 'blue'
    return str(c)
def dots(pn):
    out=[]
    for dr in d[pn].get_drawings():
        if dr['type']!='s': continue
        for it in dr['items']:
            if it[0]!='l': continue
            a,b=it[1],it[2]
            L=((a.x-b.x)**2+(a.y-b.y)**2)**.5*S
            if L<0.005:
                out.append(((a.x-X0)*S,(a.y-Y0)*S,round(dr['width']*S,4),col(dr.get('color'))))
    return out
def segs(pn):
    out=[]
    for dr in d[pn].get_drawings():
        if dr['type']!='s': continue
        for it in dr['items']:
            if it[0]!='l': continue
            a,b=it[1],it[2]
            out.append(((a.x-X0)*S,(a.y-Y0)*S,(b.x-X0)*S,(b.y-Y0)*S,round(dr['width']*S,4),col(dr.get('color'))))
    return out
if __name__=="__main__" and len(sys.argv)>1 and sys.argv[1]!="lib":
    for pn in map(int,sys.argv[1:]):
        ds=dots(pn-1)
        print('page',pn, Counter((w,c) for x,y,w,c in ds).most_common())
