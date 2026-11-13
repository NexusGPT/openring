#!/usr/bin/env python3
"""Audit of the final reply: pull every number, quoted text, path and line id out of it by pattern (no hand list),
and print for each the first saved evidence line that holds it. Claims with no match are listed at the end."""
import glob
import os
import re

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = ROOT + "/design/wiring"
reply = open(W + "/wiring-work/final-reply.txt", encoding="utf-8").read()
print("reply characters:", len(reply), "(limit 3500)", "OK" if len(reply) < 3500 else "TOO LONG")

# evidence in this order: saved run outputs first, then the delivered csv files, then sources, the notes last
ev_files = ([W + "/wiring-work/check-final7.log", W + "/wiring-work/check-final7-require.log", W + "/wiring-work/broken-final9.log", W + "/wiring-work/draw-final7.log", W + "/wiring-work/final7-run.time", W + "/wiring-work/contact-test/out-one_out_of_range.csv", W + "/wiring-work/sj-trim.log", ROOT + "/design/case/pin-travel.md", W + "/lead-decisions.md", ROOT + "/design/case/lead-specs.md", W + "/wiring-work/len_cause4.log", ROOT + "/design/ecad/band/band_calc.py", W + "/wiring-work/len_cause4.log", W + "/wiring-work/diff-fields-run8-run9.log",
             W + "/wiring-work/final-facts.log", W + "/wiring-work/final-run.time", W + "/wiring-work/kind-state.log",
             W + "/wiring-work/connections-fieldcount.log", W + "/wiring-work/apply_connections.log",
             W + "/wiring-work/cmp-run5-run6.log", W + "/wiring-work/verify-connections.log"]
            + [W + "/product-wiring.csv", W + "/system-joints.csv",
               ROOT + "/design/case/case-architecture.md", ROOT + "/design/ecad/band/band-interface.md",
               ROOT + "/design/ecad/ring/parts.csv", W + "/build_wiring.py", W + "/check_wiring.py", W + "/draw_wiring.py",
               W + "/connections.md", W + "/product-wiring-notes.md"])
ev = []
for f in ev_files:
    try:
        for i, ln in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            ev.append((f.replace(ROOT + "/", ""), i, ln.rstrip("\n")))
    except IsADirectoryError:
        pass

claims = []
claims += [("quote", q) for q in re.findall(r"`([^`]+)`", reply)]
claims += [("path", q) for q in re.findall(r"\b((?:design/|wiring-work/)?[\w./-]+\.(?:csv|py|svg|pdf|md|log|kicad_pcb))\b", reply)]
claims += [("id", q) for q in re.findall(r"\bW\d{3}\b", reply)]
claims += [("time", q) for q in re.findall(r"\b\d{2}:\d{2}:\d{2}\b", reply)]
claims += [("number", q) for q in re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", reply)]
seen = set()
bad = []
n = 0
for kind, c in claims:
    if (kind, c) in seen:
        continue
    seen.add((kind, c))
    n += 1
    hit = None
    if kind == "path":
        cands = [ROOT + "/" + c, W + "/" + c, W + "/wiring-work/" + os.path.basename(c), ROOT + "/design/ecad/ring/pcb/" + os.path.basename(c),
                 ROOT + "/design/case/" + os.path.basename(c), ROOT + "/design/ecad/band/" + os.path.basename(c),
                 ROOT + "/design/ecad/ring/" + os.path.basename(c)]
        ex = [x for x in cands if os.path.exists(x)]
        hit = ("exists", 0, ex[0].replace(ROOT + "/", "")) if ex else None
    else:
        for f, i, ln in ev:
            if kind == "number" and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(c), ln):
                hit = (f, i, ln)
                break
            if kind != "number" and c in ln:
                hit = (f, i, ln)
                break
    if hit:
        print("OK   %-6s %-40s %s:%s: %s" % (kind, c[:40], hit[0], hit[1], hit[2][:110]))
    else:
        print("NONE %-6s %s" % (kind, c))
        bad.append(c)
print("claims checked:", n, "without a match:", len(bad), bad)
