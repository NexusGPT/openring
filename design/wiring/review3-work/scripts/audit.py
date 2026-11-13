# review 3 final audit: pulls claims out of wiring-review-3.md by itself and looks each one up in the evidence and the pinned files.
#  - every double-quoted phrase: must occur in a pinned design file or an evidence file
#  - every backticked path: must exist (under ROOT, ROOT/design/..., or the work folder)
#  - every "<file> line(s) N" citation: the line must exist in that file
#  - every number: must occur in some evidence or cited file text
#  - count claims re-run: DRC clean reports, fakes result, check_all result, drawing result, flexdraw label count
import re, os, glob, subprocess, csv
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
W = R + "/design/wiring/review3-work"
REV = R + "/design/wiring/wiring-review-3.md"
text = open(REV).read()
corpus_files = [R + "/design/mfg/assembly/assembly.md", R + "/design/ecad/band/band-interface.md", R + "/design/ecad/case/pcb/board-notes.md",
    R + "/design/case/case-architecture.md", R + "/design/wiring/product-wiring.csv", R + "/design/bom.csv", R + "/design/ecad/ring/pcb/fab/stackup.txt",
    R + "/design/wiring/guide-fix-2-notes.md", R + "/design/wiring/wiring-review-2.md"]
for p in glob.glob(W + "/**/*", recursive=True):
    if os.path.isfile(p) and os.path.getsize(p) < 3_000_000 and not p.endswith(".png") and "/fakes/" not in p: corpus_files.append(p)
corpus = "\n".join(open(p, errors="replace").read() for p in corpus_files)
corpus_flat = re.sub(r"\s+", " ", corpus)
n = 0; bad = []
# quoted phrases
for q in re.findall(r'"([^"]{3,200})"', text):
    n += 1
    if re.sub(r"\s+", " ", q) not in corpus_flat: bad.append("quote not found: " + q)
# backticked paths
for b in re.findall(r"`([^`]+)`", text):
    if "/" not in b and not re.search(r"\.(md|csv|log|txt|pdf|png|py|sh|rpt|gbr|kicad_pcb)$", b): continue
    n += 1
    cands = [b, R + "/" + b, R + "/design/" + b, W + "/" + b, W + "/scripts/" + b, R + "/design/ecad/ring/pcb/" + b, R + "/design/ecad/case/pcb/" + b, R + "/design/ecad/band/" + b, R + "/design/wiring/" + b, R + "/design/case/" + b, R + "/design/mfg/assembly/" + b]
    ok = any(glob.glob(c.split(":")[0].split(" ")[0]) for c in cands)
    if not ok: bad.append("path not found: " + b)
# file line citations: `file` line N / lines N, M and N to M
files = {"assembly.md": R + "/design/mfg/assembly/assembly.md", "band-interface.md": R + "/design/ecad/band/band-interface.md",
         "board-notes.md": R + "/design/ecad/case/pcb/board-notes.md", "case-architecture.md": R + "/design/case/case-architecture.md",
         "stackup.txt": R + "/design/ecad/ring/pcb/fab/stackup.txt", "bom.csv": R + "/design/bom.csv"}
for m in re.finditer(r"`[^`]*?(assembly\.md|band-interface\.md|board-notes\.md|case-architecture\.md|stackup\.txt|bom\.csv)`\s+lines?\s+([0-9 ,andto]+)", text):
    f = files[m.group(1)]; L = open(f, newline="").read().split("\n")
    for k in re.findall(r"\d+", m.group(2)):
        n += 1
        if int(k) > len(L) or not L[int(k) - 1].strip(): bad.append("cited line missing: %s %s" % (m.group(1), k))
# numbers
nums = set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", text))
for x in sorted(nums):
    n += 1
    if x not in corpus: bad.append("number not in evidence: " + x)
# re-run counts
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
drc_v = len([p for p in glob.glob(W + "/drc/*.rpt") if "Found 0 DRC violations" in open(p).read()])
drc_u = len([p for p in glob.glob(W + "/drc/*.rpt") if "Found 0 unconnected pads" in open(p).read()])
print("recount drc reports clean: violations %d, unconnected %d, total %d" % (drc_v, drc_u, len(glob.glob(W + "/drc/*.rpt"))))
print("recount", open(W + "/check_all.log").read().strip().splitlines()[-1])
print("recount", open(W + "/fakes-run.log").read().strip().splitlines()[-1])
print("recount", open(W + "/check_pdf.log").read().strip().splitlines()[-1])
lab = [p for p in glob.glob(W + "/flexdraw/*.txt") if re.search(r"VBAT|VBUS|JOY_|land [0-9]|P\+|NTC", open(p).read())]
print("recount flex drawings with a net or land label: %d of %d" % (len(lab), len(glob.glob(W + "/flexdraw/*.txt"))))
hb = [r["id"] for r in csv.DictReader(open(R + "/design/wiring/product-wiring.csv")) if "hot bar" in r["join_A"]]
print("recount hot bar lines: %d: %s" % (len(hb), " ".join(hb)))
big = []
for s in range(7, 14):
    for r in csv.DictReader(open(W + "/pads/flex2-us%d-pads.csv" % s)):
        if float(r["sx"]) >= 1.5: big.append((s, r["ref"], r["face"]))
print("recount 1.6 mm lands on FLEX2, all sizes: %d, refs %s, faces %s" % (len(big), sorted(set(b[1] for b in big)), sorted(set(b[2] for b in big))))
# counts in the review that must agree with each other
print("review says major/minor/note:", re.findall(r"(\d+) major fault, (\d+) minor faults, (\d+) notes", text))
sev = re.findall(r"^\| G\d+ \| (major|minor|note) \|", text, re.M)
print("table severities: major %d, minor %d, note %d" % (sev.count("major"), sev.count("minor"), sev.count("note")))
p1 = re.findall(r"^\| (F\d|N\d|m3)[^|]*\| (CLOSED|PARTLY CLOSED|OPEN) \|", text, re.M)
print("part 1 rows: %d, closed %d" % (len(p1), sum(1 for x in p1 if x[1] == "CLOSED")))
for b in bad: print("UNMATCHED", b)
print("RESULT audit claims checked=%d unmatched=%d" % (n, len(bad)))
