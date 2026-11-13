# Lists every design/bom.csv:N citation in assembly.md with 90 chars of text before it and the reference cell of bom row N.
import re, csv
A=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mfg/assembly/assembly.md")
B=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/bom.csv")
rows=list(csv.reader(open(B)))
n=0
for i,l in enumerate(open(A),1):
    for m in re.finditer(r"design/bom\.csv:(\d+)", l):
        k=int(m.group(1)); n+=1
        ref=rows[k-1][1] if k-1 < len(rows) else "PAST END"
        print("assembly.md:%d cites bom.csv:%d -> row ref '%s' | text: ...%s" % (i,k,ref,l[max(0,m.start()-90):m.start()].replace("\n"," ")))
print("RESULT citations=%d"%n)
