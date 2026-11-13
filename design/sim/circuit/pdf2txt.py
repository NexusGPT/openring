import sys, fitz
src, out = sys.argv[1], sys.argv[2]
doc = fitz.open(src)
with open(out, "w") as f:
    for i, p in enumerate(doc, 1):
        f.write("\n=====PAGE %d=====\n" % i)
        f.write(p.get_text())
print(src, len(doc), "pages")
