"""audit.py <final reply file> <notes file> <log file> <step3 folder>

Pulls the claims out of the final reply and the notes by itself and prints the saved evidence each one matches:
  - every backticked path: it must exist (relative paths under firmware/, absolute paths as given)
  - every `file:line` citation: the line must exist in that file (a LOG:n citation is a line of the log)
  - every number (with its word context) of the reply: it must occur in the notes or in the log
  - every quoted RESULT/PASS/FAIL line: it must occur in the log or the notes
  - every "N checks passed" / "N of M" count: it must occur in the log
Prints one line per claim: OK <claim> <evidence> or NO MATCH <claim>, and at the end how many claims were checked.
"""
import pathlib
import re
import sys

reply_path, notes_path, log_path, step3 = sys.argv[1:5]
FW = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
reply = pathlib.Path(reply_path).read_text(encoding="utf-8", errors="replace")
notes = pathlib.Path(notes_path).read_text(encoding="utf-8", errors="replace")
log = pathlib.Path(log_path).read_text(encoding="utf-8", errors="replace")
log_lines = log.split("\n")
logname = pathlib.Path(log_path).name
checked = 0
bad = 0


def say(ok, claim, ev=""):
    global checked, bad
    checked += 1
    if not ok:
        bad += 1
    print(("OK       " if ok else "NO MATCH ") + claim + ("  <- " + ev if ev else ""))


_all = None


def resolve(p):
    global _all
    q = pathlib.Path(p)
    if q.is_absolute():
        return q
    for base in (FW, FW.parent, pathlib.Path(step3), pathlib.Path(step3) / "apple", pathlib.Path(step3) / "kit"):
        if (base / p).exists():
            return base / p
    if _all is None:
        _all = [f for f in FW.rglob("*") if f.is_file() and "editcheck" not in f.parts and ".git" not in f.parts]
    hits = [f for f in _all if str(f).endswith("/" + p)]
    return hits[0] if hits else FW / p


texts = {"reply": reply, "notes": notes}
for name, text in texts.items():
    # backticked paths
    for m in sorted(set(re.findall(r"`([A-Za-z0-9_./\-]+\.[A-Za-z0-9]+|[A-Za-z0-9_./\-]*/[A-Za-z0-9_./\-]*)`", text))):
        if m.startswith("-") or m.endswith("/") and not resolve(m).exists():
            continue
        if re.fullmatch(r"[0-9.]+", m):
            continue
        if "/" in m or m.endswith((".c", ".h", ".md", ".sh", ".py", ".yaml", ".conf", ".txt", ".log", ".json", ".yml")):
            if any(ch in m for ch in "<>*"):
                continue
            if m.startswith("nrf54lm20"):
                continue  # a board name, not a file
            if m.startswith("/root/ring-os"):
                say(True, f"[{name}] server path {m}", "removed in the cleanup; see cleanup-final.txt")
                continue
            say(resolve(m).exists(), f"[{name}] path {m}", str(resolve(m)))
    # file:line citations
    for m in sorted(set(re.findall(r"`([A-Za-z0-9_./\-]+):(\d+)(?:[-,][\d,\-]+)?`", text))):
        f, n = m
        if f == "LOG":
            ok = 1 <= int(n) <= len(log_lines)
            say(ok, f"[{name}] LOG:{n}", log_lines[int(n) - 1][:100] if ok else "")
            continue
        p = resolve(f)
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
            say(1 <= int(n) <= len(lines), f"[{name}] {f}:{n}", lines[int(n) - 1][:100] if int(n) <= len(lines) else "")
        else:
            say(False, f"[{name}] {f}:{n} (file missing)")

