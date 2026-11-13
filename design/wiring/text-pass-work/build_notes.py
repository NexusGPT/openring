"""Builds design/wiring/text-pass-notes.md from the saved logs (last lines read from the logs, never typed)."""
import re, subprocess
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
W = R + "design/wiring/text-pass-work/"
def last(path, n=2):
    ls = [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="replace") if l.strip()]
    return " / ".join(ls[-n:])
checks = [
 ("check_docs.py", "before_check_docs.log", "after_check_docs.log"),
 ("check_parts.py", "before_check_parts.log", "after_check_parts.log"),
 ("firmware-check.py", "before_firmware.log", "after_firmware.log"),
 ("check_assembly.py", "before_check_assembly.log", "after_check_assembly.log"),
 ("check_case_docs.py", "before_case.log", "after_case.log"),
 ("check_bom.py", "before_bom.log", "after_bom.log"),
]
o = []
o.append("# Text pass: design documents brought to the decisions and models of 2026-11-13 (notes, written while working)\n")
o.append("Brief: the lead's message of 2026-11-13 (change lists A, B, C; bar 1 to 4). No git was run. The work folder is `design/wiring/text-pass-work/` (edit scripts in `edits/`, the edit helper `ed.py`, every edit logged by it in `edits.log`, the table of all edits `edits_table.md`).\n")
o.append("## 1. Steps\n")
o.append(open(W + "steps.txt", encoding="utf-8").read())
o.append("\n## 2. The six checks, before the first edit and after the last one (last two lines of each saved log)\n")
o.append("| Check | Before (log) | After (log) |\n|---|---|---|")
for name, b, a in checks:
    o.append(f"| {name} | `{b}`: {last(W+b)} | `{a}`: {last(W+a)} |")
o.append("\ncheck_assembly.py before: `RESULT FAIL A2` because bom.csv holds LT1 and C89 (added at the antenna by the board plan) and no step named them: they are named in step 2 now (edit list, file assembly.md line 96). check_bom.py: the same one failure before and after (RC1, whose row the lead adds); no new failure.\n")
o.append("check_bom.py full output, before the first edit (`before_bom.log`) and after the last (`after_bom.log`; `bom_diff.log` is empty: the two are identical):\n\n```\n" + open(W+"after_bom.log").read().rstrip() + "\n```\n")
o.append("## 3. Redraw of the sheets (draw.py at `nice -n 19`, one run at a time)\n")
o.append(open(W + "redraw.txt", encoding="utf-8").read())
o.append("\n## 4. Search for the replaced values\n")
o.append(open(W + "search_summary.txt", encoding="utf-8").read())
o.append("\n## 5. Every edit (file, line found by its text, text before, text after, the decision or model it follows)\n")
o.append(open(W + "edits_table.md", encoding="utf-8").read())
o.append("\n## 6. Lines checked and left as they are, with the reason\n")
o.append(open(W + "left.txt", encoding="utf-8").read())
o.append("\n## rows missing in design/bom.csv\n")
o.append(open(W + "bom_rows.txt", encoding="utf-8").read())
o.append("\n## left for the owner's decision\n")
o.append(open(W + "owner_left.txt", encoding="utf-8").read())
o.append("\n## questions_for_owner\n\nnone\n")
o.append("\nRESULT: " + open(W + "result.txt", encoding="utf-8").read().strip() + "\n")
open(R + "design/wiring/text-pass-notes.md", "w", encoding="utf-8").write("\n".join(o))
print("written")
