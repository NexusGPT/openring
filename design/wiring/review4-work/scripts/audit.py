# Final audit: pulls claims out of a text file by itself and prints the evidence each matches.
# usage: audit.py <file>   (the review or the saved reply)
import re, os, sys, glob
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
W = ROOT + "design/wiring/review4-work/"
doc = open(sys.argv[1], encoding="utf-8").read()
BARE = {"assembly.md": "design/mfg/assembly/assembly.md", "hotbar-joint.md": "design/mfg/assembly/hotbar-joint.md",
        "process.md": "design/mfg/assembly/process.md", "board-notes.md": "design/ecad/case/pcb/board-notes.md",
        "band-interface.md": "design/ecad/band/band-interface.md", "lead-decisions.md": "design/wiring/lead-decisions.md",
        "case-architecture.md": "design/case/case-architecture.md", "body-us9.dims.csv": "design/mfg/parts/body/body-us9.dims.csv",
        "joints.csv": "design/mfg/assembly/joints.csv", "bom.csv": "design/bom.csv", "netlist.csv": "design/ecad/ring/netlist.csv", "check_board.py": "design/ecad/ring/pcb/check_board.py"}
n = 0; bad = 0
def show(tag, ok, msg):
    global n, bad
    n += 1
    if not ok: bad += 1
    print("%s %s %s" % ("OK " if ok else "BAD", tag, msg))
logs = []
for p in glob.glob(W + "**/*", recursive=True):
    if os.path.isfile(p) and p.endswith((".log", ".txt", ".csv", ".rpt", ".md")) and os.path.getsize(p) < 3_000_000 and not os.path.basename(p).startswith(("audit", "reply")):
        logs.append(p)
artifacts = [ROOT + v for v in set(BARE.values())] + [ROOT + "design/wiring/product-wiring.csv", ROOT + "design/bom.csv", ROOT + "design/ecad/ring/netlist.csv", ROOT + "design/look/s1/slit-grille-notes.md"]
corpus = {}
for p in logs + artifacts:
    try: corpus[p] = re.sub(r"\s+", " ", open(p, encoding="utf-8", errors="replace").read())
    except Exception as e: pass
# 1 backticked tokens
last_path = None
for tok in re.findall(r"`([^`]+)`", doc):
    t = tok.strip()
    m = re.fullmatch(r"(design/[^\s:]+|[A-Za-z0-9_.\-]+\.(?:md|csv|py)):(\d+)", t)
    if m:
        path = m.group(1); path = BARE.get(path, path); last_path = path; ln = int(m.group(2))
        try:
            L = open(ROOT + path, encoding="utf-8").read().split("\n"); show("cite", ln <= len(L), "%s:%d -> %s" % (path, ln, L[ln - 1][:150] if ln <= len(L) else "PAST END"))
        except Exception as e: show("cite", False, "%s:%d %s" % (path, ln, e))
        continue
    m = re.fullmatch(r":(\d+)", t)
    if m and last_path:
        ln = int(m.group(1)); L = open(ROOT + last_path, encoding="utf-8").read().split("\n")
        show("cite", ln <= len(L), "%s:%d -> %s" % (last_path, ln, L[ln - 1][:150])); continue
    if re.search(r"\.(log|txt|png|rpt|svg)$", t) or t.endswith("/"):
        cands = [W + t] + glob.glob(W + "**/" + os.path.basename(t), recursive=True) + glob.glob(ROOT + "design/**/" + os.path.basename(t), recursive=True)[:1]
        if "*" in t: cands = glob.glob(W + t)
        show("file", any(os.path.exists(c) for c in cands), t)
        continue
    if t.startswith("design/") and not re.search(r"\s", t) and not t.endswith(":N"):
        show("path", os.path.exists(ROOT + t) or bool(glob.glob(ROOT + t)), t); continue
# 2 quoted strings
for q in [x for x in re.findall(r"\"([^\"\n]*)\"", doc) if len(x) >= 12]:
    qq = re.sub(r"\s+", " ", q)
    hit = [p for p, c in corpus.items() if qq in c]
    show("quote", bool(hit), "%r in %s" % (qq[:90], os.path.relpath(hit[0], ROOT) if hit else "NOWHERE"))
# 3 counts "N of M"
for a, b in re.findall(r"(\d+) of (\d+)", doc):
    pat = "%s of %s" % (a, b)
    hit = [p for p, c in corpus.items() if pat in c or ("%s/%s" % (a, b)) in c]
    show("count", bool(hit), "%s seen in %s" % (pat, os.path.relpath(hit[0], ROOT) if hit else "no log with this phrase (check by hand)"))
# 4 last line
lastline = doc.rstrip("\n").split("\n")[-1]
show("lastline", lastline.startswith("RESULT:"), lastline[:120])
print("AUDIT claims=%d without_match=%d" % (n, bad))
