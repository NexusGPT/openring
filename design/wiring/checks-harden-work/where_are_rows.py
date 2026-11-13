# For each citation the check rejects (TOKEN lines of a log), finds the row of the cited csv whose key cell holds the first named token,
# so the owner can see the moved row. Reads only; prints guide line, cited line, token, line(s) where the token is the row key.
import csv, re, sys
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
log = sys.argv[1]
n = 0; found = 0
for l in open(log, encoding="utf-8"):
    m = re.match(r"TOKEN line (\d+): (\S+):(\d+) holds none of (.*?) \(it holds: ", l)
    if not m: continue
    n += 1
    gl, path, ln, toks = int(m.group(1)), m.group(2), int(m.group(3)), [t.strip() for t in m.group(4).split(",")]
    lines = open(ROOT + path, encoding="utf-8", errors="replace").read().splitlines()
    hdr = next(csv.reader([lines[0]]))
    keycols = [i for i, h in enumerate(hdr) if re.fullmatch(r"(?i)ref|reference|part|item|net|name|\w+_ref", h.strip())]
    hits = {}
    for i, raw in enumerate(lines[1:], 2):
        row = next(csv.reader([raw]), [])
        keys = set(re.split(r"[\s,;]+", " , ".join(row[j] for j in keycols if j < len(row))))
        for t in toks:
            if t in keys: hits.setdefault(t, []).append(i)
    first = [(t, hits[t]) for t in toks if t in hits]
    found += bool(first)
    print("guide line %d: %s:%d is not the row of %s; the key cell holds %s at line(s) %s" % (gl, path, ln, ", ".join(toks[:4]), first[0][0] if first else "-", first[0][1][:3] if first else "(not found by key cell)"))
print("REJECTED %d, of which the named token is a row key elsewhere in the same file: %d" % (n, found))
