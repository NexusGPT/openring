P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s=open(P,encoding='utf-8').read()
old="what changed is in `design/mfg/assembly/v7-update-notes.md`."
assert s.count(old)==1
s=s.replace(old,old+" On 2026-11-13 the board faces, step 2 (two solder passes), steps 4, 5 and 15 (screen turned 180 degrees, cable into J1 on the screen face) and the rows that depend on them were brought to the board as built (notes: `design/wiring/guide-fix-notes.md`).",1)
open(P,'w',encoding='utf-8').write(s)
