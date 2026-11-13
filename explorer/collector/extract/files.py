"""files (files.json + bundle.zip): every project file a person may open or download, and the partner bundle.

Source: the project folder, `design/` plus requirements.md, feasibility.md and partners.md. With git the list is
`git ls-files --cached --others --exclude-standard` (so a `.venv` kept out of git stays out); without git (a
`git archive` copy) the folder is walked. Either way the same share filter applies, because the owner puts the app
online: nothing under `.venv`, `node_modules`, `__pycache__` or `.git`, no log, no secret file, and nothing of an
exterior the owner rejected (`design/status.json` look.rejected). A file over 20 MB stays listed with its size but is
not copied into the bundle. `tracked` is the git state; a copy with no git holds only tracked files, so it reads true.

A shared copy (the public site) is built from a folder that leaves some files out on purpose. That build names a
JSON file in EXPLORER_LEFT_OUT: a list of {what, count, why}. The record then carries it as `left_out`, and the
Files screen says what is missing. Without the variable the record has no `left_out`.
"""
import csv
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

RECORD = "files"

ROOT_DOCS = ("requirements.md", "feasibility.md", "partners.md")
BUNDLE_NAME = "bundle.zip"
DATASHEET_DIR = "design/datasheets/"
DATASHEET_LIST = "datasheets-list.txt"
# CONSTRAINTS rule 6: "no file over 20 MB" (constants.json has no name for it; the contract lane owns that file)
OVERSIZE_BYTES = 20 * 1024 * 1024
SKIP_DIRS = {"node_modules", "__pycache__", ".git", "logs"}
SKIP_NAMES = {".DS_Store"}
SKIP_SUFFIXES = (".log", ".err", ".key", ".pem", ".pyc")

# longest prefix first; see docs/SOURCE-CONTRACT.md "Folder-to-area rule"
AREA_RULES = [
    ("design/look/", "look"),
    ("design/mech/", "inside"),
    ("design/mfg/", "inside"),
    ("design/ecad/", "electronics"),
    ("design/bom.csv", "parts"),
    ("design/bom-notes.md", "parts"),
    ("design/parts/", "parts"),
    ("design/datasheets/", "parts"),
    ("design/firmware", "behaviour"),
    ("design/case/", "case"),
    ("design/architecture.md", "open"),
    ("design/status.json", "open"),
    ("requirements.md", "open"),
    ("feasibility.md", "open"),
    ("partners.md", "open"),
]


def area_of(path):
    for prefix, area in AREA_RULES:
        if path.startswith(prefix):
            return area
    return "other"


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def _is_own_repo(root):
    top = _git(root, "rev-parse", "--show-toplevel")
    return bool(top) and Path(top.decode().strip()).resolve() == Path(root).resolve()


def rejected_looks(root):
    """Look ids the owner rejected, from design/status.json; their folders stay out of the share."""
    try:
        d = json.loads((Path(root) / "design" / "status.json").read_text(encoding="utf-8"))
        return [str(x) for x in d["look"]["rejected"]]
    except (OSError, ValueError, KeyError, TypeError):
        return []


MFG = "design/mfg/"
MFG_HELPER_SUFFIXES = (".py", ".pyc", ".sh", ".orig", ".broken")


def mfg_helper(rel):
    """A helper script or leftover under design/mfg/tools or design/mfg/parts: kept out of the share."""
    if not rel.startswith(MFG):
        return False
    name = rel.rsplit("/", 1)[-1]
    if rel.startswith(MFG + "tools/"):
        return True
    return rel.startswith(MFG + "parts/") and (name.endswith(MFG_HELPER_SUFFIXES) or ".csv." in name)


_US = re.compile(r"-us(\d+)$")


def mfg_kind(rel):
    """drawing | specification | step | stl | view for a maker file by folder and extension, else None."""
    ext = rel.rsplit(".", 1)[-1].lower() if "." in rel.rsplit("/", 1)[-1] else ""
    if rel.startswith(MFG + "drawings/"):
        return {"pdf": "drawing", "svg": "view"}.get(ext)
    if rel.startswith(MFG + "specs/"):
        return "specification" if ext == "md" else None
    if rel.startswith(MFG + "parts/"):
        return {"step": "step", "stp": "step", "stl": "stl"}.get(ext)
    return None


