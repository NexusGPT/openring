"""Checks of the case record's links (case/index.json: lines, counts, boards, nodes). Each returns a list of problems in
plain words; an empty list means the record passes. Used by collector/tests/collector-case against the real design and
against kept broken inputs. Nothing here reads the extractor: the list's own lines come from the file passed in."""
import csv
import re

CLASSES = ("solid", "board", "not-fitted", "no-solid")


def parts_list_ids(bom_path):
    """[(id, quantity)] of the rows of the case parts list, read here from the file itself (one id per row: its first token)."""
    out = []
    with open(bom_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            toks = [t.strip() for t in re.split(r"[,;]", row.get("reference", "")) if t.strip()]
            if toks:
                out.append((f"case:{toks[0]}", int((row.get("quantity") or "0").strip() or 0)))
    return out


def check_classes(case, bom_ids, no_solid_bound):
    """Every line of the parts list has exactly one class; the class counts add up to the lines; the lines without a solid
    stay under the bound; a quantity-0 line is 'not-fitted' and a 'not-fitted' line has quantity 0."""
    problems = []
    lines = case.get("lines") or []
    ids = [x["id"] for x in lines]
    for i, q in bom_ids:
        mine = [x for x in lines if x["id"] == i]
        if len(mine) != 1:
            problems.append(f"{i}: {len(mine)} entries in the record, not 1")
            continue
        c = mine[0]["class"]
        if c not in CLASSES:
            problems.append(f"{i}: class {c!r} is not one of {CLASSES}")
        if q == 0 and c != "not-fitted":
            problems.append(f"{i}: quantity 0 but class {c!r}, not 'not-fitted'")
        if q > 0 and c == "not-fitted":
            problems.append(f"{i}: quantity {q} but class 'not-fitted'")
    extra = [i for i in ids if i not in {b for b, _ in bom_ids}]
    if extra:
        problems.append(f"entries for lines the parts list does not have: {extra[:3]}")
    n = case.get("counts") or {}
    total = n.get("solid", 0) + n.get("board", 0) + n.get("not_fitted", 0) + n.get("no_solid", 0)
    if total != len(bom_ids):
        problems.append(f"the four class counts add up to {total}, the parts list has {len(bom_ids)} lines")
    for k, cls in (("solid", "solid"), ("board", "board"), ("not_fitted", "not-fitted"), ("no_solid", "no-solid")):
        have = sum(1 for x in lines if x["class"] == cls)
        if n.get(k) != have:
            problems.append(f"counts.{k} is {n.get(k)}, the lines hold {have}")
    if n.get("no_solid", 0) > no_solid_bound:
        problems.append(f"{n.get('no_solid')} lines without a solid, the bound is {no_solid_bound}")
    for x in lines:
        if x["class"] == "no-solid" and not (x.get("reason") or "").strip():
            problems.append(f"{x['id']}: no solid and no reason in words")
    return problems


def check_nodes(case, solids, unlinked_bound):
    """Every solid of the model is in the record; a solid is linked, or named in unlinked_nodes; the number of solids left
    without a line stays under the bound; each class 'solid' line names at least one solid that holds its id; every id a
    node holds is a line of the list."""
    problems = []
    nodes = ((case.get("glb") or {}).get("nodes")) or []
    names = [n["name"] for n in nodes]
    for s in solids:
        if s not in names:
            problems.append(f"solid {s!r} of the model is not in the record")
    unl = [u["name"] for u in case.get("unlinked_nodes") or []]
    for n in nodes:
        if not n["part_ids"] and n["name"] not in unl:
            problems.append(f"solid {n['name']!r} links to nothing and is not listed as without a parts-list line")
        if n["part_ids"] and n["name"] in unl:
            problems.append(f"solid {n['name']!r} links to a line and is listed as without one")
    if len(unl) > unlinked_bound:
        problems.append(f"{len(unl)} solids without a parts-list line, the bound is {unlinked_bound}")
    n = case.get("counts") or {}
    linked = sum(1 for x in nodes if x["part_ids"])
    if n.get("nodes_linked") != linked:
        problems.append(f"counts.nodes_linked is {n.get('nodes_linked')}, {linked} solids hold a line")
    if n.get("nodes_unlinked") != len(unl):
        problems.append(f"counts.nodes_unlinked is {n.get('nodes_unlinked')}, {len(unl)} solids are listed without a line")
    known = {i for x in case.get("lines") or [] for i in x["part_ids"]}
    for n in nodes:
        for i in n["part_ids"]:
            if i not in known:
                problems.append(f"solid {n['name']!r} links to {i}, which is not a line of the list")
    by_node = {n["name"]: set(n["part_ids"]) for n in nodes}
    for x in case.get("lines") or []:
        if x["class"] == "solid":
            if not x["nodes"] or not all(x["id"] in by_node.get(m, ()) for m in x["nodes"]):
                problems.append(f"{x['id']}: class solid, but no solid holds its id")
    return problems


def check_in_parts(case, parts):
    """Every id the record links (lines, solids, board parts) is an id of the parts record."""
    have = {i for l in parts["lines"] if l["bom"] == "case" for i in l["part_ids"]}
    problems = []
    for x in case.get("lines") or []:
        for i in x["part_ids"]:
            if i not in have:
                problems.append(f"line {i} is not in the parts record")
    for n in ((case.get("glb") or {}).get("nodes")) or []:
        for i in n["part_ids"]:
            if i not in have:
                problems.append(f"solid {n['name']!r}: {i} is not in the parts record")
    for b in case.get("boards") or []:
        for p in b["parts"]:
            if p["part_id"] and p["part_id"] not in have:
                problems.append(f"board {b['key']}: {p['ref']} links {p['part_id']}, not in the parts record")
    return problems
