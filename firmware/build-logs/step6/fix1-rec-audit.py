"""fix1 (recorder) final audit: every line citation and every quoted text of the final reply, matched against the saved files.
Usage: python3 -B -I fix1-rec-audit.py <firmware folder>"""
import pathlib
import re
import sys

fw = pathlib.Path(sys.argv[1])
d = fw / "build-logs/step6"
reply = (d / "fix1-rec-final-reply.md").read_text()
logs = {n: (d / n).read_text().splitlines() for n in ("fix1-rec-u2.log", "fix1-rec-u3.log", "fix1-rec-s5.log", "fix1-rec-c1.log", "fix1-rec-c2.log")}
corpus = "\n".join((d / n).read_text() for n in sorted(p.name for p in d.glob("fix1-rec-*")) if (d / n).is_file()
                   and n != "fix1-rec-final-reply.md" and not n.endswith(".py"))
corpus += (fw / "docs/recorder-notes.md").read_text()
for f in ("modules/ring_rhw/include/ring_rhw/rrec_spec.h", "modules/ring_recorder/src/rrec.c",
          "modules/ring_screens/src/rscr.c"):
    corpus += (fw / f).read_text()
checked = bad = 0
# 1. line citations: l.N after the last named log
cur = "fix1-rec-u2.log"
for tok in re.finditer(r"(fix1-rec-u2\.log|fix1-rec-u3\.log|fix1-rec-s5\.log|fix1-rec-c1\.log|fix1-rec-c2\.log)|(?<!FW )l\.(\d+)((?:, \d+)*)", reply):
    if tok.group(1):
        cur = tok.group(1)
        continue
    nums = [int(tok.group(2))] + [int(x) for x in re.findall(r"\d+", tok.group(3) or "")]
    for n in nums:
        checked += 1
        line = logs[cur][n - 1] if 0 < n <= len(logs[cur]) else None
        ok = line is not None and re.search(r"RESULT|UNIT PASS|passed|exit|warnings|named case|FAIL|PASS|pictures|unmount: ", line)
        bad += 0 if ok else 1
        print(f"{'OK ' if ok else 'BAD'} {cur} l.{n}: {line[:150] if line else None}")
# 2. quoted texts in backticks
for q in re.findall(r"`([^`]+)`", reply):
    if "/" in q and not q.startswith("UNIT") and (fw / q).exists():
        checked += 1
        print(f"OK  path exists: {q}")
        continue
    checked += 1
    found = q in corpus or (fw / "build-logs/step6" / q).exists()
    bad += 0 if found else 1
    print(f"{'OK ' if found else 'BAD'} quoted: {q[:120]}")
# 3. counts
u3 = logs["fix1-rec-u3.log"]
for label, val, actual in (
        ("changed files", 36, int(re.search(r"FILES CHANGED OR ADDED: (\d+)", (d / "fix1-rec-diffs.txt").read_text()).group(1))),
        ("checklist ticked", 36, (d / "fix1-rec-CHECKLIST.md").read_text().count("- [x]")),
        ("cases per board in u3", 53, 53 if sum("53 of 53 executed test cases passed" in l for l in u3) == 2 else 0),
        ("cases per board in s5", 53, 53 if sum("53 of 53 executed test cases passed" in l for l in logs["fix1-rec-s5.log"]) == 2 else 0),
        ("records 0x0290 in u3", 2, int(re.search(r"unmount: (\d+) records 0x0290", "\n".join(u3)).group(1))),
        ("tries in u2 (one record per try)", 11, int(re.search(r"unmount: (\d+) failed unmounts reported", logs["fix1-rec-u2.log"][7578]).group(1))),
        ("tries in s5 second record", 6, int(re.search(r"record 2: errno 0, state CHARGING, try (\d+)", "\n".join(logs["fix1-rec-s5.log"])).group(1))),
        ("headers lines removed", 0, sum(int(x) for x in re.findall(r"lines removed: (\d+)", (d / "fix1-rec-headers-check.txt").read_text())))):
    checked += 1
    ok = val == actual
    bad += 0 if ok else 1
    print(f"{'OK ' if ok else 'BAD'} count {label}: reply {val}, saved {actual}")
print(f"AUDIT {checked} claims checked, {bad} without a match")
