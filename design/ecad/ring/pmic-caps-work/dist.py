import csv, math, sys
path = sys.argv[1]
rows = {}
with open(path, newline="") as f:
    for r in csv.DictReader(f):
        ref = r["reference"].split(":")[-1]
        rows[ref] = r
u = rows["U2"]
ux, uy = float(u["x_mm"]), float(u["y_mm"])
print("U2 centre x=%.3f y=%.3f" % (ux, uy))
for ref in ["C1","C2","C4","C5","C21","C31","C32","C35","C36","C60","C61","C71","C72","C73","C74","C75","C76","C77","C78","C79","C80","C81","C82","C83","C85","C86","C87","C88","L71","L72"]:
    r = rows[ref]
    x, y = float(r["x_mm"]), float(r["y_mm"])
    d = math.hypot(x-ux, y-uy)
    print("%s x=%.3f y=%.3f dist_mm=%.3f side=%s zone=%s" % (ref, x, y, d, r["side"], r["zone"]))
