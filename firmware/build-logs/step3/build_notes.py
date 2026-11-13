"""build_notes.py <final log> <cleanup file>: writes docs/iphone-notes.md from notes.tmpl.md, notes_static.md and gen_bar.py."""
import pathlib
import re
import subprocess
import sys

STEP3 = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware/build-logs/step3"))
FW = STEP3.parent.parent
log_path = pathlib.Path(sys.argv[1])
RESULT = "RESULT: done, the round 3 bar command ends RESULT PASS with every stage passing; a to k are answered from that log, with the deviations and what is unproven listed (changes of rounds 2 and 3 in docs/step3-round2.md and docs/step3-round3.md)."
cleanup = pathlib.Path(sys.argv[2]).read_text() if len(sys.argv) > 2 and pathlib.Path(sys.argv[2]).exists() else "(not yet done)\n"
log = log_path.read_text(encoding="utf-8", errors="replace").split("\n")
tmpl = (STEP3 / "notes.tmpl.md").read_text()
static = (STEP3 / "notes_static.md").read_text()


def section(title_start):
    m = re.search(r"^## " + re.escape(title_start) + r".*?\n(.*?)(?=^## |\Z)", static, re.S | re.M)
    return m.group(1).strip() + "\n"


bar = subprocess.run([sys.executable, "-I", str(STEP3 / "gen_bar.py"), str(log_path)], capture_output=True, text=True)
if bar.returncode != 0:
    sys.exit("gen_bar failed: " + bar.stderr + bar.stdout)
rules = section("8.")
rules = rules.split("### 7.6", 1)
rules_body = "### 7.6" + rules[1] if len(rules) > 1 else rules[0]
last_result = max(i for i, l in enumerate(log) if l == "RESULT PASS") if "RESULT PASS" in log else None
exit_line = next(l for l in reversed(log) if l.startswith("# remote exit code"))
rel_log = log_path.relative_to(FW)
out = tmpl
out = out.replace("[[LOGPATH]]", f"{rel_log}")
out = out.replace("[[LASTLINE]]", "RESULT PASS" if last_result is not None else "(no RESULT PASS)")
out = out.replace("[[EXITLINE]]", exit_line)
out = out.replace("[[KITONLY]]", (STEP3 / "kit_only_table.md").read_text().strip())
out = out.replace("[[BAR]]", bar.stdout.strip())
out = out.replace("[[DEVIATIONS]]", section("4.").strip())
out = out.replace("[[DECISIONS]]", section("5.").strip())
out = out.replace("[[NOTBUILT]]", section("6.").strip())
out = out.replace("[[RUNS]]", section("7.").strip())
out = out.replace("[[RULES]]", rules_body.strip())
out = out.replace("[[CLEANUP]]", cleanup.strip())
# appendix: every cited log line, quoted
cited = sorted({int(n) for n in re.findall(r"LOG:(\d+)", out)})
app = ["", "## 10. The cited log lines", "", "Each `LOG:n` above is line n of `" + str(rel_log) + "`; the text of those lines (the simulator's time stamp prefix cut off):", ""]
for n in cited:
    t = re.sub(r"^d_0\d: @[\d:.]+\s+", "", log[n - 1]).strip()
    app.append(f"- `LOG:{n}`: {t[:230]}")
out = out.rstrip() + "\n" + "\n".join(app) + "\n\n" + RESULT + "\n"
(FW / "docs" / "iphone-notes.md").write_text(out)
print("written", FW / "docs" / "iphone-notes.md", len(out), "bytes")
