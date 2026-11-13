D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/tools/draw.py"
EDITS=[
(F,'''f"{part} (STEP: {step_path})" if step_path''','''step_path if step_path''',"draw.py FILE row: shorter so it fits the title block"),
(F,'f"design/mfg/parts/{part}/{f.name}"','f"{f.name} in design/mfg/parts/{part}/"',"same"),
]
