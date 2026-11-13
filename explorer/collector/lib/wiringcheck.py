"""Checks of the connection map (electronics.json, field connection_map). Each returns a list of problems in plain words;
an empty list means the map passes. Used by collector/tests/collector-wiring against the real design and against kept
broken inputs. The count a file states is read from the file itself, never from the extractor's own field."""
import re
from pathlib import Path


def stated_in_file(text):
    """The number connections.md states ('Count: N joints'), or None."""
    m = re.search(r"^Count:\s*(\d+)\s+joints", text, re.M)
    return int(m.group(1)) if m else None


def table_joint_ids(text):
    """Ids of the rows of the Part 1 table that are joints: every id of the form R<n> or C<n> whose row does not say 'No joint'."""
    ids = []
    in_part1 = False
    for ln in text.splitlines():
        if ln.startswith("## "):
            in_part1 = ln.startswith("## Part 1")
            continue
        if not in_part1 or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and re.fullmatch(r"[RC]\d+", cells[0]) and not any(re.match(r"No joint\b", c) for c in cells[1:]):
            ids.append(cells[0])
    return ids


def check_count(cmap, connections_text):
    """The number of connections equals the count the file states and the number of joint rows in its table."""
    problems = []
    n = len(cmap["connections"])
    stated = stated_in_file(connections_text)
    rows = table_joint_ids(connections_text)
    if stated is None:
        problems.append("connections.md does not state a count")
    elif n != stated:
        problems.append(f"{n} connections, the file states {stated}")
    if n != len(rows):
        problems.append(f"{n} connections, the file's table has {len(rows)} joint rows")
    ids = [c["id"] for c in cmap["connections"]]
    if len(set(ids)) != len(ids):
        problems.append("two connections share an id")
    return problems


def check_ends_and_sources(cmap, root):
    """Every connection has two ends that name a node of the map, text on each end, and a source file that exists."""
    problems = []
    nodes = {n["id"] for n in cmap["nodes"]}
    for c in cmap["connections"]:
        ends = c.get("ends") or []
        if len(ends) != 2:
            problems.append(f"{c.get('id')}: {len(ends)} ends, not 2")
        for e in ends:
            if not (e.get("text") or "").strip():
                problems.append(f"{c['id']}: an end has no text")
            if e.get("node") not in nodes:
                problems.append(f"{c['id']}: end node {e.get('node')!r} is not in the map")
            elif str(e["node"]).startswith("unmapped-"):
                problems.append(f"{c['id']}: end {e['text']!r} matches no board or part")
        src = (c.get("source") or {}).get("file")
        if not src or not (Path(root) / src).is_file():
            problems.append(f"{c['id']}: source file {src!r} does not exist")
        for p in c.get("proof") or []:
            if not (Path(root) / p["file"]).is_file():
                problems.append(f"{c['id']}: proof file {p['file']!r} does not exist")
    return problems


def open_cells(text):
    """Ids of the Part 1 rows whose "Drawn?" cell (the last cell) says not drawn or says the joint is stated in text only,
    read here from the file's own table."""
    ids = set()
    in_part1 = False
    for ln in text.splitlines():
        if ln.startswith("## "):
            in_part1 = ln.startswith("## Part 1")
            continue
        if not in_part1 or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and re.fullmatch(r"[RC]\d+", cells[0]) and re.search(r"^(not drawn|stated in text only)\b", cells[-1], re.I):
            ids.add(cells[0])
    return ids


def check_open(cmap, connections_text):
    """The joints shown open (not drawn, or stated in text only) are exactly the rows whose "Drawn?" cell says so."""
    shown = {c["id"] for c in cmap["connections"] if c["drawn"]["state"] in ("not-drawn", "text-only")}
    cells = open_cells(connections_text)
    problems = [f"{i}: the file says it is not drawn or stated in text only, shown as drawn" for i in sorted(cells - shown)]
    problems += [f"{i}: shown open, the file's cell does not say so" for i in sorted(shown - cells)]
    return problems


# ---- conductor lines (field conductor_lines / no_conductor of a connection; conductor_file of the map) ----
PRODUCT_WIRING = "design/wiring/product-wiring.csv"
SIZE_COLUMN = re.compile(r"^(copper|cut)_mm_us(\d+)$")


def file_rows(path):
    """[(line, {column: text})] of product-wiring.csv, read here with the csv module on its own (not with the extractor's reader)."""
    import csv

    out = []
    with Path(path).open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        prev = reader.line_num
        for row in reader:
            first = prev + 1
            prev = reader.line_num
            if any(c.strip() for c in row):
                out.append((first, dict(zip(header, (row + [""] * len(header))[: len(header)]))))
    return out


