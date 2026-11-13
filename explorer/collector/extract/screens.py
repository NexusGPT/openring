"""Screen geometry and screen states for ring-model.json (a helper: no RECORD, no extract()).

rect: the lit area of the screen part. Read from the placement row whose note says "lit area W (X) x H (Y)
centred X a Y b" (design/mech/thin/placement.csv); when no row says it, from design/look/shared/envelope.py
(LIMITS screen_active_x / screen_active_y and SCREEN_CX, SCREEN_CY). cx, cy are plan coordinates in design
axes (x along the finger, y across, + thumb), mm.
band: width from the placement note of the part that says "band W x" (fallback: the exterior model's band
mesh, measured along x); inner diameter from LIMITS band_inner_d_size9 in envelope.py.
states: the table of design/firmware.md section 3.3 (screen, shown in, fields top to bottom). Each state also carries
`pictures` (the ring software's own 240 x 120 pictures of it, listed in PICTURES/manifest.md, copied into the bundle at
screens/<name>.png; the first one is shown) or, when it has none, `picture_words` saying so.
A manifest row belongs to the state whose name is the first SCR_ name in its scene; a scene with no SCR_ name (the status
and charging pictures) belongs to the state whose label starts with the same capitalised mode word.
"""
import hashlib
import re
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import md  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import find_line, pointer  # noqa: E402

FIRMWARE = "design/firmware.md"
PICTURES = "design/software/os/screens"
MANIFEST = PICTURES + "/manifest.md"
PICTURE_W, PICTURE_H, PICTURE_SCALE = 240, 120, 4  # scale: the stage shows each pixel as a 4 x 4 block of its texture
ENVELOPE = "design/look/shared/envelope.py"
SECTION = r"^3\.3\b"

_LIT = re.compile(r"lit area\s+([\d.]+)\s*\(X\)\s*x\s*([\d.]+)\s*\(Y\)\s*centred X\s*(-?[\d.]+)\s*Y\s*(-?[\d.]+)")
_BAND_W = re.compile(r"\bband\s+([\d.]+)\s*x\b")
_ENV_NUM = r"[\"']%s[\"']\s*:\s*(-?[\d.]+)"
_ENV_CENTRE = re.compile(r"^SCREEN_CX,\s*SCREEN_CY\s*=\s*\(?\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)", re.M)


def _envelope(ctx):
    p = ctx.source_path(ENVELOPE)
    return p.read_text(encoding="utf-8") if p.is_file() else None


def rect(ctx, rows):
    for r in rows:
        m = _LIT.search(r["note"] or "")
        if m:
            w, h, cx, cy = (float(g) for g in m.groups())
            return {"cx": cx, "cy": cy, "w": w, "h": h, "source": pointer("design/mech/thin/placement.csv", r["line"])}
    text = _envelope(ctx)
    if text is None:
        raise SourceError("no placement row names the lit area and design/look/shared/envelope.py is absent", ENVELOPE)
    w = re.search(_ENV_NUM % "screen_active_x", text)
    h = re.search(_ENV_NUM % "screen_active_y", text)
    c = _ENV_CENTRE.search(text)
    if not (w and h and c):
        raise SourceError("envelope.py has no screen_active_x, screen_active_y or SCREEN_CX/SCREEN_CY", ENVELOPE)
    line = find_line(text, "screen_active_x")
    return {"cx": float(c.group(1)), "cy": float(c.group(2)), "w": float(w.group(1)), "h": float(h.group(1)),
            "source": pointer(ENVELOPE, line)}


def band(ctx, rows, exterior_band_width=None):
    """(width_mm, inner_diameter_mm, source) or raises SourceError."""
    width, src = None, None
    for r in rows:
        m = _BAND_W.search(r["note"] or "")
        if m:
            width, src = float(m.group(1)), pointer("design/mech/thin/placement.csv", r["line"])
            break
    if width is None and exterior_band_width is not None:
        width, src = exterior_band_width
    text = _envelope(ctx)
    m = re.search(_ENV_NUM % "band_inner_d_size9", text or "")
    if width is None or not m:
        raise SourceError("the band width or the inner diameter cannot be found (placement note 'band W x', exterior model, "
                          "envelope.py band_inner_d_size9)", [ENVELOPE])
    return {"width_mm": width, "inner_diameter_mm": float(m.group(1)), "source": src or pointer(ENVELOPE)}


def _split_fields(cell):
    out, depth, quote, cur = [], 0, False, ""
    for ch in cell:
        if ch == '"':
            quote = not quote
        elif ch == "(" and not quote:
            depth += 1
        elif ch == ")" and not quote:
            depth -= 1
        if ch == "," and depth == 0 and not quote:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def field_kind(text):
    t = text.lower()
    for kind, words in (("dot", ("dot",)), ("timer", ("timer",)), ("battery", ("battery",)),
                        ("storage", ("storage",)), ("bar", ("progress", "percent of")), ("icon", ("icon",))):
        if any(w in t for w in words):
            return kind
    return "text"


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "field"


