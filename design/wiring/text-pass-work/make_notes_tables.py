"""Writes edits_table.md (every edit: file, line found, before, after, decision) from edits.log. Run: python3 -I make_notes_tables.py"""
import json
W = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/text-pass-work/")
rows = [json.loads(l) for l in open(W + "edits.log", encoding="utf-8")]
out = ["| # | File | Line | Text before | Text after | Follows |", "|---|---|---|---|---|---|"]
def c(s): return s.replace("|", "\\|").replace("\n", " / ")
for i, r in enumerate(rows, 1):
    out.append(f"| {i} | {r['file']} | {r['line']} | {c(r['before'])} | {c(r['after'])} | {c(r['follows'])} |")
open(W + "edits_table.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(rows), "edits")
