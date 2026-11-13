#!/usr/bin/env python3
"""Compare two fab folders: every Gerber, drill and job file of folder A against B with date lines removed; drawings by rendered pixels.
usage: compare_fab.py <fabA> <fabB> <workdir for renders> [--no-render]
A file present in B and not in A (a new paste Gerber, a notes file) is listed as NEW. Gerber order of objects may differ: the
compare is on the sorted set of lines (plus an exact-order flag)."""
import os, re, subprocess, sys

A, B, T = sys.argv[1:4]
os.makedirs(T, exist_ok=True)
DATE = re.compile(r"CreationDate|date \d{4}-|^; DRILL file|\"CreationDate\"")
names = [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]
nd = 0
for n in names:
    fa, fb = sorted(os.listdir(os.path.join(A, n))), sorted(os.listdir(os.path.join(B, n)))
    for f in fb:
        if f not in fa:
            print(f"{n}/{f}: NEW in B")
    for f in fa:
        if f not in fb:
            print(f"{n}/{f}: MISSING in B"); nd += 1; continue
        la = [l for l in open(os.path.join(A, n, f)).read().splitlines() if not DATE.search(l)]
        lb = [l for l in open(os.path.join(B, n, f)).read().splitlines() if not DATE.search(l)]
        same_order = la == lb
        same_set = sorted(la) == sorted(lb)
        if not same_set and f.endswith(".gbr"):
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import gerber_norm
            oa, ob = gerber_norm.objects(os.path.join(A, n, f)), gerber_norm.objects(os.path.join(B, n, f))
            if oa == ob:
                print(f"{n}/{f}: same geometry ({len(oa)} objects; aperture numbers or order differ)")
            else:
                nd += 1
                print(f"{n}/{f}: GEOMETRY DIFF {len(oa)} vs {len(ob)} objects, e.g. {sorted(set(oa) ^ set(ob))[:3]}")
        elif not same_set and f.endswith(".gbrjob") and all("Paste" in l or l.strip() in ("{", "},", "}") for l in set(la) ^ set(lb)):
            print(f"{n}/{f}: differs only by the paste layer entry: {sorted(set(la) ^ set(lb))}")
        elif not same_set:
            nd += 1
            diff = sorted(set(la) ^ set(lb))
            print(f"{n}/{f}: DIFF {len(diff)} lines, e.g. {diff[:3]}")
        else:
            print(f"{n}/{f}: same lines ({'same order' if same_order else 'other order'})")
    if "--no-render" in sys.argv:
        continue
    for side, root in (("a", A), ("b", B)):
        subprocess.run(["pdftoppm", "-r", "100", os.path.join(root, n + "-drawing.pdf"), os.path.join(T, f"{n}-{side}")], check=True)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ppmdiff.py"),
                        os.path.join(T, f"{n}-a-1.ppm"), os.path.join(T, f"{n}-b-1.ppm")], capture_output=True, text=True)
    print(f"{n}-drawing.pdf: {r.stdout.strip()}")
print(f"RESULT: boards {len(names)}, Gerber/drill/job files differing {nd}")
