import json, struct, sys
g = open((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/look/s1/out/ring-merged32h-us9.glb"),'rb').read()
n,_ = struct.unpack("<II", g[12:20]); j = json.loads(g[20:20+n])
print(json.dumps(j["nodes"])[:1500]); print(j["accessors"][0])
