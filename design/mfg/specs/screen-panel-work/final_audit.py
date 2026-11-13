"""Final audit: every number in final-reply.txt must appear in the delivered page, the options file, verify.log,
calc.log, read_board2.log, check_docs logs or headings-check.log; prints each number with the first file and line
where it is found. Also checks the reply length and the quoted verify.log last line.
Run: python3 final_audit.py > logs/final-audit.log 2>&1"""
import re
from pathlib import Path

W = Path(__file__).resolve().parent
S = W.parent
reply = (W / "final-reply.txt").read_text()
files = [S / "screen-panel-custom.md", W / "connection-options.md", W / "verify.log", W / "logs/calc.log",
         W / "logs/read_board2.log", W / "logs/check_docs-before.log", W / "logs/check_docs-after.log",
         W / "logs/check_docs-reads.log", W / "logs/headings-check.log", W / "logs/verify-broken.log",
         W / "logs/verify-broken-quote.log", W / "logs/read_face_b.log", W / "logs/verify-broken2.log", W / "logs/check_docs-after2.log", W / "logs/commit-id-search.log", S.parent.parent / "parts/thin-bezel-parts.md", S.parent.parent / "parts/full-face-screen.md", S.parent.parent / "ecad/ring/pcb/board-notes-r2.md", S.parent.parent / "ecad/ring-route-b/notes.md", S.parent.parent / "ecad/ring-route-c/notes.md", S.parent.parent / "ecad/ring-route-d/notes.md", S.parent.parent / "ecad/ring-route-e/notes.md", S.parent.parent / "ecad/ring-route-f/notes.md"]
texts = {f: f.read_text().splitlines() for f in files}
NUM = re.compile(r"(?<![A-Za-z0-9_.])\d+(?:\.\d+)?(?![A-Za-z0-9_]|\.\d)")
n = bad = 0
for ln, line in enumerate(reply.splitlines(), 1):
    if line.startswith("- /Users") or line.startswith("- .../"):
        body = re.sub(r"\S*/\S*", " ", line)
    else:
        body = re.sub(r"\S+\.(?:py|md|svg|log|txt)\b", " ", line)
    body = re.sub(r"^\d+\.\s", " ", body)
    for num in NUM.findall(body):
        n += 1
        hit = None
        for f, L in texts.items():
            for i, t in enumerate(L, 1):
                if re.search(r"(?<![0-9.])" + re.escape(num) + r"(?![0-9])", t):
                    hit = (f.name, i)
                    break
            if hit:
                break
        if hit:
            print(f"reply L{ln}: {num} -> {hit[0]}:{hit[1]}")
        else:
            bad += 1
            print(f"reply L{ln}: {num} NOT FOUND")
last = (W / "verify.log").read_text().strip().splitlines()[-1]
print(f"verify.log last line: {last!r}; quoted in reply: {last in reply}")
opt_last = (W / "connection-options.md").read_text().strip().splitlines()[-1]
print(f"options last line starts with RESULT: done: {opt_last.startswith('RESULT: done')}")
page = (S / "screen-panel-custom.md").read_text()
print(f"page last heading: {re.findall(r'^## (.*)$', page, re.M)[-1]}")
print(f"reply characters: {len(reply)} (limit 3500)")
print(f"reply ends with questions_for_owner block: {'questions_for_owner:' in reply}")
print(f"claims (numbers) checked {n}, not found {bad}")
