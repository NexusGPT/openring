# Runs grep -n -F for every "Quote: <path> | <text>" line of the review file.
import subprocess,sys
ROOT=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/")
rev=ROOT+'design/ecad/risk-review.md'
n=bad=0
for i,l in enumerate(open(rev,encoding='utf-8').read().splitlines(),1):
    if not l.startswith('Quote: '): continue
    path,text=l[7:].split(' | ',1)
    n+=1
    p=subprocess.run(['grep','-n','-F','--',text,ROOT+path],capture_output=True,text=True)
    hit=p.stdout.splitlines()
    if p.returncode==0:
        print(f'FOUND review line {i}: {path}:{hit[0].split(":",1)[0]} | {text}')
    else:
        bad+=1
        print(f'NOT FOUND review line {i}: {path} | {text} | rc {p.returncode} {p.stderr.strip()}')
print(f'quotes checked {n}, not found {bad}')
