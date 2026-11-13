import json, re, os
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/checks-harden-work")
def case_lines(logfile):
    d = {}
    for l in open(logfile, encoding="utf-8"):
        m = re.match(r"CASE (\S+?)/(\S+)\s+(?:want_exit=(\d+) got_exit=(\d+)|exit=(\d+) new_lines=\d+) (as expected|DIFFERS[^|]*)\|?\s*(.*)", l.rstrip("\n"))
        if m: d[m.group(2)] = (m.group(6).strip(), re.sub(r"^\|\s*", "", m.group(7).strip()))
    return d
out = []
def table(title, manifest, logfile, key_file):
    d = case_lines(logfile)
    out.append("\n" + title + "\n\n| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |\n|---|---|---|")
    for c in manifest:
        res, line = d.get(c["name"], ("no result", ""))
        f = c.get(key_file, "").replace(W + "/", "")
        out.append("| %s (%s) | %s | %s |" % (c["name"], f, res, line.replace("|", "/")[:150]))
cw = json.load(open(W + "/copies/cw/manifest.json"))
table("check_wiring.py broken copies (made by make_wiring_fakes.py from the corrected list copies/rebuilt-fixed.csv), final run logs/all-check_wiring.log, one log per copy in logs/cw/", cw, W + "/logs/all-check_wiring.log", "csv")
cj = json.load(open(W + "/copies/cj/manifest.json"))
table("check_joints.py broken copies (make_joints_fakes.py), final run logs/all-check_joints.log, one log per copy in logs/cj/", cj, W + "/logs/all-check_joints.log", "csv")
ca = json.load(open(W + "/copies/ca/manifest.json"))
table("check_assembly.py broken copies (make_assembly_fakes.py, from a snapshot of the guide taken at the start of the run), final run logs/all-check_assembly.log, one log per copy in logs/ca/", ca, W + "/logs/all-check_assembly.log", "md")
open(W + "/final/tables.md", "w").write("\n".join(out) + "\n")
print(len(out))
