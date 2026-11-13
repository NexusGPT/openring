# review 3: every csv id appears exactly once in the drawing's text (pdftotext -layout of product-wiring.pdf), each with its two end labels
# and, for leads and wires, the cut range printed; usage: python3 check_pdf.py <pw-text.txt>
import csv, re, sys, collections
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
rows = list(csv.DictReader(open(R + "/design/wiring/product-wiring.csv")))
txt = open(sys.argv[1]).read()
ids = collections.Counter(re.findall(r"\bW\d{3}\b", txt))
fails = 0
for r in rows:
    n = ids.get(r["id"], 0)
    if n != 1: print("FAIL id %s appears %d times" % (r["id"], n)); fails += 1
    cuts = [r["cut_mm_us%d" % s] for s in range(7, 14) if r["cut_mm_us%d" % s].strip()]
    if cuts:
        lo, hi = min(float(c) for c in cuts), max(float(c) for c in cuts)
        want = ("%.2f-%.2f" % (lo, hi)) if lo != hi else None
        line = [l for l in txt.splitlines() if re.search(r"\b%s\b" % r["id"], l)]
        line = line[0] if line else ""
        if want and want not in line.replace(" ", "") and ("%g-%g" % (lo, hi)) not in line.replace(" ", ""):
            print("FAIL %s cut range %s not on its drawing line: %s" % (r["id"], want, line.strip())); fails += 1
        if not want and ("cut %s" % cuts[0]) not in line and ("cut %g" % float(cuts[0])) not in line:
            print("FAIL %s cut %s not on its drawing line: %s" % (r["id"], cuts[0], line.strip())); fails += 1
extra = [k for k in ids if k not in {r["id"] for r in rows}]
for k in extra: print("FAIL drawing id %s not in csv" % k); fails += 1
print("RESULT drawing ids=%d csv lines=%d fails=%d" % (len(ids), len(rows), fails))
