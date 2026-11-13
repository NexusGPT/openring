"""audit.py <file> [<file> ...]: pulls every number, path, 'file line N' citation and quoted text out of the given files by
itself and prints the evidence line each matches in the saved evidence (check.log, logs/*, placement.csv, cited files).
Prints NO MATCH for each claim it cannot find. Last line: counts."""
import re
import sys
from pathlib import Path

ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix()))
HERE = ROOT / "design/mech/light-path"
EVID = [HERE / "check.log"] +sorted((HERE / "logs").glob("*.log")) + sorted((HERE / "logs").glob("*.txt")) + [
    ROOT / "design/mech/thin/placement.csv", HERE / "check_light_path.py", HERE / "visibility_calc.py", ROOT / "design/parts/research-reverse-led.md", ROOT / "design/mech/mic-path/mic-path.md"]
EVID = [f for f in EVID if not f.name.startswith(("audit_", "expected_", "compare_", "final_reply"))]   # never match a claim against my own claims
ev = []
for f in EVID:
    try:
        for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            ev.append((f, i, line))
    except Exception as e:
        print(f"cannot read {f}: {e}")
CITED = {"thin-notes.md": ROOT / "design/mech/thin/thin-notes.md", "thin.py": ROOT / "design/mech/thin/thin.py",
         "check_thin.py": ROOT / "design/mech/thin/check_thin.py", "placement.csv": ROOT / "design/mech/thin/placement.csv",
         "architecture.md": ROOT / "design/architecture.md", "bom.csv": ROOT / "design/bom.csv",
         "main-board.md": ROOT / "design/mfg/specs/main-board.md", "cover-glass.md": ROOT / "design/mfg/specs/cover-glass.md",
         "make_netlist.py": ROOT / "design/ecad/ring/make_netlist.py", "parts.csv": ROOT / "design/ecad/ring/parts.csv",
         "netlist.csv": ROOT / "design/ecad/ring/netlist.csv", "build_board.py": ROOT / "design/ecad/ring/pcb/build_board.py",
         "sch-notes.md": ROOT / "design/ecad/ring/sch-notes.md", "ring.kicad_pcb": ROOT / "design/ecad/ring/pcb/ring.kicad_pcb", "mic-path.md": ROOT / "design/mech/mic-path/mic-path.md"}
n_claims = n_ok = 0
for src in sys.argv[1:]:
    text = Path(src).read_text()
    print(f"===== {src}")
    if "—" in text:
        print("STYLE em dash found")
    # 1. numbers with a decimal point or 3+ digits (small integers like section numbers are skipped)
    nums = sorted(set(re.findall(r"(?<![\w.])[+-]?\d+\.\d+|(?<![\w.])\d{3,}(?![\w.])", text)))

    def matches(claim, line):
        """claim matches a number in the line when equal after rounding the line's number to the claim's decimals"""
        d = len(claim.split(".")[1]) if "." in claim else 0
        v = abs(float(claim))
        for e in re.findall(r"\d+\.\d+|\d+", line):
            if round(float(e), d) == round(v, d) and len(e.split(".")[0]) == len(claim.lstrip("+-").split(".")[0]):
                return True
        return False

    for n in nums:
        n_claims += 1
        hit = next(((f, i, l) for f, i, l in ev if matches(n, l)), None)
        if hit:
            n_ok += 1
            print(f"NUM {n}: {hit[0].name}:{hit[1]}: {hit[2].strip()[:110]}")
        else:
            print(f"NUM {n}: NO MATCH in evidence")
    # 2. citations '<file> line N' or 'lines N and M' / 'N to M'
    for m in re.finditer(r"([\w.-]+\.(?:md|py|csv|kicad_pcb)) lines? (\d+)(?: (?:and|to) (\d+))?", text):
        n_claims += 1
        f = CITED.get(m.group(1))
        if not f:
            print(f"CITE {m.group(0)}: file not in the cited list")
            continue
        lines = f.read_text(errors="replace").splitlines()
        a = int(m.group(2))
        b = int(m.group(3)) if m.group(3) else a
        ok = 1 <= a <= len(lines) and b <= len(lines)
        n_ok += ok
        shown = " | ".join(lines[k - 1].strip()[:90] for k in sorted({a, b}) if 1 <= k <= len(lines))
        print(f"CITE {m.group(0)}: {'' if ok else 'OUT OF RANGE '}{shown}")
    # 3. paths
    for p in sorted(set(x.rstrip(".") for x in re.findall(r"(?:logs|img|tools)/[\w.-]+|light_kb_[\w.-]+\.pdf|check\.log|check_light_path\.py|derived\.py|visibility_calc\.py|glass_probe\.py", text))):
        n_claims += 1
        cands = [HERE / p, ROOT / "design/datasheets" / p]
        ok = any(c.exists() for c in cands)
        n_ok += ok
        print(f"PATH {p}: {'exists' if ok else 'MISSING'}")
    # 4. quoted text in double quotes: look for it in the evidence and in cited files
    for q in sorted(set(re.findall(r"\"([^\"|]{6,80})\"", text))):
        n_claims += 1
        pool = [l for _, _, l in ev] + [l for f in CITED.values() for l in f.read_text(errors="replace").splitlines()]
        core = q.split(" ... ")[0].rstrip(".").strip()[:40]
        ok = any(core in l for l in pool)
        n_ok += ok
        print(f"QUOTE \"{q[:60]}\": {'found' if ok else 'NO MATCH (check by eye: datasheet image or my own new text)'}")
print(f"AUDIT claims checked: {n_claims}, matched: {n_ok}, unmatched: {n_claims - n_ok}")
