#!/usr/bin/env python3
"""List the small parts of the circuit board file that lie inside the new microphone outlines or their 0.2 mm keep-out.
Reads design/ecad/ring/pcb/placement-report.csv (read only; columns ref, anchor_ref, anchor_pad, net, centre_to_pad_mm, x_model, y_model, rot_deg;
the board file's x_model and y_model are the inside model's axes, board-notes.md line 25). Part centres only: the part bodies are not in that file.
New outlines: check_mic_path.py MICS (centres -10.8 and 10.8, Y -4.8, 4.0 along X, 3.0 along Y)."""
import csv

SRC = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/ecad/ring/pcb/placement-report.csv")
NEW = {"U5": (-10.8, -4.8), "U6": (10.8, -4.8)}
L, W, KEEP = 4.0, 3.0, 0.2

rows = list(csv.DictReader(open(SRC)))
print(f"{SRC}: {len(rows)} rows")
n = 0
for r in rows:
    if r["ref"] in ("U5", "U6"):
        print(f"{r['ref']} today at ({r['x_model']}, {r['y_model']}) -> new centre {NEW[r['ref']]}")
        continue
    x, y = float(r["x_model"]), float(r["y_model"])
    for u, (cx, cy) in NEW.items():
        if abs(x - cx) <= L / 2 + KEEP and abs(y - cy) <= W / 2 + KEEP:
            inside = abs(x - cx) <= L / 2 and abs(y - cy) <= W / 2
            n += 1
            print(f"{r['ref']} (net {r['net']}, anchored to {r['anchor_ref']} {r['anchor_pad']}) centre ({x}, {y}) {'INSIDE' if inside else 'in the 0.2 keep-out of'} the new {u} outline")
print(f"parts to move: {n}")
