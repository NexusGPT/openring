"""Rules a schema cannot state. Each returns a list of readable problems (empty = holds)."""
import re

from .records import constants


def _words(s):
    return len(re.findall(r"\S+", s))


def check_parts(d):
    """LINES = rows, PARTS = sum of quantity; part id = '<bom>:<ref>'; one ref belongs to one line."""
    problems, seen = [], {}
    tot = {"ring": [0, 0], "case": [0, 0]}
    for i, ln in enumerate(d.get("lines", [])):
        want = [f"{ln['bom']}:{r}" for r in ln["refs"]]
        if ln["part_ids"] != want:
            problems.append(f"lines[{i}]: part_ids {ln['part_ids']} != {want}")
        for pid in ln["part_ids"]:
            if pid in seen:
                problems.append(f"lines[{i}]: part id {pid} already belongs to lines[{seen[pid]}]")
            seen[pid] = i
        tot[ln["bom"]][0] += 1
        tot[ln["bom"]][1] += ln["quantity"]
    for bom, (lines, parts) in tot.items():
        t = d["totals"][bom]
        if (t["lines"], t["parts"]) != (lines, parts):
            problems.append(f"totals.{bom} says {t['lines']} lines / {t['parts']} parts, lines add up to {lines} / {parts}")
        priced = sum(1 for ln in d["lines"] if ln["bom"] == bom and ln["price"] is not None)
        if (t["priced_lines"], t["unpriced_lines"]) != (priced, lines - priced):
            problems.append(f"totals.{bom} priced/unpriced does not match the lines")
    return problems


def check_area_states(d):
    ids = [a["id"] for a in d["areas"]]
    return [] if len(set(ids)) == 8 else [f"areas must hold the 8 areas exactly once, got {ids}"]


def check_files(d):
    problems, paths = [], [f["path"] for f in d["files"]]
    if len(set(paths)) != len(paths):
        problems.append("files.json lists a path twice")
    for p in paths:
        if ".." in p.split("/") or p.startswith("/"):
            problems.append(f"unsafe path {p}")
    if d.get("bundle"):
        missing = [p for p in d["bundle"]["contents"] if p not in set(paths)]
        if missing:
            problems.append(f"bundle contents not in files: {missing[:3]}")
    return problems


def check_part_notes(d):
    c = constants()
    problems = []
    for pid, n in d["notes"].items():
        if _words(n["what"]) > c["NOTE_WHAT_WORDS"]:
            problems.append(f"{pid}: 'what' has more than {c['NOTE_WHAT_WORDS']} words")
        if _words(n["why"]) > c["NOTE_WHY_WORDS"]:
            problems.append(f"{pid}: 'why' has more than {c['NOTE_WHY_WORDS']} words")
    return problems


# record id -> single-record invariant
SINGLE = {"parts": check_parts, "area-states": check_area_states, "files": check_files}


def part_ids_of(rec_id, d):
    """Part ids that record `d` points at (they must exist in parts.json)."""
    if rec_id == "case":
        out = list(d["part_ids"])
        if d.get("glb"):
            for n in d["glb"]["nodes"]:
                out += n["part_ids"]
        return out
    if rec_id == "ring-model":
        return [p for n in d["nodes"] for p in n["part_ids"]]
    if rec_id == "electronics":
        return [p for b in d["blocks"] for p in b["part_ids"]]
    if rec_id == "schematic-pages":
        return [p for pg in d["pages"] for p in pg["part_ids"]]
    if rec_id == "board-files":
        return [b["part_id"] for b in d["placements"] if b["part_id"]]
    return []


def check_cross(records):
    """records: {id: data}. Every part id another record points at must exist in parts.json.
    Returns {record_id: [problems]} for the records that point at a missing part."""
    parts = records.get("parts")
    if parts is None:
        return {}
    known = {pid for ln in parts["lines"] for pid in ln["part_ids"]}
    bad = {}
    for rid, d in records.items():
        miss = sorted({p for p in part_ids_of(rid, d) if p not in known})
        if miss:
            bad[rid] = [f"unknown part id(s) {miss[:5]}"]
    return bad


_ABSOLUTE = re.compile(
    r"(?<![\w./-])/(?:Users|home|private|tmp|var|opt|etc|mnt|Volumes)/"  # a unix absolute path
    r"|(?<![\w])[A-Za-z]:\\"  # a drive path
    r"|file://|localhost|127\.0\.0\.1"
)


def check_no_absolute(d, path="$"):
    """No string in a record may hold an absolute path, a file:// address or a local host name: the bundle
    is hosted on another machine. Extractors turn source paths into repo-relative ones
    (lib.source.relativize)."""
    problems = []
    if isinstance(d, str):
        m = _ABSOLUTE.search(d)
        if m:
            problems.append(f"{path}: absolute or local address {m.group(0)!r} (use a repo-relative path)")
    elif isinstance(d, dict):
        for k, v in d.items():
            problems += check_no_absolute(v, f"{path}.{k}")
    elif isinstance(d, list):
        for i, v in enumerate(d):
            problems += check_no_absolute(v, f"{path}[{i}]")
    return problems[:5]
