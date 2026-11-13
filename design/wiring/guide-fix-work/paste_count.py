import re,sys
cur=None;cnt={}
for l in open(sys.argv[1]):
    m=re.match(r'^(D\d+)\*$',l.strip())
    if m: cur=m.group(1)
    if l.strip().endswith('D03*'): cnt[cur]=cnt.get(cur,0)+1
print(sys.argv[1].split('/')[-1],cnt)
