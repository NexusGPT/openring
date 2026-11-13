"""schematic-pages (schematic/index.json + one SVG per page).

Sources: design/ecad/ring/ring.kicad_sch (the root page and one `(sheet ...)` line per sub-page: its
Sheetname is the page title, its `(page "N")` the page number), design/ecad/ring/parts.csv (column `sheet` says
which parts sit on which page; its value is the Sheetfile name without the `<project>_` prefix),
design/ecad/ring/ring-schematic.pdf (the fallback link), design/architecture.md (current version).

Each page is exported with `kicad-cli sch export svg` at collect time. The tool is `$KICAD_CLI`, else the
KiCad app on this machine, else `kicad-cli` on the PATH. When it is missing or fails, every page keeps svg
null and a pdf link, and the status is 'missing' (or 'unparsed' when the tool ran and failed) with the reason.
The SVG files are copied into the bundle as schematic/<page id>.svg and must hold no absolute path.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import csvread, invariants  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.version import read_own  # noqa: E402

RECORD = "schematic-pages"

SCH_DIR = "design/ecad/ring"
ROOT_SCH = f"{SCH_DIR}/ring.kicad_sch"
PARTS_CSV = f"{SCH_DIR}/parts.csv"
NETLIST_CSV = f"{SCH_DIR}/netlist.csv"
OPEN_PINS_CSV = f"{SCH_DIR}/open-pins.csv"
PDF = f"{SCH_DIR}/ring-schematic.pdf"
ARCH = "design/architecture.md"
DEFAULT_TOOLS = [os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
                 "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"]

_PROP = r'\(property "%s" "([^"]*)"'
_PAGE = re.compile(r'\(page "(\d+)"\)')
_TITLE = re.compile(r'\(title "([^"]*)"\)')
_BASIS = re.compile(r"architecture\.md\s+([A-Z]{1,2}\d+(?:-[A-Za-z]+)?)")


def read_pages(root, sch_text=None):
    """[{'id','title','number','key','file','line'}] in page order: the root page first, then each sub-page.
    Raises SourceError when the root file has no page."""
    path = Path(root) / ROOT_SCH
    if not path.is_file():
        raise SourceError(f"{ROOT_SCH} is missing", ROOT_SCH)
    text = sch_text if sch_text is not None else path.read_text(encoding="utf-8")
    stem = path.stem
    t = _TITLE.search(text)
    pages = [{"id": "overview", "title": t.group(1) if t else stem, "number": 1, "key": None, "file": path.name,
              "line": 1}]
    for i, ln in enumerate(text.splitlines(), 1):
        if not ln.lstrip().startswith("(sheet "):
            continue
        name, fil = (re.search(_PROP % q, ln) for q in ("Sheetname", "Sheetfile"))
        num = _PAGE.search(ln)
        if not (name and fil and num):
            raise SourceError(f"{ROOT_SCH} line {i}: a sheet without name, file or page", ROOT_SCH)
        key = Path(fil.group(1)).stem
        key = key.split("_", 1)[1] if "_" in key else key
        pages.append({"id": re.sub(r"[^A-Za-z0-9_.-]+", "_", key), "title": name.group(1), "number": int(num.group(1)),
                      "key": key, "file": fil.group(1), "line": i})
    if len(pages) == 1:
        raise SourceError(f"{ROOT_SCH} lists no sub-page", ROOT_SCH)
    pages.sort(key=lambda p: p["number"])
    return pages


def read_part_sheets(root):
    """{reference: sheet key} from parts.csv; the line of each row is kept in the second dict."""
    rows = csvread.read(Path(root) / PARTS_CSV, required=("reference", "sheet"))
    return {r["cells"]["reference"].strip(): r["cells"]["sheet"].strip() for r in rows if r["cells"]["reference"].strip()}


def part_id(ref):
    return f"ring:{ref}"


def _tool():
    env = os.environ.get("KICAD_CLI")
    if env is not None:
        return env if Path(env).is_file() and os.access(env, os.X_OK) else None
    for c in DEFAULT_TOOLS:
        if Path(c).is_file():
            return c
    return shutil.which("kicad-cli")


def _tool_version(tool):
    try:
        r = subprocess.run([tool, "version"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    v = r.stdout.strip().splitlines()
    return v[-1].strip() if r.returncode == 0 and v else None


def _export(tool, sch_file, out):
    r = subprocess.run([tool, "sch", "export", "svg", "-o", str(out), str(sch_file)], capture_output=True, text=True,
                       timeout=300)
    return r


def extract(ctx):
    root = ctx.source_root
    pages = read_pages(root)
    by_key = {}
    for ref, key in read_part_sheets(root).items():
        by_key.setdefault(key, []).append(ref)
    arch = root / ARCH
    current = read_own(arch.read_text(encoding="utf-8")) if arch.is_file() else None
    sch_text = (root / ROOT_SCH).read_text(encoding="utf-8")
    m = _BASIS.search(sch_text)
    basis = m.group(1) if m else None
    pdf = PDF if (root / PDF).is_file() else None
    sources = [ROOT_SCH, PARTS_CSV]

    def nat(r):
        return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", r)]

    out_pages = []
    for p in pages:
        refs = sorted(by_key.get(p["key"], []), key=nat) if p["key"] else []
        out_pages.append({"id": p["id"], "title": p["title"], "number": p["number"], "svg": None, "pdf": pdf,
                          "part_ids": [part_id(r) for r in refs],
                          "source": {"file": ROOT_SCH, "line": p["line"]}})
    data = {"exporter": {"tool": "kicad-cli", "version": None}, "pages": out_pages}

    def status(st, message):
        return {"status": st, "source": sources, "basis_version": basis, "current_version": current,
                "message": message}

    tool = _tool()
    if tool is None:
        return data, status("missing", "kicad-cli was not found (set KICAD_CLI or install KiCad); each page keeps "
                                       f"its link to {PDF}")
    data["exporter"]["version"] = _tool_version(tool)
    with tempfile.TemporaryDirectory(prefix="ring-svg-") as tmp:
        try:
            r = _export(tool, root / ROOT_SCH, tmp)
        except (OSError, subprocess.TimeoutExpired) as e:
            return data, status("unparsed", f"kicad-cli could not run: {type(e).__name__}: {e}")
        if r.returncode != 0:
            tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"]
            return data, status("unparsed", f"kicad-cli sch export svg exited {r.returncode}: {tail[0]}")
        stem = Path(ROOT_SCH).stem
        missing = []
        for p, op in zip(pages, out_pages):
            src = Path(tmp) / (f"{stem}.svg" if p["key"] is None else f"{stem}-{p['title']}.svg")
            if not src.is_file():
                missing.append(p["title"])
                continue
            text = src.read_text(encoding="utf-8")
            if invariants.check_no_absolute({"svg": text}):
                return data, status("unparsed", f"the SVG of page {p['number']} holds an absolute path")
            dest = ctx.out_path(f"schematic/{p['id']}.svg")
            dest.write_text(text, encoding="utf-8")
            op["svg"] = f"schematic/{p['id']}.svg"
    if missing:
        return data, status("unparsed", f"kicad-cli wrote no SVG for page(s): {', '.join(missing)}")
    return data, status("ok", None)
