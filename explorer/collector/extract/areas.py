"""area-states (areas.json): the state of each of the 8 areas from design/status.json, each area's
basis version against the current design version, and the look pick and rejected looks.

The state words are the five the contract names. A word that is not one of them is never passed
through: the area reads 'state unknown' and `why` says what the file held. Without a status file
every area reads 'state unknown'.
"""
import json
import re

from lib.errors import SourceError  # noqa: E402
from lib.version import is_stale, read_follows, read_own  # noqa: E402

RECORD = "area-states"

STATUS = "design/status.json"
ARCH = "design/architecture.md"
AREAS = ["look", "inside", "electronics", "board", "parts", "behaviour", "case", "open"]
STATES = ["done", "in progress", "not started", "waiting on a supplier", "state unknown"]
UNKNOWN = "state unknown"

# The document that says which design version an area's work was made for.
BASIS_DOC = {
    "behaviour": "design/firmware.md",
    "parts": "design/bom-notes.md",
    "case": "design/case/case-architecture.md",
}
_VERSION_LINE = re.compile(r"\bVersion:?\s+([A-Z]{1,2}\d+(?:-[A-Za-z]+)?)")


def _read(ctx, rel):
    p = ctx.source_path(rel)
    if not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _basis(ctx, area, entry):
    given = entry.get("basis_version")
    if isinstance(given, str) and given:
        return given
    doc = BASIS_DOC.get(area)
    text = _read(ctx, doc) if doc else None
    if text is None:
        return None
    v = read_follows(text)
    if v is None:
        m = _VERSION_LINE.search(text)
        v = m.group(1) if m and re.match(r"A\d", m.group(1)) else None
    return v


def _line_of(text, area):
    m = re.search(rf'^\s*"{area}"\s*:', text, re.M)
    return text.count("\n", 0, m.start()) + 1 if m else None


def _strlist(v, name):
    if v is None:
        return []
    if not isinstance(v, list) or not all(isinstance(x, str) and x for x in v):
        raise SourceError(f"{STATUS}: look.{name} must be a list of names", STATUS)
    return list(v)


def extract(ctx):
    arch = _read(ctx, ARCH)
    current = read_own(arch) if arch else None
    status_text = _read(ctx, STATUS)
    if status_text is None:
        if ctx.source_path(STATUS).exists():
            raise SourceError(f"{STATUS} cannot be read", STATUS)
        areas = [{"id": a, "state": UNKNOWN, "why": None, "who": None, "basis_version": None,
                  "current_version": current, "stale": False, "source": None} for a in AREAS]
        data = {"design_version": None, "updated": None, "areas": areas,
                "look": {"picked": None, "rejected": [], "in_design": []}}
        return data, {"status": "missing", "source": [STATUS],
                      "message": f"{STATUS} is absent: every area reads state unknown."}
    try:
        status = json.loads(status_text)
    except ValueError as e:
        raise SourceError(f"{STATUS} is not valid JSON: {e}", STATUS)
    if not isinstance(status, dict) or not isinstance(status.get("areas", {}), dict):
        raise SourceError(f"{STATUS} must hold an object with an 'areas' object", STATUS)
    entries = status.get("areas", {})
    areas = []
    for a in AREAS:
        e = entries.get(a)
        if not isinstance(e, dict):
            areas.append({"id": a, "state": UNKNOWN, "why": None if e is None else f"{STATUS} holds no readable entry for {a}.",
                          "who": None, "basis_version": None, "current_version": current, "stale": False,
                          "source": {"file": STATUS, "line": _line_of(status_text, a)}})
            continue
        word, why = e.get("state"), e.get("why")
        who = e.get("who")
        if word not in STATES:
            why = f"{STATUS} gives the state {word!r}, which is not one of the five state words."
            word = UNKNOWN
        basis = _basis(ctx, a, e)
        areas.append({"id": a, "state": word,
                      "why": why if isinstance(why, str) else None,
                      "who": who if isinstance(who, str) else None,
                      "basis_version": basis, "current_version": current,
                      "stale": is_stale(basis, current),
                      "source": {"file": STATUS, "line": _line_of(status_text, a)}})
    look = status.get("look") or {}
    if not isinstance(look, dict):
        raise SourceError(f"{STATUS}: 'look' must be an object", STATUS)
    picked = look.get("picked")
    if picked is not None and not isinstance(picked, str):
        raise SourceError(f"{STATUS}: look.picked must be a name or null", STATUS)
    updated = status.get("updated")
    if not (isinstance(updated, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated)):
        updated = None
    dv = status.get("design_version")
    dv = dv if isinstance(dv, str) and dv else None
    data = {"design_version": dv, "updated": updated, "areas": areas,
            "look": {"picked": picked, "rejected": _strlist(look.get("rejected"), "rejected"),
                     "in_design": _strlist(look.get("in_design"), "in_design")}}
    sources = [STATUS] + ([ARCH] if arch else [])
    return data, {"status": "ok", "source": sources, "basis_version": dv, "current_version": current}