def mfg_name_and_size(rel):
    """(maker part name with any -us<size> removed, ring size or None) from a file's base name."""
    stem = rel.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    m = _US.search(stem)
    return (stem[: m.start()], int(m.group(1))) if m else (stem, None)


def mfg_map(root):
    """{maker part name: [ring part ids]} from design/mfg/part-map.csv ({} when absent)."""
    out = {}
    try:
        with (Path(root) / MFG / "part-map.csv").open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                for ref in re.split(r"[,;]", r.get("reference") or ""):
                    ref = ref.strip()
                    pid = f"ring:{ref}"
                    if ref and pid not in out.setdefault((r.get("mfg_part") or "").strip(), []):
                        out[(r.get("mfg_part") or "").strip()].append(pid)
    except OSError:
        pass
    return out


def shareable(rel, rejected):
    """True when a person may open or download `rel` (a repo-relative posix path)."""
    if mfg_helper(rel):
        return False
    parts = rel.split("/")
    if any(p in SKIP_DIRS or p.startswith(".venv") for p in parts[:-1]):
        return False
    name = parts[-1]
    if name in SKIP_NAMES or name.startswith(".env") or name.endswith(SKIP_SUFFIXES):
        return False
    if any(rel.startswith(f"design/look/{r}/") for r in rejected):
        return False
    return True


def _candidates(root, git_ok):
    """Repo-relative posix paths of every project file under the scope, before the share filter."""
    root = Path(root)
    scope = ["design", *ROOT_DOCS]
    if git_ok:
        out = _git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", *scope)
        if out is not None:
            return sorted({p for p in out.decode("utf-8").split("\0") if p})
    found = []
    for top in scope:
        p = root / top
        if p.is_file():
            found.append(top)
        elif p.is_dir():
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".venv")]
                for f in filenames:
                    found.append((Path(dirpath) / f).relative_to(root).as_posix())
    return sorted(set(found))


def index(root):
    """(entries, left_out) for the project at `root`. entries: files.json `files` items sorted by path;
    left_out: {'rejected_look': n} files kept out of the share."""
    root = Path(root)
    git_ok = _is_own_repo(root)
    tracked = None
    if git_ok:
        out = _git(root, "ls-files", "-z")
        tracked = set(out.decode("utf-8").split("\0")) if out is not None else None
    rejected = rejected_looks(root)
    entries, left_out = [], {"rejected_look": 0}
    for rel in _candidates(root, git_ok):
        full = root / rel
        if full.is_symlink() or not full.is_file():
            continue
        if not shareable(rel, rejected):
            if any(rel.startswith(f"design/look/{r}/") for r in rejected):
                left_out["rejected_look"] += 1
            continue
        st = full.stat()
        entries.append({
            "path": rel,
            "size_bytes": st.st_size,
            "modified": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "area": area_of(rel),
            "tracked": True if tracked is None else rel in tracked,
        })
    mapping = mfg_map(root)
    unmapped = []
    for e in entries:
        if not e["path"].startswith(MFG):
            continue
        name, size = mfg_name_and_size(e["path"])
        kind = mfg_kind(e["path"])
        e["part_ids"] = list(mapping.get(name, [])) if kind else []
        e["ring_size"] = size
        if kind:
            e["kind"] = kind
            if not e["part_ids"] and name not in unmapped:
                unmapped.append(name)
    left_out["unmapped_maker"] = unmapped
    return entries, left_out


