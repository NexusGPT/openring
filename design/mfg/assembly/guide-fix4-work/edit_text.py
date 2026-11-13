#!/usr/bin/env python3
"""Apply one batch of exact text replacements to one file; each old text must occur exactly
once (on the line given) and the line count must not change.

Usage: edit_text.py <batch.json>
batch.json: {"file": "<absolute path>", "edits": [{"line": N, "old": "...", "new": "..."}, ...]}
Prints one line per edit and a RESULT line; exits 1 (writing nothing) on any mismatch.
"""
import json, sys

b = json.load(open(sys.argv[1], encoding='utf-8'))
path = b['file']
text = open(path, encoding='utf-8').read()
lines = text.split('\n')
n0 = len(lines)
bad = 0
for e in b['edits']:
    i = e['line'] - 1
    c_line = lines[i].count(e['old'])
    c_file = text.count(e['old'])
    if c_line != 1 or c_file != 1:
        print(f"FAIL line {e['line']}: old text found {c_line} times on the line, {c_file} in the file: {e['old'][:80]!r}")
        bad += 1
        continue
    if '\n' in e['new']:
        print(f"FAIL line {e['line']}: new text holds a line break")
        bad += 1
        continue
    lines[i] = lines[i].replace(e['old'], e['new'])
    print(f"EDIT {path.split('/')[-1]}:{e['line']} {e['old'][:70]!r} -> {e['new'][:70]!r}")
if bad:
    print(f'RESULT FAIL {bad} edits; nothing written')
    sys.exit(1)
assert len(lines) == n0
open(path, 'w', encoding='utf-8').write('\n'.join(lines))
print(f"RESULT applied {len(b['edits'])} edits to {path}; lines {n0} before and after")
