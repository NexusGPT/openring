#!/usr/bin/env python3
"""Assembly drawing of the whole ring (US 9 outside STEP from look/s1/out) with the
angular positions (architecture 17.8, 17.10) and the bore per size (sizes.csv).
Writes design/mfg/drawings/ring-assembly.svg and .pdf. Exit 1 on any read error."""
import csv, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import draw
D = draw.MFG.parent
OUT = D / "look/s1/out"
try:
    from build123d import import_step
    shape = import_step(str(OUT / "ring-merged32c-us9.step"))
    svg, scale, dims = draw.build_svg("ring-assembly", shape)
    rows = list(csv.DictReader(open(OUT / "sizes.csv")))
except Exception as e:
    print("ERROR", e); sys.exit(1)
x, y = 250.0, 100.0
t = ['<g font-size="3.4">',
     f'<text x="{x}" y="{y-60}" font-weight="bold">ANGLES (degrees from the top of the band, plus = thumb side; architecture 17.8, 17.10)</text>']
for i, s in enumerate(["Joystick nub and frame: +150", "Record button: +88",
                       "Charging pads (outside): -150 (other side)",
                       "Vibration motor: +51", "Cell: -39 through the bottom to +167 (17.10)"]):
    t.append(f'<text x="{x}" y="{y-53+i*5}">{s}</text>')
t.append(f'<text x="{x}" y="{y-24}" font-weight="bold">BORE PER SIZE (sizes.csv)</text>')
t.append(f'<text x="{x}" y="{y-18}">US size</text><text x="{x+30}" y="{y-18}">bore mm</text><text x="{x+65}" y="{y-18}">band outer diameter mm</text>')
for i, r in enumerate(rows):
    yy = y - 12 + i * 4.6
    t.append(f'<text x="{x}" y="{yy:.1f}">{r["us_size"]}</text><text x="{x+30}" y="{yy:.1f}">{float(r["bore_mm"]):.2f}</text><text x="{x+65}" y="{yy:.1f}">{float(r["band_outer_diameter_mm"]):.2f}</text>')
t.append('</g>')
svg = svg.replace("STEP in design/mfg/parts/ring-assembly/", "STEP: design/look/s1/out/ring-merged32c-us9.step").replace("</svg>", "\n".join(t) + "\n</svg>")
o = draw.MFG / "drawings"
(o / "ring-assembly.svg").write_text(svg, encoding="utf-8")
draw.write_pdf(o / "ring-assembly.svg", o / "ring-assembly.pdf")
print(f"OK ring-assembly scale {draw.scale_text(scale)} size {dims}")
