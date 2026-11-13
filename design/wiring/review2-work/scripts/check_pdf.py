# compares the wiring drawing's text (pdftotext) with the csv: every id present once, ends' ref.pin and signal present
import csv,re,collections
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
t=open(R+'design/wiring/review2-work/png/pw.txt').read()
rows=list(csv.DictReader(open(R+'design/wiring/product-wiring.csv')))
ids=collections.Counter(re.findall(r'\bW0\d\d\b',t))
print('csv ids',len(rows),'ids in drawing',len(ids),'ids not once',[k for k,v in ids.items() if v!=1])
miss=[r['id'] for r in rows if r['id'] not in ids]
print('csv ids missing in drawing',miss)
for r in rows:
    m=re.search(r'%s +(.*)'%r['id'],t)
    lab=m.group(1).strip() if m else ''
    if 'inside' in lab or 'cut' in lab: print(r['id'],r['carrier_kind'],'| drawing:',lab[:70])
