p=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/check_netlist.py")
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
rep("usage: check_netlist.py [netlist.csv]   (a second file lets a broken copy be tested)\"\"\"",
    "usage: check_netlist.py [netlist.csv [sheet_folder]]   (a second file lets a broken copy be tested; a folder holding\nring*.kicad_sch and ring-schematic.pdf lets check A5-10 test a broken copy)\"\"\"")
rep("NETFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'netlist.csv')",
    "NETFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'netlist.csv')\nSCHDIR = sys.argv[2] if len(sys.argv) > 2 else HERE")
rep("files = sorted(f for f in os.listdir(HERE) if f.startswith('ring') and f.endswith('.kicad_sch'))\nnotA5 = [f for f in files if '(rev \"A5\")' not in open(os.path.join(HERE, f)).read() or '(rev \"A3\")' in open(os.path.join(HERE, f)).read()]",
    "files = sorted(f for f in os.listdir(SCHDIR) if f.startswith('ring') and f.endswith('.kicad_sch'))\nnotA5 = [f for f in files if '(rev \"A5\")' not in open(os.path.join(SCHDIR, f)).read() or '(rev \"A3\")' in open(os.path.join(SCHDIR, f)).read()]")
rep("pdf = fitz.open(os.path.join(HERE, 'ring-schematic.pdf'))","pdf = fitz.open(os.path.join(SCHDIR, 'ring-schematic.pdf'))")
open(p,'w').write(s)
