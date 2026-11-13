# Compare every U2 row of the ring netlist with Nordic's Table 33 (nPM1304 datasheet text copy)
import csv,re,sys
D=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/datasheets/npm1304_datasheet_v1_0.txt")
N=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/netlist.csv")
lines=[l.strip() for l in open(D).read().splitlines()[13380:13560] if l.strip()]
table={}
for i,l in enumerate(lines):
    if re.fullmatch(r'[A-E][1-7](, [A-E][1-7])?',l):
        for b in l.split(', '): table[b]=lines[i+1]
print('Table 33 balls read:',len(table))
rows=[r for r in csv.DictReader(open(N)) if r['reference']=='U2']
print('U2 rows in netlist:',len(rows))
bad=0
for r in rows:
    t=table.get(r['pin_number'])
    ok = t==r['pin_name']
    if not ok: bad+=1
    print(r['pin_number'],r['pin_name'],'| Table 33:',t,'|',r['net'] or '(no connect)','|','OK' if ok else 'DIFF')
missing=sorted(set(table)-{r['pin_number'] for r in rows})
print('balls in Table 33 not in netlist:',missing)
print('RESULT differences',bad)
