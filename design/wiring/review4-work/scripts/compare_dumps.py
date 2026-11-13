# Compares the pad dumps check_joints.py reads (joint-table-work/pads) with my dumps of the delivered boards.
import csv,os
A=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/assembly/joint-table-work/pads")
B=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work/pads")
tot=diff=0
for f in sorted(os.listdir(A)):
    if not f.endswith("-pads.csv"): continue
    a={}
    for r in csv.DictReader(open(os.path.join(A,f))): a.setdefault((r["ref"],r["pad"]),[]).append((round(float(r["x_mm"]),3),round(float(r["y_mm"]),3),r["net"]))
    b={}
    for r in csv.DictReader(open(os.path.join(B,f))): b.setdefault((r["ref"],r["pad"]),[]).append((round(float(r["x"]),3),round(float(r["y"]),3),r["net"]))
    for k in set(a)|set(b):
        tot+=1
        if sorted(a.get(k,[]))!=sorted(b.get(k,[])):
            diff+=1; print("DIFF",f,k,a.get(k),b.get(k))
print("RESULT keys=%d differ=%d"%(tot,diff))
