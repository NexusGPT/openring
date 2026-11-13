import json, struct
g = open((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin/out/thin-inside.glb"), "rb").read()
n, _ = struct.unpack("<II", g[12:20]); j = json.loads(g[20:20+n])
rows = []
for nd in j["nodes"]:
    if "mesh" in nd:
        acc = j["meshes"][nd["mesh"]]["primitives"][0]["indices"]
        rows.append((j["accessors"][acc]["count"] // 3, nd["name"]))
rows.sort(reverse=True)
print("total", sum(r[0] for r in rows), "nodes", len(rows))
for r in rows[:14]: print(r)
