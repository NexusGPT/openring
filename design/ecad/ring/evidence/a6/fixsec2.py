P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/evidence/a6/notes_a6_section.md")
s = open(P).read()
a = "K10 in `design/architecture.md` line @@arch_chg@@ (\"Charge voltage"
b = "K10 in `design/architecture.md` line @@arch_chg@@ (WAS: \"Charge voltage"
assert s.count(a) == 1; s = s.replace(a, b)
a = "still says \"nPM1300 ... charger 32 to 800 mA"
b = "still says (WAS: \"nPM1300 ... charger 32 to 800 mA"
assert s.count(a) == 1; s = s.replace(a, b)
a = "termination 3.5 to 4.45 V\"; 17.13 replaces it."
b = "termination 3.5 to 4.45 V\"); 17.13 replaces it."
assert s.count(a) == 1; s = s.replace(a, b)
open(P, 'w').write(s)
