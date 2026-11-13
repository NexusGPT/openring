"""electronics (electronics.json): blocks, links, pin plan, power budget.

Blocks are the pages of the wiring diagram (their own titles, from ring.kicad_sch, read by schematic.py). A link joins
two blocks that share a net: a net whose pins sit on two or more pages (netlist.csv for the pins, parts.csv for the
page of each reference). The pin plan is the table of architecture section 7, with the pins that section 16.6 turns
into spare test pads marked in the Notes cell. The power budget is the table of section 4 followed by the lines of
16.8 and 17.5, which replace its current figures (section 17 wins over 16, 16 over the rest).
The count of provisional pin numbers (rows of open-pins.csv that carry a pin number) goes into the status message,
because electronics.schema has no field for it.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import schematic as sch  # noqa: E402
import wiring  # noqa: E402
from lib import csvread, md, version  # noqa: E402
from lib.errors import SourceError  # noqa: E402

RECORD = "electronics"


def _nat(r):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", r)]


def build_links(net_rows, ref_sheet, order):
    """net_rows: [(net, ref)]; ref_sheet: {ref: page id}; order: page ids in page order.
    Returns [{from, to, nets}] for every pair of pages that share a net."""
    sheets = {}
    for net, ref in net_rows:
        sh = ref_sheet.get(ref)
        if sh and net:
            sheets.setdefault(net, set()).add(sh)
    pairs = {}
    for net in sorted(sheets):
        used = sorted(sheets[net], key=order.index)
        for i, a in enumerate(used):
            for b in used[i + 1:]:
                pairs.setdefault((a, b), []).append(net)
    return [{"from": a, "to": b, "nets": nets} for (a, b), nets in sorted(pairs.items(), key=lambda kv: (order.index(kv[0][0]), order.index(kv[0][1])))]


def pin_plan(text):
    t = md.table_after_heading(text, r"^7\.\s", level=2)
    if t is None:
        raise SourceError("architecture.md has no section 7 pin table", sch.ARCH)
    cols = ["Signal", "Pin", "Ball", "Notes"]
    if [c.lower() for c in t["columns"]] != [c.lower() for c in cols]:
        raise SourceError(f"architecture.md section 7 table has columns {t['columns']}", sch.ARCH)
    rows = [list(r) for r in t["rows"]]
    sec = md.section(text, r"^16\.6\b", level=3)
    if sec is not None:
        for raw in sec[2]:
            for sentence in re.split(r"(?<=\.)\s+", raw):
                if "spare" not in sentence:
                    continue
                for tok in re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", sentence):
                    for r in rows:
                        if r[0] == tok and "16.6" not in r[3]:
                            r[3] = (r[3] + "; " if r[3] else "") + "spare test pad (architecture 16.6)"
    return {"columns": cols, "rows": rows, "source": {"file": sch.ARCH, "line": t["line"]}}


def power_budget(text):
    t = md.table_after_heading(text, r"^4\.\s", level=2)
    if t is None:
        raise SourceError("architecture.md has no section 4 table", sch.ARCH)
    rows = [list(r) for r in t["rows"]]
    ncol = len(t["columns"])
    for num, level in (("16.8", 3), ("17.5", 3)):
        sec = md.section(text, rf"^{re.escape(num)}\b", level=level)
        if sec is None:
            continue
        for body in sec[2]:
            b = body.strip()
            if not b:
                continue
            b = re.sub(r"^[-*]\s+", "", b)
            row = [f"Section {num} (replaces section 4)", b] + [""] * (ncol - 2)
            rows.append(row[:ncol])
    return {"columns": t["columns"], "rows": rows, "source": {"file": sch.ARCH, "line": t["line"]}}


def extract(ctx):
    root = ctx.source_root
    pages = sch.read_pages(root)
    key_to_id = {p["key"]: p["id"] for p in pages if p["key"]}
    part_sheets = sch.read_part_sheets(root)
    ref_sheet = {r: key_to_id[k] for r, k in part_sheets.items() if k in key_to_id}
    net_rows = [(r["cells"]["net"].strip(), r["cells"]["reference"].strip())
                for r in csvread.read(root / sch.NETLIST_CSV, required=("net", "reference"))]
    blocks = []
    for p in pages:
        if not p["key"]:
            continue
        refs = sorted([r for r, i in ref_sheet.items() if i == p["id"]], key=_nat)
        blocks.append({"id": p["id"], "label": p["title"], "sheet": p["id"], "part_ids": [sch.part_id(r) for r in refs]})
    order = [b["id"] for b in blocks]
    arch_path = root / sch.ARCH
    if not arch_path.is_file():
        raise SourceError(f"{sch.ARCH} is missing", sch.ARCH)
    text = arch_path.read_text(encoding="utf-8")
    data = {"blocks": blocks, "links": build_links(net_rows, ref_sheet, order), "pin_plan": pin_plan(text),
            "power_budget": power_budget(text)}
    msg = None
    op = root / sch.OPEN_PINS_CSV
    if op.is_file():
        rows = csvread.read(op, required=("reference", "pin_number"))
        n = sum(1 for r in rows if r["cells"]["pin_number"].strip())
        msg = (f"{n} pin numbers are provisional (placeholders until the maker drawings are read): "
               f"{sch.OPEN_PINS_CSV}")
    cmap, read, wnote = wiring.build(ctx)
    if cmap is not None:
        data["connection_map"] = cmap
        msg = "; ".join(filter(None, [msg, wnote]))
    sch_text = (root / sch.ROOT_SCH).read_text(encoding="utf-8")
    m = sch._BASIS.search(sch_text)
    return data, {"status": "ok", "source": [sch.ROOT_SCH, sch.PARTS_CSV, sch.NETLIST_CSV, sch.ARCH, *read],
                  "basis_version": m.group(1) if m else None, "current_version": version.read_own(text),
                  "message": msg}
