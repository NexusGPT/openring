P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/make_netlist.py")
s = open(P).read()
old = "'S18: Nordic. The nPM1304 orderable part number is not read from a Nordic page by this task: the order code is left empty (architecture 17.9 S18, 17.13)'"
new = "'S18: Nordic. Order code left empty on the lead\\'s instruction (architecture 17.9 S18). Note for the lead: parts/research-npm1304.md section 4 lists nPM1304-CAAA-R and -R7 from Nordic spec Table 11, which disagrees with the brief\\'s \"not in the research\"; not used here'"
assert s.count(old) == 1
open(P, 'w').write(s.replace(old, new))
