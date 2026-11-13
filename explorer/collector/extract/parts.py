"""parts (parts.json): every line of the ring parts list and of the case parts list.

Sources: design/bom.csv (ring), design/case/case-bom.csv (case), design/architecture.md ("How to read this" for the
evidence legend, section 12 for the open actions of the ring), design/case/case-architecture.md (section 8 for the
open actions of the case).

A LINE is a csv row, a PART is one unit (sum of quantity). `refs` are split from the reference cell; the part id of a
ref is `<bom>:<ref>`. An open action that is only an item id (`12.2`) becomes "who: what to ask" from the supplier table;
text that already names who stays as written. Every absolute path in a cell (the lists hold some) is turned into a
repo-relative one; a path outside the project keeps its last two names and `path: null`.
The plain-words notes are not joined here: parts.schema has no field for them and content/part-notes.json stays its own
record, joined by the part card.
"""
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import csvread, md  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import pointer  # noqa: E402
from lib.version import read_own  # noqa: E402

RECORD = "parts"

RING_CSV = "design/bom.csv"
CASE_CSV = "design/case/case-bom.csv"
ARCH = "design/architecture.md"
CASE_ARCH = "design/case/case-architecture.md"
COLUMNS = ["item", "reference", "quantity", "function", "maker", "maker_part_number", "package", "size_mm", "value",
           "key_figures", "evidence", "source_file_or_url", "unit_price_and_currency_at_qty1", "open_action"]
ROOT_DOCS = {"requirements.md", "feasibility.md", "partners.md", "prices.md"}

_ABS = re.compile(r"(?<![\w.:/-])/(?:[\w.+@-]+/)+[\w.+@-]+")
_FILE = re.compile(r"(?<![\w./+@-])((?:[\w@+-]+/)*[\w@+.-]+\.(?:md|pdf|csv|txt|py|json|step|stp|png|svg|glb|stl|kicad_\w+|xlsx|zip|html))(?![\w])")
_PRICE = re.compile(r"^(?:([A-Z]{3})\s*(\d+(?:\.\d+)?)|([£$€])\s*(\d+(?:\.\d+)?))$")
_SYMBOLS = {"£": "GBP", "$": "USD", "€": "EUR"}
_LEGEND = re.compile(r"^\s*[-*]\s*\*\*\[([A-Z]+)\]\*\*\s*=\s*(.+?)\s*$")
_LEAD_ID = re.compile(r"^(\d+\.\d+|S\d+)\b:?\s*(.*)$", re.S)


def _localize(abs_path, root):
    """(repo-relative path or None when outside the project, text to show)."""
    p = abs_path.rstrip(".,)")
    try:
        rel = Path(p).resolve().relative_to(Path(root).resolve()).as_posix()
        return rel, rel
    except (ValueError, OSError):
        pass
    i = p.find("/design/")
    if i >= 0:
        return p[i + 1:], p[i + 1:]
    if p.rsplit("/", 1)[-1] in ROOT_DOCS:
        return p.rsplit("/", 1)[-1], p.rsplit("/", 1)[-1]
    return None, "/".join(p.split("/")[-2:])


def clean(text, root):
    """`text` with every absolute path made repo-relative (or cut to its last two names when outside the project)."""
    return _ABS.sub(lambda m: _localize(m.group(0), root)[1] + m.group(0)[len(m.group(0).rstrip(".,)")):], text)


def _find_file(rel, root, bom_dir):
    """(repo-relative path, on_disk) for a file name written in a source cell, or (None, False)."""
    if ".." in rel.split("/"):
        return None, False
    for cand in (rel, f"design/{rel}", f"{bom_dir}/{rel}"):
        if (Path(root) / cand).is_file():
            return cand, True
    return (rel, False) if rel.startswith("design/") else (None, False)


def parse_sources(cell, root, bom_dir):
    out = []
    for tok in (t.strip() for t in cell.split(";")):
        if not tok:
            continue
        if re.match(r"https?://", tok):
            out.append({"raw": tok, "path": None, "url": tok.split()[0], "on_disk": False})
            continue
        m = _ABS.search(tok)
        if m and _localize(m.group(0), root)[0] is None:
            out.append({"raw": clean(tok, root), "path": None, "url": None, "on_disk": False})
            continue
        raw = clean(tok, root)
        f = _FILE.search(raw)
        path, on_disk = _find_file(f.group(1), root, bom_dir) if f else (None, False)
        out.append({"raw": raw, "path": path, "url": None, "on_disk": on_disk})
    return out


def parse_price(cell, where):
    cell = cell.strip()
    if not cell:
        return None
    m = _PRICE.match(cell)
    if not m:
        raise SourceError(f"{where}: price {cell!r} is not 'CUR amount'", where.split(":")[0])
    cur = m.group(1) or _SYMBOLS[m.group(3)]
    return {"amount": float(m.group(2) or m.group(4)), "currency": cur, "raw": cell}


def supplier_table(text, heading_re):
    """{item id: (who, what, line)} from the section whose heading matches; {} when absent."""
    t = md.table_after_heading(text, heading_re, level=2)
    if not t:
        return {}
    cols = [c.lower() for c in t["columns"]]
    try:
        i_id, i_who = 0, cols.index("who")
        i_what = next(i for i, c in enumerate(cols) if c.startswith("what"))
    except (ValueError, StopIteration):
        return {}
    return {r[i_id]: (r[i_who], r[i_what], ln) for r, ln in zip(t["rows"], t["row_lines"])}


