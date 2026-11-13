"""Markdown helpers: headings and tables, with 1-based line numbers for source pointers."""
import re

_HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def headings(text):
    """[(level, title, line)] for every ATX heading outside code fences."""
    out, fence = [], False
    for i, ln in enumerate(text.splitlines(), 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
        if fence:
            continue
        m = _HEAD.match(ln)
        if m:
            out.append((len(m.group(1)), m.group(2), i))
    return out


def section(text, title_re, level=None):
    """(first_line, last_line, body_lines) of the first heading matching `title_re` (regex, searched),
    up to the next heading of the same or higher level. None if absent."""
    rx = re.compile(title_re)
    hs = headings(text)
    lines = text.splitlines()
    for idx, (lv, title, ln) in enumerate(hs):
        if (level is None or lv == level) and rx.search(title):
            end = len(lines)
            for lv2, _t2, ln2 in hs[idx + 1:]:
                if lv2 <= lv:
                    end = ln2 - 1
                    break
            return ln, end, lines[ln:end]
    return None


def _cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", row)]


def tables(text, start=1, end=None):
    """Every pipe table in lines start..end: [{'columns': [...], 'rows': [[...]], 'line': first_line,
    'row_lines': [line per row]}]."""
    lines = text.splitlines()
    end = end or len(lines)
    out, i = [], start
    while i <= end:
        ln = lines[i - 1]
        nxt = lines[i] if i < len(lines) else ""
        if ln.lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{2,}", nxt):
            cols = _cells(ln)
            rows, rls, j = [], [], i + 2
            while j <= end and lines[j - 1].lstrip().startswith("|"):
                cells = _cells(lines[j - 1])
                cells = (cells + [""] * len(cols))[: len(cols)]
                rows.append(cells)
                rls.append(j)
                j += 1
            out.append({"columns": cols, "rows": rows, "line": i, "row_lines": rls})
            i = j
        else:
            i += 1
    return out


def table_after_heading(text, title_re, level=None, index=0):
    """The `index`-th table inside the section whose heading matches `title_re`; None if the heading
    or the table is absent."""
    sec = section(text, title_re, level)
    if sec is None:
        return None
    first, last, _ = sec
    ts = tables(text, first, last)
    return ts[index] if index < len(ts) else None
