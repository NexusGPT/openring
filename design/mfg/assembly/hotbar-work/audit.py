"""Final audit of hotbar-joint.md (and the final reply): pulls the claims out of the text by itself and prints the evidence each matches.
usage: python3 -I audit.py <ROOT> <text file> [<text file> ...]
Checks, per text file:
 1. every citation `file` line N / lines N to M / N and M / file:N: the file exists, the lines exist; each quoted phrase of the
    same sentence is found on one of the cited lines (whitespace folded, '...' splits a quote into parts);
 2. every decimal number: found in a WORK log or dump, in a cited source file, or in the fixture values log; else listed UNMATCHED;
 3. no em dash or en dash; 4. the RESULT line is the last line (hotbar-joint.md only);
 5. pairs of statements that disagree: the same named quantity with two different values (a fixed list of names, found by regex).
"""
import os, re, sys, glob

ROOT = sys.argv[1]
WORK = os.path.join(ROOT, "design/mfg/assembly/hotbar-work")
index = {}
for dp, dn, fn in os.walk(os.path.join(ROOT, "design")):
    if "/out" in dp or "/.venv" in dp or "/node_modules" in dp:
        continue
    for f in fn:
        index.setdefault(f, []).append(os.path.join(dp, f))


def resolve(name):
    if name.startswith("WORK/"):
        return os.path.join(WORK, name[5:])
    full = os.path.join(ROOT, name)
    if os.path.exists(full):
        return full
    base = os.path.basename(name)
    cands = [c for c in index.get(base, []) if c.endswith(name)]
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        pref = [c for c in cands if "work" not in c.split("/design/")[-1]]
        return pref[0] if pref else cands[0]
    return None


evidence_text = ""
for pat in ("logs/*", "dumps/*", "planted/*.log", "planted/plant.diff"):
    for f in glob.glob(os.path.join(WORK, pat)):
        if f.endswith(".png"):
            continue
        try:
            evidence_text += open(f, errors="replace").read() + "\n"
        except IsADirectoryError:
            pass

total = 0
bad = 0
for tf in sys.argv[2:]:
    text = open(tf).read()
    print(f"==== {tf}")
    cited_files = set()
    sentences = re.split(r"(?<=[.;:])\s+(?=[A-Z(*`\[])|\n", text)
    cit_re = re.compile(r"`([\w./-]+\.(?:md|py|csv|txt|log|pdf|kicad_pcb|gbr))`(?:,? (?:line|lines) (\d+)(?: (?:to|and) (\d+))?)?|`([\w./-]+\.(?:md|py|csv|txt)):(\d+)`")
    for s in sentences:
        cits = []
        last_path = None
        for m in cit_re.finditer(s):
            name = m.group(1) or m.group(4)
            a = m.group(2) or m.group(5)
            b = m.group(3)
            path = resolve(name)
            total += 1
            if path is None or not os.path.exists(path):
                print(f"MISSING FILE {name}")
                bad += 1
                continue
            cited_files.add(path)
            if a:
                lines = open(path, errors="replace").read().split("\n")
                lo, hi = int(a), int(b or a)
                if b and m.group(0).find(" and ") >= 0:
                    rng = [lo, hi]
                else:
                    rng = list(range(lo, hi + 1))
                if max(rng) > len(lines):
                    print(f"LINE OUT OF RANGE {name}:{a}-{b} (file has {len(lines)})")
                    bad += 1
                    continue
                cits.append((name, rng, [lines[i - 1] for i in rng]))
                print(f"CIT {name}:{a}{'-' + b if b else ''} -> {lines[lo - 1].strip()[:110]}")
            else:
                print(f"CIT {name} (file) exists")
                if not path.endswith(".pdf"):
                    cits.append((name, [0], [open(path, errors="replace").read()]))
            last_path = (name, path)
        # a bare "(line N)" or "line N" after a cited file in the same sentence belongs to that file
        for m in re.finditer(r"(?<![`\w])\(?line (\d+)\)?", s):
            if cits and last_path and last_path[1] and not last_path[1].endswith(".pdf"):
                pre = s[max(0, m.start() - 3):m.start()]
                if "`" in pre:
                    continue
                lines = open(last_path[1], errors="replace").read().split("\n")
                n = int(m.group(1))
                if n <= len(lines):
                    cits.append((last_path[0], [n], [lines[n - 1]]))
                    total += 1
                    print(f"CIT {last_path[0]}:{n} (bare) -> {lines[n - 1].strip()[:110]}")
        for q in re.findall(r'"([^"]{6,})"', s):
            if not cits:
                continue
            parts = [p.strip(" .,") for p in q.split("...") if p.strip(" .,")]
            norm = lambda t: re.sub(r"\s+", " ", t).lower()
            ok = all(any(norm(p) in norm(" ".join(l for l in c[2])) for c in cits) for p in parts)
            total += 1
            if ok:
                print(f'QUOTE OK "{q[:70]}"')
            else:
                print(f'QUOTE NOT ON CITED LINES "{q[:90]}" cited {[(c[0], c[1][0]) for c in cits]}')
                bad += 1
    src_text = evidence_text + "".join(open(p, errors="replace").read() for p in cited_files if not p.endswith(".pdf"))
    nums = sorted(set(re.findall(r"(?<![\w.])-?\d+\.\d+", text)))
    unmatched = []
    for n in nums:
        total += 1
        variants = {n, n.lstrip("-"), n.rstrip("0").rstrip(".") if "." in n else n}
        if any(v and v in src_text for v in variants):
            continue
        unmatched.append(n)
    print(f"NUMBERS {len(nums)} decimal numbers; matched in evidence or cited files {len(nums) - len(unmatched)}; UNMATCHED {len(unmatched)}: {' '.join(unmatched)}")
    dashes = [i + 1 for i, l in enumerate(text.split("\n")) if "—" in l or "–" in l]
    total += 1
    print(f"DASHES lines with an em or en dash: {dashes if dashes else 'none'}")
    bad += bool(dashes)
    if tf.endswith("hotbar-joint.md"):
        last = text.rstrip("\n").split("\n")[-1]
        total += 1
        print(f"LAST LINE is RESULT: {last.startswith('RESULT: ')}")
        bad += not last.startswith("RESULT: ")
    # disagreement check: named quantities
    for name, rx in (("foot width", r"foot (?:is )?(\d\.\d+) (?:mm )?wide|foot (\d\.\d+) against"), ("slot width", r"slot (?:is )?(\d\.\d+)|against slot (\d\.\d+)"),
                     ("stiffener gap", r"(0\.7\d0) mm"), ("J1 distance", r"J1(?:'s body)?[^.]{0,40}?(0\.5\d0) mm"), ("free length", r"free (?:ribbon )?length (?:of )?([+-]?\d\.\d+)")):
        keep = " ".join(x for x in re.split(r"(?<=[.])\s+", text) if not any(w in x for w in ("planted", "copy", "option D", "Option D", "D1.", "D2.", "D3.", "D4.", "D5.", "D6.", "1.8 mm foot", "1.800")))
        vals = set(float(v) for t in re.findall(rx, keep) for v in (t if isinstance(t, tuple) else (t,)) if v)
        total += 1
        print(f"AGREE {name}: values {sorted(vals)} -> {'one value' if len(vals) <= 1 else 'DISAGREE'}")
        bad += len(vals) > 1
print(f"AUDIT claims checked {total}; problems {bad}")
