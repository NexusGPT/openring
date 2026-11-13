"""Builds the H2 result tables (markdown) from results/h2_*.json. Run on the Mac with python3 (numpy not needed)."""
import json, sys, os
B = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/sim/antenna/results")
cases = [("A", "h2_A", "as designed (metal body, pocket)"), ("B", "h2_B", "resin corner"), ("C", "h2_C", "antenna at the fingertip end")]
def fmt_vals(m):
    out = []
    for k, v in zip(m["pattern"], m["values_SI"]):
        out.append("%s %.2f nH" % (k, v * 1e9) if k == "L" else "%s %.2f pF" % (k, v * 1e12))
    return ", ".join(out)
def fmt_snap(m):
    out = []
    for k, v in zip(m["pattern"], m["snapped_SI"]):
        out.append("%s %.1f nH" % (k, v * 1e9) if k == "L" else "%s %.1f pF" % (k, v * 1e12))
    return ", ".join(out)
rows = []
for c, tag, name in cases:
    p = os.path.join(B, tag + ".json")
    if not os.path.exists(p): rows.append("| %s | %s | no result file |" % (c, name)); continue
    j = json.load(open(p)); e = j["eff_by_ghz"]; v = j["verdict"]
    rows.append("| %s | %s | %.1f / %.1f / %.1f | %.2f | %s | %s | %.2f | %.2f | %s | %.1f | %s |" % (
        c, name, j["s11_before_db_at"]["2.40"], j["s11_before_db_at"]["2.44"], j["s11_before_db_at"]["2.48"], j["s11_before_db_worst"],
        j["match"]["pattern"], fmt_vals(j["match"]), j["s11_after_db_worst"], j["s11_after_snapped_db_worst"], fmt_snap(j["match"]),
        100 * e["2.44"], "pass" if v["pass_"] else "fail"))
print("\n".join(rows))
