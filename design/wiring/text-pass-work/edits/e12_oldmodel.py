D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
W="w11-item-values.md items 102, 103 (old block model replaced by design/mech/thin/)"
NOTE="OLD BLOCK MODEL, replaced by the inside model in design/mech/thin/ (thin.py, model v9; notes design/mech/thin/model-v9-notes.md) with the exterior in design/look/s1/; the numbers below describe the one-block model of version A1 and are not edited"
EDITS=[
(D+"mech/mech-notes.md","# Ring recorder, 3D model notes (mechanics step; architecture.md A2; round 2)","# Ring recorder, 3D model notes (mechanics step; architecture.md A2; round 2) - "+NOTE,W),
(D+"mech/CHECKLIST.md","# Checklist, ring 3D model (brief from team-lead, 2026-11-10, start 15:04)","# Checklist, ring 3D model (brief from team-lead, 2026-11-10, start 15:04) - "+NOTE,W),
(D+"mech/ring.py","#!/usr/bin/env python3\n\"\"\"Parametric 3D model of the AI ring recorder","#!/usr/bin/env python3\n# "+NOTE+".\n\"\"\"Parametric 3D model of the AI ring recorder",W),
]