def _end_problems(cid, side, got, row, tag):
    want = {"board": row[f"end_{tag}_board"], "part": row[f"end_{tag}_ref"], "pin": row[f"end_{tag}_pin"],
            "face": row[f"end_{tag}_face"], "join": row[f"join_{tag}"]}
    return [f"{cid}: {side} terminal {k} shows {got.get(k)!r}, line says {v!r}" for k, v in want.items() if got.get(k) != v]


def check_conductor_lines(cmap, csv_path, root):
    """Problems (plain words) between the connection map and product-wiring.csv: the number of conductor lines of each connection,
    and every value shown on each conductor read back from the {file, line} it cites. A line of the file that no connection shows
    is a problem too. `csv_path` is the file the bundle is compared with (the real one, or a broken copy)."""
    problems = []
    rows = file_rows(csv_path)
    by_conn = {c["id"]: c for c in cmap["connections"]}
    want_count, none_rows = {}, {}
    for line, r in rows:
        if r["carrier_kind"].strip() == "none":
            none_rows[r["id"]] = (line, r)
        elif r["joint"] in by_conn:
            want_count.setdefault(r["joint"], []).append((line, r))
    line_rows = dict(rows)
    for cid, c in by_conn.items():
        shown = c.get("conductor_lines") or []
        want = want_count.get(cid, [])
        if len(shown) != len(want):
            problems.append(f"{cid}: {len(shown)} conductors shown, the file has {len(want)}")
        for k in c.get("conductor_lines") or []:
            src = k["source"]
            row = line_rows.get(src["line"])
            if src["file"] != PRODUCT_WIRING:
                problems.append(f"{k['id']}: cites {src['file']!r}, not {PRODUCT_WIRING}")
            if row is None or row["id"] != k["id"]:
                problems.append(f"{k['id']}: line {src['line']} of the file is {row and row['id']!r}, not this conductor")
                continue
            if row["joint"] != cid:
                problems.append(f"{k['id']}: shown on {cid}, line {src['line']} says {row['joint']!r}")
            for key, want_v, got_v in [("signal_a", row["signal_A"], k["signal_a"]), ("signal_b", row["signal_B"], k["signal_b"]),
                                       ("carrier", row["carrier"], k["carrier"]["text"]), ("carrier kind", row["carrier_kind"], k["carrier"]["kind"]),
                                       ("state", row["state"], k["state"])]:
                if want_v != got_v:
                    problems.append(f"{k['id']}: {key} shows {got_v!r}, line {src['line']} says {want_v!r}")
            problems += _end_problems(k["id"], "first", k["first"], row, "A") + _end_problems(k["id"], "last", k["last"], row, "B")
            lens = {(x["kind"], x["size"]): x["mm"] for x in k.get("lengths") or []}
            wl = {}
            for col, v in row.items():
                m = SIZE_COLUMN.match(col)
                if m and v.strip():
                    wl[(m.group(1), f"US {m.group(2)}")] = v
            if lens != wl:
                problems.append(f"{k['id']}: lengths show {sorted(lens.items())}, line {src['line']} says {sorted(wl.items())}")
    shown_none = {k["id"]: k for c in cmap["connections"] for k in c.get("no_conductor") or []}
    for rid, (line, r) in none_rows.items():
        k = shown_none.get(rid)
        if k is None:
            if r["joint"] in by_conn:
                problems.append(f"{rid}: no-conductor line {line} is not shown")
        elif k["source"]["line"] != line or k["reason"] != r["carrier"]:
            problems.append(f"{rid}: no-conductor reason or line differs from line {line}")
    shown_ids = {k["id"] for c in cmap["connections"] for k in c.get("conductor_lines") or []}
    for line, r in rows:
        if r["carrier_kind"].strip() != "none" and r["id"] not in shown_ids and r["joint"] in by_conn:
            problems.append(f"{r['id']}: line {line} of the file is not shown on {r['joint']}")
    f = cmap.get("conductor_file")
    if f is None:
        problems.append("the map has no conductor_file")
    else:
        n = sum(len(v) for v in want_count.values())
        done = sum(1 for v in want_count.values() for _, r in v if r["state"] in ("drawn and routed", "specified and landed"))
        if (f["total"], f["complete"]) != (n, done):
            problems.append(f"the count line says {f['complete']} of {f['total']}, the file has {done} of {n}")
    return problems
