D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
F=D+"mech/light-path/light-path.md"
W="lead-decisions.md row 'item 53, part S25' 2026-11-13 03:56"
EDITS=[
(F,"# Recording light path (review finding F01)","# Recording light path (review finding F01) - history: the recording light is removed in v7 (architecture 17.30), so this study describes a part the design no longer has",W+"; w11-item-values.md item 53"),
(F,"| must be clear: open item S-L1 |","| must be clear: open item S-L1 (CLOSED 2026-11-13 with S25: the recording light is removed in v7) |",W),
(F,"- S-L1, screen maker (Tailor Pixels): confirm that the ledge glass","- S-L1 (CLOSED 2026-11-13, with part S25 of architecture.md: it checked the path of the recording light, which version v7 removed, architecture.md line 523; no supplier is asked. Part S24, the screen's metal over the antenna, stays open): screen maker (Tailor Pixels): confirm that the ledge glass",W),
(F,"in the 0.3, 6-layer board, and the copper of J1 and U5 near it.","in the 0.3, 6-layer board (the board has 4 copper layers since the board plan, and the hole is removed in v7), and the copper of J1 and U5 near it.","lead-decisions.md row '7, 11 (part), W2'; item 53"),
]
