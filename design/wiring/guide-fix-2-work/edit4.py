P = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s = open(P, encoding="utf-8").read()
old = "(notes: `design/wiring/guide-fix-notes.md`). Step numbers"
assert s.count(old) == 1
s = s.replace(old, "(notes: `design/wiring/guide-fix-notes.md`). Later on 2026-11-13 steps 1, 5, 6, 7, 8 and 9 were corrected after the second wiring review: the charging pad is a soldered gold disc, the + land and the cut length of the motor leads are given, the cell is one bought pack with three tabs, and text that said the board and the ribbons did not exist was removed (notes: `design/wiring/guide-fix-2-notes.md`). Step numbers")
open(P, "w", encoding="utf-8").write(s)
print("ok")
