import json, csv, re, os
B = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/antenna")
runs = [("D free air (control)", "r4_D"), ("A metal body + pocket, finger", "r4_A"), ("B resin corner, finger", "r4_B"), ("S = B + screen ledge metal and cable at the hand end", "r4_S"),
        ("S180 = B + the same metal at the fingertip end (screen turned 180 degrees)", "r4_S180"), ("E antenna on screen face under the glass, resin corner, finger", "r4_E"), ("A0 = A without the finger", "r4_A0"), ("B0 = B without the finger", "r4_B0"), ("B2 resin corner, no floor under the antenna, finger", "r3U_B2")]
def endinfo(tag):
    s = open(f"{B}/logs/server/{tag}.log", errors="replace").read()
    m = re.search(r"end-criteria of ([-0-9.]+)dB reached after (\d+) timesteps \(([-0-9.]+)dB\)", s)
    return ("converged: %s steps, %s dB" % (m.group(2), m.group(3))) if m else "NOT CONVERGED"
out = ["| Case | Run | eps_r | End | S11 before match 2.40 / 2.44 / 2.48 (dB) | Zin at 2.44 (ohm) | Largest return loss (dB at GHz) | Radiated share of accepted power 2.40 / 2.44 / 2.48 (percent) | Radiated / incident power 2.40 / 2.44 / 2.48 (percent) | Best three-part match | Worst S11 after (dB) | Verdict |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
rk = []
for name, tag in runs:
    j = json.load(open(f"{B}/results/{tag}.json")); e = endinfo(tag); z = j["zin_at"]["2.44"]; a = j["eff_by_ghz"]; t = j["total_eff_by_ghz"]; m = j["match"]
    rows = list(csv.DictReader(open(f"{B}/results/{tag}_zin.csv"))); pk = max(rows, key=lambda r: -float(r["s11_dB"]))
    vals = ", ".join(("%s %.2f nH" % (k, v * 1e9)) if k == "L" else ("%s %.2f pF" % (k, v * 1e12)) for k, v in zip(m["pattern"], m["values_SI"]))
    out.append("| %s | %s | %.2f | %s | %.2f / %.2f / %.2f | %.1f %+.1fj | %.1f at %.3f | %.1f / %.1f / %.1f | %.2f / %.2f / %.2f | %s: %s | %.2f | %s |" % (name, tag, j["eps"], e, j["s11_before_db_at"]["2.40"], j["s11_before_db_at"]["2.44"], j["s11_before_db_at"]["2.48"], z[0], z[1], -float(pk["s11_dB"]), float(pk["f_GHz"]),
        100 * a["2.40"], 100 * a["2.44"], 100 * a["2.48"], 100 * t["2.40"], 100 * t["2.44"], 100 * t["2.48"], m["pattern"], vals, j["s11_after_db_worst"], "FAIL" if not j["verdict"]["pass_"] else "PASS"))
    rk.append((name.split(" ")[0], 100 * a["2.48"], 100 * t["2.48"]))
out.append("\nRanking by radiated share of accepted power at 2.48 GHz: " + " > ".join("%s %.1f" % (n, s) for n, s, _ in sorted(rk, key=lambda x: -x[1])))
print("\n".join(out))
