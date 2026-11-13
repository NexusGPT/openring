import sys, fitz
src, out = sys.argv[1], sys.argv[2]
d = fitz.open(src)
with open(out, 'w') as f:
    for i, p in enumerate(d, 1):
        f.write('\n=====PAGE %d=====\n' % i)
        f.write(p.get_text())
print(src, len(d), 'pages')
