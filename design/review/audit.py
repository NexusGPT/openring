"""Final audit: pull every quoted claim and citation out of design-review-1.md and reply.md by itself,
and print the evidence line each matches; then re-derive every count. Read-only on the design."""
import os, re, csv, glob, subprocess
R = (__import__("pathlib").Path(__file__).resolve().parents[2].as_posix())
O = R + "/design/review"
docs = {"design-review-1.md": open(O + "/design-review-1.md", encoding="utf-8").read(),
        "reply.md": open(O + "/reply.md", encoding="utf-8").read()}

# basename map for short citations in the reply
base = {}
for p in glob.glob(R + "/design/**/*", recursive=True):
    if os.path.isfile(p) and "/.venv/" not in p and "/node_modules/" not in p:
        base.setdefault(os.path.basename(p), []).append(p)
base.setdefault("requirements.md", []).append(R + "/requirements.md")

def resolve(path):
    if path.startswith("/"):
        return path if os.path.exists(path) else None
    for cand in (R + "/" + path, O + "/" + path):
        if os.path.exists(cand):
            return cand
    b = os.path.basename(path)
    hits = [h for h in base.get(b, []) if h.endswith(path)]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        pref = [h for h in hits if "/design/review/fakes/" not in h and "/evidence/" not in h and "/out/" not in h]
        return pref[0] if len(pref) == 1 else None
    return None

cite_re = re.compile(r"`([A-Za-z0-9_./\-]+\.(?:md|csv|log|txt|py|json))(?::(\d+))?`")
quote_re = re.compile(r'"([^"\n]+)"')
total = ok = bad = 0
owner_file = open(R + "/requirements.md", encoding="utf-8").read()
for dname, text in docs.items():
    last = None
    pos = 0
    for m in quote_re.finditer(text):
        gap = text[pos:m.start()]
        pos = m.end()
        cites = list(cite_re.finditer(gap))
        if cites:
            c = cites[-1]
            last = (c.group(1), c.group(2))
        elif "same line" in gap and last:
            pass
        else:
            last_use = None
        q = m.group(1).replace("\\|", "|")
        total += 1
        if not cites and "same line" not in gap:
            # owner or brief quote, or a label: look in requirements.md and the review folder logs
            where = "requirements.md" if q in owner_file else None
            if where is None:
                for lp in glob.glob(O + "/*.log") + glob.glob(O + "/*.txt"):
                    if q in open(lp, encoding="utf-8", errors="replace").read():
                        where = os.path.basename(lp); break
            if where:
                ok += 1; print(f"OK   [{dname}] uncited quote found in {where}: {q[:70]}")
            else:
                print(f"NOTE [{dname}] uncited quote, no file match (owner words from the brief, or my own label): {q[:90]}")
            continue
        path, line = last
        fp = resolve(path)
        if not fp:
            bad += 1; print(f"BAD  [{dname}] cannot resolve {path}"); continue
        lines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
        if line:
            n = int(line)
            src = lines[n - 1] if 0 < n <= len(lines) else ""
            hit = q in src
            where = f"{path}:{n}"
        else:
            hit = any(q in l for l in lines)
            where = path
            if not hit and path.endswith(".log"):
                hit = any(q.replace("|", "\\|") in l for l in lines)
        if hit:
            ok += 1; print(f"OK   [{dname}] {where}: {q[:80]}")
        else:
            bad += 1; print(f"BAD  [{dname}] {where}: quote not on that line: {q[:80]}")
# bare citations (file:line with no quote): line exists
for dname, text in docs.items():
    for c in cite_re.finditer(text):
        if c.group(2):
            fp = resolve(c.group(1))
            total += 1
            if fp and int(c.group(2)) <= len(open(fp, encoding="utf-8", errors="replace").read().splitlines()):
                ok += 1
            else:
                bad += 1; print(f"BAD  [{dname}] citation does not open: {c.group(1)}:{c.group(2)}")

print("== counts re-derived")
rv = docs["design-review-1.md"]
rows = re.findall(r"^\| (F\d\d) \| (S[123]) \|", rv, re.M)
sev = {s: [f for f, x in rows if x == s] for s in ("S1", "S2", "S3")}
print("findings", len(rows), {k: len(v) for k, v in sev.items()})
print("S1 ids", sev["S1"]); print("S2 ids", sev["S2"]); print("S3 ids", sev["S3"])
ks = re.findall(r"^\| (K\d+) \|", rv, re.M)
print("contradictions", len(ks), ks[0], ks[-1])
verd = re.findall(r"^\| ([^|]+) \| (not buildable as written|buildable with the listed answers|buildable as written) \|", rv, re.M)
print("verdict rows", len(verd), "not buildable:", sum(1 for a, v in verd if v == "not buildable as written"))
print("not buildable areas:", [a for a, v in verd if v == "not buildable as written"])
total += 4
for claim, val in (("S1 4", len(sev["S1"]) == 4), ("S2 12", len(sev["S2"]) == 12), ("S3 14", len(sev["S3"]) == 14), ("22 contradictions", len(ks) == 22)):
    print(("OK   " if val else "BAD  ") + "count " + claim); ok += val; bad += (not val)
for dname, text in docs.items():
    endl = text.strip().splitlines()[-1]
    print(f"end line [{dname}]: {endl}")
print("reply characters:", len(docs["reply.md"]))
print("== numeric claims in the reply, with their evidence")
pc = open(O + "/probe_chains.log").read().splitlines()
print("0.225:", [l for l in pc if "0.225" in l])
print("joystick overlap > 0 at:", [l.split(":")[0].strip() for l in pc if "joystick switch edge" in l and "overlap  0.0 deg)  ribbon" not in l])
print("slot overlap > 0 at:", [l.split(":")[0].strip() for l in pc if "ribbon slot" in l and not l.rstrip().endswith("overlap  0.0 deg)")])
at = open(O + "/attack_fwcheck.log").read().splitlines()
fakes = [l for l in at if " | " in l and not l.startswith("case")]
print("attack rows:", len(fakes), "faulty copies:", len(fakes) - 1, "caught:", sum(1 for l in fakes[1:] if l.split(" | ")[2] == "1"))
for f in ("check_bom.log", "check_netlist.log", "firmware_check.log", "check_docs.log"):
    print(f, "last line:", open(O + "/" + f).read().strip().splitlines()[-1])
print("git status of review folder:")
print(subprocess.run(["git", "-C", R, "status", "--short", "--ignored", O], capture_output=True, text=True).stdout)
print(f"CLAIMS CHECKED: {total}, matched {ok}, unmatched {bad}")
