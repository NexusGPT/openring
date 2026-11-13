"""look-options (looks/index.json, looks/<id>.glb).

Options: every folder design/look/<id>/ except viewer and shared, plus every id named in design/status.json
(look.picked, look.in_design, look.rejected). An id '<folder>-<variant>' is design/look/<folder>/out/ring-<variant>.glb; a
plain id is design/look/<id>/out/ring.glb. A folder whose variants are named in status.json is not listed again as a bare
option. An option whose model file is absent is listed with glb null (the screen says the model is missing).
Texts: design/look/<folder>/plain-text.json (or out/plain-text.json) with title, sentence, worse_at (or one entry per id),
else design/look/<folder>/direction.md (first '# ' heading, the Thesis sentence, the bullets under the 'worse' heading).
A sentence is cut to 20 words, a trade-off to 12 words. Size: the POSITION bounds of the model in mm (a file under 1 mm in
its largest size counts in metres and is scaled), in the design's own axes.
Finishes: the FINISHES table of design/look/viewer/viewer.js (name, 0xRRGGBB colour, rough), read at collect time.
rejected: the id is in look.rejected. in_design: the id is in look.in_design. Nothing is held in this file.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cad import glb  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import find_line, pointer  # noqa: E402

RECORD = "look-options"
LOOK_DIR = "design/look"
STATUS = "design/status.json"
VIEWER = "design/look/viewer/viewer.js"
EXCLUDED = {"viewer", "shared"}
MAX_SENTENCE, MAX_TRADE, MAX_TRADES = 20, 12, 3


def words_cut(text, n, clause=True):
    """At most n words, no dots added. Over the limit: the clause before the first ':' or ';' when it is 4 to n words
    (a sentence only), else the last clause end inside the first n words, else the first n whole words."""
    w = text.split()
    if len(w) <= n:
        return " ".join(w)
    if clause:
        head = re.split(r"[:;]", text, maxsplit=1)[0].split()
        if 4 <= len(head) <= n:
            return " ".join(head)
    cut = w[:n]
    stops = [k for k, x in enumerate(cut[:-1]) if x[-1] in ",;:" and k >= 3]  # a clause end inside the limit, 4 words or more
    if stops:
        cut = cut[:stops[-1] + 1]
    return " ".join(cut).rstrip(",;:")


def plain(s):
    s = re.sub(r"\*\*|`|__", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def first_sentence(text):
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return m.group(1) if m else text


def model_rel(look_id):
    folder, _, variant = look_id.partition("-")
    return f"{LOOK_DIR}/{folder}/out/ring-{variant}.glb" if variant else f"{LOOK_DIR}/{look_id}/out/ring.glb"


def read_json_file(ctx, rel):
    p = ctx.source_path(rel)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        raise SourceError(f"{rel} cannot be read: {e}", rel)


def read_status(ctx):
    d = read_json_file(ctx, STATUS)
    if d is not None and not isinstance(d, dict):
        raise SourceError(f"{STATUS} is not an object", STATUS)
    return d


def parse_direction(text):
    title = sentence = None
    worse = []
    in_worse = False
    for ln in text.splitlines():
        if title is None and ln.startswith("# "):
            title = plain(ln[2:])
            title = re.sub(r"^Look\s+\w+\s*:\s*", "", title)
            title = re.sub(r"\s*\(.*\)\s*$", "", title)
            continue
        m = re.match(r"\s*\**Thesis\.?\**:?\**\s*(.*)", ln)
        if m and sentence is None and m.group(1).strip():
            sentence = first_sentence(plain(m.group(1)))
            continue
        if ln.startswith("#"):
            in_worse = "worse" in ln.lower()
            continue
        if in_worse and re.match(r"\s*[-*] ", ln):
            body = plain(re.sub(r"^\s*[-*]\s+", "", ln))
            worse.append(first_sentence(body))
    return title, sentence, worse


def texts_for(ctx, folder, look_id, sources):
    """(title, sentence, worse_at) from plain-text.json, then direction.md."""
    title = sentence = None
    worse = []
    for rel in (f"{LOOK_DIR}/viewer/plain-text.json", f"{LOOK_DIR}/{folder}/plain-text.json",
                f"{LOOK_DIR}/{folder}/out/plain-text.json"):
        d = read_json_file(ctx, rel)
        if isinstance(d, dict):
            for key in ((look_id,) if look_id != folder and rel.startswith(f"{LOOK_DIR}/viewer/") else (look_id, folder)):
                if isinstance(d.get(key), dict):
                    d = d[key]
                    break
            else:
                if rel.startswith(f"{LOOK_DIR}/viewer/"):
                    continue  # the viewer file holds one entry per folder; this one has none
            title = d.get("title") if isinstance(d.get("title"), str) else None
            sentence = d.get("sentence") if isinstance(d.get("sentence"), str) else None
            w = d.get("worse_at", d.get("tradeoffs", d.get("trade_offs", [])))
            worse = [x for x in w if isinstance(x, str)] if isinstance(w, list) else []
            if sentence or worse:
                sources.append(rel)
                break
    dp = ctx.source_path(f"{LOOK_DIR}/{folder}/direction.md")
    if (title is None or sentence is None or not worse) and dp.is_file():
        t, s, w = parse_direction(dp.read_text(encoding="utf-8"))
        title, sentence, worse = title or t, sentence or s, worse or w
        sources.append(f"{LOOK_DIR}/{folder}/direction.md")
    return title, sentence, worse


def bounds(path):
    js, _ = glb.read(path)
    lo, hi = [None] * 3, [None] * 3
    for m in js.get("meshes", []):
        for prim in m.get("primitives", []):
            a = js["accessors"][prim["attributes"]["POSITION"]]
            if "min" not in a or "max" not in a:
                continue
            for i in range(3):
                lo[i] = a["min"][i] if lo[i] is None else min(lo[i], a["min"][i])
                hi[i] = a["max"][i] if hi[i] is None else max(hi[i], a["max"][i])
    if lo[0] is None:
        raise glb.GlbError("no mesh bounds")
    size = [hi[i] - lo[i] for i in range(3)]
    if max(size) < 1.0:  # a ring is never under 1 mm: the file counts in metres (build123d export)
        size = [v * 1000 for v in size]
    return {k: round(size[i], 3) for i, k in enumerate("xyz")}


def js_strings(text):
    return [m.replace("\\'", "'") for m in re.findall(r"'((?:[^'\\]|\\.)*)'", text)]


def variant_entry(ctx, variant):
    """(label, thesis, worse list, source pointer) of one variant from design/look/viewer/viewer.js: the label from
    VARIANT_LABELS and the thesis and worse lines set under `state.variant === '<variant>'`; None when the file or
    the entry is absent."""
    p = ctx.source_path(VIEWER)
    if not p.is_file():
        return None
    lines = p.read_text(encoding="utf-8").splitlines()
    start = next((i for i, ln in enumerate(lines) if re.search(r"state\.variant\s*===\s*'%s'" % re.escape(variant), ln)), None)
    if start is None:
        return None
    thesis = worse = None
    t_line = None
    for i in range(start + 1, min(start + 12, len(lines))):
        ln = lines[i]
        if ln.startswith("  }"):
            break
        m = re.match(r"\s*m1\.thesis\s*=\s*(.*);\s*$", ln)
        if m and js_strings(m.group(1)):
            thesis, t_line = js_strings(m.group(1))[0], i + 1
        m = re.match(r"\s*m1\.worse\s*=\s*\[(.*)\];\s*$", ln)
        if m:
            worse = js_strings(m.group(1))
    if not thesis:
        return None
    label = None
    for ln in lines:
        m = re.match(r"\s*const\s+VARIANT_LABELS\s*=\s*\{(.*)\}", ln)
        if m:
            lm = re.search(r"\b%s\s*:\s*'([^']*)'" % re.escape(variant), m.group(1))
            label = lm.group(1) if lm else None
    return label, thesis, worse or [], pointer(VIEWER, t_line)


def size_of(ctx, oid):
    """(block size {x,y,z} in mm, source pointer) of the option's block, or (None, None). s1 variants: out/measures-<variant>.json
    block_size; else the `size` text of design/look/viewer/designs.json for the folder."""
    folder, _, variant = oid.partition("-")
    if variant:
        rel = f"{LOOK_DIR}/{folder}/out/measures-{variant}.json"
        d = read_json_file(ctx, rel)
        bs = d.get("block_size") if isinstance(d, dict) else None
        if isinstance(bs, list) and len(bs) == 3 and all(isinstance(v, (int, float)) for v in bs):
            line = find_line(ctx.source_path(rel).read_text(encoding="utf-8"), '"block_size"')
            return dict(zip("xyz", [round(v, 3) for v in bs])), pointer(rel, line)
    rel = f"{LOOK_DIR}/viewer/designs.json"
    d = read_json_file(ctx, rel)
    txt = (d.get(folder) or {}).get("size") if isinstance(d, dict) and isinstance(d.get(folder), dict) else None
    m = re.match(r"\s*([0-9.]+)\s*x\s*([0-9.]+)\s*x\s*([0-9.]+)\s*mm", txt or "")
    if m:
        lines = ctx.source_path(rel).read_text(encoding="utf-8").splitlines()
        start = next((i for i, ln in enumerate(lines, 1) if re.match(r'\s*"%s"\s*:' % re.escape(folder), ln)), 1)
        line = find_line("\n".join(lines), '"size"', start)
        return dict(zip("xyz", [float(v) for v in m.groups()])), pointer(rel, line)
    return None, None


def read_finishes(ctx):
    p = ctx.source_path(VIEWER)
    if not p.is_file():
        return [], f"{VIEWER} is not in the design folder; no finishes"
    text = p.read_text(encoding="utf-8")
    m = re.search(r"const\s+FINISHES\s*=\s*\{(.*?)\n\};?", text, re.S)
    if not m:
        return [], f"{VIEWER} has no FINISHES table; no finishes"
    out = []
    for ln in m.group(1).splitlines():
        r = re.match(r"\s*['\"]([^'\"]+)['\"]\s*:\s*\{[^}]*color:\s*0x([0-9a-fA-F]{6})[^}]*rough:\s*([0-9.]+)", ln)
        if r:
            line = find_line(text, ln.strip()[:20])
            out.append({"name": r.group(1), "colour": "#" + r.group(2).lower(), "roughness": float(r.group(3)),
                        "source": pointer(VIEWER, line)})
    return out, (None if out else f"{VIEWER} FINISHES table has no readable row; no finishes")


def extract(ctx):
    from ring_model import finish  # the shared conversion and compression of the bundle

    status = read_status(ctx)
    look = (status or {}).get("look") or {}
    picked = look.get("picked") or None
    rejected = [x for x in look.get("rejected") or [] if isinstance(x, str)]
    in_design = [x for x in look.get("in_design") or [] if isinstance(x, str)]
    named = [x for x in dict.fromkeys(([picked] if picked else []) + in_design + rejected)]

    root = ctx.source_path(LOOK_DIR)
    folders = sorted(d.name for d in root.iterdir() if d.is_dir() and d.name not in EXCLUDED and not d.name.startswith((".", "_"))) if root.is_dir() else []
    covered = {i.partition("-")[0] for i in named if "-" in i}
    ids = list(named)
    for f in folders:
        if f not in covered and f not in ids:
            ids.append(f)
    ids.sort(key=lambda i: (i.partition("-")[0], i))

    notes, sources, options = [], [], []
    if status is not None:
        sources.append(STATUS)
    for oid in ids:
        folder = oid.partition("-")[0]
        osrc = []
        title, sentence, worse = texts_for(ctx, folder, oid, osrc)
        variant = oid.partition("-")[2]
        title = title or oid
        text_src = None
        if variant:
            ent = variant_entry(ctx, variant)
            if ent:
                label, sentence, worse, text_src = ent
                sources.append(VIEWER)
                if label:
                    title = f"{title}: {label}"
            else:
                notes.append(f"{oid}: no entry for variant {variant} in {VIEWER}; text from the folder's direction.md, which may describe an earlier build")
        sentence = words_cut(sentence[:1].upper() + sentence[1:], MAX_SENTENCE) if sentence else None
        worse = [words_cut(w, MAX_TRADE, clause=False) for w in worse[:MAX_TRADES]]
        rel = model_rel(oid)
        g = blk = blk_src = None
        if ctx.source_path(rel).is_file():
            try:
                b = bounds(ctx.source_path(rel))
                blk, blk_src = size_of(ctx, oid)
                if blk:
                    b = blk
                else:
                    notes.append(f"{oid}: no block size in the design files; size shown is the whole model, axes as stored")
                name = f"looks/{oid}.glb"
                finish(ctx, ctx.source_path(rel), name, notes)
                g = {"file": name, "size_bytes": ctx.out_path(name).stat().st_size, "bounds_mm": b}
                sources.append(rel)
            except (glb.GlbError, KeyError, ValueError, OSError) as e:
                notes.append(f"{oid}: model {rel} cannot be read ({e}); listed without a model")
        else:
            notes.append(f"{oid}: no model file at {rel}")
        if not osrc and not (folder in folders):
            notes.append(f"{oid}: no design/look/{folder}/ folder; no texts")
        sources += osrc
        if g and blk:
            sources.append(blk_src["file"])
            notes.append(f"{oid}: block size from {blk_src['file']} line {blk_src['line']}")
        options.append({"id": oid, "title": title, "sentence": sentence, "worse_at": worse, "glb": g,
                        "rejected": oid in rejected,
                        "in_design": oid in in_design,
                        "source": text_src or (blk_src if g and blk else pointer(rel if g else (osrc[0] if osrc else (STATUS if status is not None else LOOK_DIR))))})
    finishes, fnote = read_finishes(ctx)
    if fnote:
        notes.append(fnote)
    else:
        sources.append(VIEWER)

    data = {"picked": picked, "options": options, "finishes": finishes}
    open_n = sum(1 for o in options if not o["rejected"])
    msg = [f"{open_n} option(s) not rejected"]
    if not open_n and not picked:
        msg.append("nothing picked and nothing in design: the screen shows 'New options in design'")
    st = {"status": "ok", "source": [s for s in dict.fromkeys(sources) if ctx.source_path(s).is_file()],
          "message": "; ".join(msg + notes)}
    return data, st
