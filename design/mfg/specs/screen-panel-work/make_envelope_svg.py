"""Draw panel-envelope.svg: top view and side view of the custom panel's room in the thin block.
Every number is taken from logs/calc.log lines (parsed) or from the cited model rows; run after calc.py.
Run: python3 make_envelope_svg.py > logs/make_envelope_svg.log 2>&1"""
import re
from pathlib import Path

W = Path(__file__).resolve().parent
log = (W / "logs/calc.log").read_text()


def grab(pat, n=1):
    m = re.search(pat, log)
    if not m:
        raise SystemExit(f"not in calc.log: {pat}")
    return [float(m.group(i + 1)) for i in range(n)]


GX, GY = grab(r"GLASS FACE outline ([\d.]+) x ([\d.]+)", 2)
RC = grab(r"corner radius ([\d.]+);")[0]
PX, PY = grab(r"pocket ([\d.]+) x ([\d.]+); clearance", 2)
MX, MY = grab(r"panel max ([\d.]+) x ([\d.]+)", 2)
L05 = grab(r"LIT with border 0.5: ([\d.]+) x ([\d.]+)", 2)
L10 = grab(r"LIT with border 1.0: ([\d.]+) x ([\d.]+)", 2)
B0, B1 = grab(r"board Z ([\d.]+)\.\.([\d.]+)", 2)
F1 = grab(r"foam [\d.]+\.\.([\d.]+)")[0]
S1 = grab(r"panel [\d.]+\.\.([\d.]+)")[0]
GU = grab(r"underside [\d.]+ - [\d.]+ = ([\d.]+);")[0]
GT = grab(r"top [\d.]+ - [\d.]+ = ([\d.]+);")[0]
FLOOR = grab(r"floor top [\d.]+ - [\d.]+ = ([\d.]+);")[0]
PMAX = grab(r"PANEL THICKNESS MAX [\d.]+ - [\d.]+ - [\d.]+ = ([\d.]+)")[0]
print("inputs", GX, GY, RC, PX, PY, MX, MY, L05, L10, B0, B1, F1, S1, GU, GT, FLOOR, PMAX)
# fixed places from the design (model coordinates), each with its source
ZONE = (-13.60, -8.75, 3.10, 6.30)      # copper-free zone, ANT_KEEPOUT in ring.kicad_pcb (logs/read_board2.log)
RCX, RCY = (-14.80, -8.60), 2.05         # radio corner RC1 (placement.csv row radio_corner)
J1 = (-11.650, -0.150, 3.35, 6.10)       # J1 of the thin plan, under face (placement.csv row screen_connector), along X 3.35, Y 6.1
TAILW, TAILY = 5.0, -0.150               # tail at most 5.0 wide, centred on J1
TP = (-14.05, -13.50)                    # tail pocket of model v9 (thin.py line 530)
BOARD = (27.2, 12.6)

S = 22.0         # px per mm
out = []


def T(x, y):     # top view: model X right, Y up
    return 40 + (x + 15.5) * S, 60 + (8.5 - y) * S


def rect_top(x0, x1, y0, y1, **k):
    a, b = T(x0, y1)
    c, d = T(x1, y0)
    attrs = " ".join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{c - a:.1f}" height="{d - b:.1f}" {attrs}/>')


def text(x, y, s, size=11, anchor="middle", **k):
    attrs = " ".join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-family="Helvetica" {attrs}>{s}</text>')


def dim_h(x0, x1, y, label, off=-8):
    a, b = T(x0, y)
    c, _ = T(x1, y)
    out.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{b:.1f}" stroke="#333" stroke-width="0.8" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    text((a + c) / 2, b + off, label, 10)


def dim_v(x, y0, y1, label, off=6):
    a, b = T(x, y0)
    _, d = T(x, y1)
    out.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{a:.1f}" y2="{d:.1f}" stroke="#333" stroke-width="0.8" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    text(a + off, (b + d) / 2, label, 10, "start")


