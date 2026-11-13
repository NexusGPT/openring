import csv,math
balls={r['ball']:(float(r['x_mm']),float(r['y_mm'])) for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/w1-evidence/u1-measured-pads.csv")))}
U=(4.0,0.0)
D={'XC':((3,3),3,['A1','A2']),'XL':((5.5,3),2,['B6','B7']),'ANT':((-5.0,4.0),4,['C1']),
'USB':((-2.2,5.2),2,['H6','H7']),'LCD':((-12,0),1,['G7','G8','G9','F7','D6','H5']),'SD':((-1.0,0),1,['A9','B10','D9','D10']),
'PMIC':((8.5,0),1,['B8','E7','D8']),'JOYA':((-2.2,-5.2),1,['G1','G2','H1','H2','G10']),'MIC':((-10.8,-4.8),1,['F1','F2']),'MOT':((0,4.2),1,['F6']),
'VBUS':((-2.2,5.2),1,['H9']),'DCC':((4,-3.5),0.5,['A5'])}
rots={'rot0':lambda x,y:(x,y),'rot90':lambda x,y:(-y,x),'rot180':lambda x,y:(-x,-y),'rot270':lambda x,y:(y,-x)}
for n,f in rots.items():
    s=0;det=[]
    for k,(dst,w,bs) in D.items():
        d=sum(math.dist((U[0]+f(*balls[b])[0],U[1]+f(*balls[b])[1]),dst) for b in bs)/len(bs)
        s+=w*d; det.append(f'{k}:{d:.1f}')
    print(n,round(s,1),' '.join(det))
