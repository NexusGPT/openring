import sys, re, collections
f = sys.argv[1]
t = open(f).read()
items = re.split(r'\n(?=\[)', t)
kinds = collections.Counter(); unc = []; other = collections.defaultdict(list)
for it in items:
    m = re.match(r'\[(\w+)\]: (.*)', it)
    if not m: continue
    kinds[m.group(1)] += 1
    if m.group(1) == 'unconnected_items':
        unc.append(re.findall(r'@\(.*?\): (.*)', it))
    else:
        other[m.group(1)].append(it.replace('\n', ' | ')[:230])
print("violations by kind (key = KiCad rule id):")
for k, v in kinds.most_common(): print(f"  {k}: {v}")
nets = collections.Counter(); parts = collections.Counter(); pins = collections.Counter()
for u in unc:
    for line in u:
        m = re.search(r'\[([^\]]+)\]', line); 
        p = re.search(r'Pad (\S+) \[.*?\] of (\S+)', line)
        if m: nets[m.group(1)] += 1
        if p: parts[p.group(2)] += 1
print("unconnected items:", len(unc))
print("nets with an unconnected item (count of ends):", len(nets))
print("  " + ", ".join(sorted(nets)))
print("parts holding an unconnected pad end (count):", parts.most_common(15))
for k in other:
    if k != 'unconnected_items':
        print("sample", k, ":", other[k][0])
