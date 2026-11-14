#!/usr/bin/env python3
"""Sums the ring build's largest RAM symbols (ring-ram-symbols.txt: the 80 largest, from stage ring-ram of the full run)
into the lines of design/firmware.md 4.6 and prints the table and the symbols of each line.
Usage: python3 ram_budget.py ring-ram-symbols.txt <total RAM used in bytes, from the linker report>"""
import re
import sys

path, total = sys.argv[1], int(sys.argv[2])
# (budget line, budget bytes, rule on "name file") in the order of FW 4.6
LINES = [
    ("PDM DMA blocks, pdm20, 8 x 1,024", 8192, r"rau_hw_real\.c"),
    ("Chunk ring, 3 x 33,280", 99840, r"^ring\s.*rau\.c"),
    ("USB read buffers, 2 x 16,384", 32768, r"^(ctx|buf_a|buf_b)\s.*rxf_class\.c"),
    ("USB stack buffer pool", 8192, r"udc_common\.c|udc_dwc2\.c"),
    ("Bluetooth host and controller", 40960, r"subsys/bluetooth|nrf/subsys/bluetooth|mpsl|sdc_|hci_driver|nrf/subsys/mpsl"),
    ("Display draw buffers, 2 x 120 x 40 x 2", 19200, r"^(vdb|rot)\s.*rscr_draw\.c"),
    ("Display library heap", 24576, r"lvgl_mem\.c"),
    ("Thread stacks (10 threads)", 24576, r"stack"),
    ("Kernel, drivers, C library data", 16384, None),
    ("Log buffer", 4096, r"log_"),
    ("Crash record, retained RAM", 1024, None),
    ("Fuel gauge state", 1024, r"fuel_gauge"),
    ("Recordings list cache, 256 x 64", 16384, r"^rec_store\s.*rst\.c"),
    ("System heap", 8192, r"kheap__system_heap"),
]
NOT_IN_BUDGET = [
    ("memory display picture (stand-in for the panel)", r"^fb\s.*memdisplay\.c"),
    ("storage chunk-size work buffers scratch, scratch2", r"^scratch2?\s.*rst\.c"),
]
syms = []
for line in open(path):
    if line.startswith("#") or not line.strip():
        continue
    parts = line.rstrip("\n").split(None, 3)
    addr, size, typ, rest = parts[0], int(parts[1], 16), parts[2], parts[3] if len(parts) > 3 else ""
    syms.append((size, rest))
used = set()
rows = []
for name, budget, rule in LINES:
    s = 0
    hits = []
    if rule:
        for i, (size, rest) in enumerate(syms):
            if i in used:
                continue
            if re.search(rule, rest):
                used.add(i)
                s += size
                hits.append("%s %d" % (rest.split()[0], size))
    rows.append((name, budget, s, hits))
extra = []
for name, rule in NOT_IN_BUDGET:
    s = 0
    hits = []
    for i, (size, rest) in enumerate(syms):
        if i not in used and re.search(rule, rest):
            used.add(i)
            s += size
            hits.append("%s %d" % (rest.split()[0], size))
    extra.append((name, s, hits))
rest_sum = sum(size for i, (size, _) in enumerate(syms) if i not in used)
listed = sum(size for size, _ in syms)
print("| budget line of 4.6 | budget | measured | difference |")
print("|---|---|---|---|")
for name, budget, s, hits in rows:
    print("| %s | %d | %d | %+d |" % (name, budget, s, s - budget))
for name, s, hits in extra:
    print("| (not in 4.6) %s | 0 | %d | %+d |" % (name, s, s))
print("| (not sorted) the other symbols of the 80 largest | 0 | %d | %+d |" % (rest_sum, rest_sum))
print("| (not listed) every RAM symbol below the 80 largest | 0 | %d | %+d |" % (total - listed, total - listed))
print("| **Total** (linker: RAM used) | 305408 | %d | %+d |" % (total, total - 305408))
print()
for name, budget, s, hits in rows:
    print("%s: %s" % (name, ", ".join(hits) or "none in the 80 largest"))
for name, s, hits in extra:
    print("%s: %s" % (name, ", ".join(hits)))
print("other symbols of the 80 largest: %s" % ", ".join(
    "%s %d" % (rest.split()[0], size) for i, (size, rest) in enumerate(syms) if i not in used))
print("ram_budget: %d symbols read, %d bytes listed, total %d" % (len(syms), listed, total))
