import re, pathlib, subprocess
base = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/firmware"))
notes = (base/"docs/store-notes.md").read_text()
nl = notes.splitlines()
checked = 0; bad = []
def check(ok, what):
    global checked
    checked += 1
    print(("OK   " if ok else "FAIL ") + what)
    if not ok: bad.append(what)
cache = {}
def line(f, n):
    if f not in cache: cache[f] = (base/f).read_text().splitlines()
    return cache[f][n-1]
# 1 every "`case` (file l.N, l.M)" citation
for m in re.finditer(r"`(test_\w+)` \((build-logs/\S+) l\.(\d+), l\.(\d+)\)", notes):
    c, f, a, b = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    la, lb = line(f, a), line(f, b)
    check(f"PASS - {c} " in la and not la.startswith("d_00") and f"PASS - {c} " in lb and lb.startswith("d_00"), f"{c} l.{a}/l.{b}: {la.strip()[:60]} | {lb.strip()[22:70]}")
# 2 broken table
cons = (base/"build-logs/step6/u2-final10.console").read_text().splitlines()
for m in re.finditer(r"^\| `(\w+)` \| `([\w.]+)` \| l\.(\d+) \(native_sim\), l\.(\d+) \(simulated chip\) \|", notes, re.M):
    v, c, a, b = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    ok = all(cons[x-1].startswith(v+" on ") and "as required" in cons[x-1] and c in cons[x-1] and "63 of 63" in cons[x-1] for x in (a, b))
    check(ok, f"broken {v}: l.{a} and l.{b} name {c}, 63 of 63 ran")
nb = len(re.findall(r"^\| `\w+` \| `[\w.]+` \| l\.\d+", notes, re.M))
check(nb == 11, f"11 broken copies listed ({nb})")
# 3 cited result lines
for m in re.finditer(r"l\.(\d+): `([^`]+)`", notes):
    n, t = int(m.group(1)), m.group(2)
    check(cons[n-1].strip() == t.strip(), f"console l.{n} reads: {t}")
for m in re.finditer(r"l\.(\d+) \(native_sim\) and l\.(\d+) \(simulated chip\) \(63 of 63", notes):
    for x in map(int, m.groups()):
        check("63 of 63 executed test cases passed" in cons[x-1], f"console l.{x}: 63 of 63 passed")
# 4 counts
src = "".join(p.read_text() for p in (base/"tests/store/src").glob("test_*.c"))
check(len(re.findall(r"^ZTEST\(", src, re.M)) == 63, "63 ZTEST cases in tests/store/src")
check(len(re.findall(r"^ZTEST_SUITE\(", src, re.M)) == 9, "9 suites")
be = (base/"tests/store/broken_edit.py").read_text()
check(len(re.findall(r'^    "\w+": \("src/', be, re.M)) == 11, "11 variants in broken_edit.py")
# 5 files named in section 1 exist
for m in re.finditer(r"^\| `([^`]+)`", notes.split("## 2.")[0], re.M):
    for part in m.group(1).split(","):
        pth = part.strip().strip("`")
        if "*" in pth or "/" not in pth: continue
        check((base/pth).exists() or any((base/pth.split("[")[0]).parent.glob(pathlib.Path(pth).name.split("[")[0]+"*")), f"path exists: {pth}")
# 6 last line
check(nl[-1].startswith("RESULT: done"), "last line is the RESULT line")
check("questions_for_owner" in notes, "questions_for_owner present")
# 7 K2 counts
k2 = (base/"build-logs/step6/u2-k2-grep.log").read_text()
for s in ["disk_access_read 1", "disk_access_write 1", "disk_access_ioctl 2", "DISK_IOCTL_CTRL_DEINIT 2", "DISK_IOCTL_GET_SECTOR_COUNT 1", "crc32_ieee_update 2"]:
    check(s in k2, f"K2 grep log has '{s}'")
# 8 statements: no number words claimed beyond checked: 59 of 62, 126 of 126
for f, s in [("u2-dev1.console", "59 of 62 executed test cases passed"), ("u2-short8.console", "126 of 126 executed test cases passed")]:
    check(s in (base/"build-logs/step6"/f).read_text(), f"{f} contains '{s}'")
# 9 searches
check("none found" in (base/"build-logs/step6/u2-search-pins.log").read_text(), "pin search: none found")
check(not re.search(r"\bk_[a-z_]+\(", "".join(l for l in (base/"build-logs/step6/u2-search-pure.log").read_text().splitlines(True) if "#include" not in l and "# pure" not in l)), "pure files: no k_ call")
print(f"\nclaims checked: {checked}, failed: {len(bad)}")
