# audit.py G : pull claims from logs/final-reply.txt and notes.md by pattern (backtick quotes, numbers, cited logs) and find each in the saved logs
import os, re, sys, glob, hashlib, subprocess
G = sys.argv[1]; L = os.path.join(G, "logs")
corpus = {}
for f in sorted(glob.glob(L + "/**/*", recursive=True)):
    if os.path.isfile(f) and not f.endswith((".png", ".json")) and "final-reply" not in f and "audit" not in os.path.basename(f):
        try: corpus[f] = open(f, errors="replace").read().splitlines()
        except Exception: pass
for extra in ((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/specs/screen-panel-work/logs/read_board2.log"),):
    corpus[extra] = open(extra).read().splitlines()
def find(s, files=None):
    for f in (files or corpus):
        for i, ln in enumerate(corpus.get(f, [])):
            if s in ln: return "%s:%d" % (os.path.relpath(f, G), i + 1)
    return None
checked = 0; miss = []
reply = open(os.path.join(L, "final-reply.txt")).read()
print("== reply: backtick quotes")
for q in re.findall(r"`([^`]+)`", reply):
    if q.startswith("design/"): ok = os.path.exists(os.path.join((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix()), q)) and "path exists"
    else: ok = find(q)
    checked += 1; print("%-70s %s" % (q[:70], ok)); ok or miss.append(q)
print("== reply: numbers")
for q in sorted(set(re.findall(r"(?<![\w.])-?\d+\.\d+|(?<![\w.-])\d+(?![\w.])", reply))):
    ok = find(q); checked += 1; print("%-12s %s" % (q, ok)); ok or miss.append(q)
print("== reply: cited files exist")
for q in sorted(set(re.findall(r"logs/[\w./-]+\.(?:log|txt)", reply))):
    ok = os.path.exists(os.path.join(G, q)); checked += 1; print(q, ok); ok or miss.append(q)
print("== notes: each backtick quote on a line that cites logs/ is in one of the cited logs")
for n, ln in enumerate(open(os.path.join(G, "notes.md")).read().splitlines(), 1):
    cites = [os.path.join(G, c) for c in re.findall(r"`?(logs/[\w./-]+\.(?:log|txt|list))`?", ln)]
    if not cites: continue
    for c in cites:
        if not os.path.exists(c): miss.append("notes line %d cites missing %s" % (n, c)); print("MISSING FILE", n, c)
        elif c not in corpus: corpus[c] = open(c, errors="replace").read().splitlines()
    for q in re.findall(r"`([^`]+)`", ln):
        if q.startswith(("logs/", "scripts/", "pcb/", "steps/", "broken/", "design/", "nice ", "kicad-cli", "placement", "b.", "work.", "ring-thin", "ring.kicad", "--")) or q.endswith((".kicad_pcb", ".py", ".sh", ".txt", ".csv")): continue
        ok = find(q, cites) or find(q); checked += 1
        print("notes %3d %-60s %s" % (n, q[:60], ok)); ok or miss.append("notes %d: %s" % (n, q))
print("== counts re-run")
steps = sorted(os.listdir(os.path.join(G, "steps"))); print("step boards", len(steps), steps); checked += 1
print("du", subprocess.run(["du", "-sh", G], capture_output=True, text=True).stdout.strip()); checked += 1
base = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/ring/pcb/ring.kicad_pcb")
h = hashlib.sha256(open(base, "rb").read()).hexdigest(); same = h in open(os.path.join(L, "base-copy-sha.log")).read()
print("base board sha256 now", h[:16], "same as at copy:", same); checked += 1; same or miss.append("base sha")
fin = hashlib.sha256(open(os.path.join(G, "pcb/ring-thin-a1.kicad_pcb"), "rb").read()).hexdigest(); g3 = hashlib.sha256(open(os.path.join(G, "steps/g03-route-projfill.kicad_pcb"), "rb").read()).hexdigest()
print("final board equals g03:", fin == g3, fin[:16]); checked += 1; (fin == g3) or miss.append("final != g03")
print("claims checked", checked, "unmatched", len(miss)); [print("UNMATCHED", m) for m in miss]
