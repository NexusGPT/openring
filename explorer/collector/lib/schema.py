"""A small JSON Schema (draft 2020-12 subset) validator, standard library only.

The design venv has no jsonschema package, so the subset the contract uses is implemented here:
$ref (relative file + #/ pointer), type (name or list), enum, const, required, properties,
additionalProperties, propertyNames, items, minItems, maxItems, uniqueItems, minLength, pattern,
minimum, anyOf, and format date-time. An unknown keyword that changes validity is refused, never
ignored: validate() raises SchemaError for it.
"""
import json
import re
from datetime import datetime
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "contract" / "schema"

_ANNOTATION = {"$schema", "$id", "$defs", "title", "description", "format", "default", "examples"}
_KNOWN = {"type", "enum", "const", "required", "properties", "additionalProperties", "propertyNames",
          "items", "minItems", "maxItems", "uniqueItems", "minLength", "pattern", "minimum", "anyOf", "$ref"}


class SchemaError(Exception):
    """The schema itself uses something this validator does not implement."""


def load(name, schema_dir=SCHEMA_DIR):
    """Load contract/schema/<name>.schema.json."""
    return json.loads((Path(schema_dir) / f"{name}.schema.json").read_text(encoding="utf-8"))


def _type_ok(v, t):
    if t == "null":
        return v is None
    if t == "boolean":
        return isinstance(v, bool)
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "string":
        return isinstance(v, str)
    if t == "array":
        return isinstance(v, list)
    if t == "object":
        return isinstance(v, dict)
    raise SchemaError(f"unknown type {t!r}")


def _resolve(ref, base_dir, root):
    file_part, _, frag = ref.partition("#")
    if file_part:
        target_dir = (Path(base_dir) / file_part).resolve()
        doc = json.loads(target_dir.read_text(encoding="utf-8"))
        base = target_dir.parent
    else:
        doc, base = root, Path(base_dir)
    node = doc
    for part in [p for p in frag.split("/") if p]:
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node, base, doc


def _walk(v, s, path, base_dir, root, errs):
    for k in s:
        if k not in _KNOWN and k not in _ANNOTATION:
            raise SchemaError(f"unsupported keyword {k!r} at {path or '$'}")
    if "$ref" in s:
        node, base, doc = _resolve(s["$ref"], base_dir, root)
        _walk(v, node, path, base, doc, errs)
        return
    if "anyOf" in s:
        for alt in s["anyOf"]:
            sub = []
            _walk(v, alt, path, base_dir, root, sub)
            if not sub:
                break
        else:
            errs.append(f"{path or '$'}: matches none of the allowed shapes")
            return
    if "type" in s:
        types = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not any(_type_ok(v, t) for t in types):
            errs.append(f"{path or '$'}: expected {'|'.join(types)}, got {type(v).__name__}")
            return
    if "enum" in s and v not in s["enum"]:
        errs.append(f"{path or '$'}: {v!r} is not one of {s['enum']}")
    if "const" in s and v != s["const"]:
        errs.append(f"{path or '$'}: expected {s['const']!r}")
    if isinstance(v, str):
        if "minLength" in s and len(v) < s["minLength"]:
            errs.append(f"{path or '$'}: shorter than {s['minLength']}")
        if "pattern" in s and not re.search(s["pattern"], v):
            errs.append(f"{path or '$'}: {v!r} does not match {s['pattern']}")
        if s.get("format") == "date-time":
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                errs.append(f"{path or '$'}: {v!r} is not a date-time")
    if isinstance(v, (int, float)) and not isinstance(v, bool) and "minimum" in s and v < s["minimum"]:
        errs.append(f"{path or '$'}: {v} is below {s['minimum']}")
    if isinstance(v, list):
        if "minItems" in s and len(v) < s["minItems"]:
            errs.append(f"{path or '$'}: fewer than {s['minItems']} items")
        if "maxItems" in s and len(v) > s["maxItems"]:
            errs.append(f"{path or '$'}: more than {s['maxItems']} items")
        if s.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in v}) != len(v):
            errs.append(f"{path or '$'}: items are not unique")
        if "items" in s:
            for i, item in enumerate(v):
                _walk(item, s["items"], f"{path}[{i}]", base_dir, root, errs)
    if isinstance(v, dict):
        props = s.get("properties", {})
        for r in s.get("required", []):
            if r not in v:
                errs.append(f"{path or '$'}: missing required '{r}'")
        for k, val in v.items():
            kp = f"{path}.{k}" if path else k
            if "propertyNames" in s:
                sub = []
                _walk(k, s["propertyNames"], kp, base_dir, root, sub)
                errs.extend(sub)
            if k in props:
                _walk(val, props[k], kp, base_dir, root, errs)
            else:
                ap = s.get("additionalProperties", True)
                if ap is False:
                    errs.append(f"{path or '$'}: unexpected property '{k}'")
                elif isinstance(ap, dict):
                    _walk(val, ap, kp, base_dir, root, errs)


def validate(value, name, schema_dir=SCHEMA_DIR):
    """Errors (list of readable strings, empty when valid) of `value` against schema `name`
    ('parts', 'manifest', 'content/part-notes')."""
    path = (Path(schema_dir) / f"{name}.schema.json").resolve()
    root = json.loads(path.read_text(encoding="utf-8"))
    errs = []
    _walk(value, root, "", path.parent, root, errs)
    return errs
