import re, glob
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/")
FILES = [R+"architecture.md"] + [f for f in sorted(glob.glob(R+"mfg/specs/*.md")) if not f.endswith("/cell.md")] + [R+"mfg/assembly/assembly.md", R+"mfg/parts-notes.md", R+"mech/mic-path/mic-path.md", R+"supplier-package/v3-notes.md"]
P = re.compile(r"fold pocket|screen cable|S27|block height|3\.20 mm|3\.2 mm|cable route|screen's cable|the cable fold|foam frame", re.I)
for f in FILES:
    for i, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        m = P.search(line)
        if m:
            s = max(0, m.start()-50); e = min(len(line), m.end()+60)
            print(f"{f.replace(R,'design/')}:{i} | {line[s:e].strip()}")
