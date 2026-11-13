# writes faulty copies of the csv into the work folder; each must be caught by check_lines.py
import csv,copy
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
F=R+'design/wiring/review2-work/fakes/'
src=list(csv.DictReader(open(R+'design/wiring/product-wiring.csv')))
cols=list(src[0].keys())
def w(name,rows):
    with open(F+name,'w',newline='') as f:
        d=csv.DictWriter(f,cols); d.writeheader(); d.writerows(rows)
r=copy.deepcopy(src); r[0]['end_A_pin']='2 (UP)'; w('f1_wrong_pin.csv',r)
r=copy.deepcopy(src); [x.update(signal_B='GND') for x in r if x['id']=='W025']; w('f2_wrong_signal.csv',r)
r=copy.deepcopy(src); [x.update(cut_mm_us10='') for x in r if x['id']=='W023']; w('f3_missing_cut.csv',r)
r=copy.deepcopy(src); r.append(copy.deepcopy(r[5])); w('f4_duplicate.csv',r)
r=[x for x in copy.deepcopy(src) if x['id']!='W030']; w('f5_missing_line.csv',r)
r=copy.deepcopy(src)
for i in range(200):
    x=copy.deepcopy(src[0]); x['id']='X%03d'%i; x['end_B_ref']='SW9'; r.append(x)
w('f6_flood.csv',r)
r=copy.deepcopy(src); [x.update(end_B_face='B.Cu') for x in r if x['id']=='W001']; w('f7_wrong_face.csv',r)
r=copy.deepcopy(src); [x.update(join_A='hot bar (main board land to FLEX2 tail land 3)') for x in r if x['id']=='W026']; w('f8_wrong_tail_land.csv',r)
print('written 8')
