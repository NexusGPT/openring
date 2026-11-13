"""Bar 1: every end of the 67 wiring lines is in joints.csv or is a no-joint end of a named kind.
Prints the count per kind and the sum. Also counts ends that are the same physical joint (same board, part,
pin and face named at two wiring ends). Run: design/.venv/bin/python -B count_ends.py"""
import csv, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
wl = list(csv.DictReader(open(os.path.join(ROOT, "design/wiring/product-wiring.csv"), newline="")))
jt = list(csv.DictReader(open(os.path.join(ROOT, "design/mfg/assembly/joints.csv"), newline="")))
rows = {(r["wiring_line"], r["end"]): r for r in jt if r["wiring_line"] != "board pass"}
passes = [r for r in jt if r["wiring_line"] == "board pass"]
kinds = collections.Counter()
in_table = collections.Counter()
phys = collections.defaultdict(list)
cond = [r for r in wl if r["carrier_kind"] != "none"]
gap_lines = [r for r in wl if r["carrier_kind"] == "none"]
for r in wl:
    for e in "AB":
        j = r["join_" + e].strip()
        if (r["id"], e) in rows:
            in_table[j.split(" (")[0]] += 1
            phys[(r["end_%s_board" % e], r["end_%s_ref" % e], r["end_%s_pin" % e].split()[0], r["end_%s_face" % e].split(";")[0], j.split(" (")[0].split(",")[0])].append(r["id"] + e)
            continue
        if r["carrier_kind"] == "none":
            kinds["sensing gap W058, no conductor (join '%s')" % j] += 1
        elif j.startswith("copper (same board)"):
            kinds["copper on one board, no joint"] += 1
        elif j.startswith("made by"):
            kinds["made by the part's maker, no joint by the builder (%s)" % j] += 1
        elif j.startswith("none (not soldered)"):
            kinds["switch terminal 1 or 2, not soldered by design"] += 1
        elif j.startswith("inside the part"):
            kinds["inside the part (switch contact, pack board)"] += 1
        else:
            kinds["UNCLASSIFIED: " + j] += 1
print("wiring lines %d: conductors %d, sensing gaps %d; ends %d" % (len(wl), len(cond), len(gap_lines), 2 * len(wl)))
print("ends with a row in joints.csv, by join:")
for k, v in sorted(in_table.items()):
    print("  %3d %s" % (v, k))
print("ends with no row, by kind:")
for k, v in sorted(kinds.items()):
    print("  %3d %s" % (v, k))
a, b = sum(in_table.values()), sum(kinds.values())
print("ARITHMETIC %d ends in joints.csv + %d ends with no joint = %d = 2 x %d lines" % (a, b, a + b, len(wl)))
print("conductor ends: %d = 2 x %d; of them in joints.csv %d, no joint %d" % (
    2 * len(cond), len(cond), a, b - sum(v for k, v in kinds.items() if k.startswith("sensing gap"))))
same = {k: v for k, v in phys.items() if len(v) > 1}
print("physical joints named at two wiring ends: %d (%s)" % (len(same), "; ".join("%s:%s = %s" % (k[1], k[2], "+".join(v)) for k, v in sorted(same.items()))))
print("distinct physical joints in the wiring-end rows: %d; board pass rows: %d; rows total %d" % (len(phys), len(passes), len(jt)))
print("UNCLASSIFIED ends: %d" % sum(v for k, v in kinds.items() if k.startswith("UNCLASSIFIED")))