# ---- top view
text(40, 30, "TOP VIEW (seen from above, through the cover glass). X along the finger: hand end left, fingertip right. Y across: thumb side up. mm.", 12, "start", font_weight="bold")
a, b = T(-GX / 2, GY / 2)
out.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{GX * S:.1f}" height="{GY * S:.1f}" rx="{RC * S:.1f}" fill="#f2f2f2" stroke="#000" stroke-width="1.2"/>')
rect_top(-PX / 2, PX / 2, -PY / 2, PY / 2, fill="none", stroke="#555", stroke_width="0.8", stroke_dasharray="4 2")
rect_top(-MX / 2, MX / 2, -MY / 2, MY / 2, fill="#dfe8f5", stroke="#1f4e9c", stroke_width="1.2")
rect_top(-L05[0] / 2, L05[0] / 2, -L05[1] / 2, L05[1] / 2, fill="#c3e6c3", stroke="#2a7a2a", stroke_width="1")
rect_top(-L10[0] / 2, L10[0] / 2, -L10[1] / 2, L10[1] / 2, fill="none", stroke="#2a7a2a", stroke_width="1", stroke_dasharray="5 3")
rect_top(ZONE[0], ZONE[1], ZONE[2], ZONE[3], fill="url(#hatch)", stroke="#b00", stroke_width="1.2")
rect_top(RCX[0], RCX[1], RCY, GY / 2, fill="none", stroke="#b00", stroke_width="0.8", stroke_dasharray="2 2")
rect_top(J1[0] - J1[2] / 2, J1[0] + J1[2] / 2, J1[1] - J1[3] / 2, J1[1] + J1[3] / 2, fill="none", stroke="#a36a00", stroke_width="1", stroke_dasharray="3 2")
rect_top(TP[0], -MX / 2, TAILY - TAILW / 2, TAILY + TAILW / 2, fill="#ffd27f", stroke="#a36a00", stroke_width="1")
dim_h(-GX / 2, GX / 2, GY / 2 + 0.9, f"glass face {GX:.2f} (corner R {RC:.1f})")
dim_h(-MX / 2, MX / 2, -GY / 2 - 0.6, f"panel outline max {MX:.2f}", 16)
dim_h(-L05[0] / 2, L05[0] / 2, -1.6, f"lit, border 0.5: {L05[0]:.2f} x {L05[1]:.2f}", -6)
dim_h(-L10[0] / 2, L10[0] / 2, -3.6, f"lit, border 1.0 (dashed): {L10[0]:.2f} x {L10[1]:.2f}", -6)
dim_v(GX / 2 + 0.5, -GY / 2, GY / 2, f"{GY:.2f}")
dim_v(MX / 2 - 0.4, -MY / 2, MY / 2, f"{MY:.2f}", -40)
x, y = T(-11.2, 4.8)
text(x, y - 2, "antenna zone", 10, fill="#b00")
text(x, y + 10, "X -13.60..-8.75, Y 3.10..6.30", 9, fill="#b00")
x, y = T(-11.0, 2.4)
text(x, y, "radio corner from Y 2.05 (dotted)", 9, fill="#b00")
x, y = T(-14.4, TAILY - TAILW / 2 - 0.5)
text(x, y + 6, f"tail exit, max {TAILW:.1f} wide, centred Y {TAILY:.2f}", 10, "start", fill="#a36a00")
x, y = T(J1[0], J1[1] - J1[3] / 2 - 0.25)
text(x + 30, y + 26, "J1 on the board's under face (option A)", 9, fill="#a36a00")
x, y = T(0, 2.6)
text(x, y, "pocket in the body (dashed grey) " + f"{PX:.2f} x {PY:.2f}; panel max = pocket less 0.05 each side", 10)

# ---- side view (section along X at Y = -0.15, hand end and middle)
Y0 = 470
SZ = 60.0       # px per mm in Z (exaggerated) and X at the same 60 for the hand-end detail
text(40, Y0 - 20, "SIDE VIEW, hand end, section along the finger through the tail (Z scale = X scale, 60 px per mm). Z from the block underside.", 12, "start", font_weight="bold")


def Sx(x):
    return 80 + (x + 14.8) * SZ


def Sz(z):
    return Y0 + 260 - z * SZ


def srect(x0, x1, z0, z1, **k):
    attrs = " ".join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    out.append(f'<rect x="{Sx(x0):.1f}" y="{Sz(z1):.1f}" width="{(x1 - x0) * SZ:.1f}" height="{(z1 - z0) * SZ:.1f}" {attrs}/>')


