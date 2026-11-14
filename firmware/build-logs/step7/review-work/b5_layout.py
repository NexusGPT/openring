#!/usr/bin/env python3
"""Reviewer's layout check (step 7 review, B5): reads the partition and RAM nodes from the board dts text and checks
overlap, fit and the design/firmware.md 9.2 values. Usage: b5_layout.py <board .dts>"""
import re
import sys

src = open(sys.argv[1]).read()


def size(expr):
    m = re.match(r"DT_SIZE_K\((\d+)\)", expr.strip())
    return int(m.group(1)) * 1024 if m else int(expr.strip(), 0)


parts = []
for m in re.finditer(r"(\w+): partition@\w+ \{.*?reg = <(0x[0-9a-f]+) (DT_SIZE_K\(\d+\)|0x[0-9a-f]+)>;", src, re.S):
    parts.append((m.group(1), int(m.group(2), 16), size(m.group(3))))
spec = {"boot_partition": (0x0, 64 * 1024), "slot0_partition": (0x10000, 976 * 1024),
        "slot1_partition": (0x104000, 976 * 1024), "storage_partition": (0x1F8000, 20 * 1024)}
rram = 2036 * 1024
for name, a, s in parts:
    sa, ss = spec[name]
    print("%s addr 0x%06x size %d end 0x%06x | spec 9.2 addr 0x%06x size %d -> %s" %
          (name, a, s, a + s, sa, ss, "SAME" if (a, s) == (sa, ss) else "DIFFERENT"))
ps = sorted(parts, key=lambda p: p[1])
for (n1, a1, s1), (n2, a2, s2) in zip(ps, ps[1:]):
    print("%s ends 0x%06x, %s starts 0x%06x -> %s" % (n1, a1 + s1, n2, a2,
          "OVERLAP" if a1 + s1 > a2 else ("GAP %d" % (a2 - a1 - s1) if a2 > a1 + s1 else "adjacent")))
end = max(a + s for _, a, s in parts)
print("last end 0x%06x, RRAM 2036 KB = 0x%06x -> %s" % (end, rram, "fits" if end <= rram else "DOES NOT FIT"))

m = re.search(r"&cpuapp_sram \{\s*reg = <(0x[0-9a-f]+) (DT_SIZE_K\(\d+\))>", src)
sa, ss = int(m.group(1), 16), size(m.group(2))
m = re.search(r"memory@(\w+) \{.*?reg = <(0x[0-9a-f]+) (0x[0-9a-f]+)>", src, re.S)
ra, rs = int(m.group(2), 16), int(m.group(3), 16)
print("cpuapp_sram 0x%08x..0x%08x (%d bytes); retained 0x%08x..0x%08x (%d bytes)" % (sa, sa + ss, ss, ra, ra + rs, rs))
print("overlap sram/retained: %s; retained ends inside the SoC's 511 KB (0x%08x): %s; retained size 1024: %s" % (
    "YES" if ra < sa + ss and sa < ra + rs else "no", 0x20000000 + 511 * 1024,
    "yes" if ra + rs <= 0x20000000 + 511 * 1024 else "NO", "yes" if rs == 1024 else "NO"))
