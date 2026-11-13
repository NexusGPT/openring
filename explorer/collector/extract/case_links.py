"""case_links (helper of case.py): which line of the case parts list each solid of the case model is, and where every
line of the list is.

Sources, all read at collect time (no case value is held here):
  design/case/case-bom.csv          the 90 lines: reference, quantity, function, package, size, maker part number, source file.
  design/case/out/parts/*.step      the solids (their names come from case.py).
  design/ecad/case/pcb/*.kicad_pcb  the footprints of each case board: reference and value.
  design/wiring/lead-decisions.md   the row "block height ...: what follows" (the sentence about the case's refit).
  design/case/out/case_params.json  its file time is the model's date.

A solid is linked by the first rule that finds a line (a line of quantity 0 is never linked):
  R0 reference   a token of the solid's name is a reference of the list (a range such as P1-P4 covers the numbers in it).
  R1 own part    the line's cells name the solid in back quotes (`liner`, `usb_bezel`).
  R2 file        the line's source cell names the solid's file (out/parts/<name>.step, out/case_<name>.stl).
  R3 part number the line's maker part number is a token of the solid's name.
  R4 child       the solid's name starts with another solid's name and an underscore: it stands for what that one stands for.
  R5 words       every word of the solid's name is a word of the line's function (same word, plural, or six letters in
                 common), the line that holds most of them in its first three words when several do; else the one line
                 whose first three function words hold a word of the name.
Every line has exactly one class: not-fitted (quantity 0), solid (a solid links it), board (a footprint of a case board
carries its reference), no-solid (none of these; the reason is said in the words of its own cells).
"""
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

BOM = "design/case/case-bom.csv"
PARAMS = "design/case/out/case_params.json"
DECISIONS = "design/wiring/lead-decisions.md"
BOARD_FILES = ["design/ecad/case/pcb/case_main.kicad_pcb", "design/ecad/case/pcb/case_pins.kicad_pcb"]
NO_LINE = "no parts-list line"


# ---------------------------------------------------------------- the parts list

def read_rows(path):
    """[{line, tokens, ids, qty, item, function, package, size, pn, source}] for each row of the case parts list."""
    from lib import csvread  # noqa: PLC0415

    out = []
    for r in csvread.read(Path(path), ["reference"]):
        c = r["cells"]
        tokens = csvread.split_refs(c.get("reference", ""))
        if not tokens:
            continue
        q = (c.get("quantity") or "").strip()
        out.append({"line": r["line"], "tokens": tokens, "ids": [f"case:{t}" for t in tokens],
                    "qty": int(q) if q.isdigit() else None, "item": (c.get("item") or "").strip(),
                    "function": (c.get("function") or "").strip(), "package": (c.get("package") or "").strip(),
                    "size": (c.get("size_mm") or "").strip(), "pn": (c.get("maker_part_number") or "").strip(),
                    "source": (c.get("source_file_or_url") or "").strip()})
    return out


def in_range(token, ref):
    """True when `ref` (R5) is `token` (R5) or lies inside the range token (R3-R4, P1-P4)."""
    if token == ref:
        return True
    m = re.match(r"^([A-Za-z]+)(\d+)-(?:[A-Za-z]+)?(\d+)$", token)
    n = re.match(r"^([A-Za-z]+)(\d+)$", ref)
    return bool(m and n and m.group(1) == n.group(1) and int(m.group(2)) <= int(n.group(2)) <= int(m.group(3)))


# ---------------------------------------------------------------- solid -> lines

def words_of(text):
    return re.findall(r"[a-z]+", text.lower())


def same_word(a, b):
    if a == b or a + "s" == b or b + "s" == a:
        return True
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n >= 6


def _r0(stem, row):
    for tok in stem.split("_"):
        for ref in row["tokens"]:
            if tok == ref or (any(ch.isdigit() for ch in tok) and tok.lower() == ref.lower()) or in_range(ref, tok):
                return True
    return False


def _r1(stem, row):
    cells = " ".join((row["function"], row["package"], row["size"], row["source"]))
    return stem in re.findall(r"`([A-Za-z0-9_]+)`", cells)


def _r2(stem, row):
    for f in re.findall(r"design/case/out/(?:parts/)?([A-Za-z0-9_\-]+)\.(?:step|stl)", row["source"]):
        if f == stem or f == "case_" + stem:
            return True
    return False


def _r3(stem, row):
    toks = [t.lower() for t in re.split(r"[^A-Za-z0-9]+", row["pn"]) if len(t) >= 5 and any(ch.isdigit() for ch in t)]
    return any(t in [s.lower() for s in stem.split("_")] for t in toks)


