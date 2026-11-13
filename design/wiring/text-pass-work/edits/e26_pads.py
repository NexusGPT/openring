D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/specs/main-board.md"
W="lead's answer 1 of 2026-11-13: 15 pads, list from design/ecad/ring/parts.csv; lead-decisions.md row 'ring board round 2' 05:26"
EDITS=[
(F,"carries only the 19 flat test pads (the screen face","carries only the 15 flat test pads (19 before ring board round 2; the screen face",W),
(F,"(the 19 test pads TP1 to TP22) is the screen face","(the 15 test pads TP1, TP3, TP4, TP5, TP6, TP8, TP9, TP11, TP12, TP14, TP15, TP17, TP18, TP19, TP21; 19 in the plan file until round 2) is the screen face",W),
]
