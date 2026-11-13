"""CSV reader that keeps the 1-based source line of each row (a multi-line cell counts its lines)."""
import csv
from pathlib import Path

from .errors import SourceError


def read(path, required=()):
    """[{'line': first line of the row, 'cells': {column: text}}] for every non-empty row.
    Raises SourceError when the file lacks a `required` column."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            raise SourceError(f"{path.name} is empty", str(path))
        missing = [c for c in required if c not in header]
        if missing:
            raise SourceError(f"{path.name} lacks column(s): {', '.join(missing)}", str(path))
        out, prev = [], reader.line_num
        for row in reader:
            first = prev + 1
            prev = reader.line_num
            if not any(c.strip() for c in row):
                continue
            row = (row + [""] * len(header))[: len(header)]
            out.append({"line": first, "cells": dict(zip(header, row))})
    return out


def split_refs(cell):
    """Split a reference cell on comma or semicolon; each token is kept as written, empties dropped."""
    import re

    return [t.strip() for t in re.split(r"[,;]", cell) if t.strip()]
