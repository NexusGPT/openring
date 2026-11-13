"""Final audit: pulls claims out of band-notes.md and the final reply and matches each with saved evidence."""
import json, os, re, glob, csv
H = os.path.dirname(os.path.abspath(__file__)); E = H + "/evidence/final/"
rows = {(r["kind"], r["us"]): r for r in json.load(open(H + "/evidence/build_rows.json"))}
notes = open(H + "/band-notes.md").read(); reply = open(E + "final_reply.md").read()
n_ok = n_bad = 0
def chk(cond, msg):
    global n_ok, n_bad
    if cond: n_ok += 1; print("OK  ", msg)
    else: n_bad += 1; print("BAD ", msg)
# 1. length table of the notes against build_rows.json
for m in re.finditer(r"^\| (\d+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|$", notes, re.M):
    us = int(m.group(1)); r1, r2 = rows[("FLEX1", us)], rows[("FLEX2", us)]
    chk(abs(float(m.group(2)) - r1["flat_length"]) < 0.0006 and abs(float(m.group(3)) - r1["model_path"]) < 0.0006 and abs(float(m.group(4)) - r2["flat_length"]) < 0.0006 and abs(float(m.group(5)) - r2["model_path"]) < 0.0006, f"length row US {us}")
# 2. quoted last lines
for f, want in (("check_all.log", "RESULT: PASS boards checked 14"), ("check_swapped.log", "RESULT: FAIL boards checked 1"), ("check_missing.log", "RESULT: FAIL boards checked 1"), ("check_length.log", "RESULT: FAIL boards checked 1")):
    lines = [l for l in open(E + f).read().splitlines() if l.startswith("RESULT")]
    chk(lines and lines[-1] == want, f"{f} last RESULT line is '{want}'")
t = open(E + "check_all.log").read()
chk(t.count("kicad-cli drc: violations 0, unconnected 0") == 14, "14 boards with drc 0 and 0")
chk(len(re.findall(r"^PASS flex", t, re.M)) == 14, "14 PASS board lines")
chk("diff +0.3000" in open(E + "check_length.log").read(), "length broken copy shows diff +0.3000")
# 3. counts
chk(len(glob.glob(H + "/flex?-us*.kicad_pcb")) == 14, "14 .kicad_pcb files")
chk(len(glob.glob(H + "/fab/*-drawing.pdf")) == 14, "14 drawing PDFs")
chk(len(glob.glob(H + "/fab/*/*.drl")) == 14, "14 drill files")
chk(len(glob.glob(H + "/OpenRingBand.pretty/*.kicad_mod")) == 10, "10 footprints")
chk(len(open(E + "fab-summary.log").read().splitlines()) == 42 and all(l.endswith(" 0") for l in open(E + "fab-summary.log").read().splitlines()), "fab summary 42 lines all exit 0")
kb = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(H) for f in fs) / 1e6
chk(kb < 20, f"folder size {kb:.1f} MB under 20 (all files, not du blocks)")
chk(re.findall(r"vias (\d+)", t).count("16") == 7 and re.findall(r"vias (\d+)", t).count("11") == 7, "vias 16 on 7 flex1 boards and 11 on 7 flex2 boards")
# 4. paths named in the notes exist
for p in set(re.findall(r"design/ecad/band/[A-Za-z0-9_./-]+", notes + reply)):
    p2 = p.rstrip(".,;:)")
    chk(os.path.exists((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/") + p2), "path exists " + p2)
for p in ("design/datasheets/w4_alps_skta_catalog.pdf", "design/datasheets/w4_alps_sktaaae010_spec.pdf"):
    chk(os.path.exists((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/") + p), "path exists " + p)
# 5. numbers in the calc statements
c = open(E + "band_calc.log").read()
chk(re.search(r"13\s+6\.90\s+8\.7\s+10\.30\s+12\.9", c) is not None, "US13 motor drop 8.7 and 12.9 mV")
chk(re.search(r"13\s+6\.74\s+11\.0\s+7\.64\s+12\.5", c) is not None, "US13 cell drop 11.0 and 12.5 mV")
chk("0.20" in c and re.search(r"0\.20\s+0\.00717\s+0\.343", c) is not None, "0.20 wide: 0.00717 ohm/mm, 0.343 A")
chk(abs(2.071 - 2.0710) < 1e-3 and rows[("FLEX1", 9)]["foot_extra"] == 2.071, "foot extra 2.071")
# 6. same-thing statements agree: reply final line equals notes last line
chk(reply.strip().splitlines()[-1].split("Last line of band-notes.md: ")[-1] == notes.strip().splitlines()[-1], "reply last line equals notes last line")
print(f"claims checked {n_ok + n_bad}, matched {n_ok}, no match {n_bad}")
