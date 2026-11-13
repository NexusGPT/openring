"""Replace the citation loop of audit.py so that a backticked file without a line number (group 3) is a
whole-file citation and quotes (group 4) attach to the last citation. Writes audit.py in place (my own file)."""
p = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/review/review-3/audit.py")
t = open(p, encoding="utf-8").read()
old_start = t.index("for ln_no, ln in enumerate(text.splitlines(), 1):")
old_end = t.index("# findings table counts")
new = '''for ln_no, ln in enumerate(text.splitlines(), 1):
    cur = None
    last_path = None
    for m in tok.finditer(ln):
        if m.group(2):
            path = m.group(1) or last_path
            if not path:
                bad.append(f"review line {ln_no}: bare :{m.group(2)} with no earlier path")
                continue
            last_path = path
            fl = lines_of(path)
            checked += 1
            n = int(m.group(2))
            if fl is None:
                bad.append(f"review line {ln_no}: {path} does not open")
                cur = None
            elif n < 1 or n > len(fl):
                bad.append(f"review line {ln_no}: {path}:{n} beyond {len(fl)} lines")
                cur = None
            else:
                ok += 1
                cur = (path, n, fl)
        elif m.group(3):
            path = m.group(3)
            fl = lines_of(path)
            checked += 1
            if fl is None:
                bad.append(f"review line {ln_no}: {path} does not open")
                cur = None
            else:
                ok += 1
                last_path = path
                cur = (path, 0, fl)
        elif m.group(4) and cur:
            q = m.group(4).replace("\\\\|", "|").replace('\\\\"', '"')
            path, n, fl = cur
            window = " ".join(fl) if n == 0 else " ".join(fl[max(0, n - 3):n + 2])
            parts = [x.strip() for x in re.split(r"\\.\\.\\.", q) if x.strip()]
            checked += 1
            if all(x in window for x in parts):
                ok += 1
            else:
                bad.append(f"review line {ln_no}: quote not in {path}{':' + str(n) if n else ''}: {q[:70]}")
'''
t = t[:old_start] + new + t[old_end:]
open(p, "w", encoding="utf-8").write(t)
print("patched")
