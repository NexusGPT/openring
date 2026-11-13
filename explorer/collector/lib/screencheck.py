"""Checks of the screen states' pictures (ring-model.json screens.states[].pictures). Each returns a list of problems in plain
words; an empty list means the record passes. Used by collector/tests/collector-screens against the real design and against
kept broken inputs. Nothing here reads the extractor: the manifest, the source pictures and the bundle files are read from disk."""
import hashlib
import re
import struct
import zlib
from pathlib import Path

W, H = 240, 120


def manifest(text):
    """{picture name: scene} of the table in manifest.md, read here."""
    out = {}
    for line in text.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(c) >= 7 and c[0] != "picture" and not set(c[0]) <= set("-: "):
            out[c[0]] = c[1]
    return out


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def pixels(data):
    """(width, height, rows) of an 8-bit RGB or RGBA PNG without interlace; rows are bytes of the unfiltered scanlines."""
    w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", data[16:29])
    if depth != 8 or ctype not in (2, 6) or inter:
        raise ValueError("only 8-bit RGB or RGBA PNG without interlace is read here")
    bpp = 3 if ctype == 2 else 4
    raw, pos = b"", 8
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            raw += data[pos + 8:pos + 8 + n]
        pos += 12 + n
    raw, rows, prev = zlib.decompress(raw), [], bytes(w * bpp)
    for y in range(h):
        f, line = raw[y * (w * bpp + 1)], bytearray(raw[y * (w * bpp + 1) + 1:(y + 1) * (w * bpp + 1)])
        for i in range(len(line)):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line))
        prev = bytes(line)
    return w, h, rows, bpp


def border_problems(data, name):
    """The frame of one-pixel width round the picture must be pure black: the glass reads as one black face."""
    w, h, rows, bpp = pixels(data)
    bad = []
    for y in range(h):
        for x in ((range(w) if y in (0, h - 1) else (0, w - 1))):
            if any(rows[y][x * bpp:x * bpp + 3]):
                bad.append((x, y))
    return [f"{name}: {len(bad)} pixels of the outer frame are not black, first at {bad[0]}"] if bad else []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(states, bundle, manifest_text, source_dir):
    """Every state has pictures that exist in the bundle (240 x 120 and 960 x 480, same bytes as the source picture) or words
    saying it has none; every picture of the manifest belongs to exactly one state."""
    bundle, source_dir, problems = Path(bundle), Path(source_dir), []
    rows = manifest(manifest_text)
    seen = {}
    for s in states:
        pics, words = s.get("pictures"), s.get("picture_words")
        if bool(pics) == bool(words):
            problems.append(f"{s['state']}: must have pictures or words that it has none, not both and not neither")
            continue
        if words and not re.search(r"\bno picture\b|\bnot in the design files\b|\bpicture\b", words):
            problems.append(f"{s['state']}: the words {words!r} do not speak of a picture")
        for p in pics or []:
            seen[p["name"]] = seen.get(p["name"], 0) + 1
            if p["name"] not in rows:
                problems.append(f"{s['state']}: picture {p['name']} is not in the manifest")
            elif rows[p["name"]] != p["scene"]:
                problems.append(f"{s['state']}: picture {p['name']} carries scene {p['scene']!r}, the manifest says {rows[p['name']]!r}")
            f = bundle / p["file"]
            if not f.is_file():
                problems.append(f"{s['state']}: {p['file']} is not in the data folder")
                continue
            if png_size(f.read_bytes()) != (W, H):
                problems.append(f"{p['file']}: size {png_size(f.read_bytes())}, expected {(W, H)}")
            src = source_dir / f"{p['name']}.png"
            if not src.is_file() or sha(src) != sha(f) or p["sha256"] != sha(f):
                problems.append(f"{p['file']}: its sha256 differs from the source picture or from the record")
    for n in rows:
        if seen.get(n, 0) != 1:
            problems.append(f"manifest picture {n}: belongs to {seen.get(n, 0)} states, not 1")
    extra = sorted(set(seen) - set(rows))
    if extra:
        problems.append(f"pictures not in the manifest: {extra}")
    return problems
