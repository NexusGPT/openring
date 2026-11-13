import json, struct, csv
g = open((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin/out/thin-inside.glb"), "rb").read()
magic, ver, total = struct.unpack("<III", g[:12])
n, t = struct.unpack("<II", g[12:20])
j = json.loads(g[20:20 + n])
names = [x["name"] for x in j["nodes"]]
rows = [r["part"] for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin/placement.csv")))]
print("glb magic ok:", magic == 0x46546C67, "version", ver, "bytes", total, "len", len(g))
print("nodes", len(names), "rows", len(rows), "same set and order:", names == rows, "unique:", len(set(names)) == len(names))
print("meshes", len(j["meshes"]), "all nodes have a mesh:", all("mesh" in x for x in j["nodes"]))
