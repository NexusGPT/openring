"""For each #define of rrec_spec.h that cites "FW l.N" and has a plain number, check that the number (or its form with
thousands commas, or its hex) appears on one of the cited lines of design/firmware.md. Prints every define with the
lines it checked and MATCH or NOMATCH. Usage: python3 -I u0-check-spec-lines.py <project root>"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
fw = (root / "design/firmware.md").read_text().split("\n")
src = (root / "firmware/modules/ring_rhw/include/ring_rhw/rrec_spec.h").read_text().split("\n")
n_ok = n_bad = n_skip = 0
for i, line in enumerate(src, 1):
    m = re.match(r"#define\s+(\w+)\s+(\(?[0-9xXa-fA-F]+u?(?:\s*\*\s*1024u)?\)?|\(1u << \d\))\s*/\*(.*)", line)
    if not m:
        continue
    name, val, comment = m.groups()
    cites = [int(x) for x in re.findall(r"l\.(\d+)", comment)]
    if not cites:
        n_skip += 1
        print(f"SKIP {name} (no FW line cited) rrec_spec.h:{i}")
        continue
    v = val.strip("()").replace("u", "")
    forms = set()
    if "<<" in v:
        n_skip += 1
        print(f"SKIP {name} (bit; checked by hand) cites {cites}")
        continue
    if "*" in v:
        k = int(v.split("*")[0].strip())
        forms |= {f"{k} KB"}
    elif v.lower().startswith("0x"):
        num = int(v, 16)
        forms |= {v, f"0x{num:08X}", f"0x{num:X}", f"0x{num:02X}", f"0x{num:04X}", f"{num:,}"}
    else:
        num = int(v)
        forms |= {str(num), f"{num:,}"}
    hit = [c for c in cites if any(f in fw[c - 1] for f in forms)]
    if hit:
        n_ok += 1
        print(f"MATCH {name} = {val} on FW line(s) {hit} (cited {cites})")
    else:
        n_bad += 1
        print(f"NOMATCH {name} = {val} cited {cites}: " + " | ".join(fw[c - 1][:140] for c in cites))
print(f"checked {n_ok + n_bad} defines with a number: {n_ok} MATCH, {n_bad} NOMATCH, {n_skip} SKIP")
