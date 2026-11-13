import re, sys
log = open(sys.argv[1]).read()
checks = [
    ("hand-end wall gap 0.225", r"hand-end wall \(-X\): gap 0\.225 mm"),
    ("thumb wall gap 0.45", r"thumb-side wall \(\+Y\): gap 0\.450 mm"),
    ("floor gap 0.05", r"floor \(-Z\): gap 0\.050 mm"),
    ("floor metal 0.40 (any ray)", r"floor \(-Z\): body metal at 0\.050 to 0\.050 from the antenna face; metal thickness on these rays 0\.\d+ to 0\.400"),
    ("-Y first thing J1 housing at 0.2", r"screen_connector__polymer \(part metal flag True\) at 0\.200"),
    ("panel covers footprint fully", r"screen__screen: .*overlap with the antenna footprint 5\.120 of 5\.120"),
    ("lit area does not cover", r"screen__mark: .*overlap with the antenna footprint 0\.000 of 5\.120"),
    ("driver IC over part", r"screen__chip: .*overlap with the antenna footprint 0\.[1-9]\d* of 5\.120"),
    ("no board over antenna on the up rays", None),
    ("adhesive 0.1 on up rays", r"clear_adhesive__polymer \(layer glass, part metal flag False\) 0\.100"),
    ("last line RESULT measured", r"RESULT measured\s*$"),
]
bad = 0
for name, pat in checks:
    if pat is None:
        sec = log.split("== 2.")[1].split("== 3.")[0]
        ok = "main_board" not in sec
    else:
        ok = re.search(pat, log) is not None
    print(("MATCH   " if ok else "DIFFERS ") + name)
    bad += not ok
print("cases differing from expectation:", bad, "of", len(checks))
