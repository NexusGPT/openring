"""The record registry (contract/schema/records.json) and the single constants file."""
import json
from pathlib import Path

from .schema import SCHEMA_DIR


def registry(schema_dir=SCHEMA_DIR):
    return json.loads((Path(schema_dir) / "records.json").read_text(encoding="utf-8"))


def record_ids(schema_dir=SCHEMA_DIR):
    return [r["id"] for r in registry(schema_dir)["records"]]


def by_id(schema_dir=SCHEMA_DIR):
    return {r["id"]: r for r in registry(schema_dir)["records"]}


def constants(schema_dir=SCHEMA_DIR):
    """contract/schema/constants.json, the one place a threshold, count or port is written."""
    return json.loads((Path(schema_dir) / "constants.json").read_text(encoding="utf-8"))
