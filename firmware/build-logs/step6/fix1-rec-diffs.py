"""fix1 (recorder): the full diff of every file fix round 1 changed or added, against the base copies taken before the first
edit (build-logs/step6/fix1-rec-base/). Usage: python3 -B -I fix1-rec-diffs.py <firmware folder> > fix1-rec-diffs.txt"""
import difflib
import pathlib
import sys

fw = pathlib.Path(sys.argv[1])
base = fw / "build-logs/step6/fix1-rec-base"
# every file of the base copy, and every file now under the two folders this round owns in full (new files)
files = {str(f.relative_to(base)) for f in base.rglob("*") if f.is_file() and "__pycache__" not in f.parts}
for r in ("modules/ring_recorder", "tests/recorder"):
    files |= {str(f.relative_to(fw)) for f in (fw / r).rglob("*") if f.is_file() and "__pycache__" not in f.parts}
changed = 0
for rel in sorted(files):
    a = base / rel
    b = fw / rel
    ta = a.read_text().splitlines(keepends=True) if a.exists() else []
    tb = b.read_text().splitlines(keepends=True) if b.exists() else []
    if ta == tb:
        continue
    changed += 1
    kind = "new" if not a.exists() else ("removed" if not b.exists() else "changed")
    print(f"##### {kind}: {rel}")
    sys.stdout.writelines(difflib.unified_diff(ta, tb, f"base/{rel}", rel, n=1))
print(f"FILES CHANGED OR ADDED: {changed}")
