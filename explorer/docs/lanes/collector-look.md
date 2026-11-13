# Lane collector-look

File: collector/extract/look_options.py (record look-options -> looks/index.json, looks/<id>.glb). Tests: collector/tests/collector-look/test_look.py (10).

- Options = every design/look/<folder>/ except viewer and shared, plus every id in design/status.json (picked, in_design, rejected). Id `<folder>-<variant>` reads out/ring-<variant>.glb; a folder named by a variant id is not listed twice.
- Missing model: option listed with glb null and a message line.
- Texts: plain-text.json if present (none exist today), else direction.md (heading, Thesis sentence cut to 20 words, bullets under the "worse" heading, 3 at most, 12 words each).
- Finishes: read at collect time from the FINISHES table of design/look/viewer/viewer.js (design/look/shared/finishes.json does not exist; gap G3 stays open in the design folder).
- Size: POSITION bounds of the file in mm; a file under 1 mm in its largest size is taken as metres. Axes are those stored in the file.
- Shipped models go through the same Y-up conversion and compression as exterior.glb (ring_model.finish).
