# final audit: pulls every backticked path, quoted phrase and number-bearing RESULT/log citation out of the review and checks each against saved files
import re,os,subprocess
R=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/"); W=R+'design/wiring/review2-work/'
t=open(R+'design/wiring/wiring-review-2.md').read()
n=0;bad=0
def chk(ok,what):
    global n,bad; n+=1
    if not ok: bad+=1; print('NOMATCH',what)
for p in sorted(set(re.findall(r'`([^`]+)`',t))):
    if '/' in p or p.endswith(('.log','.md','.csv','.txt','.png','.rpt')):
        c=[W+p, W+p.split('review2-work/')[-1], R+p, R+'design/wiring/'+p, R+'design/ecad/band/'+p, R+'design/case/'+p, R+'design/ecad/case/pcb/'+p, R+'design/mfg/assembly/'+p, R+p.split(':')[0], R+'design/ecad/ring/pcb/fab/'+p]
        chk(any(os.path.exists(x.rstrip('/')) for x in c) or p.startswith(('design/ecad/ring-lines','review2-work/scripts')),'path '+p)
alltext=''.join(open(os.path.join(d,f),errors='ignore').read() for d,_,fs in os.walk(W) for f in fs if f.endswith(('.log','.txt','.csv','.rpt')))
for q in [q for line in t.split('\n') for q in re.findall(r'"([^"]{6,}?)"',line)]:
    if q[0] in ' .,;)' or q[-1]==' ' or '`' in q: continue
    src=alltext+open(R+'design/mfg/assembly/assembly.md').read()+open(R+'design/ecad/case/pcb/board-notes.md').read()+open(R+'design/ecad/band/band-interface.md').read()+open(R+'design/case/case-architecture.md').read()
    chk(q in src,'quote '+q[:60])
for r in ['RESULT lines=67 fails=0 uncovered=0 dups=0','RESULT pairing fails=0 of 28','RESULT parity wrong=0','RESULT guide facts diffs=0','heights above 2.20: 14','Found 1 unconnected pads']:
    chk(r in alltext,'result '+r)
s=open(W+'drc/summary.log').read(); chk(s.count('Found 0 DRC violations')==17 and s.count('Found 0 unconnected pads')==17 and len(s.strip().split('\n'))==51,'17 boards 0/0, 51 lines')
chk(len(re.findall(r'^== ',open(W+'fakes/run.log').read(),re.M))==8 and 'fails=0 uncovered=0 dups=0' not in open(W+'fakes/run.log').read(),'8 of 8 fakes caught')
chk(open(W+'silk-case_main.log').read().count('\nTEXT')==5,'case_main 5 texts')
d=subprocess.run(['git','-C',R,'diff','--stat','24587355','HEAD','--','design/wiring/product-wiring.csv','design/wiring/product-wiring.pdf','design/wiring/ring-case-contact.csv','design/mfg/assembly/assembly.md','design/ecad/ring/pcb/ring.kicad_pcb','design/ecad/case/pcb/case_main.kicad_pcb','design/ecad/case/pcb/case_pins.kicad_pcb','design/ecad/case/pcb/board-notes.md','design/case/case-architecture.md','design/ecad/band/band-interface.md','design/ecad/ring/netlist.csv','design/ecad/case/netlist.csv','design/ecad/band'],capture_output=True,text=True)
chk(d.stdout.strip()=='' and d.returncode==0,'judged files unchanged at HEAD')
cnt=t.count('| major |'); chk(cnt==1,'major count 1'); chk(t.count('| minor |')==6,'minor count 6'); chk(t.count('| note |')==7,'note count 7')
chk(t.strip().split('\n')[-1].startswith('RESULT: done, FAIL'),'last line')
print('claims checked',n,'no match',bad)
