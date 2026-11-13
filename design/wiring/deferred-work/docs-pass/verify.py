import csv,io,re,subprocess
ROOT=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/")
new=open(ROOT+'design/wiring/deferred-triage.csv','rb').read()
old=open('triage.before.csv','rb').read()
N=list(csv.reader(io.StringIO(new.decode(),newline='')));O=list(csv.reader(io.StringIO(old.decode(),newline='')))
print('rows',len(N),'fields per row',sorted(set(len(r) for r in N)))
print('CRLF count',new.count(b'\r\n'),'LF count',new.count(b'\n'))
chg=[];oth=0
for a,b in zip(O,N):
    for i in range(5):
        if a[i]!=b[i]: oth+=1
    if a[5]!=b[5]: chg.append(b[0])
print('rows with changed state',chg,'other columns changed',oth)
closed=nf=found=0
pat=re.compile(r'(\S+) line (\d+) "(.*?)"(?= and |;|\)|\.|$| \(|,)')
for r in N[1:]:
    if r[0] not in chg: continue
    cites=re.findall(r'(\S+) line (\d+) "(.+?)"(?:\s|;|\)|,|$)',r[5]) 
    cites=[c for c in re.findall(r'(\S+) line (\d+) "((?:[^"]|(?<=\()")*?)"(?=[;. )]|$| and)',r[5])]
    is_closed=r[5].startswith('closed 2026-11-13')
    if is_closed: closed+=1
    for f,n,q in [(c[0].lstrip('('),c[1],c[2]) for c in cites]:
        lines=open(ROOT+f,encoding='utf-8').read().split('\n')
        ok=int(n)<=len(lines) and q in lines[int(n)-1]
        g=subprocess.run(['grep','-n','-F',q,ROOT+f],capture_output=True,text=True).stdout
        print('item',r[0],'closed' if is_closed else 'open','|',f,n,'|',('FOUND at line '+n) if ok else 'NOT FOUND','|grep hit lines',[x.split(':')[0] for x in g.splitlines()][:5])
        if ok: found+=1
        else: nf+=1
    if not cites: print('item',r[0],'NO CITES'); nf+=1
print('quotes found',found)
print('closed rows %d, not found %d'%(closed,nf))
