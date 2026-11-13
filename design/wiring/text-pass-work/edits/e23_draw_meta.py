D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/tools/draw.py"
EDITS=[
(F,'''    ("flex-tail-thumb", "Band flex tail, joystick side", "FLEX1",''','''    ("footstiffener", "Foot stiffener of a band flex tail, under the main board", "FLEX1 or FLEX2 foot stiffener", "Polyimide, 0.10 (band-interface.md section 1)"),
    ("flex-tail-thumb", "Band flex tail, joystick side", "FLEX1",''',"the foot stiffener sheets (model-v9-notes.md section m, draw.py main() stem rule) carried the title of the tail they overwrote before the stem rule; each now has its own sheet and needs its own title block row"),
]
