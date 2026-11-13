import re, csv
W=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/")
det=set()
for l in open(W+"checks-harden-work/assembly/pinned-review4-guide.log"):
    m=re.match(r"TOKEN line (\d+): design/bom\.csv:(\d+) ",l)
    if m: det.add((int(m.group(1)),int(m.group(2))))
j=list(csv.DictReader(open(W+"review4-work/bom-cites-judged.csv")))
wrong={(int(r['assembly_line']),int(r['cited_row'])) for r in j if r['verdict']=='wrong'}
right={(int(r['assembly_line']),int(r['cited_row'])) for r in j if r['verdict']!='wrong'}
print("judged rows",len(j),"wrong",len(wrong),"right",len(right))
print("wrong and rejected by T1:",len(wrong&det),"; wrong and NOT rejected:",sorted(wrong-det))
print("right but rejected (false alarms):",sorted(right&det))
print("rejected bom.csv citations total",len(det),"; rejected but not in the judged list:",sorted(det-wrong-right))
