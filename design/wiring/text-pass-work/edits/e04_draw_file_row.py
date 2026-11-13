D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/tools/draw.py"
EDITS=[
(F,"def build_svg(part, shape, table=None):","def build_svg(part, shape, table=None, step_path=None):","draw.py FILE row of the title block named a folder that does not exist for the sheets that carry a file stem (for example design/mfg/parts/body-us10/)"),
(F,'''("FILE", f"{part} (STEP in design/mfg/parts/{part}/)")]''','''("FILE", f"{part} (STEP: {step_path})" if step_path else f"{part} (STEP in design/mfg/parts/{part}/)")]''',"same"),
(F,"build_svg(stem, shape, table)","build_svg(stem, shape, table, f\"design/mfg/parts/{part}/{f.name}\")","same"),
]
