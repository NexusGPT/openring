D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
M=D+"mfg/specs/main-board.md"
B=D+"mfg/specs/band-flex-tails.md"
LD="lead-decisions.md row "
EDITS=[
(M,"7. Test pads: bom.csv lists 15 plus 4 plus 3 test pads on the board; their positions come from the layout.","7. Test pads: 15 (TP1, TP3, TP4, TP5, TP6, TP8, TP9, TP11, TP12, TP14, TP15, TP17, TP18, TP19, TP21; design/ecad/ring/parts.csv) after the four of 'ring board round 2' are dropped (TP13, TP16, TP22, TP2: the debug log is send-only, DBG_TX, and the programming pads stay); their positions come from the layout.",LD+"'ring board round 2, test pads and crystal' 2026-11-13 05:26"),
(M,"456 (board 0.3 mm, 6 layers),","456 (board 0.3 mm; the line said 6 layers, 4 copper layers since the board plan),","lead-decisions.md row '7, 11 (part), W2' 00:39"),
(B,"both are the v7 drawings until they are redrawn from the files below.","both are redrawn from the model v9 files on 2026-11-13 (the foot stiffeners are drawn as flex-tail-thumb-footstiffener-us7 to -us13 and flex-tail-away-footstiffener-us7 to -us13, .svg and .pdf, in the same folder).","model-v9-notes.md section m row draw.py main() stem rule; redraw of this pass"),
]
