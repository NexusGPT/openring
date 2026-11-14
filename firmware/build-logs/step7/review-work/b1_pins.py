#!/usr/bin/env python3
"""Reviewer's own pin comparison (step 7 review, B1). Reads the board source files as text (not the author's table,
not the built zephyr.dts) and the netlist rows of U1; prints one line per U1 port-pin signal and per pin use in the files.
Usage: b1_pins.py <netlist.csv> <file> [<file> ...]"""
import csv
import re
import sys

net_path, files = sys.argv[1], sys.argv[2:]
u1 = {}          # port pin text -> (net, ball)
for r in csv.DictReader(open(net_path, newline="")):
    if r["reference"] == "U1":
        m = re.match(r"P(\d+)\.(\d+)$", r["pin_name"])
        if m:
            u1["P%d.%02d" % (int(m.group(1)), int(m.group(2)))] = (r["net"], r["pin_number"])

uses = []        # (file, line no, pin text, net comment, kind)
for f in files:
    for no, line in enumerate(open(f), 1):
        for m in re.finditer(r"<&gpio(\d+)\s+(\d+)\b", line):
            uses.append((f, no, "P%d.%02d" % (int(m.group(1)), int(m.group(2))), line.strip(), "gpio"))
        for m in re.finditer(r"NRF_PSEL\((\w+),\s*(\d+),\s*(\d+)\)", line):
            uses.append((f, no, "P%d.%02d" % (int(m.group(2)), int(m.group(3))), line.strip(), m.group(1)))

ok = bad = 0
seen = {}
for f, no, pin, text, kind in uses:
    net, ball = u1.get(pin, (None, None))
    cm = re.search(r"/\*\s*([A-Z0-9_]+)", text)
    named = cm.group(1) if cm else None
    if net is None:
        print("NOT-IN-NETLIST %s:%d %s %s" % (f.split("/")[-1], no, pin, kind)); bad += 1
    elif net == "":
        print("NO-CONNECT-PIN-USED %s:%d %s ball %s" % (f.split("/")[-1], no, pin, ball)); bad += 1
    elif named != net:
        print("COMMENT-NET-DIFFERS %s:%d %s netlist %s comment %s" % (f.split("/")[-1], no, pin, net, named)); bad += 1
    else:
        print("MATCH %s:%d %s %s netlist %s ball %s" % (f.split("/")[-1], no, pin, kind, net, ball)); ok += 1
    seen.setdefault(net, []).append(pin)

signals = sorted(set(n for n, b in u1.values() if n))
missing = [s for s in signals if s not in seen]
print("U1 port-pin signals in netlist: %d; found in board files: %d; not found: %s" %
      (len(signals), len(signals) - len(missing), " ".join(missing) or "none"))
print("pin uses read: %d, match %d, problems %d" % (len(uses), ok, bad))
