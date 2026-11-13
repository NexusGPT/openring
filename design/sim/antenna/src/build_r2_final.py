"""Builds the round 2 part 3 and 4 tables from results/r3*_*.json, results/*_zin.csv and logs/server/*.log. No number is typed by hand."""
import json, csv, re, os, sys
B = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/antenna")
sets = [("protocol (frozen stand-in, eps 28.08)", "r3L", ["D", "A", "B"]), ("re-tune 1 (22)", "r3T", ["D", "A", "B"]), ("re-tune 2 (23)", "r3U", ["D", "A", "B", "B2", "E"])]
names = {"D": "D free air", "A": "A metal body + pocket, finger", "B": "B resin corner, finger", "B2": "B2 resin corner, no floor under antenna, finger", "E": "E antenna on screen face, resin corner, finger"}
def endinfo(tag):
    s = open(f"{B}/logs/server/{tag}.log", errors="replace").read()
    m = re.search(r"end-criteria of ([-0-9.]+)dB reached after (\d+) timesteps \(([-0-9.]+)dB\)", s)
    if m: return "-40 dB reached, %s steps (%s dB)" % (m.group(2), m.group(3))
    ts = re.findall(r"Timestep:\s+(\d+) .*?Energy: ~[0-9.e+-]+ \(\s*([-0-9.]+)dB\)", s)
    return "cap, %s steps, energy %s dB" % (ts[-1][0], ts[-1][1]) if ts else "unknown"
def rlpeak(tag):
    rows = list(csv.DictReader(open(f"{B}/results/{tag}_zin.csv")))
    b = max(rows, key=lambda r: -float(r["s11_dB"])); return -float(b["s11_dB"]), float(b["f_GHz"])
out = []; rank = []
for title, pre, cases in sets:
    out.append(f"\n**{title}**\n")
    out.append("| Case | Run | eps_r | End | S11 before match at 2.40 / 2.44 / 2.48 (dB) | Zin at 2.44 (ohm) | Largest return loss in 2.0-3.0 GHz (dB at GHz) | Radiated / incident power at 2.40 / 2.44 / 2.48 (percent) | Radiated share of accepted power at 2.40 / 2.44 / 2.48 (percent) | Best three-part match | Worst S11 after (dB) | Verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cases:
        tag = f"{pre}_{c}"; p = f"{B}/results/{tag}.json"
        if not os.path.exists(p): out.append(f"| {names[c]} | {tag} | no result file |"); continue
        j = json.load(open(p)); z = j["zin_at"]["2.44"]; t = j["total_eff_by_ghz"]; e = j["eff_by_ghz"]; m = j["match"]; pk = rlpeak(tag)
        vals = ", ".join(("%s %.2f nH" % (k, v * 1e9)) if k == "L" else ("%s %.2f pF" % (k, v * 1e12)) for k, v in zip(m["pattern"], m["values_SI"]))
        out.append("| %s | %s | %.2f | %s | %.2f / %.2f / %.2f | %.2f %+.2fj | %.1f at %.3f | %.2f / %.2f / %.2f | %.1f / %.1f / %.1f | %s: %s | %.2f | %s |" % (
            names[c], tag, j["eps"], endinfo(tag), j["s11_before_db_at"]["2.40"], j["s11_before_db_at"]["2.44"], j["s11_before_db_at"]["2.48"], z[0], z[1], pk[0], pk[1],
            100 * t["2.40"], 100 * t["2.44"], 100 * t["2.48"], 100 * e["2.40"], 100 * e["2.44"], 100 * e["2.48"], m["pattern"], vals, j["s11_after_db_worst"], "FAIL" if not j["verdict"]["pass_"] else "PASS"))
        rank.append((pre, c, t["2.44"], pk))
out.append("\nRanking by radiated / incident power at 2.44 GHz (highest first), per set:")
for title, pre, cases in sets:
    r = sorted([x for x in rank if x[0] == pre], key=lambda x: -x[2])
    out.append("- %s: %s" % (title, " > ".join("%s (%.2f percent)" % (x[1], 100 * x[2]) for x in r)))
print("\n".join(out))
