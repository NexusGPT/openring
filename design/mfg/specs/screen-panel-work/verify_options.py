"""Check every number of connection-options.md against the lines its own line cites, in that file's citation style:
`name` line N, `name` lines N to M, `name` lines N, M, name.log line N (short names resolved below).
Same matching rule as verify.py (numeric equality on the cited lines, sign ignored). Run:
python3 verify_options.py connection-options.md > logs/verify-options.log 2>&1"""
import re
import sys
from pathlib import Path

ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix()))
W = ROOT / "design/mfg/specs/screen-panel-work"
SHORT = {
    "calc.log": W / "logs/calc.log",
    "read_board2.log": W / "logs/read_board2.log",
    "placement.csv": ROOT / "design/mech/thin/out/v10/before/placement.csv",
    "thin.py": ROOT / "design/mech/thin/out/v10/before/thin.py",
    "screen-cable-study.md": ROOT / "design/wiring/screen-cable-study.md",
    "hotbar-joint.md": ROOT / "design/mfg/assembly/hotbar-joint.md",
    "lead-decisions.md": ROOT / "design/wiring/lead-decisions.md",
    "merged417flat-notes.md": ROOT / "design/look/s1/merged417flat-notes.md",
    "measure-flat-final-us9.log": ROOT / "design/look/s1/out/work-flat/measure-flat-final-us9.log",
    "placement-final.csv": ROOT / "design/ecad/ring/pcb/placement-final.csv",
    "assembly.md": ROOT / "design/mfg/assembly/assembly.md",
    "slim_tailor-toh095xvt-01-p4-8.txt": ROOT / "design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt",
}
REF = re.compile(r"`?([\w./-]+\.(?:log|csv|py|md|txt))`?(?:'s)?\s+(lines?)\s+((?:\d+(?:\s*(?:,|and|to)\s*\d+)*))")
NUM = re.compile(r"(?<![A-Za-z0-9_.+-])[-+]?\d+(?:\.\d+)?(?![A-Za-z0-9_]|\.\d)")
ANYNUM = re.compile(r"[-+]?\d+(?:\.\d+)?")


def resolve(name):
    base = name.split("/")[-1]
    if base in SHORT:
        return SHORT[base]
    p = ROOT / name
    return p if p.exists() else None


checked = missing = 0
lastcite = None
text = Path(sys.argv[1]).read_text().splitlines()
for i, line in enumerate(text, 1):
    cites = []
    for m in REF.finditer(line):
        p = resolve(m.group(1))
        if p is None:
            print(f"L{i}: CANNOT RESOLVE {m.group(1)}")
            continue
        L = p.read_text(errors="replace").splitlines()
        spec = m.group(3)
        nums = [int(x) for x in re.findall(r"\d+", spec)]
        if " to " in spec and len(nums) == 2:
            rng = range(nums[0], nums[1] + 1)
        else:
            rng = nums
        for n in rng:
            if 1 <= n <= len(L):
                cites.append(L[n - 1])
            else:
                print(f"L{i}: LINE OUT OF RANGE {m.group(0)}")
                missing += 1
    body = REF.sub(" ", line)
    body = re.sub(r"`[^`]*`", " ", body)
    body = re.sub(r"^\s*\d+\.\s", " ", body)
    body = re.sub(r"^#+.*", " ", body)
    body = re.sub(r"^RESULT.*", " ", body)
    pool_txt = "\n".join(cites)
    pool = {abs(float(x)) for x in ANYNUM.findall(pool_txt)}
    for n in NUM.findall(body):
        checked += 1
        v = abs(float(n))
        if not (v in pool or n in pool_txt):
            missing += 1
            print(f"L{i}: NOT FOUND {n} (cites {len(cites)} lines) | {line[:120]}")
print(f"values checked {checked}, not found {missing}")
