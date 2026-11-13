#!/usr/bin/env python3
"""open_nets.py report.json -- lists every unconnected item of a kicad-cli DRC JSON report: net, and its two ends with
their model coordinates (KiCad - 100), plus a count per net and per 2 mm square of the board."""
import collections, json, re, sys
j = json.load(open(sys.argv[1]))
unc = j.get("unconnected_items", [])
per_net = collections.Counter(); cells = collections.Counter()
for u in unc:
    its = u["items"]
    n = ""
    for it in its:
        m = re.search(r"\[([^\]]+)\]", it["description"])
        if m: n = m.group(1); break
    per_net[n] += 1
    ends = []
    for it in its:
        x, y = it["pos"]["x"] - 100, it["pos"]["y"] - 100
        cells[(int((x + 13.6) // 2), int((y + 6.3) // 2))] += 1
        ends.append("(%.2f, %.2f) %s" % (x, y, re.sub(r"\s+", " ", it["description"])[:70]))
    print("OPEN %s: %s" % (n, " <-> ".join(ends)))
print("count of unconnected items:", len(unc))
print("per net:", ", ".join("%s %d" % kv for kv in per_net.most_common()))
print("per 2 mm square (x from -13.6, y from -6.3; ends counted):", ", ".join("X %.1f..%.1f Y %.1f..%.1f: %d" % (-13.6 + 2 * k[0], -11.6 + 2 * k[0], -6.3 + 2 * k[1], -4.3 + 2 * k[1], v) for k, v in cells.most_common(8)))
