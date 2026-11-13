"""Writes section 6 (H2 results) text from results/h2_*.json, results/h2_*_zin.csv and logs/server/h2_*.log. No number is typed by hand."""
import json, csv, re, sys
B = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/antenna")
def J(t): return json.load(open(f"{B}/results/{t}.json"))
def Z(t):
    return {round(float(r["f_GHz"]), 3): r for r in csv.DictReader(open(f"{B}/results/{t}_zin.csv"))}
def LOG(t):
    s = open(f"{B}/logs/server/{t}.log").read()
    m = re.search(r"end-criteria of ([-0-9.]+)dB reached after (\d+) timesteps \(([-0-9.]+)dB\)", s)
    m2 = re.search(r"Time for (\d+) iterations with (\d+\.?\d*) cells : ([0-9.]+) sec", s)
    return dict(crit=m.group(1), steps=int(m.group(2)), endval=m.group(3), cells_engine=m2.group(2), loop_s=m2.group(3))
def fm(m, key):
    out = []
    for k, v in zip(m["pattern"], m[key]):
        out.append(("%s %.2f nH" % (k, v * 1e9)) if k == "L" else ("%s %.2f pF" % (k, v * 1e12)))
    return ", ".join(out)
def fs(m):
    out = []
    for k, v in zip(m["pattern"], m["snapped_SI"]):
        out.append(("%s %.1f nH" % (k, v * 1e9)) if k == "L" else ("%s %.1f pF" % (k, v * 1e12)))
    return ", ".join(out)
topo = {"L": "inductor", "C": "capacitor"}
def topo_words(p): return "shunt %s, series %s, shunt %s" % tuple(topo[c] for c in p)
out = []
tags = [("A", "h2_A", "as designed: metal body with the floor pocket"), ("B", "h2_B", "resin corner")]
out.append("| Case | Run | Cells | Time steps | End value | Run time (s) | S11 before match at 2.40 / 2.44 / 2.48 GHz (dB) | Zin at 2.44 GHz (ohm) | Radiated share at 2.40 / 2.44 / 2.48 GHz (percent) | Peak gain at 2.44 GHz (dBi) |")
out.append("|---|---|---|---|---|---|---|---|---|---|")
for c, t, name in tags:
    j = J(t); L = LOG(t); e = j["eff_by_ghz"]; zin = j["zin_at"]["2.44"]
    gain = 10 * __import__("math").log10(j["dmax_by_ghz"]["2.44"] * e["2.44"])
    out.append("| %s %s | %s | %d | %d | %s dB | %.0f | %.2f / %.2f / %.2f | %.2f %+.2fj | %.1f / %.1f / %.1f | %.2f |" % (
        c, name, t, j["cells"], L["steps"], L["endval"], j["run_seconds"], j["s11_before_db_at"]["2.40"], j["s11_before_db_at"]["2.44"], j["s11_before_db_at"]["2.48"],
        zin[0], zin[1], 100 * e["2.40"], 100 * e["2.44"], 100 * e["2.48"], gain))
out.append("")
out.append("| Case | Best three-part match (topology, solved values) | Worst S11 after match, 2.400 to 2.480 GHz (dB) | Same with values snapped to 0.1 nH / 0.1 pF | Snapped values | ABCD cross-check of the unsnapped worst S11 (dB) | Return-loss rule (6 dB) | Radiated-share rule (10 percent) | Case verdict |")
out.append("|---|---|---|---|---|---|---|---|---|")
for c, t, name in tags:
    j = J(t); m = j["match"]; v = j["verdict"]
    out.append("| %s | %s: %s | %.2f | %.2f | %s | %.2f | %s (worst return loss %.2f dB) | %s | %s |" % (
        c, topo_words(m["pattern"]), fm(m, "values_SI"), j["s11_after_db_worst"], j["s11_after_snapped_db_worst"], fs(m), j["s11_after_abcd_db_worst"],
        "pass" if v["rl_ok"] else "fail", v["worst_rl_db"], "pass" if v["eff_ok"] else "fail", "FAIL (tool not validated)" if not v["pass_"] else "PASS (tool not validated)"))
out.append("")
out.append("Worst S11 of every topology the search tried (dB), from the JSON field match.all_patterns_worst_db:")
for c, t, name in tags:
    j = J(t); out.append("- %s: %s" % (c, ", ".join("%s %.2f" % (k, v) for k, v in j["match"]["all_patterns_worst_db"].items())))
out.append("")
out.append("Input impedance before matching (results/h2_*_zin.csv, at the port):")
out.append("| Case | 2.00 GHz | 2.40 GHz | 2.44 GHz | 2.48 GHz | 2.50 GHz | 3.00 GHz |")
out.append("|---|---|---|---|---|---|---|")
for c, t, name in tags:
    z = Z(t); row = []
    for f in (2.0, 2.4, 2.44, 2.48, 2.5, 3.0):
        r = z[round(f, 3)]; row.append("%.2f %+.2fj (S11 %.2f dB)" % (float(r["Re_Zin"]), float(r["Im_Zin"]), float(r["s11_dB"])))
    out.append("| %s | %s |" % (c, " | ".join(row)))
print("\n".join(out))
