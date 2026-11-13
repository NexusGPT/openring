import csv,os,sys
P=sys.argv[1]; R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad")
rn={(r["reference"],r["pin_number"]) for r in csv.DictReader(open(R+"/ring/netlist.csv"))}
cn={(r["reference"],r["pin_number"]) for r in csv.DictReader(open(R+"/case/netlist.csv"))}
allc=set()
for f in sorted(os.listdir(P)):
    if not f.endswith("-pads.csv"): continue
    nl=cn if f.startswith("case") else rn
    for r in csv.DictReader(open(os.path.join(P,f))):
        if f.startswith("case"): allc.add((r["ref"],r["pad"]))
        if (r["ref"],r["pad"]) not in nl: print("not in netlist:",f,r["ref"],r["pad"],r["net"],r["layers"][:20])
for k in sorted(cn):
    if k not in allc: print("case netlist pin with no pad:",k)
