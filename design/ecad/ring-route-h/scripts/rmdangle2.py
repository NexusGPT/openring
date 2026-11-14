# rmdangle2.py in out drc.json : delete every track / via (unlocked or locked) that the rules check calls dangling, except GND, RF and USB nets; refill; save
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[3]))
KEEP = {"GND", "RF_FEED", "ANT_TRIM", "ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "USB_DP", "USB_DN"}
ids = {it["uuid"] for v in d["violations"] if v["type"] in ("track_dangling", "via_dangling") for it in v["items"]}
rm = [t for t in b.GetTracks() if t.m_Uuid.AsString() in ids and t.GetNetname() not in KEEP]
info = [(t.GetNetname(), t.GetClass(), t.IsLocked()) for t in rm]
for t in rm: b.Delete(t)
print("deleted", len(info), info, flush=True)
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("saved", flush=True)