def datasheet_urls(root):
    """{datasheet path: source URL} where a parts-list row names both a datasheet file and a web address."""
    out = {}
    for rel in ("design/bom.csv", "design/case/case-bom.csv"):
        try:
            with (Path(root) / rel).open(newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
        except OSError:
            continue
        for r in rows:
            cell = r.get("source_file_or_url") or ""
            urls = re.findall(r"https?://[^\s;]+", cell)
            for m in re.finditer(r"(?:/|\b)(design/datasheets/[^\s;]+?\.[A-Za-z0-9]+)(?![\w])", cell):
                if urls:
                    out.setdefault(m.group(1), urls[0])
    return out


def datasheet_list_text(root, entries):
    urls = datasheet_urls(root)
    lines = ["The maker datasheets are in the project folder. Open them one by one from the Files screen of the app."]
    for e in entries:
        if e["path"].startswith(DATASHEET_DIR):
            lines.append(f"{e['path']}\t{e['size_bytes']} bytes" + (f"\t{urls[e['path']]}" if e["path"] in urls else ""))
    return "\n".join(lines) + "\n"


def bundle_contents(entries):
    """Paths copied into the zip: not oversize, not a datasheet (those are listed in datasheets-list.txt instead)."""
    return [e["path"] for e in entries if e["size_bytes"] <= OVERSIZE_BYTES and not e["path"].startswith(DATASHEET_DIR)]


def write_bundle(zip_path, root, entries):
    """Write the partner zip of exactly bundle_contents(entries), so the zip and files.json come from one list.
    The datasheet list is the zip's comment (a zip entry that is not a project file would break the rule that the
    entry list equals files.json `bundle.contents`). Returns the contents list."""
    root = Path(root)
    contents = bundle_contents(entries)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in contents:
            z.write(root / name, arcname=name)
        z.comment = datasheet_list_text(root, entries).encode("utf-8")[:65535]
    return contents


LEFT_OUT_ENV = "EXPLORER_LEFT_OUT"


def left_out_list(path):
    """Rows {what, count, why} from the JSON file at `path`; [] when no file is named. A file that is named but
    unreadable or badly shaped raises ValueError: a shared copy must never hide what it leaves out."""
    if not path:
        return []
    try:
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"{LEFT_OUT_ENV}={path}: {e}") from e
    if not isinstance(rows, list):
        raise ValueError(f"{LEFT_OUT_ENV}={path}: not a list")
    out = []
    for r in rows:
        ok = isinstance(r, dict) and isinstance(r.get("what"), str) and r["what"].strip() and isinstance(r.get("why"), str) and r["why"].strip() \
            and isinstance(r.get("count"), int) and not isinstance(r.get("count"), bool) and r["count"] >= 0
        if not ok:
            raise ValueError(f"{LEFT_OUT_ENV}={path}: a row needs what (text), count (whole number) and why (text): {r!r}")
        if r["count"]:
            out.append({"what": r["what"].strip(), "count": r["count"], "why": r["why"].strip()})
    return out


def extract(ctx):
    root = ctx.source_root
    if not ctx.design_dir.is_dir():
        return None, "missing"
    entries, left_out = index(root)
    oversize = [e["path"] for e in entries if e["size_bytes"] > OVERSIZE_BYTES]
    zip_path = ctx.out_path(BUNDLE_NAME)
    contents = write_bundle(zip_path, root, entries)
    data = {
        "files": entries,
        "bundle": {"file": BUNDLE_NAME, "size_bytes": zip_path.stat().st_size, "contents": contents},
    }
    notes = []
    left = left_out_list(os.environ.get(LEFT_OUT_ENV))
    if left:
        data["left_out"] = left
        notes.append("This copy leaves out " + ", ".join(f"{r['count']} file(s) of {r['what']}" for r in left))
    if oversize:
        notes.append(f"{len(oversize)} file(s) over 20 MB are listed but not copied into {BUNDLE_NAME}: " + ", ".join(oversize))
    if left_out["rejected_look"]:
        notes.append(f"{left_out['rejected_look']} file(s) of the rejected exteriors are left out")
    un = left_out["unmapped_maker"]
    if un:
        notes.append(f"{len(un)} maker part name(s) not in design/mfg/part-map.csv, so no part: " + ", ".join(un[:8]) + (" ..." if len(un) > 8 else ""))
    return data, {"status": "ok", "source": ["design"], "message": "; ".join(notes) or None}
