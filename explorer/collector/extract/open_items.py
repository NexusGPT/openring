"""open-items (open.json): supplier requests, bench tests, risks, the owner's dated decisions.

Supplier requests: architecture section 12 (rows 12.n become S<n>), then the S rows of every later
"Open items added by" table; a later row with the same id ("S1 (changed)") replaces the earlier one.
Bench tests: section 13 (B rows), the B rows of the later tables, and the [CHECK n] lines of
design/bench/bench-plan.md. Risks: requirements.md section 6. Decisions: every line of the design
documents where the owner's words are quoted next to a date (see _decisions).
A row that cannot be read reliably is left out and named, with its reason, in the status message;
nothing is guessed. Case supplier items belong to the case record. The parts list's open actions are
in the parts record and are not copied here.
"""
import re
from pathlib import Path

from lib import md  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.version import read_own  # noqa: E402

RECORD = "open-items"

ARCH = "design/architecture.md"
REQS = "requirements.md"
BENCH_PLAN = "design/bench/bench-plan.md"
DECISION_GLOBS = ["requirements.md", "feasibility.md", "partners.md", "design/*.md", "design/bench/*.md",
                  "design/parts/*.md", "design/case/*.md"]

_ISO = r"\d{4}-\d{2}-\d{2}"
_OWNER_DATE = re.compile(r"\b[Oo]wner, (" + _ISO + ")")
_QUOTE = re.compile(r'"([^"\n]{3,})"')


def _src(file, line):
    return {"file": file, "line": line}


def _clean(s):
    return re.sub(r"\s+", " ", s.replace("**", "").strip())


def _later_tables(text, problems):
    """Rows of the tables under every heading 'Open items added by ...': (id, item, who, section, line)."""
    rows = []
    for lv, title, ln in md.headings(text):
        m = re.match(r"^(\d+\.\d+)\s+Open items added by", title)
        if not m:
            continue
        sec = md.section(text, "^" + re.escape(title) + "$", lv)
        t = md.tables(text, sec[0], sec[1])
        if not t:
            problems.append(f"{ARCH} section {m.group(1)}: no table found")
            continue
        tab = t[0]
        cols = [c.lower() for c in tab["columns"]]
        if len(cols) < 3 or not cols[2].startswith("who"):
            problems.append(f"{ARCH}:{tab['line']}: table columns {tab['columns']} are not '# | Item | Who closes it'")
            continue
        for cells, rl in zip(tab["rows"], tab["row_lines"]):
            rows.append((cells[0], _clean(cells[1]), _clean(cells[2]), m.group(1), rl))
    return rows


def _suppliers_and_bench(arch, problems):
    suppliers, bench = {}, {}
    s12 = md.section(arch, r"^12\.", 2)
    if s12 is None:
        raise SourceError("architecture.md has no section 12", ARCH)
    t12 = md.tables(arch, s12[0], s12[1])
    if not t12:
        raise SourceError("architecture.md section 12 has no table", ARCH)
    for cells, rl in zip(t12[0]["rows"], t12[0]["row_lines"]):
        m = re.fullmatch(r"12\.(\d+)", cells[0])
        item, who, ask = (_clean(c) for c in cells[1:4])
        if not m:
            problems.append(f"{ARCH}:{rl}: id {cells[0]!r} is not 12.<n>")
        elif not who or not item or not ask:
            problems.append(f"{ARCH}:{rl}: row 12.{m.group(1)} has an empty Item, Who or What-to-ask cell")
        else:
            suppliers[f"S{m.group(1)}"] = {"id": f"S{m.group(1)}", "item": item, "who": who, "ask": ask,
                                           "section": "12", "source": _src(ARCH, rl)}
    s13 = md.section(arch, r"^13\.", 2)
    t13 = md.tables(arch, s13[0], s13[1]) if s13 else []
    if not t13:
        problems.append(f"{ARCH}: section 13 or its table not found")
    else:
        for cells, rl in zip(t13[0]["rows"], t13[0]["row_lines"]):
            bid = cells[0].strip()
            choice, test, changes = (_clean(c) for c in cells[1:4])
            if not re.fullmatch(r"B\d+", bid) or not choice or not test:
                problems.append(f"{ARCH}:{rl}: bench row {bid!r} has no usable id, choice or test")
                continue
            bench[bid] = {"id": bid, "title": choice, "source": _src(ARCH, rl),
                          "detail": f"Test: {test}." + (f" Changes to: {changes}." if changes else "")}
    for rid, item, who, sec, rl in _later_tables(arch, problems):
        base = re.match(r"^([SB]\d+)\b", rid)
        if not base:
            problems.append(f"{ARCH}:{rl}: id {rid!r} is not S<n> or B<n>")
        elif not item or not who:
            problems.append(f"{ARCH}:{rl}: row {rid} has an empty Item or Who cell")
        elif base.group(1)[0] == "S":
            suppliers[base.group(1)] = {"id": base.group(1), "item": item, "who": who, "ask": item,
                                        "section": sec, "source": _src(ARCH, rl)}
        else:
            bench[base.group(1)] = {"id": base.group(1), "title": item, "source": _src(ARCH, rl),
                                    "detail": f"Closed by: {who}."}
    key = lambda d: int(d["id"][1:])  # noqa: E731
    return sorted(suppliers.values(), key=key), sorted(bench.values(), key=key)


