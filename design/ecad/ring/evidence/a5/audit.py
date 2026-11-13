import csv, re, os, collections, fitz, sys
R=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/")
E=R+'evidence/a5/'
bad=0; n=0
def chk(claim, got, want):
    global bad, n
    n+=1
    ok = got==want
    if not ok: bad+=1
    print(('OK   ' if ok else 'DIFF ')+claim+' | file says %r | claimed %r'%(got,want))
rep=open(E+'final_reply.txt').read(); notes=open(R+'sch-notes.md').read()
nl=list(csv.DictReader(open(R+'netlist.csv'))); pl=list(csv.DictReader(open(R+'parts.csv')))
op=list(csv.DictReader(open(R+'open-pins.csv'))); ad=list(csv.DictReader(open(R+'additions.csv')))
sy=set(x['symbol'] for x in csv.DictReader(open(R+'symbols.csv')))
chk('netlist rows',len(nl),365); chk('nets',len(set(x['net'] for x in nl if x['net'])),91)
chk('no-connect pins',sum(1 for x in nl if x['pin_type']=='no_connect'),15)
chk('parts',len(pl),113); chk('symbols',len(sy),26)
chk('sheets',len(set(p['sheet'] for p in pl)),8)
chk('open rows',len(op),89); chk('OPEN parts',sum(1 for x in op if x['pin_number']==''),3)
chk('provisional pins',sum(1 for x in op if x['pin_number']!=''),86)
k=collections.Counter(a['kind'] for a in ad)
chk('added',k['added'],34); chk('not placed',k['bom_not_placed'],20); chk('testpads',k['testpad'],22)
cl=open(E+'check_final_run.log').read().splitlines()
chk('check last line',cl[-1],'check exit 0'); chk('check RESULT line',cl[-2],'RESULT PASS netlist netlist.csv')
chk('ok lines',sum(1 for l in cl if l.startswith('ok ')),33)
chk('A5 ok lines',sorted(re.match(r'ok\s+(A5-\d+)',l).group(1) for l in cl if re.match(r'ok\s+A5-',l)),sorted('A5-%d'%i for i in range(1,11)))
er=open(E+'erc_cmd.log').read(); chk('ERC 0 violations','Found 0 violations' in er and er.strip().endswith('erc exit 0'),True)
ex=open(E+'broken/exits.txt').read().splitlines()
chk('broken copies',len(ex),10); chk('all exit 1 with own tag',all(' exit 1 ' in l and l.endswith('FAIL-lines-with-tag 1') for l in ex),True)
d=fitz.open(R+'ring-schematic.pdf'); chk('pdf pages',len(d),9)
chk('Rev A5 on every page',sum(1 for p in d if re.search(r'Rev:?\s*A5',p.get_text())),9)
rl=open(E+'render_a5.log').read(); chk('overlap total','TOTAL overlapping word pairs 0' in rl,True)
chk('pngs p1..p9',all(os.path.exists(R+'evidence/pdf_a5_p%d.png'%i) for i in range(1,10)),True)
# each cited path exists
for m in sorted(set(re.findall(r'(?:evidence/[A-Za-z0-9_./-]+|prove_a5\.sh|sch-notes\.md)',rep+notes))):
    pth=m.rstrip('.,;:')
    if '*' in pth or pth.endswith('/'): continue
    chk('path exists '+pth,os.path.exists(R+pth),True)
# last line of notes equals last line of reply
chk('RESULT line identical',notes.strip().splitlines()[-1],rep.strip().splitlines()[-1])
# conflict line numbers in notes against architecture
A=open(R+'../../architecture.md').read().splitlines()
for ln,txt in ((290,'RT1 = 10'),(439,'Wiring: two flex'),(284,'W7'),(369,'Flex strip: 6'),(373,'Microphones: one stereo'),(374,'JOY_CENTER P0.03'),(450,'JOY_CENTER spare'),(281,'W4'),(278,'W1'),(181,'MIC_B_CLK'),(182,'MIC_B_DATA'),(199,'JOY_CENTER')):
    chk('arch line %d has %r'%(ln,txt),txt in A[ln-1],True)
# 'the old joystick lines had no pull-ups': before netlist JOY nets members
bn=list(csv.DictReader(open(E+'netlist_before.csv')))
for net in ('JOY_UP','JOY_DOWN','JOY_LEFT','JOY_RIGHT','JOY_CENTER'):
    refs=sorted(set(x['reference'] for x in bn if x['net']==net))
    chk('before %s members have no R/C/D'%net,[r for r in refs if r[0] in 'RCD'],[])
# A5 count in sentences
chk('9 pad count J_BAND_B',sum(1 for x in nl if x['reference']=='J_BAND_B'),9)
chk('6 pad count J_BAND_A',sum(1 for x in nl if x['reference']=='J_BAND_A'),6)
chk('U3 pad 8 not provisional',[x for x in op if x['reference']=='U3'],[])
chk('live bom still lists J2 J3',all(re.search(r'(^|[ ,"])%s([ ,"]|$)'%j,open(R+'../../bom.csv').read(),re.M) is not None for j in ('J2','J3')),True)
print('claims checked',n,'differences',bad)
sys.exit(1 if bad else 0)
