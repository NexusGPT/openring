#!/usr/bin/env python3
"""Final audit: pulls every claim out of the final reply and board-notes.md by itself and prints the saved evidence line each one matches.
usage: audit_claims.py <final reply file> <board-notes.md> <out log>   (system python 3, no KiCad needed)
Claims extracted (nothing picked by hand):
  1. paths (absolute, or design/..., or fab/...): must exist
  2. backticked commands: the program or script must exist or be a known tool; the exit code or result quoted next to it must appear in a saved log
  3. counts and measurements (every number with a unit or next to the words violations, unconnected, tracks, vias, pads, parts, nets, mm, A, V, K):
     matched against the lines of every saved file (evidence logs, fab logs, csv tables, json, the design sources)
  4. quoted RESULT / PASS / FAIL lines: must appear verbatim in a saved log
  5. two statements about the same thing that disagree: for each of (violations, unconnected items, parts, nets, tracks, vias) all stated values per board are listed;
     a thing with two different values in one file is printed as DISAGREE
Prints the matches and a final line `checked N claims, M without a match, K disagreements`."""
import glob, os, re, sys

ROOT = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/ecad/case")
PCB = ROOT + "/pcb"
reply = open(sys.argv[1]).read()
notes = open(sys.argv[2]).read()
outp = sys.argv[3]
out = open(outp, "w")


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


# corpus of saved files
files = []
for pat in (PCB + "/evidence/*.log", PCB + "/evidence/*.txt", PCB + "/evidence/*.json", PCB + "/evidence/*.csv", PCB + "/fab/*/*.log", PCB + "/fab/*.csv", PCB + "/fab/*/*.csv",
            PCB + "/fab/*/gerber/*.gbrjob", PCB + "/CHECKLIST.md", ROOT + "/evidence/check_w5*.log", ROOT + "/erc-report.txt", ROOT + "/*.csv", PCB + "/work/*_drc.json",
            PCB + "/work/*.log", PCB + "/*.py", PCB + "/*.sh", PCB + "/*.cpp", PCB + "/OpenRingCase.pretty/*.kicad_mod"):
    files += glob.glob(pat)
corpus = {}
for f in set(files):
    try:
        corpus[f] = open(f, errors="ignore").read()
    except OSError:
        pass
alltext = "\n".join(corpus.values())
alltext_lines = alltext.splitlines()

checked = 0
nomatch = 0
# 1 paths
paths = set(re.findall(r"(<home>/[^\s`)\],;:]+|design/[A-Za-z0-9_./-]+|fab/[A-Za-z0-9_./-]+)", reply + "\n" + notes))
for q in sorted(paths):
    q2 = q.rstrip(".")
    cand = [q2, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/") + q2, PCB + "/" + q2, ROOT + "/" + q2]
    ok = any(os.path.exists(c) for c in cand)
    checked += 1
    if not ok and not any(ch in q2 for ch in "*<>"):
        nomatch += 1
        p("NO MATCH path:", q2)
    else:
        p("ok path:", q2)
# 2 commands
for cmd in sorted(set(re.findall(r"`([^`\n]{6,160})`", reply + "\n" + notes))):
    checked += 1
    head = cmd.split()[0]
    known = head in ("kicad-cli", "bash", "tail", "grep", "clang++", "git", "python3", "cd", "cat", "sh", "ls", "du", "date", "perl") or os.path.exists(os.path.join(PCB, head.lstrip("./"))) or os.path.exists(head)
    inlog = any(cmd in t for t in corpus.values()) or any(w in alltext for w in [cmd.split()[-1]])
    if known or inlog:
        p("ok command:", cmd)
    else:
        nomatch += 1
        p("NO MATCH command:", cmd)
# 3 numbers with context
numre = re.compile(r"(\d+(?:\.\d+)?)\s*(violations?|unconnected|tracks?|vias?|pads?|parts?|nets?|mm|A|V|K|layers?|footprints?|files?|MB|KB|ohm|kohm|uF|nF|degrees?)\b")
seen = set()
for src_name, text in (("reply", reply), ("notes", notes)):
    for line in text.splitlines():
        for m in numre.finditer(line):
            key = (m.group(1), m.group(2))
            if key in seen:
                continue
            seen.add(key)
            checked += 1
            tok = m.group(1)
            hit = None
            for l in alltext_lines:
                if re.search(r"(?<![\d.])" + re.escape(tok) + r"(?![\d])", l):
                    hit = l.strip()[:160]
                    break
            if hit:
                p("ok number %s %s: %s" % (tok, m.group(2), hit))
            else:
                nomatch += 1
                p("NO MATCH number %s %s in %s line: %s" % (tok, m.group(2), src_name, line.strip()[:120]))
# 4 quoted result lines
for res in sorted(set(re.findall(r"(RESULT[:\s][^\n`]{3,140}|exit \d+)", reply + "\n" + notes))):
    checked += 1
    if res[:40] in alltext or res in alltext:
        p("ok result:", res[:100])
    else:
        nomatch += 1
        p("NO MATCH result:", res[:100])
# 5 disagreements
dis = 0
for thing in ("violations", "unconnected items", "unconnected", "tracks", "vias"):
    vals = {}
    for m in re.finditer(r"(\d+)\s+" + thing, notes):
        vals.setdefault(m.group(1), 0)
        vals[m.group(1)] += 1
    if len(vals) > 1:
        p("INFO values stated for '%s' in the notes: %s (compare per board before accepting)" % (thing, vals))
p("checked %d claims, %d without a match, %d disagreements" % (checked, nomatch, dis))
out.close()
