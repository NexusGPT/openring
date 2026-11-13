#!/usr/bin/env python3
"""Final audit: pulls claims out of final-reply.md and band-paste-notes.md by itself and matches each with saved evidence.
- every backticked text that starts with RESULT, flex2-us13 or claims must be a line of some log in WORK/logs (exact, trailing blanks ignored);
- every path named (fab/..., logs/..., design/...) must exist;
- counts: 12 and 16 openings per board, 8 of 8 and 7 of 7, 14 of 14 drc lines, 98 same files, text heights, sizes;
- line counts of band-interface.md (148) and position of the band-notes.md RESULT line (150);
- the reply is under 3500 characters; the notes and the reply end with a RESULT line; no em dash."""
import glob, os, re, sys

W = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(W)
LOG = os.path.join(W, "logs")
reply = open(os.path.join(W, "final-reply.md")).read()
notes = open(os.path.join(B, "band-paste-notes.md")).read()
logs = {os.path.basename(p): open(p, errors="replace").read() for p in glob.glob(LOG + "/*.log")}
all_lines = set()
for t in logs.values():
    all_lines |= {l.rstrip() for l in t.splitlines()}
ok = bad = 0


def chk(c, m):
    global ok, bad
    if c:
        ok += 1; print("OK  ", m)
    else:
        bad += 1; print("BAD ", m)


for name, txt in (("reply", reply), ("notes", notes)):
    for q in re.findall(r"`([^`]+)`", txt):
        if q.startswith(("RESULT", "flex2-us13", "claims")):
            chk(q.rstrip() in all_lines, f"{name}: quoted line is in a log: {q[:90]}")
    for p in set(re.findall(r"(?:logs/|fab/|band-paste-work/logs/)[A-Za-z0-9_.*/-]+", txt)):
        p = p.rstrip(".,;:)")
        if "*" in p or "flexK-usN" in p or "usN" in p:
            continue
        cands = [os.path.join(W, p), os.path.join(B, p), os.path.join(W, "logs", os.path.basename(p))]
        chk(any(os.path.exists(c) for c in cands), f"{name}: path exists {p}")
    chk(txt.strip().splitlines()[-1].startswith("RESULT: done"), f"{name}: last line is the RESULT line")
    chk("—" not in txt, f"{name}: no em dash")
chk(len(reply) < 3500, f"reply length {len(reply)} under 3500")
cp = logs["count_paste5.log"]
chk(len(re.findall(r"^PASS flex1-us\d+: paste openings 12 \(want 12; flashes 12", cp, re.M)) == 7, "7 FLEX1 boards with 12 openings")
chk(len(re.findall(r"^PASS flex2-us\d+: paste openings 16 \(want 16; flashes 0, closed circles 16\).*smallest gap opening to via 0\.050", cp, re.M)) == 7, "7 FLEX2 boards with 16 openings, gap 0.050")
cd = logs["check_drawings5.log"]
chk(len(re.findall(r"^PASS flex1-us\d+: land labels 8 of 8, marks 1 of 1", cd, re.M)) == 7, "FLEX1 8 of 8 at 7 sizes")
chk(len(re.findall(r"^PASS flex2-us\d+: land labels 7 of 7, marks 3 of 3", cd, re.M)) == 7, "FLEX2 7 of 7 at 7 sizes")
d4 = logs["drc5.log"]
chk(len(re.findall(r"exit 0 \*\* Found 0 DRC violations \*\* \*\* Found 0 unconnected pads", d4)) == 14, "drc 14 of 14 zero and zero")
cb = logs["check_band6.log"]
chk(cb.count("kicad-cli drc: violations 0, unconnected 0") == 14, "check_band 14 drc lines 0 and 0")
chk(logs["check_band6.log"].strip().splitlines()[-1] == "exit 0", "check_band exit 0")
chk(len(re.findall(r"same geometry|same lines", logs["compare-fab-final5.log"])) == 98, "98 same files before vs final")
ts = logs["text_scale5.log"]
h = [float(x) for x in re.findall(r"text 0\.3 mm -> ([\d.]+) mm", ts)]
nn = [float(x) for x in re.findall(r"land numbers 0\.6 mm -> ([\d.]+) mm", ts)]
sc = [float(x) for x in re.findall(r"scale ([\d.]+) : 1", ts)]
chk(len(h) == 14 and min(h) == 1.77 and max(h) == 2.12, f"text on paper {min(h)} to {max(h)} of 14")
chk(min(nn) == 3.53 and max(nn) == 4.24 and min(sc) == 5.89 and max(sc) == 7.06, "land numbers 3.53 to 4.24, scale 5.89 to 7.06")
px = [int(x) for x in re.findall(r"pixels \d+x\d+, differing (\d+)", logs["compare-fab-repro2.log"])]
chk(len(px) == 14 and min(px) == 1 and max(px) == 14, f"repro drawings differ by {min(px)} to {max(px)} pixels")
chk("ctl" and "paste openings 11 (want 12" in logs["ctl5-count-paste1.log"] and "paste openings 15 (want 16" in logs["ctl5-count-paste2.log"], "controls 11 and 15")
chk("10792" in logs["du2.log"] and "189336" in logs["du1.log"] and "12824" in logs["du4.log"], "work folder 189336 KB, 10792 KB after removal, 12824 KB now")
chk(len(logs["ppm-removed-listing.log"].splitlines()) == 60, "60 PPM files listed before removal")
bi = open(os.path.join(B, "band-interface.md")).read()
chk(bi.count("\n") == 148 and open(os.path.join(W, "before", "band-interface.md")).read().count("\n") == 148, "band-interface.md 148 lines before and after")
bn = open(os.path.join(B, "band-notes.md")).read().splitlines()
bn0 = open(os.path.join(W, "before", "band-notes.md")).read().splitlines()
chk(bn[150].startswith("RESULT: done, 14 boards") and bn0[139].startswith("RESULT: done, 14 boards") and len(bn) == 151, "band-notes RESULT line 140 -> 151")
for ln in (55, 58, 91, 106, 116, 123, 137, 141):
    a = open(os.path.join(W, "before", "band-interface.md")).read().splitlines()[ln - 1]
    chk(bi.splitlines()[ln - 1].startswith(a) and bi.splitlines()[ln - 1] != a, f"band-interface.md line {ln} extended in place")
