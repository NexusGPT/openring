# review 3: print each product-wiring.csv line compactly (file line number, id, ends, join, carrier, marking, cuts, solder_first)
import csv, sys
p = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/product-wiring.csv")
rows = list(csv.DictReader(open(p)))
for i, r in enumerate(rows, start=2):
    cuts = [r["cut_mm_us%d" % s] for s in range(7, 14)]
    print("L%d %s | A: %s %s.%s %s [%s] join=%s | B: %s %s.%s %s [%s] join=%s | carrier=%s | mark=%s | gauge=%s | cuts=%s | note=%s | first=%s | state=%s" % (
        i, r["id"], r["end_A_board"], r["end_A_ref"], r["end_A_pin"], r["end_A_face"], r["signal_A"], r["join_A"],
        r["end_B_board"], r["end_B_ref"], r["end_B_pin"], r["end_B_face"], r["signal_B"], r["join_B"],
        r["carrier"], r["carrier_marking"], r["carrier_gauge_or_model"], "/".join(cuts), r["cut_note"], r["solder_first"], r["state"]))
print("RESULT rows=%d" % len(rows))
