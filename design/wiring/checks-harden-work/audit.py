# Final audit: pulls the claims out of the notes and of the final reply by itself and prints the saved evidence line each one matches.
import glob, os, re, sys
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
W = ROOT + "/design/wiring/checks-harden-work"
files = sys.argv[1:]
logs = {}
for p in glob.glob(W + "/**/*", recursive=True):
    if os.path.isfile(p) and p.endswith((".log", ".md", ".csv", ".txt", ".py", ".json")) and os.path.getsize(p) < 3_000_000 and "/copies/board" not in p:
        try: logs[p] = open(p, encoding="utf-8", errors="replace").read().splitlines()
        except OSError: pass
for p in (ROOT + "/design/wiring/review4-work/fakes-check_wiring.log", ROOT + "/design/wiring/review4-work/fakes-check_joints.log", ROOT + "/design/wiring/review4-work/fakes-check_assembly.log",
          ROOT + "/design/wiring/review4-work/bom-cites-judged.csv"):
    logs[p] = open(p, encoding="utf-8", errors="replace").read().splitlines()
n_claims = n_ok = 0
def find(pat, limit=1):
    out = []
    for p, ls in logs.items():
        if p.endswith("checks-harden-notes.md") or "/final/notes" in p or "/final/reply" in p: continue
        for l in ls:
            if re.search(pat, l):
                out.append((p.replace(ROOT + "/", ""), l.strip()[:150]))
                if len(out) >= limit: return out
    return out
for f in files:
    text = open(f, encoding="utf-8").read()
    print("== audit of", f)
    # 1 paths and file names in backticks
    seen = set()
    for m in re.finditer(r"`([^`\n]+)`", text):
        tok = m.group(1).strip()
        if not re.search(r"\.(log|md|csv|py|json|txt|svg|gbr)\b", tok) or " " in tok or tok in seen or "*" in tok or tok.startswith("-") : continue
        seen.add(tok); n_claims += 1
        path = tok.split(":")[0]
        cands = [path, ROOT + "/" + path, W + "/" + path, ROOT + "/design/" + path, ROOT + "/design/wiring/" + path, ROOT + "/design/mfg/assembly/" + path, W + "/logs/" + path, W + "/final/" + path,
                 ROOT + "/design/wiring/review4-work/" + path, ROOT + "/design/mfg/assembly/joint-table-work/" + path]
        hit = next((c for c in cands if os.path.exists(c)), None)
        n_ok += bool(hit)
        print("PATH %-70s %s" % (tok[:70], "exists" if hit else "NO MATCH"))
    # 2 'N of M' and counts
    for m in re.finditer(r"(\d+) of (\d+)", text):
        n_claims += 1
        pat = r"\b%s of %s\b|ok=%s of %s|%s of %s as expected" % (m.group(1), m.group(2), m.group(1), m.group(2), m.group(1), m.group(2))
        ev = find(pat)
        n_ok += bool(ev)
        print("COUNT %-12s %s" % (m.group(0), ev[0] if ev else "NO MATCH"))
    for m in re.finditer(r"RESULT[ :=][^\n`]{0,80}", text):
        ev = find(re.escape(m.group(0)[:40]))
        print("RESULTLINE %-45s %s" % (m.group(0)[:45], ev[0] if ev else "(quoted in prose; not a log line)"))
print("claims checked: %d, with a matching evidence line or existing file: %d" % (n_claims, n_ok))
