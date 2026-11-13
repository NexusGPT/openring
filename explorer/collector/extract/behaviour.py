"""firmware-rules (behaviour.json): what the behaviour engine interprets.

Reads design/firmware.md: the state list (1.1), the transition table (1.2), the record button tables
(2.1), the joystick table (2.2), the motor table (3.1) and the light rule (3.2). The tables are found by
their column headings, never by their position or by a state's name. The ring facts that changed after
the design the firmware was written for (design/architecture.md 16.5, 17.3, 17.8) travel as plain notes.
The record's basis is the version firmware.md says it follows; its current version is the architecture's own.
"""
import re

from lib import md  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import find_line_re, pointer  # noqa: E402
from lib.version import read_follows, read_own  # noqa: E402

RECORD = "firmware-rules"

FIRMWARE = "design/firmware.md"
ARCH = "design/architecture.md"

_TICKED = re.compile(r"`([A-Za-z][A-Za-z0-9_]*)`")
_MOTOR = re.compile(r"\bM[0-9A-Z]\b")


def classify(event):
    """event kind of a transition's event text."""
    t = event.lower()
    if "long press" in t:
        return "long_press"
    if "short press" in t:
        return "short_press"
    if "double press" in t:
        return "double_press"
    if "joystick" in t:
        return "joystick"
    if t.startswith("init done"):
        return "other"
    if "vbus" in t:
        return "vbus"
    if "battery" in t:
        return "battery"
    if re.search(r"free space|storage|chunk write", t):
        return "storage"
    return "other"


def _read(ctx, rel):
    path = ctx.source_path(rel)
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SourceError(f"{rel} cannot be read: {e}", rel)


def _table(text, title_re, columns_re, what):
    """The first table, in the section whose heading matches title_re, whose first column heading matches columns_re."""
    sec = md.section(text, title_re)
    if sec is None:
        raise SourceError(f"{FIRMWARE} has no section for {what}", FIRMWARE)
    first, last, _ = sec
    for t in md.tables(text, first, last):
        if re.search(columns_re, t["columns"][0], re.I):
            return t
    raise SourceError(f"{FIRMWARE}: no {what} table found", FIRMWARE)


def _ticked(cell):
    m = _TICKED.search(cell)
    return m.group(1) if m else None


def _src(line, rel=FIRMWARE):
    return pointer(rel, line)


def _states(text):
    t = _table(text, r"^1\.1\b", r"^State$", "state list")
    cols = [c.lower() for c in t["columns"]]
    col = {
        "microphones": next(i for i, c in enumerate(cols) if c.startswith("microphones")),
        "storage": next(i for i, c in enumerate(cols) if c.startswith("storage")),
        "screen": next(i for i, c in enumerate(cols) if c.startswith("screen")),
        "radio": next(i for i, c in enumerate(cols) if c.startswith("radio")),
        "meaning": next(i for i, c in enumerate(cols) if c.startswith("meaning")),
    }
    out = []
    for row, line in zip(t["rows"], t["row_lines"]):
        sid = _ticked(row[0])
        if not sid:
            continue
        mic = row[col["microphones"]].strip().lower()
        out.append({
            "id": sid, "label": sid.replace("_", " ").capitalize(), "meaning": row[col["meaning"]] or sid,
            "microphones": "on" if mic.startswith("on") else "off",
            "storage": row[col["storage"]] or None, "screen": row[col["screen"]] or None,
            "radio": row[col["radio"]] or None, "source": _src(line),
        })
    if not out:
        raise SourceError(f"{FIRMWARE}: the state list holds no state", FIRMWARE)
    return out


def _transitions(text, state_ids):
    t = _table(text, r"^1\.2\b", r"^From$", "transition")
    out = []
    for row, line in zip(t["rows"], t["row_lines"]):
        frm, to = _ticked(row[0]), _ticked(row[2])
        if not frm or not to:
            continue
        if frm not in state_ids or to not in state_ids:
            raise SourceError(f"{FIRMWARE}:{line}: transition names a state that is not in the state list", FIRMWARE)
        actions = row[3].strip() or None
        out.append({
            "from": frm, "event_text": row[1], "event_kind": classify(row[1]), "to": to, "actions": actions,
            "motor_ids": sorted(set(_MOTOR.findall(actions or ""))), "source": _src(line),
        })
    if not out:
        raise SourceError(f"{FIRMWARE}: the transition table holds no row", FIRMWARE)
    return out