def _bench_checks(root, problems):
    p = Path(root) / BENCH_PLAN
    if not p.is_file():
        return []
    out = []
    for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        m = re.search(r"\[CHECK (\d+)\]\s*(.*)", ln)
        if m:
            body = _clean(m.group(2))
            if not body:
                problems.append(f"{BENCH_PLAN}:{i}: [CHECK {m.group(1)}] has no text")
                continue
            first, _, rest = body.partition(". ")
            out.append({"id": f"CHECK {m.group(1)}", "title": first.rstrip("."), "detail": rest or None,
                        "source": _src(BENCH_PLAN, i)})
    return out


def _risks(root, problems):
    p = Path(root) / REQS
    if not p.is_file():
        problems.append(f"{REQS}: file missing, no risks read")
        return []
    text = p.read_text(encoding="utf-8")
    sec = md.section(text, r"^6\.\s*Risks", 2)
    t = md.tables(text, sec[0], sec[1]) if sec else []
    if not t:
        problems.append(f"{REQS}: risks table not found")
        return []
    out = []
    for n, (cells, rl) in enumerate(zip(t[0]["rows"], t[0]["row_lines"]), 1):
        risk, why, fix = (_clean(c) for c in cells[:3])
        if not risk:
            problems.append(f"{REQS}:{rl}: risk row has no text")
            continue
        text_ = risk + (f". Why: {why}" if why else "") + (f". What reduces it: {fix}" if fix else "")
        out.append({"id": f"R{n}", "text": text_, "source": _src(REQS, rl)})
    return out


def _decisions(root):
    """A decision is a line whose first 'owner' mark is 'owner, <date>' or a line that starts with 'Owner,'
    (date: first date in the line, else the date in the nearest heading above), followed by quoted words.
    Each quoted sentence after the mark is one decision, kept verbatim, with its file and line."""
    root = Path(root)
    files = sorted({p for g in DECISION_GLOBS for p in root.glob(g) if p.is_file()})
    out = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        heading_date = None
        for i, ln in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if ln.startswith("#"):
                m = re.search(r"\((?:[^()]*?)(" + _ISO + ")", ln)
                heading_date = m.group(1) if m else None
                continue
            m = _OWNER_DATE.search(ln)
            if m:
                date, pos = m.group(1), m.end()
            elif re.match(r"^\s*(?:[-*]\s+)?Owner,", ln):
                d = re.search(_ISO, ln)
                date, pos = (d.group(0) if d else heading_date), 0
            else:
                continue
            if not date:
                continue
            for q in _QUOTE.finditer(ln, pos):
                out.append({"date": date, "speaker": "Owner", "quote": q.group(1), "source": _src(rel, i)})
    return out


def extract(ctx):
    arch_path = ctx.source_path(ARCH)
    if not arch_path.is_file():
        return None, {"status": "missing", "source": [ARCH], "message": f"{ARCH} is not on disk."}
    arch = arch_path.read_text(encoding="utf-8")
    problems = []
    suppliers, bench = _suppliers_and_bench(arch, problems)
    bench += _bench_checks(ctx.source_root, problems)
    data = {"supplier_requests": suppliers, "bench_tests": bench,
            "risks": _risks(ctx.source_root, problems), "decisions": _decisions(ctx.source_root)}
    msg = None
    if problems:
        msg = f"{len(problems)} row(s) left out, not readable: " + "; ".join(problems[:6])
    return data, {"status": "ok", "source": [ARCH, REQS, BENCH_PLAN], "basis_version": read_own(arch),
                  "current_version": read_own(arch), "message": msg}