def states(ctx):
    p = ctx.source_path(FIRMWARE)
    if not p.is_file():
        raise SourceError(f"{FIRMWARE} is absent", FIRMWARE)
    text = p.read_text(encoding="utf-8")
    t = md.table_after_heading(text, SECTION)
    if not t:
        raise SourceError(f"{FIRMWARE} has no screen table under a heading numbered 3.3", FIRMWARE)
    cols = [c.lower() for c in t["columns"]]
    try:
        i_shown = next(i for i, c in enumerate(cols) if c.startswith("shown"))
        i_fields = next(i for i, c in enumerate(cols) if c.startswith("fields"))
    except StopIteration:
        raise SourceError(f"{FIRMWARE} 3.3 table lacks the 'Shown in' or 'Fields' column", FIRMWARE)
    out = []
    for row, ln in zip(t["rows"], t["row_lines"]):
        state = row[0].strip("` ").strip()
        src = pointer(FIRMWARE, ln)
        fields, seen = [], {}
        for f in _split_fields(row[i_fields]):
            label = f.replace("`", "").strip()
            fid = _slug(label)
            seen[fid] = seen.get(fid, 0) + 1
            if seen[fid] > 1:
                fid = f"{fid}-{seen[fid]}"
            fields.append({"id": fid, "kind": field_kind(label), "label": label, "source": src})
        out.append({"state": state, "label": row[i_shown].replace("`", "").strip() or state, "fields": fields, "source": src})
    return out


_SCR = re.compile(r"\bSCR_[A-Z0-9_]+\b")
_MODE = re.compile(r"^[A-Z][A-Z_]+")
WORDS_NONE = "The ring software has no picture for this screen."
WORDS_NO_SET = "The ring software's screen pictures are not in the design files, so no screen has a picture."
WORDS_BAD = "The ring software lists a picture for this screen, but %s."


def manifest_rows(text):
    """[{name, scene, size, sha16, sha16_4x, line}] of the picture table of manifest.md (read here, one row per picture)."""
    rows = []
    for ln, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 7 or c[0].lower() == "picture":
            continue
        rows.append({"name": c[0], "scene": c[1], "size": c[2], "sha16": c[5], "sha16_4x": c[6], "line": ln})
    return rows


def png_size(data):
    """(width, height) of a PNG, or None when the bytes are not one."""
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def owner_of(row, state_list):
    """The index of the state a manifest row belongs to, or None."""
    names = [re.match(r"\w+", s["state"]).group(0) for s in state_list]
    m = _SCR.search(row["scene"])
    if m:
        return names.index(m.group(0)) if m.group(0) in names else None
    mode = _MODE.match(row["scene"])
    if mode:
        hits = [i for i, s in enumerate(state_list) if (_MODE.match(s["label"]) or [None])[0] == mode.group(0)]
        return hits[0] if len(hits) == 1 else None
    return None


def _picture(ctx, row, notes):
    """The record entry of one manifest row, with its two files copied into the bundle, or the reason in words."""
    p = ctx.source_path(f"{PICTURES}/{row['name']}.png")
    if not p.is_file():
        return None, f"its file {row['name']}.png is missing"
    data = p.read_bytes()
    if png_size(data) != (PICTURE_W, PICTURE_H):
        return None, f"its file {row['name']}.png is not {PICTURE_W} x {PICTURE_H} pixels"
    sha = hashlib.sha256(data).hexdigest()
    if not sha.startswith(row["sha16"]):
        return None, f"its file {row['name']}.png differs from the one the manifest describes"
    shutil.copyfile(p, ctx.out_path(f"screens/{row['name']}.png"))
    return {"name": row["name"], "file": f"screens/{row['name']}.png", "width": PICTURE_W, "height": PICTURE_H, "scale": PICTURE_SCALE,
            "sha256": sha, "scene": row["scene"], "source": pointer(MANIFEST, row["line"])}, None


def attach_pictures(ctx, state_list, notes):
    """Adds `pictures` or `picture_words` to every state (in place) and copies the pictures into the bundle."""
    p = ctx.source_path(MANIFEST)
    if not p.is_file():
        for s in state_list:
            s["picture_words"] = WORDS_NO_SET
        notes.append(f"{MANIFEST} is not in the design folder; no screen has a picture")
        return
    owned = {i: [] for i in range(len(state_list))}
    bad = {}
    for row in manifest_rows(p.read_text(encoding="utf-8")):
        i = owner_of(row, state_list)
        if i is None:
            notes.append(f"picture {row['name']} belongs to no screen state of firmware.md 3.3")
            continue
        pic, why = _picture(ctx, row, notes)
        if pic:
            owned[i].append(pic)
        else:
            bad.setdefault(i, why)
            notes.append(f"picture {row['name']}: {why}")
    for i, s in enumerate(state_list):
        if owned[i]:
            s["pictures"] = owned[i]
        else:
            s["picture_words"] = WORDS_BAD % bad[i] if i in bad else WORDS_NONE
