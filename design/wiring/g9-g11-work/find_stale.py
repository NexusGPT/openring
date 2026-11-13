import re, glob
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
pat = re.compile(r"2\.28(?!\d)|2\.42(?!\d)|2\.280|2\.418|0\.138|0\.144|1\.97(?!\d)|1\.9745|2\.277|2\.421")
files = []
for g in ("design/case/*.md", "design/ecad/case/pcb/*.md", "design/ecad/case/*.md", "design/wiring/*.csv", "design/wiring/*.py",
          "design/wiring/*.md", "design/mfg/**/*.md", "design/mfg/**/*.csv", "design/guide*/**/*.md", "design/*.md", "design/*.csv",
          "explorer/**/*.md", "explorer/**/*.csv"):
    files += glob.glob(R + g, recursive=True)
for f in sorted(set(files)):
    if "g9-g11-work" in f:
        continue
    for i, l in enumerate(open(f, errors="replace"), 1):
        for m in pat.finditer(l):
            print("%s:%d: ...%s" % (f[len(R):], i, l[max(0, m.start() - 60):m.end() + 40].strip()))
