P=(__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/assembly/assembly.md")
s=open(P,encoding='utf-8').read()
old="for the cable's fold, 0.44 mm deep, X 13.725 to 14.165, Y +-6.40"
assert s.count(old)==1
s=s.replace(old,"for the cable's fold, X 13.725 to 14.165 (0.44 mm along the finger), Y +-6.40")
open(P,'w',encoding='utf-8').write(s)
