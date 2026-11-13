#!/usr/bin/env python3
"""Compare two dump folders (from dump_boards.py).
usage: python3 compare_dumps.py <dumpA> <dumpB> [--allow-paste-and-text]
Without the flag: every line must be equal (a rebuild must reproduce the board).
With the flag: the copper classes must be equal (PAD, TRACK, VIA, EDGE, NETS, FP placement); differences are allowed only in
  paste layers of pads (PADLAYERS lines whose copper part is equal), new paste-only pads (PAD lines with empty cu), and drawing text or graphics on
  Dwgs.User / Cmts.User (TEXT, DRAW, DIM, FPTEXT). Every difference is listed with its class."""
import os, re, sys

a, b = sys.argv[1], sys.argv[2]
allow = "--allow-paste-and-text" in sys.argv
names = [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]
COPPER = ("PAD", "TRACK", "VIA", "EDGE", "NETS", "FP")
bad = 0
tot = {}
for n in names:
    A = open(os.path.join(a, n + ".dump")).read().splitlines()
    B = open(os.path.join(b, n + ".dump")).read().splitlines()
    gone = sorted(set(A) - set(B)); new = sorted(set(B) - set(A))
    if len(A) != len(set(A)) or len(B) != len(set(B)):
        # multiset compare for duplicates
        from collections import Counter
        ca, cb = Counter(A), Counter(B)
        gone = sorted((ca - cb).elements()); new = sorted((cb - ca).elements())
    ok_n = True
    for kind, lines in (("-", gone), ("+", new)):
        for ln in lines:
            cls = ln.split(" ", 1)[0]
            allowed = False
            if allow:
                if cls == "PAD" and " cu  attr" in ln and kind == "+":
                    allowed = True          # new paste-only (aperture) pad, no copper
                elif cls == "PADLAYERS":
                    allowed = True          # checked below: copper part of each pad unchanged via PAD lines
                elif cls in ("TEXT", "DRAW", "DIM", "FPTEXT") and (" User.Drawings " in ln or " User.Comments " in ln):
                    allowed = True          # drawing layer Dwgs.User (pcbnew prints its user name User.Drawings)
                elif cls == "DRAW" and kind == "+" and (" B.Paste " in ln or " F.Paste " in ln):
                    allowed = True          # new paste opening drawn as a shape on a paste layer
            tot[(cls, kind, allowed)] = tot.get((cls, kind, allowed), 0) + 1
            if not allowed:
                ok_n = False
                print(f"{n} {kind} NOT ALLOWED {ln}")
    # PADLAYERS: compare with paste layers removed
    if allow:
        strip = lambda s: re.sub(r",?[FB]\.Paste", "", s).replace("layers ,", "layers ")
        pa = sorted(strip(x) for x in A if x.startswith("PADLAYERS"))
        pb = sorted(strip(x) for x in B if x.startswith("PADLAYERS") and not re.search(r"layers [FB]\.Paste$", x))
        if pa != pb:
            ok_n = False
            print(f"{n} PADLAYERS differ beyond paste: {sorted(set(pa) ^ set(pb))[:4]}")
    print(f"{n}: {'SAME' if not gone and not new else ('ONLY ALLOWED' if ok_n else 'DIFF')} removed {len(gone)} added {len(new)}")
    bad += 0 if ok_n else 1
for k in sorted(tot):
    print("count", k, tot[k])
print(f"RESULT: {'PASS' if bad == 0 else 'FAIL'} boards compared {len(names)}, boards with a not-allowed difference {bad}, mode {'paste-and-text allowed' if allow else 'identical'}")
sys.exit(0 if bad == 0 else 1)
