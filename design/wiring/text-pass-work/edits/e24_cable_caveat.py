D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
W="lead-decisions.md row 'item 96, rest (screen stack)': both can change with the screen cable study"
EDITS=[
(D+"mfg/assembly/assembly.md","Nitto SCF AN010, no adhesive, held by the screen's pressure |","Nitto SCF AN010, no adhesive, held by the screen's pressure (can change with the screen cable study) |",W),
(D+"mfg/assembly/assembly.md","| tesa 69404, 0.10 mm optically clear adhesive, glass to screen over the whole face (17.30) |","| tesa 69404, 0.10 mm optically clear adhesive, glass to screen over the whole face (17.30; can change with the screen cable study) |",W),
(D+"mfg/specs/body.md","Nitto SCF AN010, 0.10 mm, no adhesive, held by the screen's pressure (item 96, rest) |","Nitto SCF AN010, 0.10 mm, no adhesive, held by the screen's pressure (item 96, rest; can change with the screen cable study) |",W),
(D+"mfg/specs/body.md","tesa 69404, optically clear, 100 um (item 96, rest) |","tesa 69404, optically clear, 100 um (item 96, rest; can change with the screen cable study) |",W),
]
