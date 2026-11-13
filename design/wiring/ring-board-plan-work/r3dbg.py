import sys
sys.argv=['x']
src=open('make_placement3.py').read()
src=src[:src.index("best=None; tried=0; fails={}")]
exec(src)
for rot in (0,90,180,270):
  for X,Y in ((4.0,-4.0),(4.0,-4.5),(3.5,-4.5),(4.5,-4.5),(5.0,-4.5),(4.0,-5.0)):
    placed=dict(base)
    c=cyat('U4',X,Y,rot)
    if not ok('U4',c,placed): print(rot,X,Y,'U4 blocked'); continue
    placed['U4']=(X,Y,rot,c,'Z12')
    b=place_cons('L10',placed)
    if not b: print(rot,X,Y,'L10 none'); continue
    placed['L10']=(b[0],b[1],b[2],b[3],'Z12')
    res=[]
    for ref,pins,lim in MUSTB:
        bb=place_cons(ref,placed)
        res.append((ref,None if not bb else round(bb[4],2)))
    print(rot,X,Y,'L10',b[:3],round(b[4],2),res)
