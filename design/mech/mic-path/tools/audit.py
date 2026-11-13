#!/usr/bin/env python3
"""Final audit of mic-path.md and the final reply. Pulls claims out of the files by pattern (not from a hand list):
numbers, check.log tags, quoted strings, file-and-line citations; prints the evidence each matches, or NO MATCH.
Also: em dash count, last line of mic-path.md, reply length."""
import re
import sys
from pathlib import Path

D = Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design"))
M = D / "mech/mic-path"
DOCS = [M / "mic-path.md", M / "evidence/final-reply.md"]
CORPUS = {
    "check.log": M / "check.log", "acoustic.log": M / "acoustic.log", "board-conflicts.log": M / "board-conflicts.log",
    "spk0641": M / "datasheets/knowles-spk0641ht4h-1_chipsmall.txt", "spk0838": M / "datasheets/knowles-spk0838ht4h-b_eicom.txt",
    "gettop": M / "datasheets/gettop-wd-gfa261-h10f_szlcsc.txt", "pui": M / "datasheets/pui-wideband-mems-app-guide.txt",
    "im68d128b-brief.txt": D / "datasheets/mic-research/im68d128b-brief.txt", "placement.csv": D / "mech/thin/placement.csv",
    "architecture.md": D / "architecture.md", "bom.csv": D / "bom.csv", "thin.py": D / "mech/thin/thin.py",
    "check_thin.py": D / "mech/thin/check_thin.py", "thin-notes.md": D / "mech/thin/thin-notes.md",
    "research": D / "parts/research-microphone-port.md", "sch-notes.md": D / "ecad/ring/sch-notes.md",
    "exterior.py": D / "look/s1/exterior.py", "firmware.md": D / "firmware.md", "bench-plan.md": D / "bench/bench-plan.md",
    "make_netlist.py": D / "ecad/ring/make_netlist.py", "parts.csv": D / "ecad/ring/parts.csv", "check_netlist.py": D / "ecad/ring/check_netlist.py",
    "build_board.py": D / "ecad/ring/pcb/build_board.py", "check_board.py": D / "ecad/ring/pcb/check_board.py",
    "check_mic_path.py": M / "check_mic_path.py", "acoustic_estimates.py": M / "acoustic_estimates.py",
    "ingress-search.log": M / "evidence/ingress-search.log", "check-final-exit.log": M / "evidence/check-final-exit.log",
    "render.log": M / "evidence/pages/render.log", "review": D.parent / "_review/design-review-1.md",
}
TEXT = {k: open(p, newline="", errors="replace").read() for k, p in CORPUS.items()}
LINES = {k: t.split("\n") for k, t in TEXT.items()}
FILEKEY = {"check.log": "check.log", "acoustic.log": "acoustic.log", "placement.csv": "placement.csv", "architecture.md": "architecture.md",
           "bom.csv": "bom.csv", "thin.py": "thin.py", "check_thin.py": "check_thin.py", "thin-notes.md": "thin-notes.md",
           "sch-notes.md": "sch-notes.md", "exterior.py": "exterior.py", "firmware.md": "firmware.md", "bench-plan.md": "bench-plan.md",
           "make_netlist.py": "make_netlist.py", "parts.csv": "parts.csv", "check_netlist.py": "check_netlist.py", "build_board.py": "build_board.py",
           "check_board.py": "check_board.py", "im68d128b-brief.txt": "im68d128b-brief.txt", "knowles-spk0641ht4h-1_chipsmall.txt": "spk0641",
           "knowles-spk0838ht4h-b_eicom.txt": "spk0838", "gettop-wd-gfa261-h10f_szlcsc.txt": "gettop", "PUI guide": "pui"}

