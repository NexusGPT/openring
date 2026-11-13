import os, sys, io, csv
ROOT=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix())
try:
    import pcbnew
except ImportError:
    os.execve("/bin/bash", ["/bin/bash", ROOT+"/design/ecad/ring/pcb/run_kipy.sh", os.path.abspath(__file__)], dict(os.environ, WIRING_REEXEC="1"))
os.environ["WIRING_NO_DRC"]="1"
sys.path.insert(0, ROOT+"/design/wiring")
import build_wiring as bw
class Cap(io.StringIO):
    def close(self): self.seen=True
buf=Cap()
def fake_open(path,*a,**k):
    if os.path.abspath(path)==bw.p(bw.OUT): return buf
    return open(path,*a,**k)
bw.open=fake_open
import contextlib
with contextlib.redirect_stdout(io.StringIO()): bw.main()
new=list(csv.DictReader(io.StringIO(buf.getvalue(),newline="")))
old=list(csv.DictReader(open(ROOT+"/design/wiring/product-wiring.csv",newline="")))
print(len(new),len(old))
for a,b in zip(new,old):
    for k in b:
        if a.get(k)!=b[k]: print(b["id"],a["id"],k,repr(a.get(k))[:100],"|",repr(b[k])[:100])
