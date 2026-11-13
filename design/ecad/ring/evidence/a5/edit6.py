p=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s=open(p).read()
a="'4.4V 135mAh', 'Grepow custom'"
assert a in s
s=s.replace(a,"'4.35V 20-26mAh curved', 'Grepow custom'")
a="'CELL': ('custom cell, tab order and protection wiring not drawn', 'Grepow cell drawing (action 12.7)'),"
assert a in s
s=s.replace(a,"'CELL': ('custom curved cell 1.6 x 6.0 x 38 mm in the band (A5 17.3); tab order and its protection circuit (on the tab, at -77 degrees) not drawn', 'Grepow cell drawing (action 12.7, open item S12)'),")
open(p,'w').write(s)
