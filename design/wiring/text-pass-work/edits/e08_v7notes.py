D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mfg/assembly/v7-update-notes.md"
EDITS=[
(F,"- The inside model v7 is not built yet. Placement.csv still holds the v6.3 light rows and the rectangular joystick_cap row (section 6, row 6).","- (Old statement of 2026-11-11, stale, checked 2026-11-13: \"The inside model v7 is not built yet. Placement.csv still holds the v6.3 light rows and the rectangular joystick_cap row (section 6, row 6).\" The inside model v7 was built and exported (`design/mfg/parts/export_parts_v7.py`), and `design/mfg/parts/index.csv` now reads `design/mech/thin/thin.py v9 built at US 9`: the model is v9, placement.csv has no light rows, and joystick_cap is the round cap CAP1.)","w11-item-values.md item 160, design/mfg/assembly/v7-update-notes.md line 29"),
]