XR = -6.0   # right edge of the detail
srect(-GX / 2, XR, 0.0, GU, fill="#e6e6e6", stroke="none")                 # body metal (schematic)
srect(-PX / 2, XR, FLOOR, GU, fill="#ffffff", stroke="none")                # cavity
srect(TP[0], TP[1], B0 - 0.3, S1, fill="#ffffff", stroke="#a36a00", stroke_width="0.6", stroke_dasharray="3 2")
srect(-GX / 2, XR, GU, GT, fill="#cfe3f7", stroke="#000", stroke_width="0.8")      # flat glass
srect(-MX / 2, XR, S1, GU, fill="#f7f0c8", stroke="#888", stroke_width="0.5")        # adhesive
srect(-MX / 2, XR, F1, S1, fill="#dfe8f5", stroke="#1f4e9c", stroke_width="1.2")    # panel envelope
srect(-BOARD[0] / 2, XR, F1 - 0.1, F1, fill="#f5d0e0", stroke="#888", stroke_width="0.5")  # foam
srect(-BOARD[0] / 2, XR, B0, B1, fill="#7fb77f", stroke="#2a5a2a", stroke_width="0.8")    # board
srect(J1[0] - J1[2] / 2, J1[0] + J1[2] / 2, 1.43 - 0.9, 1.43, fill="#e8d2a6", stroke="#a36a00", stroke_width="0.8")  # J1
# tail path (option A): from the panel end down the pocket, under the board to J1's front face
pts = [(-MX / 2, S1 - 0.1), (-13.85, S1 - 0.1), (-13.85, 1.43 - 0.45), (J1[0] - J1[2] / 2 + 0.2, 1.43 - 0.45)]
out.append('<polyline points="' + " ".join(f"{Sx(x):.1f},{Sz(z):.1f}" for x, z in pts) + '" fill="none" stroke="#a36a00" stroke-width="3"/>')
for z, lab in ((0.0, "0 block underside"), (FLOOR, f"{FLOOR:.2f} floor top"), (B0, f"{B0:.2f} board underside"), (B1, f"{B1:.2f} board top"),
               (F1, f"{F1:.2f} foam top = panel back"), (S1, f"{S1:.2f} panel front (max)"), (GU, f"{GU:.3f} glass underside"), (GT, f"{GT:.4f} glass top")):
    out.append(f'<line x1="{Sx(XR):.1f}" y1="{Sz(z):.1f}" x2="{Sx(XR) + 18:.1f}" y2="{Sz(z):.1f}" stroke="#333" stroke-width="0.6"/>')
    text(Sx(XR) + 22, Sz(z) + (13 if z in (S1, B1) else 4), lab, 10, "start")
out.append(f'<line x1="{Sx(-8.0):.1f}" y1="{Sz(B1):.1f}" x2="{Sx(-8.0):.1f}" y2="{Sz(GU):.1f}" stroke="#b00" stroke-width="1" marker-start="url(#ar)" marker-end="url(#ar)"/>')
text(Sx(-8.0) + 6, Sz(GT) - 12, f"{GU - B1:.2f} = foam 0.10 + panel {PMAX:.2f} max + adhesive 0.10", 10, "start", fill="#b00")
text(Sx(-12.0), Sz(0.2), "J1 (0.9 high, under face)", 10, fill="#a36a00")
text(Sx(-13.7), Sz(GT) - 10, f"tail pocket X {TP[0]}..{TP[1]}", 10, fill="#a36a00")
text(Sx(-10.5), Sz(0.0) + 22, f"panel envelope: outline max {MX:.2f} x {MY:.2f}, thickness max {PMAX:.2f}", 10, fill="#1f4e9c")

H = Y0 + 300
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{H}" viewBox="0 0 900 {H}">',
       '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0,1 L8,4 L0,7 z" fill="#333"/></marker>',
       '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#b00" stroke-width="1.2"/></pattern></defs>',
       '<rect width="100%" height="100%" fill="#ffffff"/>'] + out + [
       f'<text x="40" y="{H - 10}" font-size="10" font-family="Helvetica">Made by screen-panel-work/make_envelope_svg.py from logs/calc.log. Not to be scaled for production; the numbers rule.</text>', '</svg>']
(W / "panel-envelope.svg").write_text("\n".join(svg))
print(f"wrote {W / 'panel-envelope.svg'} ({len(out)} elements)")
print("RESULT svg done")
