import sys, json, numpy as np
sys.path.insert(0, "/work/src")
import ringsim_lib as L
lab = json.load(open("/work/tests/hand_labels_p4.json"))
rows = []
for c in lab["cases"]:
    s11 = np.array([10 ** (c["dB_S11"] / 20)])
    rl = L.rl_db(s11)[0]
    limit = 10.0 if c["marker"] in ("m3", "invented_3dB") else 6.0
    scorer = bool(rl >= limit)
    rows.append(dict(marker=c["marker"], rl_db=float(rl), limit=limit, scorer=scorer, hand=c["hand_label_pass"], agree=scorer == c["hand_label_pass"]))
json.dump(rows, open("/work/results/test_hand_labels.json", "w"), indent=1)
print(json.dumps(rows)); assert all(r["agree"] for r in rows); print("C3 agreement: %d of %d" % (sum(r["agree"] for r in rows), len(rows)))
