import csv,re
D=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/")
front=[r['Ref'] for r in csv.DictReader(open(D+'ecad/ring/pcb/fab/ring-pos-front.csv'))]
back=[r['Ref'] for r in csv.DictReader(open(D+'ecad/ring/pcb/fab/ring-pos-back.csv'))]
l=open(D+'mfg/assembly/assembly.md').read().splitlines()[95]
old=set(re.findall(r'(?<![A-Za-z0-9_])([A-Z]{1,4}\d+)(?![A-Za-z0-9_])',l))
print('front',len(front),'back',len(back))
print('in front not in old step 2:',sorted(set(front)-old))
print('in old step 2 not in front:',sorted(old-set(front)))
print('front list:',', '.join(front))
