#!/usr/bin/env python3
"""Final audit of step7-review.md: pulls every citation (file name followed by line numbers, `l.N` after the last named
file on the same line, `path:N`), every review-work file named, and prints the cited line; re-runs the counts.
Usage: audit.py <review.md> <project root>"""
import os
import re
import subprocess
import sys

rev, root = sys.argv[1], sys.argv[2]
W = os.path.join(root, "firmware/build-logs/step7/review-work")
S = os.path.join(root, "firmware/build-logs/step7")
files = {
    "s7-full1.console": os.path.join(S, "s7-full1.console"),
    "s7-build1.console": os.path.join(S, "s7-build1.console"),
    "s7-build2.console": os.path.join(S, "s7-build2.console"),
    "s7-explore3.console": os.path.join(S, "s7-explore3.console"),
    "dts": os.path.join(root, "firmware/boards/ringrec/ringrec_nrf54lm20a_cpuapp.dts"),
    "ringrec_nrf54lm20a_cpuapp.dts": os.path.join(root, "firmware/boards/ringrec/ringrec_nrf54lm20a_cpuapp.dts"),
    "pinctrl.dtsi": os.path.join(root, "firmware/boards/ringrec/ringrec_nrf54lm20a_cpuapp-pinctrl.dtsi"),
    "ringrec_nrf54lm20a_cpuapp-pinctrl.dtsi": os.path.join(root, "firmware/boards/ringrec/ringrec_nrf54lm20a_cpuapp-pinctrl.dtsi"),
    "netlist.csv": os.path.join(root, "design/ecad/ring/netlist.csv"),
    "README": os.path.join(root, "firmware/README.md"),
    "README.md": os.path.join(root, "firmware/README.md"),
    "board-notes": os.path.join(W, "board-notes-as-read.md"),
    "board-notes.md": os.path.join(W, "board-notes-as-read.md"),
    "sys-notes.md": os.path.join(root, "firmware/docs/sys-notes.md"),
    "recorder-notes.md": os.path.join(root, "firmware/docs/recorder-notes.md"),
    "FW": os.path.join(root, "design/firmware.md"),
    "firmware.md": os.path.join(root, "design/firmware.md"),
    "build_all.sh": os.path.join(root, "firmware/tools/build_all.sh"),
    "check_ring_pins.py": os.path.join(root, "firmware/tools/check_ring_pins.py"),
    "rhw.c": os.path.join(root, "firmware/modules/ring_rhw/src/rhw.c"),
    ".conf": os.path.join(root, "firmware/app/boards/ringrec_nrf54lm20a_cpuapp.conf"),
    "test_gesture.c": os.path.join(root, "firmware/tests/core/src/test_gesture.c"),
    "rrec_mics.c": os.path.join(root, "firmware/modules/ring_recorder/src/rrec_mics.c"),
}
cache = {}


def line(f, n):
    if f not in cache:
        cache[f] = open(files[f], errors="replace").read().split("\n")
    L = cache[f]
    return L[n - 1][:150] if 0 < n <= len(L) else "<OUT OF RANGE %d>" % len(L)


names = sorted(files, key=len, reverse=True)
pat_name = "|".join(re.escape(n) for n in names)
claims = 0
text = open(rev).read().split("\n")
for i, t in enumerate(text, 1):
    cur = None
    for m in re.finditer(r"(%s)|l\.(\d+)(?: to (\d+))?((?:, \d+)*)|:(\d+)(?: to `?:?(\d+))?" % pat_name, t):
        if m.group(1):
            cur = m.group(1)
            continue
        if cur is None:
            continue
        nums = []
        if m.group(2):
            a = int(m.group(2)); b = int(m.group(3)) if m.group(3) else a
            nums = [a, b] + [int(x) for x in re.findall(r"\d+", m.group(4) or "")]
        elif m.group(5):
            a = int(m.group(5)); b = int(m.group(6)) if m.group(6) else a
            nums = [a, b]
        for n in sorted(set(nums)):
            claims += 1
            print("review l.%d %s:%d -> %s" % (i, cur, n, line(cur, n)))
named = sorted(set(re.findall(r"`([\w.-]+\.(?:txt|md|py))`", "\n".join(text))))
for n in named:
    p = os.path.join(W, n)
    if os.path.exists(p):
        claims += 1
        last = open(p, errors="replace").read().rstrip("\n").split("\n")[-1][:150]
        print("evidence %s exists; last line: %s" % (n, last))
print("== recounts")
print("EQUAL lines:", open(os.path.join(W, "version-check.txt")).read().count("EQUAL "))
c = open(os.path.join(S, "s7-full1.console"), errors="replace").read().split("\n")
ends = [x for x in c if re.match(r"^=== stage .* end .* exit ", x)]
print("stage end lines:", len(ends), "not exit 0:", len([x for x in ends if not x.endswith("exit 0")]))
seg = c[29511:29578]
print("ring-pins NO NODE BY NATURE rows:", len([x for x in seg if x.startswith("NO NODE BY NATURE")]))
sig = set(x.split()[1] for x in seg if x.startswith("SAME "))
print("ring-pins SAME signals:", len(sig))
print("severity counts in findings table:", {s: len(re.findall(r"^\| S7-\d+ \| %s \|" % s, "\n".join(text), re.M))
                                            for s in ("blocker", "major", "minor", "note")})
print("bar verdicts:", re.findall(r"^\| (B\d) [^|]*\| (PASS|FAIL|NOT PROVEN) \|", "\n".join(text), re.M))
print("claims checked:", claims)
