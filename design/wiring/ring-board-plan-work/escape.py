import fitz, csv, math, sys
from matplotlib.path import Path
PDF=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf")
S=25.4/72/12
X0,Y0=255.1175537109375, 97.51171875
d=fitz.open(PDF)
CX,CY=7.0092,5.5149  # body centre from pads (A1 -1.302,-0.978 -> 5.7072,4.5369)
LAYERS={'L1':0,'L2':2,'L3':3,'L4':4,'L5':5,'L6':6,'L7':7,'L8':9}  # page index; L6 page 7 labelled Mid-Layer 6 (duplicate label), L7 page 8 'Mid-Layer 5'
def iscopper(c):
    if c is None: return False
    if c[0]>0.95 and c[1]>0.95 and c[2]>0.95: return False
    if max(c)<0.4: return False
    return True
def layer(pn):
    segs=[];dots=[];holes=[];fills=[]
    for dr in d[pn].get_drawings():
        c=dr.get('color') if dr['type']=='s' else dr.get('fill')
        white = c is not None and c[0]>0.95 and c[1]>0.95 and c[2]>0.95
        if dr['type']=='s':
            w=(dr.get('width') or 0)*S
            for it in dr['items']:
                if it[0]!='l': continue
                a,b=it[1],it[2]
                A=((a.x-X0)*S,(a.y-Y0)*S); B=((b.x-X0)*S,(b.y-Y0)*S)
                L=math.dist(A,B)
                if white:
                    if L<0.005: holes.append((A,round(w,3)))
                elif iscopper(c):
                    if L<0.005: dots.append((A,round(w,3)))
                    else: segs.append((A,B,round(w,3)))
        elif dr['type'] in('f','fs') and iscopper(c) and not white:
            pts=[]
            for it in dr['items']:
                if it[0]=='l': pts+= [it[1],it[2]]
                elif it[0]=='c': pts+= [it[1],it[4]]
                elif it[0]=='re':
                    r=it[1]; pts+=[r.tl,r.tr,r.br,r.bl]
                elif it[0]=='qu':
                    q=it[1]; pts+=[q.ul,q.ur,q.lr,q.ll]
            if len(pts)>=3:
                fills.append(Path([((p.x-X0)*S,(p.y-Y0)*S) for p in pts]))
    return dict(segs=segs,dots=dots,holes=holes,fills=fills)
L={k:layer(v) for k,v in LAYERS.items()}
if __name__=='__main__':
    for k,v in L.items(): print(k,len(v['segs']),len(v['dots']),len(v['holes']),len(v['fills']))
