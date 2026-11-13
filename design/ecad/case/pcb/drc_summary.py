import json, collections, sys
r = json.load(open(sys.argv[1]))
print("violations", len(r["violations"]), "unconnected", len(r["unconnected_items"]))
print(collections.Counter(v["type"] for v in r["violations"]))
skip = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
n = 0
for v in r["violations"]:
    if v["type"] in skip:
        continue
    print(v["type"], v["description"][:90], [(i["description"][:46], i["pos"]) for i in v["items"]][:2])
    n += 1
    if n > 25:
        break
