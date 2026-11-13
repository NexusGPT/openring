# checks guide facts against board pad dumps: test pad places and signals (step 5), J1 place and contact 1 side (step 15),
# J_BAND sides (step 14); and pin working heights vs the maker range 1.90..2.20, as built (disc) and without the 0.07 disc
import csv,re
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
W=R+'design/wiring/review2-work/'
pads=list(csv.DictReader(open(W+'pads/ring.csv')))
g=open(R+'design/mfg/assembly/assembly.md').read().split('\n')
s5=g[119]
fr=lambda r:(round(float(r['x'])-100,3),round(float(r['y'])-100,3))  # ring frame X=kx-100, Y=ky-100 (B.Cu seen from +Z)
bad=0
for m in re.finditer(r'(TP\d+) \(Y (-?[\d.]+)\)',s5):
    tp,y=m.group(1),float(m.group(2))
    r=[p for p in pads if p['ref']==tp][0]; X,Y=fr(r)
    col=re.search(r'column X (-?[\d.]+):[^c]*\b%s\b'%tp,s5)
    ok=abs(Y-y)<0.01 and col and abs(float(col.group(1))-X)<0.01 and r['fp_layer']=='B.Cu'
    bad+=not ok; print('step5',tp,'guide X',col and col.group(1),'Y',y,'board',X,Y,r['fp_layer'],'OK' if ok else 'DIFF')
sig={'TP3':'SWDCLK','TP4':'SWDIO','TP5':'NRESET','TP17':'VDD_1V8','TP18':'GND','TP1':'DBG_TX','TP19':'SHPHLD','TP21':'MIC_B_DATA','TP6':'SPARE_P1_00','TP12':'SPARE_P2_00','TP14':'SPARE_P3_03','TP15':'SPARE_P3_04'}
for k,v in sig.items():
    n=[p['net'] for p in pads if p['ref']==k][0]; ok=n==v; bad+=not ok; print('step5 signal',k,'guide',v,'board',n,'OK' if ok else 'DIFF')
j=[p for p in pads if p['ref']=='J1' and p['pad'].isdigit()]
X,Y=fr(j[0]); print('J1 fp centre ring frame',round(float(j[0]['fp_x'])-100,3),round(float(j[0]['fp_y'])-100,3),'(guide -4.933, -0.003)')
ys={int(p['pad']):fr(p)[1] for p in j}
print('J1 pad1 Y',ys[1],'pad15 Y',ys[15],'monotonic falling',all(ys[k]>ys[k+1] for k in range(1,15)))
ant=[p for p in pads if p['ref']=='ANT1'][0]; print('ANT1 Y',round(float(ant['fp_y'])-100,3),'contact 1 on ANT1 side:',(ys[1]>0)==(float(ant['fp_y'])-100>0))
for jb in('J_BAND_A','J_BAND_B'):
    r=[p for p in pads if p['ref']==jb][0]; print(jb,'Y',round(float(r['fp_y'])-100,3),r['fp_layer'])
hs=list(csv.DictReader(open(R+'design/wiring/ring-case-contact.csv')))
h=[float(r['working_height_mm']) for r in hs]
print('heights rows',len(h),'min',min(h),'max',max(h),'all in 1.90..2.20:',all(1.90<=x<=2.20 for x in h))
out=[(r['case_pin'],r['ring_size'],round(float(r['working_height_mm'])+0.07,3)) for r in hs if float(r['working_height_mm'])+0.07>2.20]
print('without the 0.07 disc (guide step 8 default), heights above 2.20:',len(out),out)
print('RESULT guide facts diffs=%d'%bad)
