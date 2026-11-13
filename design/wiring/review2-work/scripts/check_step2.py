# compares the part lists of assembly.md step 2 (pass 1 and pass 2) with the KiCad position files
import csv,re
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
lines=open(R+'design/mfg/assembly/assembly.md').read().split('\n')
s2=[l for l in lines if l.startswith('- **Join:** the board parts of `design/bom.csv` to PCB1 in TWO')][0]
p1,p2=s2.split('PASS 2',1)
p2=p2.split('The two ribbon land rows')[0]
def refs(t):
    t=re.sub(r'`[^`]*`','',t)
    return set(re.findall(r'\b(?:U|C|R|L|X|J|FB|TP|ANT|LT)\d+\b',t))
g1,g2=refs(p1),refs(p2)
front={r['Ref'] for r in csv.DictReader(open(R+'design/ecad/ring/pcb/fab/ring-pos-front.csv'))}
back={r['Ref'] for r in csv.DictReader(open(R+'design/ecad/ring/pcb/fab/ring-pos-back.csv'))}
print('pos front rows',len(front),'pos back rows',len(back))
print('guide pass1 refs',len(g1),sorted(g1))
print('guide pass2 refs',len(g2))
print('back not in pass1:',sorted(back-g1))
print('pass1 not in back:',sorted(g1-back))
print('front not in pass2:',sorted(front-g2))
print('pass2 not in front:',sorted(g2-front))
print('pass2 refs that are on back:',sorted(g2&back))
print('pass1 refs that are on front:',sorted(g1&front))
