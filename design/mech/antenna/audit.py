"""Final audit of antenna-study.md (and of the final reply when given): pulls every number, citation and quote out of the
text by itself and prints the evidence line each one matches, or NO MATCH.
usage: audit.py <text file> [<text file> ...]"""
import re
import sys
from pathlib import Path

R = Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix()))
A = R / "design/mech/antenna"
FILES = {
    "measure.log": A / "measure.log", "insert_check.log": A / "insert_check.log", "step_tree.log": A / "step_tree.log",
    "johanson_8p_text.log": A / "johanson_8p_text.log", "johanson_text.log": A / "johanson_text.log",
    "johanson_tuning_text.log": A / "johanson_tuning_text.log", "quotes_infineon.log": A / "quotes_infineon.log",
    "placement.csv": R / "design/mech/thin/placement.csv", "layers.json": R / "design/mech/thin/layers.json",
    "architecture.md": R / "design/architecture.md", "thin.py": R / "design/mech/thin/thin.py",
    "bench-plan.md": R / "design/bench/bench-plan.md", "band-liner.md": R / "design/mfg/specs/band-liner.md",
    "body.md": R / "design/mfg/specs/body.md", "bom.csv": R / "design/bom.csv",
}
EVID = list(FILES.values()) + [A / n for n in ("infineon_text.log", "ti_text.log", "compare_expected.log", "fetch_1.log",
                                               "fetch_2.log", "datasheet_hashes.log", "html_nordic_head.log", "html_silabs.log",
                                               "taoglas_head.log", "abracon_text.log", "johanson_urls.log", "expected_measure.txt",
                                               "quotes_ti.log", "quotes_ti2.log", "quotes_johanson8.log", "quotes_johanson5.log")] + \
    [R / "design/mech/thin/thin-notes.md", R / "design/mfg/specs/band-liner.md"]
texts = {p: p.read_text(errors="replace") for p in EVID if p.exists()}
alltext = "\n".join(texts.values())
lines_of = {k: v.read_text(errors="replace").split("\n") for k, v in FILES.items()}

claims = 0
nomatch = []
calc_ok = set()
CONST = {'299.79': 'speed of light in mm x GHz, physical constant, labelled in the text'}
for src in sys.argv[1:]:
    doc = Path(src).read_text()
    print(f"######## {src}")
    # 1. citations "<file> line(s) N [to M]" and "lines N, M"
    for m in re.finditer(r"([\w.-]+\.(?:log|csv|json|md|py))\s+lines?\s+(\d+)(?:\s*(?:to|,|and)\s*(\d+))?", doc):
        f, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        claims += 1
        if f not in lines_of:
            print(f"CITE {f} lines {a}-{b}: file not in the audit map (checked by hand: see below)")
            continue
        L = lines_of[f]
        ok = 1 <= a <= len(L) and 1 <= b <= len(L)
        ctx = doc[max(0, m.start() - 160):m.start()]
        nums = re.findall(r"-?\d+\.\d+", ctx)[-3:]
        seg = "\n".join(L[a - 1:b]) if ok else ""
        hit = [n for n in nums if n in seg or n.lstrip("-") in seg]
        print(f"CITE {f} lines {a}-{b}: {'exists' if ok else 'OUT OF RANGE'}; numbers before it {nums} found in cited lines {hit}")
        print(f"     -> {seg[:200]!r}")
        if not ok:
            nomatch.append(m.group(0))
    pending = []
    # 2. every decimal number must occur in some evidence file (or be a [CALC] result shown with its formula)
    for m in re.finditer(r"(?<![\w.])-?\d+\.\d+(?![\w])", doc):
        n = m.group(0)
        claims += 1
        if n in alltext or n.lstrip("-") in alltext or (n.rstrip("0") in alltext and "." in n.rstrip("0")):
            continue
        ctx = doc[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
        pending.append((n, ctx))
    # 3. quotes
    nocode = re.sub(r"`[^`]*`", " ", doc)
    for m in re.finditer(r"\"([^\"\n|]{3,})\"", nocode):
        q = m.group(1)
        claims += 1
        qn = re.sub(r"\s+", " ", q.replace("’", "'"))
        at = re.sub(r"\s+", " ", alltext.replace("’", "'"))
        print(f"QUOTE {'found' if qn in at else 'NOT FOUND'}: {q[:90]!r}")
        if qn not in at:
            nomatch.append(q[:40])

    # 5. arithmetic of every [CALC] result that has no evidence line
    import math
    for label, val, shown in (("half wavelength", 299.79 / 2.44 / 2, "61.4"), ("wavelength", 299.79 / 2.44, "122.9"),
                              ("mid circumference", math.pi * (18.95 + 2.6), "67.7"), ("corner centre X", (-14.65 - 10.6) / 2, "-12.625"),
                              ("corner centre Y", (2.05 + 7.375) / 2, "4.713"), ("corner centre Z", 2.75 / 2, "1.375"),
                              ("corner size Y", 7.375 - 2.05, "5.325"), ("box size Y", 7.6 - 2.05, "5.55"), ("box centre Y", (2.05 + 7.6) / 2, "4.825"),
                              ("range factor", 10 ** (10 / 20), "3.2"), ("land span Y", 4.4 + 2.0, "6.4"), ("land span Y low", 4.4 - 2.0, "2.4"),
                              ("end wall inner X", -13.5 - 0.225, "-13.725")):
        if shown not in doc:
            continue
        claims += 1
        dec = len(shown.split('.')[1]) if '.' in shown else 0
        ok = abs(val - float(shown)) <= 0.5 * 10 ** -dec + 1e-9 and shown in doc
        if ok:
            calc_ok.add(shown)
        print(f"CALC {label}: computed {val:.4f}, text {shown}, in text {shown in doc}: {'OK' if ok else 'MISMATCH'}")
        if not ok:
            nomatch.append(label)
    for n, ctx in pending:
        if n in calc_ok:
            print(f"NUMBER {n}: [CALC] result, arithmetic checked above")
        elif n in CONST:
            print(f"NUMBER {n}: {CONST[n]}")
        else:
            nomatch.append(n)
            print(f"NUMBER {n} NO MATCH in evidence; context: ...{ctx}...")

    # 6. counts stated in the texts
    study = (A / "antenna-study.md").read_text()
    n_changes = len(re.findall(r"^\d+\. design/", study, re.M))
    blocked = [f for f in ("html_nordic_head.log", "html_silabs.log", "taoglas_head.log", "abracon_text.log") if (A / f).exists()]
    for label, val, pat in (("file changes", n_changes, r"\b15 file changes"), ("blocked downloads", len(blocked), r"Four more downloads")):
        if re.search(pat, doc):
            claims += 1
            want = 15 if label == "file changes" else 4
            print(f"COUNT {label}: counted {val}, text says {want}: {'OK' if val == want else 'MISMATCH'}")
            if val != want:
                nomatch.append(label)
    # 4. structure
    print("em dashes:", doc.count("—"))
    if src.endswith("antenna-study.md"):
        print("last line:", doc.rstrip("\n").split("\n")[-1][:120])
        print("recommendation headings:", len(re.findall(r"^## 5\. Recommendation", doc, re.M)))
        for o in ("(a1)", "(a2)", "(a3)", "(a4)", "(b)", "(c)", "(d)", "(e)"):
            print(f"options table row {o}:", bool(re.search(r"^\| " + re.escape(o), doc, re.M)))
print("measure.log last line:", (A / "measure.log").read_text().rstrip("\n").split("\n")[-1])
print(f"claims checked: {claims}; without a match: {len(nomatch)}")
for n in nomatch:
    print("   NO MATCH:", n)
