"""j-audit.py: checks the claims of the final reply (j-final.md) and the notes against the saved evidence."""
import pathlib
import re

F = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/firmware"))
S = F / "build-logs/step6"
reply = (S / "j-work/j-final.md").read_text()
notes = (F / "docs/recorder-notes.md").read_text()
n_checked = 0
bad = 0


def check(desc, ok, where=""):
    global n_checked, bad
    n_checked += 1
    if not ok:
        bad += 1
    print("%s | %s | %s" % ("OK " if ok else "BAD", desc, where))


def line_of(path, needle):
    for i, ln in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if needle in ln:
            return i
    return 0


# 1. every log or file name in backticks that looks like a path or a j- log exists
for text, name in ((reply, "reply"), (notes, "notes")):
    for tok in sorted(set(re.findall(r"`([^`\s]+)`", text))):
        if re.match(r"^j-[\w.-]+\.(log|txt|out)$", tok):
            p = S / tok if (S / tok).exists() else S / "j-work" / tok
            check("%s names %s" % (name, tok), p.exists(), str(p))
        elif "/" in tok and re.search(r"\.(c|h|py|sh|md|log|txt|conf|overlay|yaml)$", tok):
            if "*" in tok or "{" in tok:
                print("SKIP | %s names a pattern %s (not a file)" % (name, tok))
                continue
            cands = [F / tok, F.parent / tok, S / tok, pathlib.Path(tok), F / "modules/ring_recorder" / tok,
                     F / "modules/ring_glue" / tok]
            if tok.startswith("firmware/"):
                cands.append(F.parent / tok)
            check("%s names %s" % (name, tok), any(c.exists() for c in cands), "")
# 2. quoted result lines are on lines of the cited logs
u = S / "j-unit1.log"
check("UNIT PASS tests/recorder in j-unit1.log", line_of(u, "UNIT PASS tests/recorder") > 0, "l.%d" % line_of(u, "UNIT PASS tests/recorder"))
check("RESULT PASS in j-unit1.log", line_of(u, "RESULT PASS") > 0, "l.%d" % line_of(u, "RESULT PASS"))
check("remote exit 0 in j-unit1.log", line_of(u, "# remote exit code: 0") > 0, "")
last = u.read_text().splitlines()[-1]
check("last line of j-unit1.log quoted in reply", last in reply, last)
ul = u.read_text().splitlines()
check("43 of 43 at l.22", "43 of 43 executed test cases passed" in ul[21], ul[21][:80])
check("43 of 43 at l.44", "43 of 43 executed test cases passed" in ul[43], ul[43][:80])
check("12 copies named case failed on both boards", sum(1 for x in ul if "the named case failed, as required" in x) == 24,
      str(sum(1 for x in ul if "the named case failed, as required" in x)))
cases = (S / "j-cases1.log").read_text().splitlines()
check("86 passed case lines", sum(1 for x in cases if x.endswith(" passed")) == 86, "")
check("no non-passed case lines", not any(re.search(r" (failed|error|blocked|skipped)$", x) for x in cases), "")
for f, needle in (("j-stages1.log", "STAGES PASS"), ("j-stages1.log", "ring-os recorder: boot done, state STANDBY"),
                  ("j-stages1.log", "=== stage dk end"), ("j-stages1.log", "=== stage stack-report end"),
                  ("j-power2.log", "UNIT PASS tests/power"), ("j-work/j-compare-screens.txt", "RESULT EQUAL"),
                  ("j-bsim1.log", "BSIM screens exit 0"), ("j-bsim1.log", "BSIM control exit 0"),
                  ("j-bsim1.log", "BSIM iphone exit 0"), ("j-bsim1.log", "BSIM relay exit 0"),
                  ("j-work/j-unit1.console", "free on the server's /: 27 GB"),
                  ("j-work/j-editcheck1.log", "sd_on_in_standby"), ("j-power2.log", "and only it, as required")):
    p = S / f
    check("%s holds %s" % (f, needle), p.exists() and line_of(p, needle) > 0, "l.%d" % (line_of(p, needle) if p.exists() else 0))
st = (S / "j-stages1.log").read_text()
check("dk stage exit 0", re.search(r"=== stage dk end \S+ exit 0", st) is not None, "")
check("stack-report exit 0", re.search(r"=== stage stack-report end \S+ exit 0", st) is not None, "")
for s in ("recorder-one-mic-path", "recorder-no-start-path", "recorder-no-raw-pins", "recorder-product-drivers"):
    check("stage %s exit 0" % s, re.search(r"=== stage %s end \S+ exit 0" % s, st) is not None, "")
    check("stage %s self test ok" % s, ("%s: self test ok" % s) in st, "")
# 3. other copies failing named in the reply match the log
for copy, other in (("sd_off_before_mic_off", "test_ship_closes_everything_first"),
                    ("usb_long_press", "test_factory_gestures_reach_the_jig"),
                    ("sd_on_in_standby", "test_sd_rail_per_state")):
    check("%s also fails %s" % (copy, other), any(copy in x and "cases that failed" in x and other in x for x in ul), "")
others = [x for x in ul if "cases that failed (distinct)" in x and "(lines with FAIL: 1)" not in x]
check("exactly 3 copies with more than one failing case (x2 boards)", len(others) == 6, str(len(others)))
# 4. the notes end with the RESULT line; questions present
check("notes last line RESULT", notes.strip().splitlines()[-1].startswith("RESULT: done"), "")
check("notes have questions_for_owner", "## questions_for_owner" in notes, "")
# 5. no server address, no /dev/null, no secret path in my files
mine = [l.strip() for l in (S / "j-work/j-owned.log").read_text().splitlines()]
mine = [m for m in mine if m.startswith(("app/", "modules/ring_recorder", "modules/ring_glue", "modules/ring_power", "tests/recorder",
                                         "tests/power", "tools/", "README", "docs/recorder-notes"))]
addr = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
for m in mine:
    t = (F / m).read_text(errors="replace")
    check("%s: no IP address, /dev/null or secret path" % m,
          not addr.search(t) and "/dev/null" not in t and "<platform>-secrets" not in t, "")
for m in (reply, notes):
    check("text has no IP address", not addr.search(m), "")
# 6. owned files only (the factory builder's and the lead's files listed apart)
others_files = [l.strip() for l in (S / "j-work/j-owned.log").read_text().splitlines() if l.strip() and l.strip() not in mine]
print("changed files not mine (factory builder, lead):", others_files)
check("every changed file outside my list belongs to factory/lead", all(o.startswith(("modules/ring_factory", "tests/factory", "tests/bsim/factory", "docs/factory-notes", "docs/lane-dag")) for o in others_files), "")
print("claims checked: %d; bad: %d" % (n_checked, bad))
