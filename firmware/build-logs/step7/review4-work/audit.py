# Audit of step7-review-4.md: prints the source line for each `file:line` citation and for each quoted log fragment
# found in f3-stages3.console, and lists quoted strings not found in the cited log.
import re, sys, os
review, fw = sys.argv[1], sys.argv[2]
txt = open(review).read()
files = {
    "rst_hw_real.c": fw + "/modules/ring_store/src/rst_hw_real.c",
    "rst.c": fw + "/modules/ring_store/src/rst.c",
    "rrec.c": fw + "/modules/ring_recorder/src/rrec.c",
    "rrec_boot.c": fw + "/modules/ring_recorder/src/rrec_boot.c",
    "rpw_hw_real.c": fw + "/modules/ring_power/src/rpw_hw_real.c",
    "rpw.c": fw + "/modules/ring_power/src/rpw.c",
    "rsy_hw_real.c": fw + "/modules/ring_sys/src/rsy_hw_real.c",
    "rrec_spec.h": fw + "/modules/ring_rhw/include/ring_rhw/rrec_spec.h",
    "rhw.h": fw + "/modules/ring_rhw/include/ring_rhw/rhw.h",
}
n = 0
for name, path in files.items():
    lines = open(path).read().split("\n")
    for m in re.finditer(r"`?" + re.escape(name) + r":(\d+)`?(?: to `?:(\d+)`?)?", txt):
        a = int(m.group(1)); b = int(m.group(2) or a)
        for k in (a, b):
            n += 1
            print("%s:%d | %s" % (name, k, lines[k - 1].strip()[:150]))
    for m in re.finditer(r"(?<![\w.])" + re.escape(name) + r"`?((?:, `?:\d+`?)+)", txt):
        for k in re.findall(r":(\d+)", m.group(1)):
            n += 1
            print("%s:%s | %s" % (name, k, lines[int(k) - 1].strip()[:150]))
log = open(fw + "/build-logs/step7/fix3/f3-stages3.console").read().split("\n")
for k in sorted(set(int(x) for x in re.findall(r"\bl\.(\d{4})\b", txt))):
    n += 1
    print("f3-stages3 l.%d | %s" % (k, log[k - 1][:150]))
for q in re.findall(r"`([^`]{12,})`", txt):
    if any(q in l for l in log):
        n += 1
        print("FOUND in f3-stages3: %s" % q[:100])
print("claims checked: %d" % n)