def link_solids(names, rows):
    """{solid name: {'ids': [part ids], 'rule': 'R0'..'R5'}} for every solid some rule links."""
    live = [r for r in rows if r["qty"] != 0]
    out = {}
    for rule, test in (("R0", _r0), ("R1", _r1), ("R2", _r2), ("R3", _r3)):
        for n in names:
            if n in out:
                continue
            ids = [i for r in live if test(n, r) for i in r["ids"]]
            if ids:
                out[n] = {"ids": ids, "rule": rule}
    _children(names, out)
    roots = [n for n in names if not any(p != n and n.startswith(p + "_") for p in names)]
    _words(names, rows, live, out, roots)
    _children(names, out)
    _words(names, rows, live, out, [n for n in names if n not in roots])
    _children(names, out)  # a child of a solid that only the word rule linked
    return out


def _words(names, rows, live, out, todo):
    """R5 for the solids in `todo` that no rule has linked yet."""
    for n in todo:
        if n in out:
            continue
        ws = [w for w in words_of(n.replace("_", " ")) if len(w) > 1]
        if not ws:
            continue
        whole, part = [], []
        for r in live:
            fw = words_of(r["function"])
            hit = [w for w in ws if any(same_word(w, x) for x in fw)]
            if len(hit) == len(ws):
                whole.append(r)
            elif hit and any(len(w) >= 5 and any(same_word(w, x) for x in fw[:3]) for w in hit):
                part.append(r)
        if len(whole) > 1:  # the line that names the thing first, not one that mentions it in passing
            head = {id(r): sum(1 for w in ws if any(same_word(w, x) for x in words_of(r["function"])[:3])) for r in whole}
            top = max(head.values())
            whole = [r for r in whole if head[id(r)] == top]
        pick = whole or (part if len(part) == 1 else [])
        if pick:
            out[n] = {"ids": [i for r in pick for i in r["ids"]], "rule": "R5"}


def _children(names, out):
    """R4: a solid named <parent>_<more> stands for what its longest linked parent stands for."""
    for n in sorted(names, key=len, reverse=True):
        if n in out:
            continue
        parents = [p for p in names if p != n and n.startswith(p + "_") and p in out]
        if parents:
            out[n] = {"ids": list(out[max(parents, key=len)]["ids"]), "rule": "R4"}


# ---------------------------------------------------------------- boards

def footprints(text):
    """[(reference, value)] of every footprint of a KiCad board file."""
    out = []
    for blk in re.split(r"\n\t\(footprint\s", text)[1:]:
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk)
        val = re.search(r'\(property "Value" "([^"]*)"', blk)
        if ref:
            out.append((ref.group(1), (val.group(1) if val else "").strip()))
    return out


def board_key(path):
    """'main' for case_main.kicad_pcb, 'pins' for case_pins.kicad_pcb: the word after the file's first underscore."""
    stem = Path(path).stem
    return stem.split("_", 1)[1] if "_" in stem else stem


def board_node(key, names, links):
    """The solid that is the board: its name holds the board word (main, pin) and the word 'board', and it is not a
    child of another solid (the shortest such name)."""
    cands = [n for n in names if "board" in words_of(n.replace("_", " "))
             and any(same_word(key, w) for w in words_of(n.replace("_", " ")))
             and links.get(n, {}).get("rule") != "R4"]
    return min(cands, key=len) if cands else None


def picker_group(rel):
    """The group of the Board screen's picker (boards.GROUPS) whose pattern holds a board file: {id, title}, or None."""
    import fnmatch  # noqa: PLC0415

    import boards  # noqa: PLC0415  (a peer helper)

    for g in boards.GROUPS:
        if any(fnmatch.fnmatch(rel, p) for p in g["glob"]):
            return {"id": g["id"], "title": g["title"]}
    return None


# ---------------------------------------------------------------- classes

def reason_of(row):
    pk = row["package"]
    m = re.match(r"feature of (the [^;,(]+)", pk, re.I) or re.search(r"feature of (the [^;,(]+)", row["function"], re.I)
    if m:
        return f"it is a feature of {m.group(1).strip()}, not a solid of its own (parts list: {pk or row['function']!r})"
    return ("no solid of the model carries its reference, its own-part name or its file, and no board footprint holds it"
            + (f" (parts list: {pk!r})" if pk else ""))