def _ints(s):
    return [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", s)]


def _gestures(text, state_ids):
    sec = md.section(text, r"^2\.1\b")
    if sec is None:
        raise SourceError(f"{FIRMWARE} has no record button section (2.1)", FIRMWARE)
    first, last, _ = sec
    tabs = md.tables(text, first, last)
    gest = next((t for t in tabs if re.match(r"^Gesture$", t["columns"][0], re.I)), None)
    par = next((t for t in tabs if re.match(r"^Parameter$", t["columns"][0], re.I)), None)
    if gest is None or par is None:
        raise SourceError(f"{FIRMWARE}: gesture or parameter table of 2.1 not found", FIRMWARE)
    # one state per column headed "In `STATE`"
    state_cols = [(i, _ticked(c)) for i, c in enumerate(gest["columns"]) if i > 1 and _ticked(c) in state_ids]
    other_col = next((i for i, c in enumerate(gest["columns"]) if "every other" in c.lower()), None)
    params = {r[0].lower(): (r[1], ln) for r, ln in zip(par["rows"], par["row_lines"])}

    def param(name):
        for k, v in params.items():
            if k.startswith(name):
                return v
        return None

    long_p, short_p, dbl_p = param("long press"), param("short press"), param("double-press")
    if not (long_p and short_p and dbl_p):
        raise SourceError(f"{FIRMWARE}: the 2.1 parameter table lacks a long press, short press or double-press row", FIRMWARE)
    long_ms = _ints(long_p[0])[0]
    short_lo, short_hi = _ints(short_p[0])[:2]
    window = _ints(dbl_p[0])[0]
    kinds = {"long press": ("long_press", long_ms, None, None, "while_held", long_p[1]),
             "short press": ("short_press", short_lo, short_hi, window, "after_window", short_p[1]),
             "double press": ("double_press", short_lo, short_hi, window, "after_window", dbl_p[1])}
    out = []
    for row, line in zip(gest["rows"], gest["row_lines"]):
        name = row[0].strip().lower()
        if name not in kinds:
            continue
        kind, lo, hi, win, fires, pline = kinds[name]
        per = [{"state": s, "effect": row[i]} for i, s in state_cols if row[i]]
        if other_col is not None and row[other_col]:
            per.append({"state": "*", "effect": row[other_col]})
        out.append({"kind": kind, "timing_text": row[1], "min_hold_ms": lo, "max_hold_ms": hi, "window_ms": win,
                    "fires": fires, "per_state": per, "source": _src(line)})
    if {g["kind"] for g in out} != {"long_press", "short_press", "double_press"}:
        raise SourceError(f"{FIRMWARE}: the 2.1 gesture table lacks a long, short or double press row", FIRMWARE)
    # joystick repeat: "Holding a direction for 500 ms repeats it every 150 ms"
    jl = find_line_re(text, r"Holding a direction for \d+ ms", first)
    if jl:
        line_txt = text.splitlines()[jl - 1]
        out.append({"kind": "joystick", "timing_text": re.sub(r"^[\s\-*]+", "", line_txt).strip(),
                    "min_hold_ms": None, "max_hold_ms": None, "window_ms": _ints(line_txt)[0] if _ints(line_txt) else None,
                    "fires": "while_held", "per_state": [], "source": _src(jl)})
    return out


def _joystick(text):
    t = _table(text, r"^2\.2\b", r"^Screen$", "joystick")
    dirs = [("up", "Up"), ("down", "Down"), ("toward the hand", "Left"), ("toward the fingertip", "Right"), ("centre", "Centre")]
    idx = {c.lower(): i for i, c in enumerate(t["columns"])}
    out = []
    for name, col in dirs:
        i = idx.get(col.lower())
        if i is None:
            raise SourceError(f"{FIRMWARE}: joystick table has no {col} column", FIRMWARE)
        parts = [f"{r[0]}: {r[i]}" for r in t["rows"] if r[i]]
        out.append({"direction": name, "effect": "; ".join(parts) or "none", "source": _src(t["line"])})
    return out


def _motors(text):
    t = _table(text, r"^3\.1\b", r"^Id$", "motor")
    out = []
    for row, line in zip(t["rows"], t["row_lines"]):
        if not re.fullmatch(r"M[0-9A-Z]", row[0].strip()):
            continue
        toks = re.findall(r"(\d+)\s*(on|off)", row[2])
        pulses, cur = [], None
        for n, kind in toks:
            if kind == "on":
                cur = {"on_ms": int(n), "off_ms": 0}
                pulses.append(cur)
            elif cur is not None:
                cur["off_ms"] = int(n)
        if not pulses:
            raise SourceError(f"{FIRMWARE}:{line}: motor pattern {row[0]} has no readable pulse", FIRMWARE)
        total = sum(p["on_ms"] + p["off_ms"] for p in pulses)
        stated = _ints(row[3])
        if stated and stated[0] != total:
            raise SourceError(f"{FIRMWARE}:{line}: motor pattern {row[0]} adds up to {total} ms, the table says {stated[0]}", FIRMWARE)
        out.append({"id": row[0].strip(), "event": row[1], "pulses": pulses, "total_ms": total, "source": _src(line)})
    if not out:
        raise SourceError(f"{FIRMWARE}: the motor table holds no pattern", FIRMWARE)
    return out


def _light(text):
    sec = md.section(text, r"^3\.2\b")
    if sec is None:
        raise SourceError(f"{FIRMWARE} has no recording light section (3.2)", FIRMWARE)
    first, last, body = sec
    for off, ln in enumerate(body):
        if re.search(r"exactly while VDD_MIC is on", ln):
            txt = re.sub(r"^[\s\-*]+", "", ln).strip()
            return {"text": txt, "on_where_microphones_on": True, "source": _src(first + 1 + off)}
    # the present design (v7, architecture 17.30): the recording light is removed and the screen is the recording sign
    for off, ln in enumerate(body):
        if re.search(r"No recording light", ln):
            txt = re.sub(r"^[\s\-*]+", "", ln).replace("**", "").strip()
            return {"text": txt, "on_where_microphones_on": False, "source": _src(first + 1 + off)}
    raise SourceError(f"{FIRMWARE}: 3.2 states neither that the light is on exactly while the microphones are on nor that there is no recording light", FIRMWARE)


def _notes(arch):
    """What changed in the ring since the design the firmware followed, each with its file and line."""
    if arch is None:
        return []
    wants = [
        (r"^16\.5\b", r"four SKTAAAE010 switches", "The joystick is four switches: up, down, toward the hand, toward the fingertip."),
        (r"^16\.5\b", r"Centre press:", "A centre press is read when both switches of an opposite pair close within 40 ms; there is no fifth switch."),
        (r"^16\.5\b", r"^- Record button:", "The record button is its own switch, on its own cap."),
        (r"^17\.3\b", r"Switch names", "Switch names: SW1 up, SW3 down, SW4 toward the hand, SW5 toward the fingertip, SW2 record button."),
        (r"^17\.8\b", r"Flex tails", "In the latest look the thumb side carries the record switch and the four joystick switches."),
    ]
    out = []
    for head, needle, text in wants:
        sec = md.section(arch, head)
        if sec is None:
            continue
        first, last, _ = sec
        for i, ln in enumerate(arch.splitlines(), 1):
            if first < i <= last and re.search(needle, ln):
                out.append({"text": text, "source": pointer(ARCH, i)})
                break
        else:
            if head.startswith(r"^17\.3"):
                # the switch-name line sits after the 17.3 table, before the next heading; none found: skip
                pass
    return out


def extract(ctx):
    fw = _read(ctx, FIRMWARE)
    if fw is None:
        return None, {"status": "missing", "source": [FIRMWARE], "message": f"{FIRMWARE} is absent."}
    arch = _read(ctx, ARCH)
    states = _states(fw)
    ids = {s["id"] for s in states}
    data = {
        "design_version": read_own(arch) if arch else None,
        "basis_version": read_follows(fw),
        "states": states,
        "transitions": _transitions(fw, ids),
        "gestures": _gestures(fw, ids),
        "motor_patterns": _motors(fw),
        "joystick": _joystick(fw),
        "light_rule": _light(fw),
        "notes": _notes(arch),
    }
    mic_on = [s["id"] for s in states if s["microphones"] == "on"]
    msg = None
    if len(mic_on) != 1:
        msg = f"The state list has {len(mic_on)} states with the microphones on; the rule says exactly one."
    return data, {"status": "ok", "source": [FIRMWARE] + ([ARCH] if arch else []),
                  "basis_version": data["basis_version"], "current_version": data["design_version"], "message": msg}
