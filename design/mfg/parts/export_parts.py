"""Maker files of model v9 (inside model design/mech/thin/thin.py: v8 band circuits as drawn, v9 board parts at the board plan's places, resin radio corner RC1),
every ring size US 7 to 13, and index.csv. The v7 version of this file is kept as export_parts_v7.py.
v9: each size is built by design/mech/thin/out/v9/export/export_size.py; the two band circuit folders (flex-tail-thumb, flex-tail-away) are not
written here (their files come from design/mech/thin/out/v8/export_ribbons.py); their index rows are merged from out/v8/rows_flex_usN.json.
(v7 text follows.) Maker files of model v7 (inside model design/mech/thin/thin.py: round joystick, no recording light, pad row at X -1.0), every ring size US 7 to 13, and index.csv.

Each size is built in its own process by design/mech/thin/out/v7-export/export_size.py with the exterior and bore of that
size's fit check (every size: look/s1/out/ring-merged32h-usN.step, the accepted exterior; bores from the
measures json of each file). US 9 also writes the parts that are the same at every size.
Run from this folder: nice -n 19 ../../.venv/bin/python export_parts.py [sizes...]   (then check_parts.py)
Without sizes it only merges the rows already written (out/v7-export/rows_usN.json) into index.csv."""
import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
OUTD = os.path.join(DESIGN, "mech/thin/out/v9/export")
FLEXD = os.path.join(DESIGN, "mech/thin/out/v8")          # v9: rows of the band circuit files (rows_flex_usN.json)
PY = os.path.join(DESIGN, ".venv/bin/python")
SIZES = {n: (f"ring-merged32h-us{n}.step", b) for n, b in ((7, 17.3196), (8, 18.1324), (9, 18.9452), (10, 19.758), (11, 20.5708), (12, 21.3836), (13, 22.1964))}
COLS = ["part", "ring_size", "format", "path", "units", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm",
        "bbox_xmin", "bbox_ymin", "bbox_zmin", "volume_mm3", "solids", "triangles", "watertight", "source", "status"]


def run(size):
    ext, bore = SIZES[size]
    env = dict(os.environ, THIN_EXTERIOR=os.path.join(DESIGN, "look/s1/out", ext), THIN_OVERRIDE=f"bore_d={bore}")
    args = ["nice", "-n", "19", PY, os.path.join(OUTD, "export_size.py"), str(size)] + (["all"] if size == 9 else [])
    with open(os.path.join(OUTD, f"export_us{size}.log"), "w") as f:
        r = subprocess.run(args, env=env, stdout=f, stderr=subprocess.STDOUT)
    print(f"US {size}: export_size.py exit {r.returncode}", flush=True)
    return r.returncode


def merge():
    rows = []
    for s in (9, 7, 8, 10, 11, 12, 13):
        p = os.path.join(OUTD, f"rows_us{s}.json")
        if os.path.isfile(p):
            rows += json.load(open(p))
        pf = os.path.join(FLEXD, f"rows_flex_us{s}.json")
        if os.path.isfile(pf):
            rows += json.load(open(pf))
    with open(os.path.join(HERE, "index.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in rows:
            w.writerow([r.get(c, "") for c in COLS])
    print(f"index.csv: {len(rows)} rows")


if __name__ == "__main__":
    bad = 0
    for a in sys.argv[1:]:
        bad += run(int(a)) != 0
    merge()
    sys.exit(1 if bad else 0)
