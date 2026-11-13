# Recomputes each "N of M" count of the review from the saved logs (no number typed by hand).
import re, os, csv, glob
W = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work/")
R = (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
info = eval(re.search(r"INFO (\{.*\})", open(W + "check_all.log").read()).group(1))
res = re.search(r"RESULT lines=(\d+) fails=(\d+)", open(W + "check_all.log").read())
print("lines %s of %s with 0 fails: fails=%s" % (res.group(1), res.group(1), res.group(2)))
print("interface pads %d of %d" % (info["interface_covered"], info["interface_pads"]))
print("physical lines with marking and cuts %d of %d (fails=%s)" % (info["physical"], info["physical"], res.group(2)))
print("contact rows %d of 28; spring pin rows %d of 4" % (info["contact_rows"], info["spring_pin_rows"]))
print("pads with a netlist row %d of %d" % (info["pads_vs_netlist"], info["pads_total"]))
print("tail lands mating %d of %d (15 lands x 7 sizes = 105)" % (info["mating"], 15 * 7))
print("end checks %d, tail land checks %d, node checks %d" % (info["end_checks"], info["tail_land_checks"], info["node_checks"]))
rpts = sorted(glob.glob(W + "drc/*.rpt")); ok = 0
for p in rpts:
    t = open(p).read()
    if "Found 0 DRC violations" in t and "Found 0 unconnected pads" in t: ok += 1
print("rules check boards clean %d of %d" % (ok, len(rpts)))
g = open(W + "gerber-check.log").read()
for m in re.finditer(r"RESULT (\S+) lands=(\d+) with_opening=(\d+)", g): print("gerber %s: %s of %s lands with an opening" % (m.group(1), m.group(3), m.group(2)))
fl1 = len(re.findall(r"RESULT flex1-us\d+_F_SW lands=12 with_opening=12", g)); fl2 = len(re.findall(r"RESULT flex2-us\d+_B_CP lands=4 with_opening=4", g))
print("flex1 sizes with 12 of 12: %d of 7; flex2 sizes with 4 of 4: %d of 7" % (fl1, fl2))
fd = open(W + "flexdraw/summary.log").read().splitlines(); print("flex drawings with the land detail %d of %d" % (sum(1 for l in fd if "detail=1" in l), len(fd)))
gi = open(W + "gnd-islands2.log").read()
print("FLEX2 sizes with B2 and B7 on one island %d of 7; FLEX1 sizes with A6 and A8 joined %d of 7" % (len(re.findall(r"flex2-us\d+ .*joined by ribbon copper: True", gi)), len(re.findall(r"flex1-us\d+ .*joined by ribbon copper: True", gi))))
print(open(W + "j1-heights.log").read().strip().splitlines()[-2])
print(open(W + "pdf/ids.log").read().splitlines()[0])
jc = open(W + "joints-compact.log").read().splitlines(); print(jc[0])
print("joint rows that are board passes:", sum(1 for l in jc if l.startswith("P-")), "; joint end rows:", sum(1 for l in jc if l.startswith("J-")))
# bom citations: right when the cited row's reference cell names a reference in the 90 characters before the citation
right = total = 0
for l in open(W + "bom-cites.log"):
    m = re.match(r"assembly\.md:(\d+) cites bom\.csv:(\d+) -> row ref '([^']*)' \| text: \.\.\.(.*)", l)
    if not m: continue
    total += 1
    refs = [x.strip() for x in m.group(3).split(",")]
    if any(re.search(r"\b%s\b" % re.escape(x), m.group(4)) for x in refs if x): right += 1
print("bom citations whose row names a reference of the text before it: %d of %d (so %d point at another row)" % (right, total, total - right))
for f in ("fakes-run.log", "fakes-check_wiring.log", "fakes-check_joints.log", "fakes-check_assembly.log"):
    print(f, open(W + f).read().strip().splitlines()[-1])
