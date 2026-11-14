#!/usr/bin/env python3
"""Every chip pin named in design/firmware.md next to a net name, against the netlist rows of U1.
Usage: python3 fw_pin_compare.py <firmware.md> <netlist.csv>
Prints one line per (line number, net, pin) pair found as "<NET> P<port>.<pin>" or "<NET> (P<port>.<pin>" and its
verdict SAME / DIFFERENT (netlist pin) / NOT A U1 NET; then every pin named alone with the netlist's net of that pin."""
import csv
import re
import sys

fw, net = sys.argv[1], sys.argv[2]
pin2net, net2pins = {}, {}
for r in csv.DictReader(open(net, newline="")):
    if r["reference"] == "U1" and re.match(r"P\d\.\d+$", r["pin_name"]):
        pin2net[r["pin_name"]] = r["net"]
        net2pins.setdefault(r["net"], []).append(r["pin_name"])
pair = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\s*,?\s*\(?\s*(P\d\.\d{2})\b")
alone = re.compile(r"\b(P\d\.\d{2})\b")
same = diff = other = 0
for n, line in enumerate(open(fw), 1):
    for m in pair.finditer(line):
        name, pin = m.group(1), m.group(2)
        if name in net2pins:
            if pin in net2pins[name]:
                same += 1
                print("l.%d SAME %s %s" % (n, name, pin))
            else:
                diff += 1
                print("l.%d DIFFERENT %s firmware.md %s netlist %s" % (n, name, pin, ",".join(net2pins[name])))
        else:
            other += 1
            print("l.%d NOT A U1 NET %s %s (netlist net of %s: %r)" % (n, name, pin, pin, pin2net.get(pin)))
    for m in alone.finditer(line):
        pin = m.group(1)
        print("l.%d PIN %s netlist net %r" % (n, pin, pin2net.get(pin, "no U1 row")))
print("fw_pin_compare: SAME %d DIFFERENT %d NOT-A-U1-NET %d" % (same, diff, other))