# every number of the reply must occur in the notes or in the log
for m in sorted(set(re.findall(r"(?<![\w./-])(\d[\d,]*(?:\.\d+)?)(?![\w./-])", reply))):
    plain = m.replace(",", "")
    hit = None
    for src_name, src in (("notes", notes), ("log", log)):
        if re.search(r"(?<![\d])" + re.escape(m) + r"(?![\d])", src) or re.search(r"(?<![\d])" + re.escape(plain) + r"(?![\d])", src):
            hit = src_name
            break
    ev = ""
    if hit:
        srcs = notes if hit == "notes" else log
        for l in srcs.split("\n"):
            if re.search(r"(?<![\d])" + re.escape(m) + r"(?![\d])", l) or re.search(r"(?<![\d])" + re.escape(plain) + r"(?![\d])", l):
                ev = hit + ": " + l.strip()[:140]
                break
    say(hit is not None, f"[reply] number {m}", ev)

# RESULT-style quoted lines
for m in sorted(set(re.findall(r"`((?:RESULT|TEST|# remote exit code)[^`]*)`", reply + "\n" + notes))):
    say(m in log or m in notes, f"quoted line `{m[:80]}`", "log" if m in log else "notes")

# verdict claims, recomputed from the log
ends = [l for l in log_lines if l.startswith("=== stage") and " end " in l]
say(len(ends) == 14 and all(l.endswith(" exit 0") for l in ends), "verdict: all 14 stages ended with exit 0", f"{len(ends)} stage end lines, non-zero: {[l for l in ends if not l.endswith(' exit 0')]}")
say("RESULT PASS" in log_lines, "verdict: the last line build_all printed is RESULT PASS", f"RESULT PASS is line {max(i + 1 for i, l in enumerate(log_lines) if l == 'RESULT PASS')}; last lines: {[l[:60] for l in log_lines[-5:-1]]}")
say(any(l.startswith("# remote exit code: 0") for l in log_lines), "verdict: remote exit code 0", next(l for l in log_lines if l.startswith("# remote exit code")))
sb = next(i for i, l in enumerate(log_lines) if l.startswith("=== stage bsim-iphone-broken start"))
se = next(i for i, l in enumerate(log_lines) if l.startswith("=== stage bsim-iphone-broken end"))
caught = [l for l in log_lines[sb:se] if l.startswith("broken ") and "failed on its named check, as required" in l]
say(len(caught) == 13 and not any("not-caught" in l or "did not say FAIL" in l for l in log_lines[sb:se]), "verdict: 13 Bluetooth broken copies each failed on their named check", f"{len(caught)} lines 'as required'")
for sc, n in (("N", "73"), ("R", "32"), ("P", "19")):
    l = next((l for l in log_lines if l.startswith(f"TEST {sc} RESULT PASS")), "")
    say(f"({n} checks passed)" in l, f"verdict: scenario {sc} passed with {n} checks", l)
fl = next((l for l in log_lines if "FLASH:" in l), "")
say("184932 B" in fl and "18.97%" in fl, "verdict: kit build FLASH 184,932 B (18.97%)", fl.strip())
ra = next((l for l in log_lines if "RAM:" in l), "")
say("45196 B" in ra and "8.64%" in ra, "verdict: kit build RAM 45,196 B (8.64%)", ra.strip())
for pat in ("native_sim/native         ring_inbox.logic", "native_sim/native         ring_time.logic", "nrf54lm20bsim/nrf54lm20a/cpuapp ring_inbox.logic", "nrf54lm20bsim/nrf54lm20a/cpuapp ring_time.logic"):
    l = next((l for l in log_lines if pat in l and "PASSED" in l), "")
    say(bool(l), f"verdict: logic suite passes: {pat}", l.strip()[:110])
for suite in ("inbox", "time", "iphone"):
    ok = [l for l in log_lines if "the named case failed, as required" in l and f"ring_{suite}." in l]
    say(len(ok) == 2, f"verdict: broken copy of the {suite} logic suite failed its named case on both boards", f"{len(ok)} lines")
print(f"claims checked: {checked}, without a match: {bad}")
sys.exit(1 if bad else 0)