def resolve_action(cell, table):
    """Open action text: a leading item id found in the supplier `table` becomes 'who: what to ask'."""
    cell = cell.strip()
    if not cell:
        return None
    m = _LEAD_ID.match(cell)
    if m and m.group(1) in table:
        who, what, _ln = table[m.group(1)]
        rest = m.group(2).strip()
        if rest and who.split()[0].lower() in rest.lower():
            return cell  # the cell already names who must answer
        return f"{who}: {what}" + (f" ({rest})" if rest else "")
    return cell


def read_bom(root, rel, bom, arch_table):
    path = Path(root) / rel
    rows = csvread.read(path, required=COLUMNS)
    lines = []
    for r in rows:
        c, ln = r["cells"], r["line"]
        where = f"{rel}:{ln}"
        refs = csvread.split_refs(c["reference"])
        if not refs:
            raise SourceError(f"{where}: the reference cell is empty", rel)
        try:
            qty = int(c["quantity"].strip())
        except ValueError:
            raise SourceError(f"{where}: quantity {c['quantity']!r} is not a whole number", rel)
        if qty < 0:
            raise SourceError(f"{where}: quantity {qty} is below 0", rel)
        # quantity 0 is a history line ("history only, NOT fitted"): read, kept, and counted as 0 parts; the line says so in its function cell
        ev = c["evidence"].strip().upper() or None

        def text(k):
            v = clean(c[k].strip(), root)
            return v or None

        lines.append({
            "bom": bom, "row": ln, "item": clean(c["item"].strip(), root) or f"line {ln}", "refs": refs,
            "part_ids": [f"{bom}:{x}" for x in refs], "quantity": qty,
            "function": text("function"), "maker": text("maker"), "maker_part_number": text("maker_part_number"),
            "package": text("package"), "size_mm": text("size_mm"), "value": text("value"),
            "key_figures": text("key_figures"), "evidence": ev,
            "sources": parse_sources(c["source_file_or_url"], root, str(Path(rel).parent.as_posix())),
            "price": parse_price(c["unit_price_and_currency_at_qty1"], where),
            "open_action": resolve_action(clean(c["open_action"], root), arch_table),
            "source": pointer(rel, ln),
        })
    return lines


def totals(lines):
    priced = sum(1 for x in lines if x["price"] is not None)
    return {"lines": len(lines), "parts": sum(x["quantity"] for x in lines),
            "priced_lines": priced, "unpriced_lines": len(lines) - priced}


def priced_sums(lines):
    acc = {}
    for x in lines:
        if x["price"] is None:
            continue
        try:
            amt = Decimal(str(x["price"]["amount"])) * x["quantity"]
        except InvalidOperation:
            continue
        key = (x["bom"], x["price"]["currency"])
        acc[key] = acc.get(key, Decimal(0)) + amt
    return [{"bom": b, "currency": cur, "amount": float(a)} for (b, cur), a in sorted(acc.items())]


def legend(arch_text):
    """[{code, meaning, source}] from the bullets after 'How to read this' in architecture.md."""
    sec = [i for i, ln in enumerate(arch_text.splitlines(), 1) if ln.strip().lower().startswith("how to read this")]
    if not sec:
        return []
    out = []
    for i, ln in enumerate(arch_text.splitlines(), 1):
        if i <= sec[0]:
            continue
        if ln.startswith("## "):
            break
        m = _LEGEND.match(ln)
        if m:
            out.append({"code": m.group(1), "meaning": m.group(2), "source": pointer(ARCH, i)})
    return out


def _basis_version(text):
    m = re.search(r"\b(?:built against|follows|made for)\b[^\n]{0,120}?\bversion\s+([A-Z]{1,2}\d+(?:-[A-Za-z]+)?)", text, re.I)
    return m.group(1) if m else None


def extract(ctx):
    root = ctx.source_root
    ring_path = root / RING_CSV
    if not ring_path.is_file():
        return None, "missing"
    arch_text = (root / ARCH).read_text(encoding="utf-8") if (root / ARCH).is_file() else None
    case_arch_text = (root / CASE_ARCH).read_text(encoding="utf-8") if (root / CASE_ARCH).is_file() else None
    ring_table = supplier_table(arch_text, r"^12\.\s") if arch_text else {}
    case_table = supplier_table(case_arch_text, r"^8\.\s") if case_arch_text else {}

    lines = read_bom(root, RING_CSV, "ring", ring_table)
    sources, notes = [RING_CSV], []
    case_lines = []
    if (root / CASE_CSV).is_file():
        case_lines = read_bom(root, CASE_CSV, "case", case_table)
        sources.append(CASE_CSV)
    else:
        notes.append(f"{CASE_CSV} not found: no case lines")
    lines += case_lines

    if arch_text is None:
        notes.append(f"{ARCH} not found: no evidence meanings and no section 12 supplier names")
    leg = legend(arch_text) if arch_text else []
    if arch_text:
        sources.append(ARCH)
        used = {x["evidence"] for x in lines if x["evidence"]} - {e["code"] for e in leg}
        if used:
            notes.append("evidence code(s) without a meaning in the legend: " + ", ".join(sorted(used)))
    # The case list is made for an older ring. The record stays ok (the ring lines are current): the case lines
    # say so in the message, and the case record carries the stale status.
    basis, current = _basis_version(case_arch_text or ""), read_own(arch_text or "")
    if case_lines and basis and current and basis.split("-")[0] != current.split("-")[0]:
        notes.append(f"Case lines were made for design {basis}; the design is now {current}.")

    data = {
        "lines": lines,
        "totals": {"ring": totals([x for x in lines if x["bom"] == "ring"]),
                   "case": totals([x for x in lines if x["bom"] == "case"])},
        "priced_sums": priced_sums(lines),
        "evidence_legend": leg,
    }
    return data, {"status": "ok", "source": sources, "message": " ".join(notes) or None}