total = 0
nomatch = []
for doc in DOCS:
    s = doc.read_text()
    print(f"==== {doc}")
    # 1 check.log tags
    for tag in sorted(set(re.findall(r"\bC\d\d[w]?(?:\.[A-Za-z0-9_.]+)?", s))):
        total += 1
        base = tag.split(".")[0]
        hits = [l for l in LINES["check.log"] if l.startswith(base)]
        print(f"TAG {tag}: {len(hits)} check.log lines" + ("" if hits else "  NO MATCH"))
        if not hits:
            nomatch.append(("tag", tag))
    # 2 quotes
    for q in re.findall(r"\"([^\"]{6,})\"", s):
        total += 1
        qn = q.replace("≥", "≥").strip()
        where = [k for k, t in TEXT.items() if qn in t]
        if not where:
            # try with whitespace collapsed
            where = [k for k, t in TEXT.items() if " ".join(qn.split()) in " ".join(t.split())]
        print(f"QUOTE \"{q[:70]}\": {where[:4] if where else 'NO MATCH'}")
        if not where:
            nomatch.append(("quote", q))
    # 3 citations: <file> line N / lines N to M
    for m in re.finditer(r"`?([\w./-]+\.(?:md|csv|py|txt|log))`?,? (?:text )?lines? (\d+)(?: (?:to|and) (\d+))?", s):
        f, a, b = m.group(1).split("/")[-1], int(m.group(2)), m.group(3)
        key = FILEKEY.get(f)
        total += 1
        if key is None:
            print(f"CITE {f} line {a}: file not in corpus (check by hand)")
            continue
        ls = LINES[key]
        rng = range(a, (int(b) if b else a) + 1)
        if " and " in m.group(0):
            rng = [a, int(b)]
        shown = " | ".join(ls[i - 1][:90].strip() for i in rng if 0 < i <= len(ls))
        print(f"CITE {f} {list(rng)}: {shown if shown else 'LINE OUT OF RANGE'}")
        if not shown:
            nomatch.append(("cite", m.group(0)))
    # 3b bare "text line N" (the SPK0641HT4H-1 copy) and "PUI guide lines N"
    for m in re.finditer(r"(text|PUI guide(?: text)?) lines? (\d+)(?: to (\d+))?", s):
        key = "spk0641" if m.group(1) == "text" else "pui"
        a, b = int(m.group(2)), m.group(3)
        total += 1
        ls = LINES[key]
        shown = " | ".join(ls[i - 1][:90].strip() for i in range(a, (int(b) if b else a) + 1) if 0 < i <= len(ls))
        print(f"CITE {key} {a}{'-' + b if b else ''}: {shown if shown else 'LINE OUT OF RANGE'}")
        if not shown:
            nomatch.append(("cite", m.group(0)))
    # 4 numbers
    nums = re.findall(r"(?<![\w.])-?\d+\.\d+|(?<![\w.])\d{2,}(?![\w.])", s)
    allt = "\n".join(TEXT.values())
    miss = sorted(set(n for n in nums if n.lstrip("-") not in allt))
    total += len(set(nums))
    print(f"NUMBERS: {len(set(nums))} distinct; not found verbatim in any evidence or source file: {miss}")
    for n in miss:
        nomatch.append(("number", n))
    # 5 style
    print(f"EM DASHES: {s.count(chr(0x2014))}; EN DASHES: {s.count(chr(0x2013))}")
for f in M.rglob("*"):
    if f.suffix in (".md", ".py") and f.is_file():
        c = f.read_text(errors="replace").count(chr(0x2014))
        if c:
            print(f"EM DASH in {f}: {c}")
print("LAST LINE of mic-path.md:", DOCS[0].read_text().rstrip().splitlines()[-1][:120])
print("REPLY length:", len(DOCS[1].read_text()), "characters (limit 3500)")
print("CHECK last line:", LINES["check.log"][-1])
print(f"claims checked: {total}; with no match: {len(nomatch)}")
md = DOCS[0].read_text()
def why(k, v):
    if k == "tag" and ("C31, C32" in md or "C35, C36" in md) and v in ("C31", "C32", "C35", "C36"):
        return "capacitor designator, not a check tag"
    if k == "quote" and ("..." in v or v[:1] in ":,]" or "\n" in v):
        return "shortened present text (marked with ...) or a parse across backticked code; the cited line is printed in a CITE row"
    if k == "number":
        i = md.find(v)
        ctx = md[max(0, i - 120): i + 60]
        if "[CALC" in ctx or "page image" in ctx or "line" in ctx:
            return "derived ([CALC] in its sentence), read from a page image, or a line number whose CITE row is printed"
    return None
left = 0
for k, v in nomatch:
    w = why(k, v)
    if w is None:
        left += 1
    print("NO MATCH", k, v[:120], "->", w or "UNEXPLAINED")
print(f"unexplained: {left}")
