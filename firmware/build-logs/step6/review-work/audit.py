"""Final audit of firmware/docs/step6-review.md (and the final reply). Pulls by itself: every file:line citation, every
quote followed by its citation, every W/ evidence file, every count of the form "N of M". Prints each with what it found.
Usage: python3 -I audit.py <review.md> [<reply.md>]"""
import pathlib
import re
import sys

ROOT = pathlib.Path((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix()))
F = ROOT / "firmware"
W = F / "build-logs/step6/review-work"
texts = [pathlib.Path(p).read_text() for p in sys.argv[1:]]
text = "\n".join(texts)
index = {}
for p in list(F.rglob("*")) + [ROOT / "design/firmware.md"]:
    if p.is_file() and "/broken/copy-" not in str(p) and "/review-work/" not in str(p) and "/docs/review/" not in str(p):
        index.setdefault(p.name, []).append(p)


def resolve(name):
    name = name.strip("`")
    if name.startswith("F/"):
        p = F / name[2:]
        return [p] if p.exists() else []
    if name.startswith("W/"):
        p = W / name[2:]
        return [p] if p.exists() else []
    if "/" in name:
        for base in (ROOT, F):
            if (base / name).exists():
                return [base / name]
        return [p for p in index.get(pathlib.Path(name).name, []) if str(p).endswith(name)]
    return index.get(name, [])


n = bad = 0
# 1. file:line and file:a to b citations
for m in re.finditer(r"([A-Za-z0-9_./-]+\.(?:c|h|py|md|log|console|conf|txt))(?::| l\.)(\d+)(?: to (\d+))?", text):
    name, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
    cands = resolve(name)
    n += 1
    ok = False
    for p in cands:
        L = p.read_text(errors="replace").splitlines()
        if 1 <= a <= b <= len(L):
            ok = True
            print(f"CITE ok   {name}:{a}-{b} -> {p.relative_to(ROOT)} | {L[a-1].strip()[:110]}")
            break
    if not ok:
        bad += 1
        print(f"CITE BAD  {name}:{a}-{b} candidates={len(cands)}")
# 2. quotes followed by a citation: `quote` (file:line)
for m in re.finditer(r"`([^`]{8,})`[^`|]{0,40}?\(([A-Za-z0-9_./-]+\.(?:c|h|md|log|console|conf))?:?(?:l\.)?(\d+)\)", text):
    q, name, line = m.group(1), m.group(2), int(m.group(3))
    if name is None:
        continue
    n += 1
    hit = False
    for p in resolve(name):
        L = p.read_text(errors="replace").splitlines()
        if 1 <= line <= len(L) and q.replace("\\|", "|") in L[line - 1]:
            hit = True
    print(("QUOTE ok  " if hit else "QUOTE BAD ") + f"{name}:{line} `{q[:70]}`")
    bad += 0 if hit else 1
# 3. evidence files W/...
for m in sorted(set(re.findall(r"W/([A-Za-z0-9_.-]+)", text))):
    n += 1
    ok = (W / m).exists()
    bad += 0 if ok else 1
    print(("EVID ok   " if ok else "EVID BAD  ") + m)
# 4. counts "N of M"
for m in sorted(set(re.findall(r"\b(\d+) of (\d+)\b", text))):
    n += 1
    print(f"COUNT     {m[0]} of {m[1]}")
# 5. finding ids and severities agree with the counts line
sev = re.findall(r"\| R6-(\d+) \| (blocker|major|minor|note) \|", text)
cnt = {s: sum(1 for _, x in sev if x == s) for s in ("blocker", "major", "minor", "note")}
print("SEVERITY counts from the table:", cnt)
for s, word in (("blocker", "blocker"), ("major", "major"), ("minor", "minor"), ("note", "notes")):
    for m in re.finditer(r"(\d+) " + word + r"\b", text):
        n += 1
        ok = int(m.group(1)) == cnt[s]
        bad += 0 if ok else 1
        print(("SEV ok    " if ok else "SEV BAD   ") + m.group(0))
print(f"AUDIT: {n} claims checked, {bad} without a match")
