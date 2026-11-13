#!/usr/bin/env python3
"""Removes the routes of the nets that the router could not separate (negotiation did not converge), so that the board has no rule violation.
Run with KiCad's Python:  run_kipy.sh declash.py <in board> <out board>
Loop: kicad-cli drc; every violation of a copper-to-copper kind names two nets; the net that appears most often has all its tracks and vias deleted (the pads stay,
so the nets come back as unconnected items); repeat until 0 violations.  Writes the list of removed nets to <out board>.removed.txt."""
import collections, os, re, shutil, sys
import pcbnew
import build_boards as BB

src, dst = sys.argv[1], sys.argv[2]
tmp = dst.replace(".kicad_pcb", "_dc.kicad_pcb")
shutil.copy(src.replace(".kicad_pcb", ".kicad_pro"), tmp.replace(".kicad_pcb", ".kicad_pro"))
KINDS = {"tracks_crossing", "clearance", "shorting_items", "hole_clearance", "hole_to_hole", "track_width", "connection_width", "via_diameter", "copper_edge_clearance", "annular_width"}
b = pcbnew.LoadBoard(src)
removed = []
for rnd in range(60):
    BB.fill_all(b)
    pcbnew.SaveBoard(tmp, b)
    b = pcbnew.LoadBoard(tmp)      # reload: removing items leaves stale pointers in the python wrappers
    rc, nv, nu, rep = BB.drc(tmp, tmp + ".json")
    cnt = collections.Counter()
    other = 0
    for v in rep["violations"]:
        if v["type"] not in KINDS:
            other += 1
            continue
        nets = set()
        for it in v["items"]:
            m = re.search(r"\[([^\]]+)\]", it["description"])
            if m and m.group(1) != "GND" and not it["description"].startswith("Pad"):
                nets.add(m.group(1))
        for n in nets:
            cnt[n] += 1
    print("round %d: violations %d (other kinds %d), unconnected %d, removed so far %d" % (rnd, nv, other, nu, len(removed)))
    if not cnt:
        break
    worst = cnt.most_common(1)[0][0]
    n_del = 0
    victims = [t for t in b.GetTracks() if t.GetNetname() == worst]
    for t in victims:
        b.RemoveNative(t)
        n_del += 1
    removed.append(worst)
    print("  removed the routes of net %s (%d tracks and vias)" % (worst, n_del))
BB.fill_all(b)
pcbnew.SaveBoard(dst, b)
shutil.copy(src.replace(".kicad_pcb", ".kicad_pro"), dst.replace(".kicad_pcb", ".kicad_pro"))
open(dst + ".removed.txt", "w").write("\n".join(removed) + "\n")
print("removed nets:", removed)
