import sys, fitz
path = sys.argv[1]
pages = sys.argv[2] if len(sys.argv) > 2 else None
doc = fitz.open(path)
sel = range(len(doc))
if pages:
    a, b = pages.split('-'); sel = range(int(a)-1, min(int(b), len(doc)))
print(f"# {path} pages={len(doc)}")
for i in sel:
    t = doc[i].get_text()
    print(f"\n--- page {i+1} ({len(t)} chars) ---\n{t}")
