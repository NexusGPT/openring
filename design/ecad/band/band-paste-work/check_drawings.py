#!/usr/bin/env python3
"""Check the text of the band drawings (pdftotext) for every land number with its net.
usage: check_drawings.py <dir with flexK-usN-drawing.pdf> <band-interface.md> <text out dir> [names ...]
Expected pairs are parsed from band-interface.md section 2 (tables J_BAND_B and J_BAND_A: | Land | Name | Net | ...), not from the
generator. A pair counts when the line 'LAND <n> = <NET>' is in the PDF text. FLEX1 also needs the motor mark '1 +: VMOT' and
FLEX2 the three tab names 'P+ tab: VBAT', 'NTC tab: NTC', 'P- tab: GND'."""
import os, re, subprocess, sys

src, md, out = sys.argv[1:4]
names = sys.argv[4:] or [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]
os.makedirs(out, exist_ok=True)
lines = open(md).read().splitlines()
tables, cur = {}, None
for ln in lines:
    if ln.startswith("J_BAND_B (FLEX2"):
        cur = "B"
    elif ln.startswith("J_BAND_A (FLEX1"):
        cur = "A"
    elif ln.startswith("Rules for the board layout"):
        cur = None
    elif cur and re.match(r"\| \d+ \|", ln):
        c = [x.strip() for x in ln.strip("|").split("|")]
        tables.setdefault(cur, []).append((c[0], c[2]))
print("pairs from band-interface.md: A", tables.get("A"), "B", tables.get("B"))
bad = 0
for n in names:
    k = n[4]
    pdf = os.path.join(src, n + "-drawing.pdf")
    txt = os.path.join(out, n + ".txt")
    r = subprocess.run(["pdftotext", "-layout", pdf, txt], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL {n}: pdftotext exit {r.returncode} {r.stderr.strip()}"); bad += 1; continue
    t = re.sub(r"[ \t]+", " ", open(txt).read())
    pairs = tables["A" if k == "1" else "B"]
    found = [(l, net) for l, net in pairs if re.search(rf"LAND {l} = {re.escape(net)}\b", t)]
    miss = [p for p in pairs if p not in found]
    marks = ["1 +: VMOT"] if k == "1" else ["P+ tab: VBAT", "NTC tab: NTC", "P- tab: GND"]
    mmiss = [m for m in marks if m not in t]
    ok = not miss and not mmiss and len(pairs) == (8 if k == "1" else 7)
    bad += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} {n}: land labels {len(found)} of {len(pairs)}, marks {len(marks) - len(mmiss)} of {len(marks)}"
          + (f"; missing {miss + mmiss}" if miss or mmiss else ""))
print(f"RESULT: {'PASS' if bad == 0 else 'FAIL'} drawings checked {len(names)}, failing {bad}")
sys.exit(0 if bad == 0 else 1)
