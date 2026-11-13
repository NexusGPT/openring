P = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s = open(P, encoding="utf-8").read()
old = "(BT1 with PRT1 and RT1 inside it as one part,"
assert s.count(old) == 1
s = s.replace(old, "(BT1 with PRT1 (`cell_protection`) and RT1 inside it as one part,")
open(P, "w", encoding="utf-8").write(s)
print("ok")
