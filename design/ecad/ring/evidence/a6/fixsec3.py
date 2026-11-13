P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/evidence/a6/notes_a6_section.md")
s = open(P).read()
a = "RESULT: PENDING\n"
b = "RESULT: done, check_netlist.py ends \"RESULT PASS netlist netlist.csv\" (exit 0), KiCad ERC \"Found 0 violations\" (0 errors), check_bom.py 0 failures; F07 settled with the level shifter U10 SN74AXC4T774RSVR on sources (chip I/O follows VDD at 1.8 V, storage VIH 1.875 V at 3.0 V, storage has no 1.8 V option) and F14 settled as the 8 x 10 name grid right with the ball pitch left open to Nordic; open points O1 to O8\n"
assert s.count(a) == 1
open(P, 'w').write(s.replace(a, b))
