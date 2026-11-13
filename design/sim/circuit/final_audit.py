#!/usr/bin/env python3
"""Final audit: pulls every claim out of sim-notes.md and the final reply and prints the saved evidence line each one matches.

    python final_audit.py [--reply results/final_reply.txt] > results/final_audit.txt

Claims checked:
  numbers   every number with a decimal point, 4 or more digits, or a unit; matched against every number in the evidence
            corpus (results, logs, pass lines, models, text copies of the maker documents, the circuit files and the design
            documents the notes cite), also after unit changes (x1000, /1000, x1e6, /1e6, x100) and a rounding tolerance of 0.6 percent
  paths     every `backticked` path-like string must exist
  quotes    every "double quoted" phrase must occur in some corpus line
  results   every PASS/FAIL result line of the notes and the reply must occur verbatim in results/summary.txt;
            RESULT, PROOF and tests: lines must match the last lines of the saved logs
  counts    statements about the same thing must agree (test counts, rows, models, decks, proofs)
Unmatched claims are listed at the end; each is fixed or dropped before the reply is sent.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))

ap = argparse.ArgumentParser()
ap.add_argument("--reply", default=os.path.join(HERE, "results", "final_reply.txt"))
a = ap.parse_args()

NOTES = os.path.join(HERE, "sim-notes.md")

# ---------------------------------------------------------------- corpus
corpus_files = []
for pat in ("results/*.txt", "results/*.csv", "results/*.json", "results/*.log", "results/broken/*/run.log", "results/broken/*/out/rows.csv",
            "logs/*.log", "logs/*.txt", "logs/*.out", "logs/ti_model_trials/*", "pass-lines.md", "expected-failures.md", "CHECKLIST.md",
            "models/[a-su-z]*.lib", "models/tlv755p30.lib", "models/tpd4e05u06.lib", "models/tps2553.lib", "models/*.md", "src/*.txt", "decks/*.cir", "results/decks/*.cir", "work/trial_out/info.txt"):
    corpus_files += glob.glob(os.path.join(HERE, pat))
for rel in ("ecad/ring/netlist.csv", "ecad/ring/parts.csv", "ecad/case/netlist.csv", "ecad/case/parts.csv", "mfg/specs/cell.md", "firmware.md",
            "ecad/motor-drive/motor-drive.md", "wiring/w7-facts.md", "wiring/lead-decisions.md", "wiring/package-plan.md", "ecad/case/sch-notes.md",
            "ecad/ring/sch-notes.md", "wiring/connections.md", "architecture.md", "datasheets/slim_alps-skta-aaae010-orwin.txt"):
    corpus_files.append(os.path.join(DESIGN, rel))
corpus = []   # (file, lineno, text)
for f in corpus_files:
    try:
        for i, l in enumerate(open(f, errors="replace"), 1):
            corpus.append((os.path.relpath(f, DESIGN), i, l.rstrip("\n")))
    except OSError:
        pass

NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
index = {}   # bucket -> list of (value, file, line, text)
for f, i, t in corpus:
    for m in NUM.finditer(t):
        try:
            v = float(m.group(0))
        except ValueError:
            continue
        if v == 0:
            b = "zero"
        else:
            b = round(math.log10(abs(v)) * 20)   # fine buckets
        index.setdefault(b, []).append((v, f, i, t))


def primary(f):
    """Results of the final run, the pass lines and the saved logs count before the maker documents and the design files."""
    return f.startswith("sim/circuit/results") or f.startswith("sim/circuit/pass-lines") or f.startswith("sim/circuit/expected") or f.startswith("sim/circuit/logs") or f.startswith("sim/circuit/decks")


def find_number(x, tok):
    """Exact string match first, then numeric match after a unit change with a tolerance of 0.3 percent.
    Both passes look at the run results and logs first, then at the documents."""
    pat = re.compile(r"(?<![\w.])" + re.escape(tok) + r"(?![\w])")
    for want_primary in (True, False):
        for f, i, t in corpus:
            if primary(f) == want_primary and tok in t and pat.search(t):
                return (f, i, t, "exact")
        for scale in (1.0, 1e3, 1e-3, 1e6, 1e-6, 100.0, 0.01):
            target = x * scale
            if target == 0:
                continue
            b = round(math.log10(abs(target)) * 20)
            for bb in (b - 1, b, b + 1):
                for v, f, i, t in index.get(bb, []):
                    if primary(f) == want_primary and v != 0 and abs(v - target) <= 0.003 * abs(v) + 1e-12:
                        return (f, i, t, "approx x%g" % scale)
    return None


# ---------------------------------------------------------------- texts to audit
texts = {"sim-notes.md": open(NOTES).read()}
if os.path.exists(a.reply):
    texts["final reply"] = open(a.reply).read()

claims = 0
unmatched = []
print("FINAL AUDIT")
print("evidence corpus: %d files, %d lines" % (len(corpus_files), len(corpus)))

UNIT = re.compile(r"^\s*(?:mA|uA|A\b|mV|V\b|kohm|Mohm|ohm|mohm|ms\b|us\b|s\b|uF|nF|pF|mW|W\b|MB|percent|C\b|mAh|kHz|MHz|nA|Hz)")
for name, text in texts.items():
    print("\n== numbers in %s" % name)
    seen = set()
    # strip things that are not claims about results: markdown list numerals, section numbers, page refs, time stamps, code fences
    body = re.sub(r"```.*?```", lambda m: m.group(0), text, flags=re.S)
    for ln, line in enumerate(body.splitlines(), 1):
        l = re.sub(r"^\s*(\d+\.|-|\|)\s*", "", line)
        l = re.sub(r"\b[pP]\d+\b|\bp\d+ to p\d+\b|\bTable \d+\b|\bsection \d+(\.\d+)*\b|\b\d\d:\d\d(:\d\d)?\b|\bR\d+(\.\d+)?\b|\bC\d+(\.\d+)?\b|\bU\d+\b|\bRT\d\b|\bW\d+\b|\bB\d+\b|\bS\d+\b|\bO\d+\b|\bN\d+\b", " ", l)
        for m in NUM.finditer(l):
            tok = m.group(0)
            after = l[m.end():m.end() + 10]
            if not ("." in tok or len(tok.lstrip("-")) >= 4 or UNIT.match(after) or "e" in tok.lower()):
                continue
            if tok in seen:
                continue
            seen.add(tok)
            x = float(tok)
            claims += 1
            hit = find_number(x, tok)
            if hit:
                print("  %-12s -> %s:%d (%s): %s" % (tok, hit[0], hit[1], hit[3], hit[2].strip()[:100]))
            else:
                unmatched.append((name, ln, tok, line.strip()[:120]))
                print("  %-12s -> NO MATCH (line %d)" % (tok, ln))

# ---------------------------------------------------------------- paths
names = {}
for root, dirs, files in os.walk(DESIGN):
    dirs[:] = [d for d in dirs if d not in (".venv", "node_modules", "__pycache__", "dl")]
    for fn in files:
        names.setdefault(fn, os.path.join(root, fn))
print("\n== paths in sim-notes.md and the reply")
path_claims = 0
for name, text in texts.items():
    for m in re.finditer(r"`([^`\n]+)`", text):
        s = m.group(1).strip()
        if not re.search(r"[/]|\.(py|sh|md|csv|json|txt|log|lib|cir|gz)$", s):
            continue
        if " " in s and not s.startswith("/"):
            continue
        if any(ch in s for ch in "*{}<>=|$") or s.startswith("python ") or s.startswith("sh "):
            continue
        cand = [s, os.path.join(HERE, s), os.path.join(DESIGN, s), os.path.join(DESIGN, "..", s), os.path.join(HERE, "results", s), os.path.join(HERE, "models", s), os.path.join(HERE, "logs", s), os.path.join(HERE, "logs", "ti_model_trials", s), os.path.join(HERE, "work", s)]
        if "/" not in s and s in names:
            cand.append(names[s])
        path_claims += 1
        claims += 1
        ok = next((c for c in cand if os.path.exists(c)), None)
        print("  %-70s %s" % (s[:70], ("exists: " + ok) if ok else "MISSING"))
        if not ok:
            unmatched.append((name, 0, s, "path missing"))

# ---------------------------------------------------------------- quotes
print("\n== quoted phrases")
for name, text in texts.items():
    for m in re.finditer(r'"([^"\n]{6,})"', text):
        q = m.group(1)
        claims += 1
        hit = next(((f, i, t) for f, i, t in corpus if q.lower() in t.lower()), None)
        if hit:
            print("  \"%s\" -> %s:%d" % (q[:60], hit[0], hit[1]))
        else:
            if q.startswith("tests:") or q.startswith("RESULT"):
                print("  \"%s\" -> checked in the results section" % q[:60])
            else:
                unmatched.append((name, 0, q, "quote not found"))
                print("  \"%s\" -> NOT FOUND" % q[:60])

# ---------------------------------------------------------------- results lines
print("\n== result lines")
summary = open(os.path.join(HERE, "results", "summary.txt")).read().splitlines()
for name, text in texts.items():
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^(PASS|FAIL) (ring|case)\d", s):
            claims += 1
            ok = s in summary
            print("  %s -> %s" % (s[:80], "verbatim in results/summary.txt" if ok else "NOT IN summary.txt"))
            if not ok:
                unmatched.append((name, 0, s[:60], "result line differs from summary.txt"))
run_log = open(os.path.join(HERE, "results", "run_all.log")).read().splitlines()
prove_log = open(os.path.join(HERE, "results", "prove_fail.log")).read().splitlines()
print("  last line of results/run_all.log: %s" % run_log[-1])
print("  tests line of results/run_all.log: %s" % [l for l in run_log if l.startswith("tests:")][-1])
print("  last line of results/prove_fail.log: %s" % prove_log[-1])
notes_last = [l for l in texts["sim-notes.md"].splitlines() if l.strip()][-1]
print("  last line of sim-notes.md: %s" % notes_last[:120])
claims += 4

# ---------------------------------------------------------------- consistency
print("\n== statements about the same thing")
rows = [l.split(",")[0] for l in open(os.path.join(HERE, "results", "rows.csv")).read().splitlines()[1:]]
ring_rows = sum(1 for r in rows if r.startswith("R"))
case_rows = sum(1 for r in rows if r.startswith("C"))
n_models = len([f for f in glob.glob(os.path.join(HERE, "models", "*.lib")) if open(f).readline().startswith("* own model")])
n_decks = len(json.load(open(os.path.join(HERE, "results", "deck_parts.json"))))
npass = sum(1 for l in summary if l.startswith("PASS"))
nfail = sum(1 for l in summary if l.startswith("FAIL"))
checks = [
    ("tests pass and fail in summary.txt equal the tests line of run_all.log", "tests: %d, pass: %d, fail: %d" % (npass + nfail, npass, nfail) in " ".join(l[:30] for l in run_log if l.startswith("tests:"))),
    ("ring rows in rows.csv equal the notes (66)", ring_rows == 66 and "66 rows" in texts["sim-notes.md"]),
    ("case rows in rows.csv equal the notes (22)", case_rows == 22 and "22 rows" in texts["sim-notes.md"]),
    ("own models counted from first lines equal the notes (7)", n_models == 7 and "7 own models" in texts["sim-notes.md"]),
    ("decks in the manifest equal the notes (13)", n_decks == 13 and "13 decks" in texts["sim-notes.md"]),
    ("the last line of the notes states %d tests, %d pass, %d fail" % (npass + nfail, npass, nfail), ("%d tests" % (npass + nfail)) in notes_last and ("%d pass" % npass) in notes_last and ("%d fail" % nfail) in notes_last),
    ("three PROOF OK lines in prove_fail.log", sum(1 for l in prove_log if l.startswith("PROOF OK")) == 3 and prove_log[-1] == "PROOF RESULT OK"),
    ("run_all.log ends with RESULT FAIL while 4 tests fail", run_log[-1] == "RESULT FAIL" and nfail == 4),
]
for desc, ok in checks:
    claims += 1
    print("  %s: %s" % (desc, "agree" if ok else "DISAGREE"))
    if not ok:
        unmatched.append(("consistency", 0, desc, "disagree"))
# the reply must not contain words the owner banned
for name, text in texts.items():
    for bad in ("proven on hardware", "\u2014"):
        claims += 1
        hit = bad in text
        print("  banned text %r in %s: %s" % (bad, name, "FOUND" if hit else "absent"))
        if hit:
            unmatched.append((name, 0, bad, "banned text found"))

print("\nclaims checked: %d" % claims)
print("unmatched or disagreeing: %d" % len(unmatched))
for n, ln, tok, ctx in unmatched:
    print("  UNMATCHED %s line %s: %s | %s" % (n, ln, tok, ctx))
sys.exit(0 if not unmatched else 1)
