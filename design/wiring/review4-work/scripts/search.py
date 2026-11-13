# usage: search.py <regex> <file>...  prints file:line: snippet (200 chars around the first hit)
import re,sys
rx=re.compile(sys.argv[1])
for f in sys.argv[2:]:
    for i,l in enumerate(open(f,errors="replace"),1):
        m=rx.search(l)
        if m:
            a=max(0,m.start()-150); print("%s:%d: %s"%(f,i,l[a:m.end()+150].strip()))
