# J1 contact n against DISP1 contact n in the ring netlist; min and max working height of the ring-case contact table.
import csv
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design")
nl={(r["reference"],r["pin_number"]):r["net"] for r in csv.DictReader(open(R+"/ecad/ring/netlist.csv"))}
same=0
for n in range(1,16):
    a,b=nl.get(("J1",str(n))),nl.get(("DISP1",str(n)))
    print("contact %d J1=%r DISP1=%r %s"%(n,a,b,"same" if a==b else "DIFFERENT")); same+= a==b
print("RESULT J1 contacts with the same net as DISP1: %d of 15"%same)
h=[float(r["working_height_mm"]) for r in csv.DictReader(open(R+"/wiring/ring-case-contact.csv"))]
print("RESULT contact rows %d, height min %.3f max %.3f"%(len(h),min(h),max(h)))
