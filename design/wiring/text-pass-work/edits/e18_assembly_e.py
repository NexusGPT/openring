D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/assembly/assembly.md"
LD="lead-decisions.md row "
M9="model-v9-notes.md section m"
EDITS=[
(F,"| 9 | Radio corner seams, only if adopted |","| 9 | Radio corner seams (RC1, the lead's default; the owner can overrule) |",M9+" row assembly.md lines 62, 84, 158, 165, 270, 345, 376"),
(F,"the first bench housing (B8) with the cast-in-place route of step 21,","the first bench housing (B8) with the cast-in-place route of step 21 (before the first ring a test strip of the circuit stack in a 0.3 mm skin is cast and cut, item 36),",LD+"'item 36' 2026-11-13 03:56"),
]
