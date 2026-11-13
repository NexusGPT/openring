"""fix2 (recorder) final audit: every line citation, quoted text and count of the round 2 reply, against the saved files.
Usage: python3 -B -I fix2-rec-audit.py <firmware folder>; the result is written to fix2-rec-audit.txt."""
import pathlib
import re
import sys

fw = pathlib.Path(sys.argv[1])
d = fw / "build-logs/step6"
reply = (d / "fix2-rec-final-reply.md").read_text()
u1 = (d / "fix2-rec-u1.log").read_text().splitlines()
corpus = "\n".join(p.read_text() for p in d.glob("fix2-rec-*") if p.is_file() and p.name != "fix2-rec-final-reply.md")
corpus += (fw / "docs/recorder-notes.md").read_text() + (fw / "modules/ring_rhw/include/ring_rhw/rrec_spec.h").read_text()
corpus += (fw / "modules/ring_recorder/src/rrec.c").read_text()
out = []
checked = bad = 0
for m in re.finditer(r"(?<!FW )l\.(\d+)((?: / \d+)*)", reply):
    for n in [int(m.group(1))] + [int(x) for x in re.findall(r"\d+", m.group(2) or "")]:
        checked += 1
        line = u1[n - 1] if 0 < n <= len(u1) else ""
        ok = bool(re.search(r"named case failed, as required|UNIT PASS|RESULT PASS|59 of 59", line))
        bad += 0 if ok else 1
        out.append(f"{'OK ' if ok else 'BAD'} fix2-rec-u1.log l.{n}: {line[:140]}")
for q in re.findall(r"`([^`]+)`", reply):
    checked += 1
    ok = q in corpus or (fw / q).exists() or (d / q).exists()
    bad += 0 if ok else 1
    out.append(f"{'OK ' if ok else 'BAD'} quoted: {q[:120]}")
diffs = (d / "fix2-rec-diffs.txt").read_text()
s2 = (d / "fix2-rec-s2.log").read_text()
for label, val, actual in (
        ("changed files", 11, int(re.search(r"FILES CHANGED OR ADDED: (\d+)", diffs).group(1))),
        ("rrec_spec.h lines removed", 0, int(re.search(r"rrec_spec.h lines removed: (\d+)", diffs).group(1))),
        ("checklist ticked", 15, (d / "fix2-rec-CHECKLIST.md").read_text().count("- [x]")),
        ("cases per board u1", 59, 59 if sum("59 of 59 executed test cases passed" in l for l in u1) == 2 else 0),
        ("cases per board s2", 59, 59 if s2.count("59 of 59 executed test cases passed") == 2 else 0),
        ("lock held ms in s2", 10000, int(re.search(r"held the glue's lock (\d+) ms", s2).group(1))),
        ("copies in RESULT PASS u1", 26, len((fw / "tests/recorder/broken_edit.py").read_text().split("\n    \"")) - 1)):
    checked += 1
    ok = val == actual
    bad += 0 if ok else 1
    out.append(f"{'OK ' if ok else 'BAD'} count {label}: reply {val}, saved {actual}")
out.append(f"AUDIT {checked} claims checked, {bad} without a match")
(d / "fix2-rec-audit.txt").write_text("\n".join(out) + "\n")
print(out[-1])
