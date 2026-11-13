import re,sys
t=open(sys.argv[1]).read()
for m in re.finditer(r'\(footprint "([^"]+)"\s*(?:\(layer "([^"]+)"\))?.*?\(at ([-\d. ]+)\)',t,re.S):
    pass
# simpler: split into footprint blocks
blocks=t.split('\n\t(footprint ')
for b in blocks[1:]:
    ref=re.search(r'\(property "Reference" "([^"]+)"',b)
    at=re.search(r'\n\t\t\(at ([-\d. ]+)\)',b)
    lay=re.search(r'\n\t\t\(layer "([^"]+)"\)',b)
    if ref and ref.group(1) in sys.argv[2:]:
        print(ref.group(1),lay.group(1) if lay else '?',at.group(1) if at else '?')
        for p in re.finditer(r'\(pad "([^"]*)" \w+ \w+\s*\(at ([-\d. ]+)\)',b):
            print('  pad',p.group(1),p.group(2))
