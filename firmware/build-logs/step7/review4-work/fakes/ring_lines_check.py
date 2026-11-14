import re, sys
src = open(sys.argv[1]).read()
code = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
def body(name):
    m = re.search(r"static int " + name + r"\(void\)\s*\{(.*?)\n\}", code, flags=re.S)
    return " ".join(m.group(1).split()) if m else None
fail = []
def rule(name, ok, what):
    print("ring-lines-safe: %s %s: %s" % ("SAME" if ok else "DIFFERENT", name, what))
    if not ok and name not in fail:
        fail.append(name)
ls = body("lines_safe")
rule("lines_safe", ls is not None and "GPIO_DISCONNECTED" in ls and "pinctrl_apply_state(spi00_pins, PINCTRL_STATE_SLEEP)" in ls
     and not re.search(r"\b(if|bus_up|device_is_ready|pm_device_action_run|return 0)\b", ls),
     "no condition, no device state; SD_CS GPIO_DISCONNECTED and spi00's sleep pin state: %s" % ls)
bs = body("b_suspend")
rule("b_suspend", bs == "int r = suspend_inner(); int s = lines_safe(); return r != 0 ? r : s;",
     "one wrapper that always ends in lines_safe(): %s" % bs)
br = body("b_resume")
rule("b_resume", br == "int r = resume_inner(); if (r != 0) { (void)lines_safe(); } return r;",
     "lines_safe() on every failure: %s" % br)
for f, n in (("suspend_inner", 2), ("resume_inner", 2)):
    c = len(re.findall(r"\b" + f + r"\(", code))
    rule(f, c == n, "%d occurrences (its definition and the one call in its wrapper: %d wanted)" % (c, n))
ri = body("resume_inner") or ""
calls = len(re.findall(r"\bbus_first_init\(\)\s*;", code))
rule("bus_first_init", "return bus_first_init();" in ri and calls == 1,
     "called once, from resume_inner: %d call(s)" % calls)
rule("sdbus", ".suspend = b_suspend, .resume = b_resume" in code, "the sdbus table names the two wrappers")
if fail:
    print("ring-lines-safe: RESULT FAIL failing: " + " ".join(fail))
    sys.exit(1)
print("ring-lines-safe: RESULT PASS")
