# rmdangle.py board drc.json NET : delete the tracks/vias of NET (locked included) that the rules check calls dangling; refill; save
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2])); n = sys.argv[3]
ids = {it["uuid"] for v in d["violations"] if v["type"] in ("track_dangling", "via_dangling") for it in v["items"]}
rm = [t for t in b.GetTracks() if t.m_Uuid.AsString() in ids and t.GetNetname() == n]
info = [(t.GetClass(), t.IsLocked()) for t in rm]
for t in rm: b.Delete(t)
print("deleted", len(info), info, flush=True)
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[1]); print("saved", flush=True)
