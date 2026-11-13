"""List every function of every public header of step 6 (prototypes and function-pointer members) with the
"FW l.N" citations of its own comment (the comment block right above it, or on its line). Prints a markdown table and
a count of functions without a citation. Usage: python3 -I u0-map-functions.py <firmware folder>"""
import pathlib
import re
import sys

fw = pathlib.Path(sys.argv[1])
HEADERS = [
    "modules/ring_rhw/include/ring_rhw/rhw.h",
    "modules/ring_rhw/include/ring_rhw/rhw_sim.h",
    "modules/ring_rhw/include/ring_rhw/rrec_spec.h",
    "modules/ring_store/include/ring_store/rst.h",
    "modules/ring_audio/include/ring_audio/rau.h",
    "modules/ring_xfer/include/ring_xfer/rxf.h",
    "modules/ring_power/include/ring_power/rpw.h",
    "modules/ring_motor/include/ring_motor/rmo.h",
    "modules/ring_sys/include/ring_sys/rsy.h",
    "modules/ring_factory/include/ring_factory/rfa.h",
    "modules/ring_recorder/include/ring_recorder/rrec.h",
]
proto = re.compile(r"^(?:extern\s+)?(?:const\s+)?(?:struct\s+|enum\s+)?\w+[\s\*]+\**(\w+)\((?!\*)")
member = re.compile(r"\(\*(\w+)\)\(")
typedef = re.compile(r"^typedef .*\(\*(\w+)\)\(")
total = 0
missing = 0
print("| Header | Function | Line | FW lines cited |")
print("|---|---|---|---|")
for h in HEADERS:
    lines = (fw / h).read_text().split("\n")
    struct = None
    for i, line in enumerate(lines):
        s = line.strip()
        m = re.match(r"^struct (\w+) \{", s)
        if m:
            struct = m.group(1)
        if s.startswith("};"):
            struct = None
        name = None
        mt = typedef.match(s)
        mm = member.search(s)
        mp = proto.match(line) if not line.startswith((" ", "\t", "#", "/", "*")) else None
        if mt:
            name = "typedef " + mt.group(1)
        elif mm and struct:
            name = f"{struct}.{mm.group(1)}"
        elif mp and s.endswith((";", ",")) is not None and "(" in s:
            name = mp.group(1)
        if name is None:
            continue
        # the comment: this line's own comment, and the block of comment lines right above
        text = line
        j = i - 1
        while j >= 0 and (lines[j].strip().startswith(("/*", "*", "*/")) or lines[j].strip().endswith("*/")):
            text = lines[j] + " " + text
            if lines[j].strip().startswith("/*"):
                break
            j -= 1
        # a function whose arguments continue on the next lines
        k = i + 1
        while not re.sub(r"/\*.*?\*/", "", lines[k - 1]).rstrip().endswith((";", "{")) and k < len(lines):
            text += " " + lines[k]
            k += 1
        cites = sorted(set(int(x) for x in re.findall(r"FW l\.(\d+)|, l\.(\d+)|\bl\.(\d+)", text) for x in x if x))
        total += 1
        if not cites:
            missing += 1
        print(f"| {h.split('/')[-1]} | `{name}` | {h.split('/')[-1]}:{i + 1} | {', '.join(str(c) for c in cites) or 'NONE'} |")
print()
print(f"functions: {total}; without a FW line in their own comment: {missing}")
