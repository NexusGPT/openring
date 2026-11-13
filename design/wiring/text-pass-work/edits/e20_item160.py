D=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/")
W="w11-item-values.md item 160"
EDITS=[
(D+"supplier-package/v3-notes.md","1. **Exterior files still hold a `light` solid.**","1. **Exterior files still hold a `light` solid.** (Checked 2026-11-13: stale for the files now on disk. `grep -c -a -i light` gives 0 on all seven `design/look/s1/out/ring-merged32h-us*.step` and all eight `ring-merged32h*.glb`, log `design/wiring/text-pass-work/check_light_solid.log`. The statement below describes the files of the package at the time.)",W),
(D+"supplier-package/v3-notes.md","4. `design/mfg/specs/record-cap.md` has no v7 content and is not in the package.","4. `design/mfg/specs/record-cap.md` has no v7 content and is not in the package. (Checked 2026-11-13: `grep -c v7` gives 0, true; the page describes a part the design removed and now says so at its top.)",W),
(D+"mfg/specs/record-cap.md","# Specification: record cap reference CAP2 (design/bom.csv line 78, design/mfg/part-map.csv)","# Specification: record cap reference CAP2 (design/bom.csv line 78, design/mfg/part-map.csv) - THIS PAGE DESCRIBES A PART THE DESIGN REMOVED: the ring has one control, the joystick (architecture 17.11); there is no record cap",W+"; brief: record-cap.md says so at its top"),
]
