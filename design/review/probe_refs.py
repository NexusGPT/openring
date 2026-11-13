"""Compare designators in bom.csv with parts.csv and netlist.csv (read-only probe)."""
import csv, re, sys
D = (__import__("pathlib").Path(__file__).resolve().parents[2].as_posix() + "/design")
def expand(s):
    out = []
    for tok in re.split(r"[,\s]+", s.strip()):
        if tok:
            out.append(tok)
    return out
bom = {}
with open(D + "/bom.csv", newline="") as f:
    for row in csv.DictReader(f):
        for r in expand(row["reference"]):
            bom[r] = row["item"]
parts = {}
with open(D + "/ecad/ring/parts.csv", newline="") as f:
    for row in csv.DictReader(f):
        parts[row["reference"]] = row
net = {}
with open(D + "/ecad/ring/netlist.csv", newline="") as f:
    for row in csv.DictReader(f):
        net.setdefault(row["reference"], []).append((row["net"], row["pin_number"], row["pin_name"]))
print("bom designators:", len(bom), " parts.csv:", len(parts), " netlist refs:", len(net))
print("IN BOM NOT IN parts.csv:", sorted(set(bom) - set(parts)))
print("IN parts.csv NOT IN BOM:", sorted(set(parts) - set(bom)))
print("IN parts.csv NOT IN netlist:", sorted(set(parts) - set(net)))
# mpn mismatches
with open(D + "/bom.csv", newline="") as f:
    for row in csv.DictReader(f):
        for r in expand(row["reference"]):
            if r in parts and row["maker_part_number"] and parts[r]["mpn"] and row["maker_part_number"] != parts[r]["mpn"]:
                print("MPN DIFF", r, "bom=", row["maker_part_number"], "parts=", parts[r]["mpn"])
            if r in parts and row["value"] and parts[r]["value"] and row["value"].replace(" ", "").lower()[:6] != parts[r]["value"].replace(" ", "").lower()[:6]:
                print("VALUE DIFF", r, "bom=", row["value"], "parts=", parts[r]["value"])
for r in ["U2", "Q2", "LED1", "BT1", "M1", "RT1"]:
    print(r, net.get(r))
# nets with U2 load switch inputs
with open(D + "/ecad/ring/netlist.csv", newline="") as f:
    for row in csv.DictReader(f):
        if row["reference"] == "U2" and re.search(r"LS|VOUT|VSET|SHPHLD|GPIO0|NTC|VBUS|VSYS", row["pin_name"]):
            print("U2", row["pin_number"], row["pin_name"], "->", row["net"])
