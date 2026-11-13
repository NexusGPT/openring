import sys
W = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/case-proc-work/")
ok = True
for t in ("pins", "main"):
    b = open(W + "dump_before_%s.log" % t).read().split("\n")
    a = open(W + "dump_after_%s.log" % t).read().split("\n")
    kb = {k: sorted(l for l in b if l.startswith(k)) for k in ("PAD", "TRK", "ZONE")}
    ka = {k: sorted(l for l in a if l.startswith(k)) for k in ("PAD", "TRK", "ZONE")}
    eb = sorted(l for l in b if l.startswith("DRAW") and "Edge.Cuts" in l)
    ea = sorted(l for l in a if l.startswith("DRAW") and "Edge.Cuts" in l)
    same = kb == ka and eb == ea
    ok = ok and same
    print(t, "pads", len(ka["PAD"]), "trk", len(ka["TRK"]), "zones", len(ka["ZONE"]), "edge", len(ea), "IDENTICAL" if same else "DIFFERENT")
print("CU IDENTICAL both boards" if ok else "CU DIFFERENT")
