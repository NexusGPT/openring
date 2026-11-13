"""Source pointers: {file, line}, file relative to the repository root with forward slashes."""
import re
from pathlib import Path


def rel(path, root):
    """Repo-root-relative posix path of `path` (absolute or relative to root)."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(root) / p
    return p.resolve().relative_to(Path(root).resolve()).as_posix()


def pointer(file, line=None):
    """A source pointer. `file` must already be relative; `line` is 1-based or None."""
    if file.startswith("/") or ".." in Path(file).parts:
        raise ValueError(f"source file must be relative to the repo root, got {file!r}")
    if line is not None and line < 1:
        raise ValueError("source line is 1-based")
    return {"file": file, "line": line}


def find_line(text, needle, start=1):
    """1-based line number of the first line at or after `start` containing `needle`, else None."""
    for i, ln in enumerate(text.splitlines(), 1):
        if i >= start and needle in ln:
            return i
    return None


def find_line_re(text, pattern, start=1):
    rx = re.compile(pattern)
    for i, ln in enumerate(text.splitlines(), 1):
        if i >= start and rx.search(ln):
            return i
    return None


def relativize(text, source_root):
    """Replace every absolute path under `source_root` in free text with its repo-relative form, so
    '/abs/repo/design/parts/mcu.md section 1a' becomes 'design/parts/mcu.md section 1a'."""
    root = str(Path(source_root).resolve()).rstrip("/")
    return text.replace(root + "/", "")
