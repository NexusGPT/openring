"""Final audit: pulls every quoted string, path and number-with-unit out of final-reply.txt and prints the saved evidence line each matches (searches E, the notes, board-notes.md, netlist/parts files).
Prints counts; a claim with no match is listed as NOMATCH."""
import re, os, glob, sys
R = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix())
E = R + "/design/ecad/case/pcb/evidence/marks"
txt = open(E + "/final-reply.txt").read()
files = [f for f in glob.glob(E + "/**/*", recursive=True) if os.path.isfile(f) and not f.endswith(("final-reply.txt", "audit_reply.py", "audit_reply.out", ".pdf", ".png", ".step", ".gbr", ".drl"))]
files += [R + "/design/wiring/case-marks-notes.md", R + "/design/ecad/case/pcb/board-notes.md", R + "/design/ecad/case/pcb/evidence/capab_jlc.html.txt",
          R + "/design/ecad/case/evidence/check_marks_s4.log", R + "/design/case/case-architecture.md", R + "/design/wiring/lead-decisions.md"]
corpus = {}
for f in files:
    try:
        corpus[f] = open(f, errors="replace").read()
    except Exception:
        pass
def find(s):
    for f, t in corpus.items():
        if s in t:
            i = t.index(s); ln = t.count("\n", 0, i) + 1
            return "%s:%d" % (f.replace(R + "/", ""), ln)
    return None
claims = []
for line in txt.splitlines():
    claims += [("quote", m) for m in re.findall(r'"([^"]{6,})"', line)]
claims += [("path", m) for m in re.findall(r"((?:design/|E )[\w./\-*]+\.\w+)", txt)]
claims += [("number", m) for m in set(re.findall(r"\b\d+(?:\.\d+)?(?: mm| kHz| rows| parts| nets| files| pads)\b", txt))]
bad = 0
for k, c in claims:
    if k == "path":
        c2 = c[2:] if c.startswith("E ") else c
        hit = None
        for base in (E + "/", R + "/", R + "/design/ecad/case/pcb/", R + "/design/ecad/case/pcb/evidence/", R + "/design/ecad/case/"):
            if os.path.exists(base + c2.replace("*", "")):
                hit = base + c2
                break
        print("PATH   %-60s %s" % (c, "exists" if hit else "NOMATCH"))
        bad += 0 if hit else 1
    else:
        h = find(c)
        print("%-6s %-70s %s" % (k.upper(), c[:70], h or "NOMATCH"))
        bad += 0 if h else 1
print("claims checked:", len(claims), "no match:", bad)
