p=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s=open(p).read()
a="        if p['reference'] in A5_KEEP and p['reference'] in bom and p['mpn'] != bom[p['reference']]:\n            print('A5 keeps', p['reference'], repr(p['mpn']), '; bom.csv still says', bom[p['reference']])\n        elif p['reference'] in bom"
assert a in s
s=s.replace(a,"        if p['reference'] in bom")
b="# references whose maker part changed in A5 (architecture 16.4, 17.4): bom.csv is behind, the lead updates it\nA5_KEEP = {'U3', 'U5', 'U6', 'M1', 'SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'J1'}\n"
assert b in s
s=s.replace(b,"")
open(p,'w').write(s)
