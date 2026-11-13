"""print the FAIL lines, the test-17 result per size and the last lines of a check log. usage: summarize_check.py <log>"""
import re
import sys

L = open(sys.argv[1]).read().split("\n")
for l in L:
    if l.startswith("FAIL"):
        print(l[:220])
for l in L:
    m = re.match(r"17 US (\d+): lifted .*?smallest free space ([\d.]+) mm to (.+?) at lift ([\d.]+) mm, next ([\d.]+) to (.+?) at ([\d.]+);"
                 r" seat contacts smallest ([\d.]+) mm \((.+?) at ([\d.]+)\); (\d+) exact.*?boundaries meet: (\d+) \((.*?)\), largest common volume ([\d.]+) mm3 \(limit [\d.]+\): (\w+)", l)
    if m:
        print("US %s: free %s mm to %s at lift %s; next %s to %s at %s; seat %s (%s at %s); exact %s; touches %s (%s); common %s; %s" % m.groups())
for l in L[-4:]:
    print(l[:300])
