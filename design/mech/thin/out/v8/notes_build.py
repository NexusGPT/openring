#!/usr/bin/env python3
"""Writes design/mech/thin/band-fit-notes.md from the saved logs in out/v8 (every number in the generated blocks is read from a log line) and the prose below.
Run: python3 out/v8/notes_build.py  (rewrites band-fit-notes.md; the prose is edited here)."""
import re, subprocess, sys
from pathlib import Path

T = Path((__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin"))
V = T / "out" / "v8"
LOGS = {7: "v8b_us7.log", 8: "v8_us8.log", 9: "v8_us9_default.log", 10: "v8_us10.log", 11: "v8_us11.log", 12: "v8b_us12.log", 13: "v8_us13.log"}


def lines(p):
    p = Path(p)
    return p.read_text(errors="replace").splitlines() if p.exists() else []


def grab(p, pat, last=False):
    hits = [l for l in lines(p) if re.search(pat, l)]
    if not hits:
        return "no line"
    return hits[-1] if last else hits[0]


def block(p, pat):
    return "\n".join(l for l in lines(p) if re.search(pat, l))


def fence(txt):
    return "```\n" + txt + "\n```"


out = []
W = out.append
W(Path(V / "notes_head.md").read_text())
# ---- c. per size table
W("### c.1 Fit check per size (command: out/v8/run_check.sh with the size and a label, which runs check_thin.py with the exterior ring-merged32h-usN.step of look/s1/out and the bore of that size at nice -n 19; US 9 is the default build run by out/v8/run_default.sh v8)\n")
W("| size | log | start | end | pairs line | findings line | last line | exit line |")
W("|---|---|---|---|---|---|---|---|")
for us, name in LOGS.items():
    L = lines(V / name)
    if not L:
        W(f"| US {us} | {name} | no log | | | | | |")
        continue
    ex = [l for l in L if l.startswith("exit")]
    dates = [l for l in L if re.match(r"^\S+\. \d+ \S+\. 2026", l)]
    res = [l for l in L if l.startswith("RESULT")]
    W(f"| US {us} | out/v8/{name} | {dates[0] if dates else '?'} | {dates[-1] if dates else '?'} | {grab(V / name, r'^pairs checked')} | {grab(V / name, r'^check_thin:')} | {res[-1] if res else 'no RESULT line'} | {ex[-1] if ex else 'no exit line'} |")
W("")
W(Path(V / "notes_c2.md").read_text())
W("### c.3 Smallest clearance per ribbon pair group and size (out/v8/ribbon_table.py reads the RIBBON-CLEARANCE lines of the logs above; mm)\n")
W(subprocess.run([sys.executable, str(V / "ribbon_table.py")], capture_output=True, text=True).stdout)
W(Path(V / "notes_c4.md").read_text())
for part in ("notes_d.md", "notes_e.md"):
    W(Path(V / part).read_text())
# ---- f
W("## f. Named test: the ribbons as drawn\n")
W(Path(V / "notes_f.md").read_text())
W("Passing run (US 9 default, the real check, log out/v8/v8_us9_default.log), the test's own lines:\n")
W(fence(block(V / "v8_us9_default.log", r"^band circuit")))
W("\nBroken copy: out/v8/broken_trunk/thin.py differs from thin.py in ONE place (diff below); the named test is run on it by out/v8/broken_trunk/broken_named_test.py (log out/v8/broken_trunk/named_test.log).\n")
d = subprocess.run(["diff", str(T / "thin.py"), str(V / "broken_trunk" / "thin.py")], capture_output=True, text=True).stdout
W(fence(d.strip()))
W(fence(block(V / "broken_trunk" / "named_test.log", r"FAIL|findings|^RESULT|^exit|^BAND")))
W("")
W(Path(V / "notes_g.md").read_text())
W("### g.1 placement.csv\n")
d = subprocess.run(["diff", str(V / "placement_v7_before.csv"), str(T / "placement.csv")], capture_output=True, text=True).stdout
changed = [l.split(",")[0].replace("> ", "").replace("< ", "") for l in d.splitlines() if l[:2] in ("< ", "> ")]
W("Rows that differ from out/v8/placement_v7_before.csv (names only; `diff` of the two files): " + ", ".join(sorted(set(changed))) + ".\n")
W("### g.2 Maker files of the ribbons (exporter out/v8/export_ribbons.py, derived from out/v7-export/export_size.py: same emit(), same fresh copy and solid-count and volume checks)\n")
tot = []
for us in (7, 8, 9, 10, 11, 12, 13):
    tot.append(block(V / f"export_flex_us{us}.log", r"^STEP flex-tail|^exit"))
W(fence("\n".join(tot)))
W("")
W("### g.3 Path length of the delivered STEP files against the boards (out/v8/measure_step_v8.py, log out/v8/measure_step_v8.log)\n")
W(fence("\n".join(lines(V / "measure_step_v8.log"))))
W("")
W("### g.4 check_band.py (command: `design/ecad/ring/pcb/run_kipy.sh design/ecad/band/check_band.py`)\n")
W(f"Early look before the exports (log out/v8/check_band_early.log): `{grab(V / 'check_band_early.log', r'^RESULT')}`, `{grab(V / 'check_band_early.log', r'^exit')}`. Final run after the exports (log out/v8/check_band_final.log): `{grab(V / 'check_band_final.log', r'^RESULT')}`, `{grab(V / 'check_band_final.log', r'^exit')}`.\n")
W(Path(V / "notes_g2.md").read_text())
W(Path(V / "notes_h.md").read_text())
W(Path(V / "notes_end.md").read_text())
W("")
W(Path(V / "notes_result.md").read_text().strip())
(T / "band-fit-notes.md").write_text("\n".join(out) + "\n")
print("written", T / "band-fit-notes.md")
