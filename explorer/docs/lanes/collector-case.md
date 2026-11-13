# Lane collector-case

Files: `collector/extract/case.py` (record case, `case/index.json`, `case/case.glb`), tests `collector/tests/collector-case/test_case.py` (8).

Model: one node per STEP file stem of `design/case/out/parts/` (names kept, `+` and `-` included), built with build123d (this python, else `design/.venv/bin/python` in a subprocess), converted to glTF Y-up, meshopt-compressed with `gltf-transform`, held under GLB_MAX_MB. Of the `ring_US<n>_*` files only the smallest n is seated (the ring on the pins). `lid` is `lid_node`; the hinge is the long axis and centre of the node whose stem starts with `hinge`, in DESIGN coordinates (Z up). Node `part_ids`: the first `_` token of the stem when it is a reference of `case-bom.csv` (a range token such as `P1-P4` covers its numbers).

Facts (each with the file and line holding it, found by sentence, never by position): size from `case_size.txt`, cell capacity, transfer minutes per recorded hour, minutes a ring charge takes, recorded hours copied in one ring charge, ring charges per full case cell, from `case-architecture.md`. Size is value `33.6 x 33.4 x 55.2` unit `mm`; cell is value 700 unit `mAh`. A fact whose sentence is gone is left out and named in the manifest message.

Transfer figure: the file says 6.37 min per recorded hour (version C2, 464.4 MB at 1.216 MB/s). The lead's 6.3 and the test plan's 6.3 are the older rounding; the record holds the file's 6.37.

Part ids: `case:<ref>` for every ref of `case-bom.csv`, split like the parts reader; the lines live in `parts.json`. Supplier items: the section 8 table ("Items only a supplier can close"), who and ask taken from its columns.

Stale: the file says "Built against ... architecture.md version A1"; the runner compares it with the design's current version and sets `stale`. The manifest message carries `design/status.json` `areas.case.why` (the plain reason). Not tested against a real KiCad/other tool; the model test builds made-up STEP boxes with build123d and is skipped when the design venv is absent.