def classify(rows, links, boards):
    """One entry per row: {id, part_ids, line, class, nodes, boards, reason}. `boards` is [{key, refs}]."""
    out = []
    for r in rows:
        nodes = sorted(n for n, v in links.items() if any(i in r["ids"] for i in v["ids"]))
        on = [b["key"] for b in boards if any(in_range(t, ref) for t in r["tokens"] for ref in b["refs"])]
        e = {"id": r["ids"][0], "part_ids": r["ids"], "line": r["line"], "class": None, "nodes": [], "boards": on, "reason": None}
        if r["qty"] == 0:
            e["class"] = "not-fitted"
            e["reason"] = "quantity 0 in the parts list: history only, not fitted"
        elif nodes:
            e["class"], e["nodes"] = "solid", nodes
        elif on:
            e["class"] = "board"
        else:
            e["class"], e["reason"] = "no-solid", reason_of(r)
        out.append(e)
    return out


def counts(lines, names, links):
    c = {k: sum(1 for x in lines if x["class"] == k) for k in ("solid", "board", "not-fitted", "no-solid")}
    return {"lines": len(lines), "solid": c["solid"], "board": c["board"], "not_fitted": c["not-fitted"],
            "no_solid": c["no-solid"], "nodes": len(names), "nodes_linked": sum(1 for n in names if n in links),
            "nodes_unlinked": sum(1 for n in names if n not in links)}


# ---------------------------------------------------------------- the whole record part

def build(ctx, names, notes):
    """The extra fields of case/index.json, or {} when the parts list is not there. `names` are the solids' names."""
    from lib.source import pointer  # noqa: PLC0415

    p = ctx.source_path(BOM)
    if not p.is_file():
        return {}
    rows = read_rows(p)
    links = link_solids(names, rows)
    boards, board_parts = [], []
    for rel in BOARD_FILES:
        f = ctx.source_path(rel)
        if not f.is_file():
            notes.append(f"{rel} is not there: its parts are not listed")
            continue
        fps = footprints(f.read_text(encoding="utf-8"))
        boards.append({"key": board_key(rel), "refs": [r for r, _ in fps], "rel": rel, "fps": fps})
    lines = classify(rows, links, boards)
    by_id = {i: r for r in rows for i in r["ids"]}
    node_of = {b["key"]: board_node(b["key"], names, links) for b in boards}
    # the solid of a board also stands for the parts the board carries (its own line stays first)
    ids_of = {n: list(v["ids"]) for n, v in links.items()}
    for e in lines:
        if e["class"] == "board":
            for k in e["boards"]:
                n = node_of.get(k)
                if n:
                    ids_of[n] = ids_of.get(n, []) + [i for i in e["part_ids"] if i not in ids_of.get(n, [])]
    board_out = []
    for b in boards:
        parts = []
        for ref, value in b["fps"]:
            row = next((r for r in rows if any(in_range(t, ref) for t in r["tokens"])), None)
            parts.append({"ref": ref, "value": value, "part_id": row["ids"][0] if row else None,
                          "what": (row["function"] if row else None) or None})
        grp = picker_group(b["rel"])
        board_out.append({"key": b["key"], "title": grp["title"] if grp else b["key"], "node": node_of.get(b["key"]),
                          "picker": grp["id"] if grp else None, "file": b["rel"], "parts": parts})
    unlinked = [{"name": n, "text": NO_LINE} for n in names if n not in links]
    bom_lines = [{"id": e["id"], "part_ids": e["part_ids"], "class": e["class"], "nodes": e["nodes"], "boards": e["boards"],
                  "reason": e["reason"], "source": pointer(BOM, e["line"])} for e in lines]
    return {"links": [{"name": n, "part_ids": ids_of.get(n, []), "rule": links[n]["rule"] if n in links else None} for n in names],
            "lines": bom_lines, "counts": counts(lines, names, links), "unlinked_nodes": unlinked, "boards": board_out}


# ---------------------------------------------------------------- honest state

def model_source(ctx):
    """{file, time}: the model's parameters file and its file time ('2026-11-13 05:55'), or None."""
    p = ctx.source_path(PARAMS)
    if not p.is_file():
        return None
    return {"file": PARAMS, "time": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")}


def refit_note(ctx):
    """The decision cell of the row 'block height ...: what follows' of the lead's decisions, with its place; or None."""
    from lib import md  # noqa: PLC0415
    from lib.source import pointer  # noqa: PLC0415

    p = ctx.source_path(DECISIONS)
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8")
    for t in md.tables(text):
        cols = [c.lower() for c in t["columns"]]
        if "item" not in cols or "decision" not in cols:
            continue
        ii, di = cols.index("item"), cols.index("decision")
        for cells, line in zip(t["rows"], t["row_lines"]):
            if re.match(r"block height\b.*what follows\s*$", cells[ii], re.I) and cells[di].strip():
                return {"item": cells[ii], "text": cells[di].strip(), "source": pointer(DECISIONS, line)}
    return None
