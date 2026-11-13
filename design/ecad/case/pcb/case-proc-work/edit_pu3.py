F=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/board-notes.md")
t=open(F,encoding="utf-8").read()
a="cannot be seen at 10 times, and no file gives a check for them: open, for the lead."
b="cannot be seen at 10 times; (g) below is the only check the files support, and it does not prove them all (it lists what it does not prove)."
assert t.count(a)==1
t=t.replace(a,b)
open(F,"w",encoding="utf-8").write(t)
print("ok")
