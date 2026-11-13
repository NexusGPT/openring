#!/usr/bin/env python3
"""Collector runner: design files -> explorer/public/data/<record> + manifest.json.

  python collector/run.py                         build every record from the repo this folder sits in
  python collector/run.py --source <dir>          read the design from <dir> instead (a copy for tests)
  python collector/run.py --out <dir>             write the bundle to <dir> (default public/data)
  python collector/run.py --extractors <dir>      load extractors from <dir> (default collector/extract)
  python collector/run.py --content <dir>         read content/part-notes.json from <dir> (default explorer/content)
  python collector/run.py --commit <sha>          git commit to record when <source> is not a git repo
  python collector/run.py --check-schemas         load every schema, print its name, exit 0
  python collector/run.py --validate <record> <file.json>   exit 1 when the file breaks the record's schema

An extractor is a module in the extractors folder exposing RECORD (one of the 13 record ids) and
extract(ctx) -> (data, status). data is the record's JSON (or None); status is 'ok' | 'missing' |
'unparsed' | 'stale' or a dict {status, source, basis_version, current_version, message}. Each
extractor runs alone: an exception makes only its record 'unparsed'. A module without extract() is a
helper and is skipped. The run exits 0 whatever the sources hold; a bug in an extractor's contract
(unknown or repeated RECORD) exits 1.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lib import invariants, records, schema  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.version import is_stale  # noqa: E402

EXPLORER = HERE.parent
STATUSES = ("ok", "missing", "unparsed", "stale")


class Ctx:
    """What an extractor receives."""

    def __init__(self, record, source_root, out_dir, commit):
        self.record = record
        self.source_root = Path(source_root)
        self.design_dir = self.source_root / "design"
        self.out_dir = Path(out_dir)
        self.explorer_dir = EXPLORER
        self.commit = commit

    def rel(self, path):
        from lib.source import rel

        return rel(path, self.source_root)

    def source_path(self, rel_path):
        """Absolute path of a repo-relative file in the source tree."""
        return self.source_root / rel_path

    def out_path(self, rel_path):
        """Absolute path inside the bundle for an extra file (GLB, SVG, zip). Parent folders are made.
        Refuses a path that leaves the bundle."""
        p = (self.out_dir / rel_path).resolve()
        if self.out_dir.resolve() not in p.parents:
            raise ValueError(f"{rel_path!r} leaves the bundle folder")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def find_commit(source_root, override):
    if override:
        return override
    sha = git(source_root, "rev-parse", "HEAD")
    return sha


def is_dirty(source_root):
    out = git(source_root, "status", "--porcelain", "--", "design", "requirements.md", "feasibility.md", "partners.md")
    return bool(out)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def clear_record(out_dir, rec):
    for rel in [rec["file"], *rec["extra"]]:
        p = out_dir / rel
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    # the record's own folder, when the primary file lives in one
    parent = (out_dir / rec["file"]).parent
    if parent != out_dir and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()


def load_extractors(folder):
    """[(module_name, module)] for every extractor module; a module with no extract() is a helper."""
    folder = Path(folder)
    mods = []
    if not folder.is_dir():
        return mods
    parent = str(folder.parent)
    for f in sorted(folder.glob("*.py")):
        if f.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"extract_{f.stem}", f)
        mod = importlib.util.module_from_spec(spec)
        try:
            sys.path.insert(0, parent)
            spec.loader.exec_module(mod)
        except Exception as e:  # an import failure belongs to that module's record, found below
            mod = type("Broken", (), {"RECORD": getattr(mod, "RECORD", None), "_import_error": e})
        finally:
            if parent in sys.path:
                sys.path.remove(parent)
        mods.append((f.stem, mod))
    return mods


def normalise_status(status):
    if isinstance(status, str):
        status = {"status": status}
    s = {"status": status.get("status", "ok"), "source": list(status.get("source", [])),
         "basis_version": status.get("basis_version"), "current_version": status.get("current_version"),
         "message": status.get("message")}
    if s["status"] not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}, got {s['status']!r}")
    return s


def entry(status, source=(), basis=None, current=None, message=None):
    return {"status": status, "source": list(source), "basis_version": basis, "current_version": current,
            "message": message}


def run(args):
    source_root = Path(args.source).resolve()
    out_dir = Path(args.out).resolve()
    reg = records.by_id()
    commit = find_commit(source_root, args.commit)
    if not commit:
        print(f"collector: {source_root} is not a git repository and no --commit was given", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_records = {rid: entry("missing", message="No extractor for this record yet.") for rid in reg}
    claimed = {}
    contract_errors = []
    jobs = []
    for name, mod in load_extractors(args.extractors):
        rid = getattr(mod, "RECORD", None)
        has_extract = callable(getattr(mod, "extract", None)) or hasattr(mod, "_import_error")
        if not has_extract:
            continue  # helper module
        if rid not in reg:
            contract_errors.append(f"{name}: RECORD {rid!r} is not one of {sorted(reg)}")
            continue
        if rid in claimed:
            contract_errors.append(f"{name}: RECORD {rid!r} is already claimed by {claimed[rid]}")
            continue
        claimed[rid] = name
        jobs.append((rid, name, mod))
    if contract_errors:
        for e in contract_errors:
            print(f"collector: {e}", file=sys.stderr)
        return 1

    built = {}
    for rid, name, mod in sorted(jobs, key=lambda j: list(reg).index(j[0])):
        rec = reg[rid]
        clear_record(out_dir, rec)
        ctx = Ctx(rid, source_root, out_dir, commit)
        try:
            if hasattr(mod, "_import_error"):
                raise mod._import_error
            data, status = mod.extract(ctx)
            st = normalise_status(status)
            if is_stale(st["basis_version"], st["current_version"]) and st["status"] == "ok":
                st["status"] = "stale"
            if data is None:
                if st["status"] in ("ok", "stale"):
                    raise ValueError("extractor returned no data with status " + st["status"])
                manifest_records[rid] = st
                continue
            errs = schema.validate(data, rec["schema"])
            if not errs:
                errs = invariants.check_no_absolute(data)
            if not errs and rid in invariants.SINGLE:
                errs = invariants.SINGLE[rid](data)
            if errs:
                shown = "; ".join(errs[:3]) + (f" (+{len(errs) - 3} more)" if len(errs) > 3 else "")
                manifest_records[rid] = entry("unparsed", st["source"], st["basis_version"], st["current_version"],
                                              f"Output of {name} breaks the {rec['schema']} schema: {shown}")
                clear_record(out_dir, rec)
                continue
            write_json(out_dir / rec["file"], data)
            built[rid] = data
            manifest_records[rid] = st
        except SourceError as e:
            clear_record(out_dir, rec)
            manifest_records[rid] = entry("unparsed", e.files, message=str(e))
        except Exception as e:  # isolation: one extractor never stops the run
            clear_record(out_dir, rec)
            tail = traceback.format_exc().strip().splitlines()[-1]
            manifest_records[rid] = entry("unparsed", message=f"{type(e).__name__}: {e}" if str(e) else tail)

    for rid, problems in invariants.check_cross(built).items():
        clear_record(out_dir, reg[rid])
        manifest_records[rid] = entry("unparsed", manifest_records[rid]["source"],
                                      message="; ".join(problems))

    content_entry = copy_part_notes(args.content, out_dir)

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    built_at = (datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc))
    manifest = {
        "built_at": built_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": commit,
        "git_dirty": is_dirty(source_root),
        "source_root": source_root.name,
        "records": {rid: manifest_records[rid] for rid in reg},
        "content": {"part-notes": content_entry},
    }
    errs = schema.validate(manifest, "manifest")
    if errs:
        print("collector: manifest breaks its own schema: " + "; ".join(errs[:3]), file=sys.stderr)
        return 1
    write_json(out_dir / "manifest.json", manifest)
    counts = {s: sum(1 for e in manifest["records"].values() if e["status"] == s) for s in STATUSES}
    print(f"collector: {commit[:7]} -> {out_dir}  " + "  ".join(f"{k} {v}" for k, v in counts.items() if v))
    return 0


def copy_part_notes(content_dir, out_dir):
    """content/part-notes.json is hand-written, not extracted. It travels with the bundle as
    <bundle>/content/part-notes.json so dataUrl('content/part-notes.json') works in dev, preview and
    the static build. Returns its manifest entry."""
    target = out_dir / "content" / "part-notes.json"
    if target.exists():
        target.unlink()
    src = Path(content_dir) / "part-notes.json"
    label = "content/part-notes.json"
    if not src.is_file():
        return entry("missing", message="No part notes file yet.")
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except ValueError as e:
        return entry("unparsed", [label], message=f"ValueError: {e}")
    errs = schema.validate(data, "content/part-notes") or invariants.check_no_absolute(data) or invariants.check_part_notes(data)
    if errs:
        return entry("unparsed", [label], message="Part notes break the contract: " + "; ".join(errs[:3]))
    write_json(target, data)
    return entry("ok", [label])


def check_schemas():
    reg = records.registry()
    names = [r["schema"] for r in reg["records"]] + [reg["manifest"]["schema"]]
    schema.load("common")
    for n in names:
        schema.load(n)
        print(n)
    for c in reg["content"]:
        schema.load(c["schema"])
        print(f"content: {c['schema']}", file=sys.stderr)
    return 0


def validate_file(record, path):
    reg = records.registry()
    names = {r["id"]: r["schema"] for r in reg["records"]}
    names["manifest"] = reg["manifest"]["schema"]
    names.update({c["id"]: c["schema"] for c in reg["content"]})
    if record not in names:
        print(f"collector: unknown record {record!r}; known: {sorted(names)}", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"collector: cannot read {path}: {e}", file=sys.stderr)
        return 1
    errs = schema.validate(data, names[record])
    if not errs and record in invariants.SINGLE:
        errs = invariants.SINGLE[record](data)
    if record == "part-notes" and not errs:
        errs = invariants.check_part_notes(data)
    for e in errs:
        print(f"{record}: {e}", file=sys.stderr)
    if errs:
        return 1
    print(f"{record}: valid")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=str(EXPLORER.parent))
    ap.add_argument("--out", default=str(EXPLORER / "public" / "data"))
    ap.add_argument("--extractors", default=str(HERE / "extract"))
    ap.add_argument("--content", default=str(EXPLORER / "content"))
    ap.add_argument("--commit", default=None)
    ap.add_argument("--check-schemas", action="store_true")
    ap.add_argument("--validate", nargs=2, metavar=("RECORD", "FILE"))
    args = ap.parse_args(argv)
    if args.check_schemas:
        return check_schemas()
    if args.validate:
        return validate_file(*args.validate)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