changed = [i + 1 for i, (x, y) in enumerate(zip(open(os.path.join(W, "before", "band-interface.md")).read().splitlines(), bi.splitlines())) if x != y]
chk(changed == [55, 58, 91, 106, 116, 123, 137, 141], f"band-interface.md changed lines {changed}")
changed_n = [i + 1 for i, (x, y) in enumerate(zip(bn0[:139], bn[:139])) if x != y]
chk(changed_n == [18, 43, 65], f"band-notes.md changed lines among 1-139: {changed_n}")
cl = logs["cited-lines.log"]
cited_notes = sorted({int(m) for m in re.findall(r"band-notes\.md(?::|`? lines? | line )(\d+)", cl)})
chk(cited_notes == [49, 61, 71], f"band-notes.md cited lines {cited_notes}")
chk("C90 has no row" in logs["ring_check_footprints_before.log"] and "C90 has no row" in logs["ring_check_footprints_after6.log"] and "RESULT FAIL 2 " in logs["ring_check_footprints_after6.log"] and "has 16 pads, footprint-sources.csv says 8" in logs["ring_check_footprints_helperlib.log"], "ring footprint check: FAIL 2 before and after; helper pad form adds J_BAND fails")
chk('"BoardThickness": 1.6' in open(os.path.join(W, "before", "fab", "flex1-us9", "flex1-us9-job.gbrjob")).read(), "old job file BoardThickness 1.6")
lib = logs["lib-final.log"]
lib = logs["lib6.log"]
chk(lib.count(" same") == 6 and lib.count("DIFF") == 4, "library: 6 footprints same, 4 changed")
chk("claims checked 36, matched 36, no match 0" in logs["audit_notes_after2.log"], "old audit 36 of 36")
chk(len(re.findall(r"^notes flex\d-us\d+ 0$", logs["make_fab5.log"], re.M)) == 14, "14 fab notes written")
cw = logs["check_wiring6.log"]
chk(cw.strip().splitlines()[-1].startswith("RESULT PASS lines 67") and "problems 0" in cw and "FAIL" not in cw and open(os.path.join(LOG, "check_wiring6.exit")).read().strip() == "exit 0", "check_wiring exit 0, problems 0, no FAIL")
chk("COMPLETE 66 of 66 conductors (100 percent)" in cw, "66 of 66")
jt = logs["jband_paste_test.log"]
chk(jt.count("centred openings [(0.3, 0.44, True)]") == 15 and "pads 8 numbers" in jt and "pads 7 numbers" in jt, "J_BAND 15 centred 0.30 x 0.44 openings, pads 8 and 7")
chk(open(os.path.join(W, "jband", "jband-F_Paste.gbr")).read().count("G36") == 15, "J_BAND paste Gerber 15 regions")
chk("('PAD'," not in logs["compare-after5.log"] and "('PADLAYERS', '+', True) 84" in logs["compare-after5.log"], "no PAD line added in the final compare (only 84 pad layer lines changed)")
chk(len(re.findall(r"^PASS", logs["check_drawings5.log"], re.M)) == 14, "14 drawings pass")
chk(len(re.findall(r"exit 0 \*\* Found 0 DRC violations \*\* \*\* Found 0 unconnected pads", logs["drc5.log"])) == 14, "drc5 14 of 14")
print(f"claims checked {ok + bad}, matched {ok}, no match {bad}")
sys.exit(0 if bad == 0 else 1)
